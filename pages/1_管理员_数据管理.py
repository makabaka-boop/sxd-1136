import streamlit as st
import pandas as pd
import os
from utils.data_processor import (
    load_courses, save_courses,
    load_assignments, save_assignments,
    load_submissions, save_submissions,
    load_activity, save_activity,
    load_grading, save_grading,
    generate_pending_grading
)
from utils.scheduler import generate_sample_data, generate_sample_csv_files

st.set_page_config(page_title="管理员 - 数据管理", layout="wide")

st.title("🔧 管理员控制台")
st.markdown("管理课程、作业和学生数据")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 课程管理", 
    "📝 作业管理", 
    "📤 提交记录管理",
    "👥 活跃度管理",
    "⚡ 快速操作"
])

with tab1:
    st.subheader("课程管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### 现有课程")
        courses_df = load_courses()
        if not courses_df.empty:
            st.dataframe(courses_df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无课程数据")
    
    with col2:
        st.write("### 上传课程CSV")
        course_file = st.file_uploader("选择课程CSV文件", type=['csv'], key='course_upload')
        if course_file is not None:
            try:
                df = pd.read_csv(course_file)
                st.write("预览:")
                st.dataframe(df.head())
                if st.button("导入课程数据", type="primary"):
                    existing = load_courses()
                    if not existing.empty:
                        merged = pd.concat([existing, df], ignore_index=True)
                        merged = merged.drop_duplicates(subset=['course_id'], keep='last')
                    else:
                        merged = df
                    save_courses(merged)
                    st.success(f"成功导入 {len(df)} 条课程数据")
                    st.rerun()
            except Exception as e:
                st.error(f"导入失败: {e}")
        
        st.write("### 手动添加课程")
        with st.form("add_course_form"):
            course_id = st.text_input("课程ID")
            course_name = st.text_input("课程名称")
            instructor = st.text_input("授课老师")
            start_date = st.date_input("开始日期")
            end_date = st.date_input("结束日期")
            submitted = st.form_submit_button("添加课程")
            
            if submitted and course_id and course_name:
                new_course = pd.DataFrame([{
                    'course_id': course_id,
                    'course_name': course_name,
                    'instructor': instructor,
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                }])
                existing = load_courses()
                if not existing.empty:
                    merged = pd.concat([existing, new_course], ignore_index=True)
                else:
                    merged = new_course
                save_courses(merged)
                st.success("课程添加成功")
                st.rerun()

with tab2:
    st.subheader("作业管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### 现有作业")
        assignments_df = load_assignments()
        if not assignments_df.empty:
            st.dataframe(assignments_df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无作业数据")
    
    with col2:
        st.write("### 上传作业CSV")
        assignment_file = st.file_uploader("选择作业CSV文件", type=['csv'], key='assignment_upload')
        if assignment_file is not None:
            try:
                df = pd.read_csv(assignment_file)
                st.write("预览:")
                st.dataframe(df.head())
                if st.button("导入作业数据", type="primary"):
                    existing = load_assignments()
                    if not existing.empty:
                        merged = pd.concat([existing, df], ignore_index=True)
                        merged = merged.drop_duplicates(subset=['assignment_id'], keep='last')
                    else:
                        merged = df
                    save_assignments(merged)
                    st.success(f"成功导入 {len(df)} 条作业数据")
                    st.rerun()
            except Exception as e:
                st.error(f"导入失败: {e}")
        
        st.write("### 手动添加作业")
        with st.form("add_assignment_form"):
            assignment_id = st.text_input("作业ID")
            course_id = st.text_input("所属课程ID")
            assignment_name = st.text_input("作业名称")
            due_date = st.date_input("截止日期")
            total_score = st.number_input("总分", value=100, min_value=0)
            submitted = st.form_submit_button("添加作业")
            
            if submitted and assignment_id and course_id:
                new_assignment = pd.DataFrame([{
                    'assignment_id': assignment_id,
                    'course_id': course_id,
                    'assignment_name': assignment_name,
                    'due_date': str(due_date),
                    'total_score': total_score
                }])
                existing = load_assignments()
                if not existing.empty:
                    merged = pd.concat([existing, new_assignment], ignore_index=True)
                else:
                    merged = new_assignment
                save_assignments(merged)
                st.success("作业添加成功")
                st.rerun()

with tab3:
    st.subheader("提交记录管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### 提交记录")
        submissions_df = load_submissions()
        if not submissions_df.empty:
            st.dataframe(submissions_df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无提交记录")
    
    with col2:
        st.write("### 上传提交记录CSV")
        submission_file = st.file_uploader("选择提交记录CSV文件", type=['csv'], key='submission_upload')
        if submission_file is not None:
            try:
                df = pd.read_csv(submission_file)
                st.write("预览:")
                st.dataframe(df.head())
                if st.button("导入提交记录", type="primary"):
                    existing = load_submissions()
                    if not existing.empty:
                        merged = pd.concat([existing, df], ignore_index=True)
                        merged = merged.drop_duplicates(subset=['submission_id'], keep='last')
                    else:
                        merged = df
                    save_submissions(merged)
                    
                    new_grading = generate_pending_grading(df)
                    if not new_grading.empty:
                        existing_grading = load_grading()
                        if not existing_grading.empty:
                            all_grading = pd.concat([existing_grading, new_grading], ignore_index=True)
                            all_grading = all_grading.drop_duplicates(subset=['grading_id'], keep='first')
                        else:
                            all_grading = new_grading
                        save_grading(all_grading)
                        st.success(f"成功导入 {len(df)} 条提交记录，自动生成 {len(new_grading)} 条待批改任务")
                    else:
                        st.success(f"成功导入 {len(df)} 条提交记录")
                    st.rerun()
            except Exception as e:
                st.error(f"导入失败: {e}")

with tab4:
    st.subheader("活跃度管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### 活跃记录")
        activity_df = load_activity()
        if not activity_df.empty:
            st.dataframe(activity_df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无活跃记录")
    
    with col2:
        st.write("### 上传活跃度CSV")
        activity_file = st.file_uploader("选择活跃度CSV文件", type=['csv'], key='activity_upload')
        if activity_file is not None:
            try:
                df = pd.read_csv(activity_file)
                st.write("预览:")
                st.dataframe(df.head())
                if st.button("导入活跃度数据", type="primary"):
                    existing = load_activity()
                    if not existing.empty:
                        merged = pd.concat([existing, df], ignore_index=True)
                    else:
                        merged = df
                    save_activity(merged)
                    st.success(f"成功导入 {len(df)} 条活跃记录")
                    st.rerun()
            except Exception as e:
                st.error(f"导入失败: {e}")

with tab5:
    st.subheader("快速操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 生成示例数据")
        if st.button("生成完整示例数据", type="primary"):
            generate_sample_data()
            st.success("✅ 示例数据已生成")
            st.rerun()
        
        if st.button("生成示例CSV文件"):
            generate_sample_csv_files()
            st.success("✅ 示例CSV文件已生成到 samples 目录")
    
    with col2:
        st.write("### 清空数据")
        if st.button("清空所有数据", type="secondary"):
            if st.session_state.get('confirm_clear', False):
                save_courses(pd.DataFrame())
                save_assignments(pd.DataFrame())
                save_submissions(pd.DataFrame())
                save_activity(pd.DataFrame())
                save_grading(pd.DataFrame())
                st.session_state['confirm_clear'] = False
                st.success("✅ 所有数据已清空（含批改数据）")
                st.rerun()
            else:
                st.warning("再次点击确认清空")
                st.session_state['confirm_clear'] = True

st.sidebar.header("📥 下载示例文件")
samples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'samples')
if os.path.exists(samples_dir):
    for filename in os.listdir(samples_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(samples_dir, filename)
            with open(filepath, 'rb') as f:
                st.sidebar.download_button(
                    label=f"下载 {filename}",
                    data=f,
                    file_name=filename,
                    mime='text/csv'
                )
