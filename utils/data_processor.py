import pandas as pd
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CACHE_FILE = os.path.join(DATA_DIR, 'cache.json')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_csv(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return pd.read_csv(filepath)

def save_csv(df: pd.DataFrame, filepath: str):
    ensure_data_dir()
    df.to_csv(filepath, index=False, encoding='utf-8-sig')

def load_courses() -> pd.DataFrame:
    filepath = os.path.join(DATA_DIR, 'courses.csv')
    return load_csv(filepath)

def save_courses(df: pd.DataFrame):
    filepath = os.path.join(DATA_DIR, 'courses.csv')
    save_csv(df, filepath)

def load_assignments() -> pd.DataFrame:
    filepath = os.path.join(DATA_DIR, 'assignments.csv')
    return load_csv(filepath)

def save_assignments(df: pd.DataFrame):
    filepath = os.path.join(DATA_DIR, 'assignments.csv')
    save_csv(df, filepath)

def load_submissions() -> pd.DataFrame:
    filepath = os.path.join(DATA_DIR, 'submissions.csv')
    return load_csv(filepath)

def save_submissions(df: pd.DataFrame):
    filepath = os.path.join(DATA_DIR, 'submissions.csv')
    save_csv(df, filepath)

def load_grading() -> pd.DataFrame:
    filepath = os.path.join(DATA_DIR, 'grading.csv')
    return load_csv(filepath)

def save_grading(df: pd.DataFrame):
    filepath = os.path.join(DATA_DIR, 'grading.csv')
    save_csv(df, filepath)

def load_activity() -> pd.DataFrame:
    filepath = os.path.join(DATA_DIR, 'activity.csv')
    return load_csv(filepath)

def save_activity(df: pd.DataFrame):
    filepath = os.path.join(DATA_DIR, 'activity.csv')
    save_csv(df, filepath)

def load_cache() -> Dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(data: Dict):
    ensure_data_dir()
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_default_thresholds() -> Dict:
    return {
        'submission_rate': 70.0,
        'overdue_count': 3,
        'grading_delay': 2
    }

def load_thresholds() -> Dict:
    cache = load_cache()
    return cache.get('thresholds', get_default_thresholds())

def save_thresholds(thresholds: Dict):
    cache = load_cache()
    cache['thresholds'] = thresholds
    save_cache(cache)

def merge_all_data() -> pd.DataFrame:
    courses = load_courses()
    assignments = load_assignments()
    submissions = load_submissions()
    grading = load_grading()
    activity = load_activity()
    
    if courses.empty or assignments.empty:
        return pd.DataFrame()
    
    merged = assignments.merge(courses, on='course_id', how='left', suffixes=('', '_course'))
    
    if not submissions.empty:
        merged = merged.merge(submissions, on='assignment_id', how='left', suffixes=('', '_sub'))
    
    if not grading.empty:
        merged = merged.merge(grading, on='assignment_id', how='left', suffixes=('', '_grade'))
    
    if not activity.empty:
        merged = merged.merge(activity, on='student_id', how='left', suffixes=('', '_act'))
    
    return merged

def calculate_metrics(report_date: Optional[str] = None) -> Dict:
    if report_date is None:
        report_date = datetime.now().strftime('%Y-%m-%d')
    
    courses = load_courses()
    assignments = load_assignments()
    submissions = load_submissions()
    grading = load_grading()
    activity = load_activity()
    
    total_courses = len(courses)
    total_assignments = len(assignments)
    total_submissions = len(submissions) if not submissions.empty else 0
    total_students = activity['student_id'].nunique() if not activity.empty else 0
    
    submission_rate = 0.0
    if total_assignments > 0 and total_students > 0:
        expected = total_assignments * total_students
        submission_rate = (total_submissions / expected) * 100 if expected > 0 else 0
    
    graded_count = len(grading[grading['status'] == 'graded']) if not grading.empty else 0
    grading_progress = (graded_count / total_submissions) * 100 if total_submissions > 0 else 0
    
    overdue_count = 0
    if not submissions.empty and 'submission_date' in submissions.columns and 'due_date' in assignments.columns:
        merged = submissions.merge(assignments[['assignment_id', 'due_date']], on='assignment_id', how='left')
        if not merged.empty:
            merged['submission_date'] = pd.to_datetime(merged['submission_date'])
            merged['due_date'] = pd.to_datetime(merged['due_date'])
            overdue_count = len(merged[merged['submission_date'] > merged['due_date']])
    
    avg_grading_delay = 0.0
    if not grading.empty and 'graded_date' in grading.columns and 'submission_date' in submissions.columns:
        merged = grading.merge(submissions[['assignment_id', 'student_id', 'submission_date']], 
                               on=['assignment_id', 'student_id'], how='left')
        if not merged.empty:
            merged['submission_date'] = pd.to_datetime(merged['submission_date'])
            merged['graded_date'] = pd.to_datetime(merged['graded_date'])
            merged['delay'] = (merged['graded_date'] - merged['submission_date']).dt.days
            avg_grading_delay = merged['delay'].mean()
    
    active_students = activity['student_id'].nunique() if not activity.empty else 0
    activity_rate = (active_students / total_students) * 100 if total_students > 0 else 0
    
    return {
        'report_date': report_date,
        'total_courses': total_courses,
        'total_assignments': total_assignments,
        'total_students': total_students,
        'total_submissions': total_submissions,
        'submission_rate': round(submission_rate, 2),
        'grading_progress': round(grading_progress, 2),
        'overdue_count': overdue_count,
        'avg_grading_delay': round(avg_grading_delay, 2),
        'active_students': active_students,
        'activity_rate': round(activity_rate, 2)
    }
