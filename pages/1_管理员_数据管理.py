import streamlit as st
import pandas as pd
import os
from utils.data_processor import (
    load_courses, save_courses,
    load_assignments, save_assignments,
    load_submissions, save_submissions,
    load_activity, save_activity,
    load_grading, save_grading,
    load_extensions, save_extensions,
    generate_pending_grading
)
from datetime import datetime
from utils.scheduler import generate_sample_data, generate_sample_csv_files

st.set_page_config(page_title="管理员 - 数据管理", layout="wide")

st.title("🔧 管理员控制台")
st.markdown("管理课程、作业和学生数据")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📚 课程管理", 
    "📝 作业管理", 
    "📤 提交记录管理",
    "👥 活跃度管理",
    "📅 延期管理",
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
    st.subheader("延期申请管理")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### 延期申请列表")
        extensions_df = load_extensions()
        assignments_df = load_assignments()
        
        if not extensions_df.empty:
            if not assignments_df.empty:
                extensions_display = extensions_df.merge(
                    assignments_df[['assignment_id', 'assignment_name', 'course_id']], 
                    on='assignment_id', 
                    how='left'
                )
            else:
                extensions_display = extensions_df.copy()
            
            status_map = {
                'pending': '待审批',
                'approved': '已批准',
                'rejected': '已拒绝'
            }
            extensions_display['审批状态'] = extensions_display['approval_status'].map(status_map)
            
            display_cols = [col for col in [
                'extension_id', 'student_name', 'assignment_name', 
                'reason', 'original_due_date', 'extended_due_date', 
                '审批状态', 'created_at'
            ] if col in extensions_display.columns]
            
            st.dataframe(extensions_display[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("暂无延期申请记录")
    
    with col2:
        st.write("### 录入延期申请")
        
        assignments = load_assignments()
        submissions = load_submissions()
        
        if not assignments.empty and not submissions.empty:
            with st.form("add_extension_form"):
                student_options = []
                for _, sub in submissions.iterrows():
                    label = f"{sub['student_name']} ({sub['student_id']})"
                    if label not in [opt['label'] for opt in student_options]:
                        student_options.append({
                            'label': label,
                            'student_id': sub['student_id'],
                            'student_name': sub['student_name']
                        })
                
                selected_student = st.selectbox(
                    "选择学员",
                    options=[opt['label'] for opt in student_options],
                    key='ext_student'
                )
                student_info = next((opt for opt in student_options if opt['label'] == selected_student), None)
                
                assignment_options = []
                for _, assign in assignments.iterrows():
                    assignment_options.append({
                        'label': f"{assign['assignment_name']} ({assign['assignment_id']})",
                        'assignment_id': assign['assignment_id'],
                        'assignment_name': assign['assignment_name'],
                        'due_date': assign['due_date']
                    })
                
                selected_assignment = st.selectbox(
                    "选择作业",
                    options=[opt['label'] for opt in assignment_options],
                    key='ext_assignment'
                )
                assignment_info = next((opt for opt in assignment_options if opt['label'] == selected_assignment), None)
                
                reason = st.text_area("申请原因", key='ext_reason')
                
                original_due = st.date_input(
                    "原截止时间",
                    value=datetime.strptime(assignment_info['due_date'], '%Y-%m-%d').date() if assignment_info else datetime.now().date(),
                    key='ext_original_due'
                )
                
                extended_due = st.date_input(
                    "延期后截止时间",
                    value=datetime.now().date(),
                    key='ext_extended_due'
                )
                
                approval_status = st.selectbox(
                    "审批状态",
                    options=['pending', 'approved', 'rejected'],
                    format_func=lambda x: {'pending': '待审批', 'approved': '已批准', 'rejected': '已拒绝'}[x],
                    key='ext_status'
                )
                
                submitted = st.form_submit_button("提交延期申请", type="primary")
                
                if submitted and student_info and assignment_info:
                    extension_id = f"EXT_{student_info['student_id']}_{assignment_info['assignment_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    new_extension = pd.DataFrame([{
                        'extension_id': extension_id,
                        'assignment_id': assignment_info['assignment_id'],
                        'student_id': student_info['student_id'],
                        'student_name': student_info['student_name'],
                        'reason': reason,
                        'original_due_date': str(original_due),
                        'extended_due_date': str(extended_due),
                        'approval_status': approval_status,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }])
                    
                    existing = load_extensions()
                    if not existing.empty:
                        merged = pd.concat([existing, new_extension], ignore_index=True)
                    else:
                        merged = new_extension
                    save_extensions(merged)
                    st.success("延期申请已提交！")
                    st.rerun()
        else:
            st.warning("请先导入作业和提交数据")
    
    if not extensions_df.empty:
        st.write("---")
        st.write("### 批量审批")
        
        pending_ext = extensions_df[extensions_df['approval_status'] == 'pending']
        if not pending_ext.empty:
            for _, ext in pending_ext.iterrows():
                with st.expander(f"⏳ {ext['student_name']} - {ext['assignment_id']}"):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        st.write(f"**申请原因:** {ext.get('reason', '无')}")
                        st.write(f"**原截止时间:** {ext['original_due_date']}")
                        st.write(f"**延期后截止:** {ext['extended_due_date']}")
                    with col_b:
                        if st.button("✅ 批准", key=f"approve_{ext['extension_id']}", type="primary"):
                            extensions = load_extensions()
                            extensions.loc[extensions['extension_id'] == ext['extension_id'], 'approval_status'] = 'approved'
                            save_extensions(extensions)
                            st.success("已批准")
                            st.rerun()
                    with col_c:
                        if st.button("❌ 拒绝", key=f"reject_{ext['extension_id']}"):
                            extensions = load_extensions()
                            extensions.loc[extensions['extension_id'] == ext['extension_id'], 'approval_status'] = 'rejected'
                            save_extensions(extensions)
                            st.success("已拒绝")
                            st.rerun()
        else:
            st.info("暂无待审批的延期申请")

with tab6:
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
                save_extensions(pd.DataFrame())
                st.session_state['confirm_clear'] = False
                st.success("✅ 所有数据已清空（含批改、延期数据）")
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
