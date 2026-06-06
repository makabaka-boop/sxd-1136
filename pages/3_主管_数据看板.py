import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from utils.data_processor import (
    calculate_metrics, load_thresholds, save_thresholds,
    get_default_thresholds
)
from utils.risk_analyzer import (
    analyze_risks, get_risk_summary, get_submission_trend, get_grading_progress
)
from utils.report_generator import generate_daily_report, list_reports, get_report_path
from utils.scheduler import simulate_daily_import

def _get_risk_type_name(risk_type: str) -> str:
    names = {
        'low_submission_rate': '课程提交率低',
        'student_overdue': '学员逾期过多',
        'grading_delay': '批改延迟过高',
        'inactive_student': '学员不活跃'
    }
    return names.get(risk_type, risk_type)

def _get_object_name_short(item: dict) -> str:
    if 'course_name' in item:
        return item['course_name']
    elif 'student_name' in item:
        return item['student_name']
    elif 'grader_name' in item:
        return item['grader_name']
    return '未知'

st.set_page_config(page_title="主管 - 数据看板", layout="wide")

st.title("📊 主管数据看板")
st.markdown("实时监控课程进度与风险预警")

if 'thresholds' not in st.session_state:
    st.session_state.thresholds = load_thresholds()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 总览看板", 
    "⚠️ 风险清单", 
    "🎯 阈值设置",
    "📄 日报管理"
])

with tab1:
    st.subheader("核心指标看板")
    
    metrics = calculate_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "作业提交率", 
            f"{metrics['submission_rate']}%",
            delta=None,
            help="已提交作业数 / 应提交作业总数"
        )
        submission_threshold = st.session_state.thresholds['submission_rate']
        if metrics['submission_rate'] < submission_threshold:
            st.error(f"⚠️ 低于阈值 {submission_threshold}%")
        elif metrics['submission_rate'] < submission_threshold + 10:
            st.warning(f"⚡ 接近阈值 {submission_threshold}%")
    
    with col2:
        st.metric(
            "批改进度", 
            f"{metrics['grading_progress']}%",
            help="已批改作业数 / 已提交作业数"
        )
    
    with col3:
        st.metric(
            "逾期作业数", 
            metrics['overdue_count'],
            help="超过截止日期提交的作业数量"
        )
        overdue_threshold = st.session_state.thresholds['overdue_count']
        if metrics['overdue_count'] >= overdue_threshold:
            st.error(f"⚠️ 超过阈值 {overdue_threshold} 个")
    
    with col4:
        st.metric(
            "平均批改延迟", 
            f"{metrics['avg_grading_delay']} 天",
            help="从提交到批改的平均天数"
        )
        delay_threshold = st.session_state.thresholds['grading_delay']
        if metrics['avg_grading_delay'] > delay_threshold:
            st.error(f"⚠️ 超过阈值 {delay_threshold} 天")
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("提交趋势")
        trend_df = get_submission_trend()
        if not trend_df.empty:
            fig = px.line(trend_df, x='日期', y='提交数', title='每日作业提交趋势')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无提交数据")
    
    with col2:
        st.subheader("批改进度")
        grading_data = get_grading_progress()
        if sum(grading_data.values()) > 0:
            labels = list(grading_data.keys())
            values = list(grading_data.values())
            colors = ['#27ae60', '#f39c12', '#3498db']
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors))])
            fig.update_layout(title='批改状态分布', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无批改数据")
    
    st.write("---")
    
    st.subheader("学员活跃度")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总学员数", metrics['total_students'])
    with col2:
        st.metric("活跃学员", metrics['active_students'])
    with col3:
        st.metric("活跃率", f"{metrics['activity_rate']}%")

with tab2:
    st.subheader("风险预警清单")
    
    risks = analyze_risks(st.session_state.thresholds)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总风险数", risks['total_risks'])
    with col2:
        st.metric("高风险", risks['high_risk_count'], delta_color="inverse")
    with col3:
        st.metric("中风险", risks['medium_risk_count'], delta_color="inverse")
    
    st.write("---")
    
    risk_df = get_risk_summary(risks)
    if not risk_df.empty:
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
        
        st.write("### 高风险详情")
        for risk in risks['high_risks']:
            with st.expander(f"🔴 {risk['message']} - {_get_object_name_short(risk)}"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write("**指标:**", risk['metric'])
                with col2:
                    st.write("**当前值:**", risk['value'])
                with col3:
                    st.write("**阈值:**", risk['threshold'])
                with col4:
                    st.write("**风险等级:** 高")
    else:
        st.success("✅ 当前无风险项，一切正常！")
    
    st.write("---")
    
    with st.expander("📋 查看所有风险明细"):
        if risks['all_risks']:
            for risk in risks['all_risks']:
                level_color = "🔴" if risk['level'] == 'high' else "🟡"
                st.write(f"{level_color} **{_get_risk_type_name(risk['type'])}** - {_get_object_name_short(risk)}")
                st.caption(f"{risk['metric']}: {risk['value']} (阈值: {risk['threshold']})")

with tab3:
    st.subheader("预警阈值设置")
    st.markdown("拖动滑块调整预警阈值，所有页面风险清单将实时刷新")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        submission_rate_val = st.slider(
            "提交率预警阈值 (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.thresholds['submission_rate'],
            step=1.0,
            help="当课程提交率低于此值时触发预警",
            key='slider_submission_rate'
        )
    
    with col2:
        overdue_count_val = st.slider(
            "逾期数预警阈值 (个)",
            min_value=1,
            max_value=20,
            value=int(st.session_state.thresholds['overdue_count']),
            step=1,
            help="当学员逾期作业达到此数量时触发预警",
            key='slider_overdue_count'
        )
    
    with col3:
        grading_delay_val = st.slider(
            "批改延迟预警阈值 (天)",
            min_value=0,
            max_value=14,
            value=int(st.session_state.thresholds['grading_delay']),
            step=1,
            help="当平均批改延迟超过此值时触发预警",
            key='slider_grading_delay'
        )
    
    new_thresholds = {
        'submission_rate': submission_rate_val,
        'overdue_count': overdue_count_val,
        'grading_delay': grading_delay_val
    }
    
    if new_thresholds != st.session_state.thresholds:
        st.session_state.thresholds = new_thresholds
    
    st.write("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 保存阈值设置", type="primary"):
            save_thresholds(new_thresholds)
            st.success("阈值设置已保存！")
    
    with col2:
        if st.button("🔄 恢复默认值"):
            default = get_default_thresholds()
            save_thresholds(default)
            st.session_state.thresholds = default
            st.success("已恢复默认阈值")
            st.rerun()
    
    st.write("---")
    
    st.subheader("实时预览")
    st.info("调整阈值后，「总览看板」「风险清单」「阈值设置」页面将同步更新")
    
    preview_risks = analyze_risks(st.session_state.thresholds)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总风险数", preview_risks['total_risks'])
    with col2:
        st.metric("高风险", preview_risks['high_risk_count'])
    with col3:
        st.metric("中风险", preview_risks['medium_risk_count'])
    
    preview_df = get_risk_summary(preview_risks)
    if not preview_df.empty:
        st.dataframe(preview_df, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("日报管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### 生成日报")
        report_date = st.date_input("选择报告日期", value=datetime.now())
        if st.button("📊 生成今日日报", type="primary"):
            with st.spinner("正在生成日报..."):
                report_path = generate_daily_report(report_date.strftime('%Y-%m-%d'))
                st.success(f"✅ 日报已生成: {report_path}")
                
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.download_button(
                        label="📥 下载日报 HTML",
                        data=html_content,
                        file_name=f"daily_report_{report_date.strftime('%Y-%m-%d')}.html",
                        mime="text/html"
                    )
    
    with col2:
        st.write("### 模拟定时任务")
        if st.button("🔄 模拟每日数据导入"):
            with st.spinner("正在模拟数据导入..."):
                report_path = simulate_daily_import()
                st.success("✅ 数据导入完成，日报已生成")
                st.rerun()
    
    st.write("---")
    
    st.write("### 历史报告")
    reports = list_reports()
    if reports:
        for report in reports:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"📄 {report['filename']}")
            with col2:
                st.caption(f"生成时间: {report['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            with col3:
                if os.path.exists(report['filepath']):
                    with open(report['filepath'], 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    st.download_button(
                        label="下载",
                        data=html_content,
                        file_name=report['filename'],
                        mime="text/html",
                        key=f"dl_{report['filename']}"
                    )
    else:
        st.info("暂无历史报告")
