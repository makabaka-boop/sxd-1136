import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_processor import (
    load_grading, save_grading,
    load_submissions, load_assignments, load_courses,
    get_extension_info
)

st.set_page_config(page_title="助教 - 批改管理", layout="wide")

st.title("📝 助教批改台")
st.markdown("管理作业批改状态和评分")

tab1, tab2, tab3 = st.tabs(["📋 待批改列表", "✅ 已批改记录", "📊 批改统计"])

with tab1:
    st.subheader("待批改作业")
    
    submissions_df = load_submissions()
    grading_df = load_grading()
    assignments_df = load_assignments()
    courses_df = load_courses()
    
    if grading_df.empty or submissions_df.empty:
        st.info("暂无待批改作业，请先上传数据")
    else:
        pending = grading_df[grading_df['status'] == 'pending'].copy()
        
        if not pending.empty:
            if not submissions_df.empty:
                sub_cols = ['submission_id', 'assignment_id', 'student_id', 'student_name']
                sub_cols = [c for c in sub_cols if c in submissions_df.columns]
                pending = pending.merge(
                    submissions_df[sub_cols], 
                    on=['assignment_id', 'student_id'] if 'student_id' in pending.columns and 'student_id' in submissions_df.columns else 'assignment_id', 
                    how='left'
                )
            if not assignments_df.empty:
                pending = pending.merge(
                    assignments_df[['assignment_id', 'assignment_name', 'course_id']], 
                    on='assignment_id', how='left'
                )
            if not courses_df.empty:
                pending = pending.merge(
                    courses_df[['course_id', 'course_name']], 
                    on='course_id', how='left'
                )
            
            st.write(f"共有 **{len(pending)}** 份待批改作业")
            
            course_filter = st.selectbox(
                "按课程筛选",
                options=["全部"] + list(pending['course_name'].dropna().unique())
            )
            
            if course_filter != "全部":
                pending = pending[pending['course_name'] == course_filter]
            
            for idx, row in pending.iterrows():
                student_name = row.get('student_name', row.get('student_id', '未知学生'))
                assignment_id = row['assignment_id']
                student_id = row['student_id']
                
                ext_info = get_extension_info(assignment_id, student_id)
                ext_badge = ""
                if ext_info and ext_info['approval_status'] == 'approved':
                    ext_badge = " 📅 [已延期]"
                elif ext_info and ext_info['approval_status'] == 'pending':
                    ext_badge = " ⏳ [待审批]"
                
                with st.expander(f"📄 {row.get('assignment_name', row['assignment_id'])} - {student_name}{ext_badge}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**课程:** {row.get('course_name', '未知')}")
                        st.write(f"**作业:** {row.get('assignment_name', row['assignment_id'])}")
                        st.write(f"**学生:** {student_name}")
                        st.write(f"**提交ID:** {row.get('submission_id', 'N/A')}")
                        
                        if ext_info:
                            st.write("---")
                            if ext_info['approval_status'] == 'approved':
                                st.success(f"📅 已批准延期: 原截止 {ext_info['original_due_date']} → 延期至 {ext_info['extended_due_date']}")
                                if ext_info.get('reason'):
                                    st.caption(f"延期原因: {ext_info['reason']}")
                            elif ext_info['approval_status'] == 'pending':
                                st.warning(f"⏳ 延期待审批: 申请延期至 {ext_info['extended_due_date']}")
                                if ext_info.get('reason'):
                                    st.caption(f"申请原因: {ext_info['reason']}")
                            else:
                                st.error(f"❌ 延期申请已被拒绝")
                    
                    with col2:
                        with st.form(f"grade_form_{row['grading_id']}"):
                            score = st.number_input("得分", min_value=0, max_value=100, value=80, key=f"score_{row['grading_id']}")
                            feedback = st.text_area("评语", value="", key=f"feedback_{row['grading_id']}")
                            status = st.selectbox("状态", options=["graded", "grading"], key=f"status_{row['grading_id']}")
                            submitted = st.form_submit_button("提交批改")
                            
                            if submitted:
                                grading_df = load_grading()
                                mask = grading_df['grading_id'] == row['grading_id']
                                grading_df.loc[mask, 'score'] = score
                                grading_df.loc[mask, 'feedback'] = feedback
                                grading_df.loc[mask, 'status'] = status
                                grading_df.loc[mask, 'graded_date'] = datetime.now().strftime('%Y-%m-%d')
                                save_grading(grading_df)
                                st.success("批改已提交！")
                                st.rerun()
        else:
            st.success("🎉 所有作业都已批改完成！")

with tab2:
    st.subheader("已批改记录")
    
    grading_df = load_grading()
    
    if grading_df.empty:
        st.info("暂无批改记录")
    else:
        graded = grading_df[grading_df['status'] == 'graded'].copy()
        
        if not assignments_df.empty:
            graded = graded.merge(
                assignments_df[['assignment_id', 'assignment_name', 'course_id']], 
                on='assignment_id', how='left'
            )
        if not courses_df.empty:
            graded = graded.merge(
                courses_df[['course_id', 'course_name']], 
                on='course_id', how='left'
            )
        
        st.write(f"共批改 **{len(graded)}** 份作业")
        
        extensions_loaded = __import__('utils.data_processor', fromlist=['load_extensions']).load_extensions()
        if not extensions_loaded.empty:
            approved_ext = extensions_loaded[extensions_loaded['approval_status'] == 'approved'][
                ['assignment_id', 'student_id', 'extended_due_date', 'reason']
            ]
            graded = graded.merge(
                approved_ext,
                on=['assignment_id', 'student_id'],
                how='left'
            )
            graded['延期说明'] = graded.apply(
                lambda x: f"已延期至 {x['extended_due_date']}" if pd.notna(x['extended_due_date']) else "无",
                axis=1
            )
        
        display_cols = [col for col in ['assignment_name', 'course_name', 'student_name', 'score', 'feedback', 'graded_date', 'grader_name', '延期说明'] if col in graded.columns]
        st.dataframe(graded[display_cols], use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if len(graded) > 0 and 'score' in graded.columns:
                avg_score = graded['score'].mean()
                st.metric("平均分", f"{avg_score:.1f}")
        with col2:
            if len(graded) > 0:
                st.metric("批改总数", len(graded))

with tab3:
    st.subheader("批改统计")
    
    grading_df = load_grading()
    assignments_df = load_assignments()
    
    if not grading_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        status_counts = grading_df['status'].value_counts()
        total = len(grading_df)
        graded = status_counts.get('graded', 0)
        pending = status_counts.get('pending', 0)
        grading = status_counts.get('grading', 0)
        
        with col1:
            st.metric("总作业数", total)
        with col2:
            st.metric("已批改", graded)
        with col3:
            st.metric("批改中", grading)
        with col4:
            progress = (graded / total * 100) if total > 0 else 0
            st.metric("批改进度", f"{progress:.1f}%")
        
        st.progress(progress / 100)
        
        st.write("### 按作业统计")
        if not assignments_df.empty and 'assignment_id' in grading_df.columns:
            grading_with_assign = grading_df.merge(
                assignments_df[['assignment_id', 'assignment_name']], 
                on='assignment_id', how='left'
            )
            assign_stats = grading_with_assign.groupby('assignment_name').agg(
                总数=('grading_id', 'count'),
                已批改=('status', lambda x: (x == 'graded').sum()),
                待批改=('status', lambda x: (x == 'pending').sum()),
                平均分=('score', lambda x: x.dropna().mean())
            ).reset_index()
            st.dataframe(assign_stats, use_container_width=True, hide_index=True)
    else:
        st.info("暂无批改数据")

st.sidebar.header("📥 批量导入批改")
grading_file = st.sidebar.file_uploader("上传批改CSV", type=['csv'], key='grading_upload_sidebar')
if grading_file is not None:
    try:
        df = pd.read_csv(grading_file)
        st.sidebar.write("预览:")
        st.sidebar.dataframe(df.head())
        if st.sidebar.button("导入批改数据", type="primary"):
            existing = load_grading()
            if not existing.empty:
                merged = pd.concat([existing, df], ignore_index=True)
                merged = merged.drop_duplicates(subset=['grading_id'], keep='last')
            else:
                merged = df
            save_grading(merged)
            st.sidebar.success(f"成功导入 {len(df)} 条批改数据")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"导入失败: {e}")
