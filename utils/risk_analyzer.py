import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
from utils.data_processor import (
    load_courses, load_assignments, load_submissions, 
    load_grading, load_activity, load_thresholds,
    load_extensions, get_extensions_summary
)

def analyze_risks(thresholds: Dict = None) -> Dict:
    if thresholds is None:
        thresholds = load_thresholds()
    
    courses = load_courses()
    assignments = load_assignments()
    submissions = load_submissions()
    grading = load_grading()
    activity = load_activity()
    
    risk_items = []
    
    submission_rate_threshold = thresholds.get('submission_rate', 70.0)
    overdue_threshold = thresholds.get('overdue_count', 3)
    grading_delay_threshold = thresholds.get('grading_delay', 2)
    
    if not courses.empty and not assignments.empty and not submissions.empty:
        for _, course in courses.iterrows():
            course_id = course['course_id']
            course_assignments = assignments[assignments['course_id'] == course_id]
            course_submissions = submissions[submissions['assignment_id'].isin(course_assignments['assignment_id'])]
            
            total_students = activity['student_id'].nunique() if not activity.empty else 10
            expected_submissions = len(course_assignments) * total_students
            actual_submissions = len(course_submissions)
            
            if expected_submissions > 0:
                submission_rate = (actual_submissions / expected_submissions) * 100
                
                if submission_rate < submission_rate_threshold:
                    risk_items.append({
                        'type': 'low_submission_rate',
                        'level': 'high' if submission_rate < 50 else 'medium',
                        'course_id': course_id,
                        'course_name': course.get('course_name', course_id),
                        'metric': '提交率',
                        'value': round(submission_rate, 2),
                        'threshold': submission_rate_threshold,
                        'message': f"课程提交率低于阈值"
                    })
    
    if not submissions.empty and not assignments.empty:
        merged = submissions.merge(assignments[['assignment_id', 'assignment_name', 'due_date', 'course_id']], 
                               on='assignment_id', how='left')
        extensions = load_extensions()
        if not extensions.empty and not merged.empty:
            approved_ext = extensions[extensions['approval_status'] == 'approved'][
                ['assignment_id', 'student_id', 'extended_due_date']
            ]
            merged = merged.merge(
                approved_ext, 
                on=['assignment_id', 'student_id'], 
                how='left'
            )
            merged['effective_due_date'] = merged['extended_due_date'].fillna(merged['due_date'])
        else:
            merged['effective_due_date'] = merged['due_date']
        
        if not merged.empty:
            merged['submission_date'] = pd.to_datetime(merged['submission_date'])
            merged['effective_due_date'] = pd.to_datetime(merged['effective_due_date'])
            merged['is_overdue'] = merged['submission_date'] > merged['effective_due_date']
            
            student_overdue = merged.groupby('student_id').agg(
                overdue_count=('is_overdue', 'sum'),
                student_name=('student_name', 'first')
            ).reset_index()
            
            for _, student in student_overdue.iterrows():
                if student['overdue_count'] >= overdue_threshold:
                    risk_items.append({
                        'type': 'student_overdue',
                        'level': 'high' if student['overdue_count'] >= 5 else 'medium',
                        'student_id': student['student_id'],
                        'student_name': student.get('student_name', student['student_id']),
                        'metric': '逾期作业数',
                        'value': int(student['overdue_count']),
                        'threshold': overdue_threshold,
                        'message': f"学员逾期作业过多"
                    })
    
    if not grading.empty and not submissions.empty:
        merged = grading.merge(submissions[['assignment_id', 'student_id', 'submission_date']], 
                              on=['assignment_id', 'student_id'], how='left')
        if not merged.empty:
            merged['submission_date'] = pd.to_datetime(merged['submission_date'])
            merged['graded_date'] = pd.to_datetime(merged['graded_date'])
            merged['delay_days'] = (merged['graded_date'] - merged['submission_date']).dt.days
            
            ta_delays = merged.groupby('grader_id').agg(
                avg_delay=('delay_days', 'mean'),
                grader_name=('grader_name', 'first')
            ).reset_index()
            
            for _, ta in ta_delays.iterrows():
                if ta['avg_delay'] > grading_delay_threshold:
                    risk_items.append({
                        'type': 'grading_delay',
                        'level': 'high' if ta['avg_delay'] >= 5 else 'medium',
                        'grader_id': ta['grader_id'],
                        'grader_name': ta.get('grader_name', ta['grader_id']),
                        'metric': '平均批改延迟',
                        'value': round(ta['avg_delay'], 2),
                        'threshold': grading_delay_threshold,
                        'message': f"助教批改延迟过高"
                    })
    
    if not activity.empty:
        last_7_days = datetime.now() - pd.Timedelta(days=7)
        activity['activity_date'] = pd.to_datetime(activity['activity_date'])
        recent_activity = activity[activity['activity_date'] >= last_7_days]
        
        all_students = activity['student_id'].unique()
        inactive_students = set(all_students) - set(recent_activity['student_id'].unique())
        
        for student_id in inactive_students:
            student_info = activity[activity['student_id'] == student_id].iloc[0]
            risk_items.append({
                'type': 'inactive_student',
                'level': 'medium',
                'student_id': student_id,
                'student_name': student_info.get('student_name', student_id),
                'metric': '活跃度',
                'value': 0,
                'threshold': 1,
                'message': f"学员近7天无活动"
            })
    
    high_risk = [item for item in risk_items if item['level'] == 'high']
    medium_risk = [item for item in risk_items if item['level'] == 'medium']
    
    extensions_summary = get_extensions_summary()
    
    return {
        'total_risks': len(risk_items),
        'high_risk_count': len(high_risk),
        'medium_risk_count': len(medium_risk),
        'high_risks': high_risk,
        'medium_risks': medium_risk,
        'all_risks': risk_items,
        'thresholds_used': thresholds,
        'extensions_summary': extensions_summary
    }

def get_risk_summary(risks: Dict) -> pd.DataFrame:
    if not risks or not risks.get('all_risks'):
        return pd.DataFrame()
    
    risk_data = []
    for item in risks['all_risks']:
        risk_data.append({
            '风险等级': '高' if item['level'] == 'high' else '中',
            '风险类型': _get_risk_type_name(item['type']),
            '关联对象': _get_object_name(item),
            '指标': item['metric'],
            '当前值': item['value'],
            '阈值': item['threshold'],
            '描述': item['message']
        })
    
    return pd.DataFrame(risk_data)

def _get_risk_type_name(risk_type: str) -> str:
    names = {
        'low_submission_rate': '课程提交率低',
        'student_overdue': '学员逾期过多',
        'grading_delay': '批改延迟过高',
        'inactive_student': '学员不活跃'
    }
    return names.get(risk_type, risk_type)

def _get_object_name(item: Dict) -> str:
    if 'course_name' in item:
        return f"课程: {item['course_name']}"
    elif 'student_name' in item:
        return f"学员: {item['student_name']}"
    elif 'grader_name' in item:
        return f"助教: {item['grader_name']}"
    return '未知'

def get_submission_trend() -> pd.DataFrame:
    submissions = load_submissions()
    if submissions.empty:
        return pd.DataFrame()
    
    submissions['submission_date'] = pd.to_datetime(submissions['submission_date'])
    daily = submissions.groupby(submissions['submission_date'].dt.date).size().reset_index()
    daily.columns = ['日期', '提交数']
    return daily.sort_values('日期')

def get_grading_progress() -> Dict:
    grading = load_grading()
    if grading.empty:
        return {'已批改': 0, '待批改': 0, '批改中': 0}
    
    status_counts = grading['status'].value_counts().to_dict()
    return {
        '已批改': status_counts.get('graded', 0),
        '待批改': status_counts.get('pending', 0),
        '批改中': status_counts.get('grading', 0)
    }
