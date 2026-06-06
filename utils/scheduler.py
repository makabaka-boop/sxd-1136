import os
import pandas as pd
from datetime import datetime, timedelta
import random
from utils.data_processor import (
    save_courses, save_assignments, save_submissions, 
    save_grading, save_activity, save_extensions, ensure_data_dir
)
from utils.report_generator import generate_daily_report

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'samples')

def generate_sample_data():
    ensure_data_dir()
    
    courses_data = [
        {'course_id': 'C001', 'course_name': 'Python基础编程', 'instructor': '张老师', 'start_date': '2026-05-01', 'end_date': '2026-07-31'},
        {'course_id': 'C002', 'course_name': '数据分析实战', 'instructor': '李老师', 'start_date': '2026-05-15', 'end_date': '2026-08-15'},
        {'course_id': 'C003', 'course_name': '机器学习入门', 'instructor': '王老师', 'start_date': '2026-06-01', 'end_date': '2026-09-01'},
    ]
    save_courses(pd.DataFrame(courses_data))
    
    assignments_data = [
        {'assignment_id': 'A001', 'course_id': 'C001', 'assignment_name': 'Python环境搭建', 'due_date': '2026-05-10', 'total_score': 100},
        {'assignment_id': 'A002', 'course_id': 'C001', 'assignment_name': '基础语法练习', 'due_date': '2026-05-20', 'total_score': 100},
        {'assignment_id': 'A003', 'course_id': 'C001', 'assignment_name': '函数与模块', 'due_date': '2026-06-05', 'total_score': 100},
        {'assignment_id': 'A004', 'course_id': 'C002', 'assignment_name': 'Pandas基础', 'due_date': '2026-05-25', 'total_score': 100},
        {'assignment_id': 'A005', 'course_id': 'C002', 'assignment_name': '数据可视化', 'due_date': '2026-06-10', 'total_score': 100},
        {'assignment_id': 'A006', 'course_id': 'C003', 'assignment_name': '线性回归', 'due_date': '2026-06-15', 'total_score': 100},
    ]
    save_assignments(pd.DataFrame(assignments_data))
    
    students = [
        ('S001', '小明'), ('S002', '小红'), ('S003', '小刚'), ('S004', '小丽'),
        ('S005', '小华'), ('S006', '小强'), ('S007', '小美'), ('S008', '小军'),
        ('S009', '小芳'), ('S010', '小伟')
    ]
    
    submissions_data = []
    grading_data = []
    activity_data = []
    
    assignment_ids = ['A001', 'A002', 'A003', 'A004', 'A005', 'A006']
    due_dates = {
        'A001': '2026-05-10', 'A002': '2026-05-20', 'A003': '2026-06-05',
        'A004': '2026-05-25', 'A005': '2026-06-10', 'A006': '2026-06-15'
    }
    
    for student_id, student_name in students:
        for assign_id in assignment_ids:
            if random.random() < 0.85:
                due_date = datetime.strptime(due_dates[assign_id], '%Y-%m-%d')
                offset_days = random.randint(-5, 8)
                submit_date = due_date + timedelta(days=offset_days)
                
                submissions_data.append({
                    'submission_id': f'SUB_{student_id}_{assign_id}',
                    'assignment_id': assign_id,
                    'student_id': student_id,
                    'student_name': student_name,
                    'submission_date': submit_date.strftime('%Y-%m-%d'),
                    'content': f'{student_name}的{assign_id}作业内容'
                })
                
                if random.random() < 0.7:
                    grade_offset = random.randint(0, 5)
                    graded_date = submit_date + timedelta(days=grade_offset)
                    grading_data.append({
                        'grading_id': f'GRD_{student_id}_{assign_id}',
                        'assignment_id': assign_id,
                        'student_id': student_id,
                        'grader_id': 'TA001' if assign_id in ['A001', 'A002', 'A003'] else 'TA002',
                        'grader_name': '李助教' if assign_id in ['A001', 'A002', 'A003'] else '王助教',
                        'score': random.randint(60, 100),
                        'status': 'graded',
                        'graded_date': graded_date.strftime('%Y-%m-%d'),
                        'feedback': '作业完成良好'
                    })
                else:
                    grading_data.append({
                        'grading_id': f'GRD_{student_id}_{assign_id}',
                        'assignment_id': assign_id,
                        'student_id': student_id,
                        'grader_id': 'TA001' if assign_id in ['A001', 'A002', 'A003'] else 'TA002',
                        'grader_name': '李助教' if assign_id in ['A001', 'A002', 'A003'] else '王助教',
                        'score': None,
                        'status': 'pending',
                        'graded_date': None,
                        'feedback': None
                    })
        
        for day_offset in range(1, 31):
            if random.random() < 0.6:
                activity_date = datetime.now() - timedelta(days=day_offset)
                activity_data.append({
                    'activity_id': f'ACT_{student_id}_{day_offset}',
                    'student_id': student_id,
                    'student_name': student_name,
                    'activity_date': activity_date.strftime('%Y-%m-%d'),
                    'activity_type': random.choice(['login', 'video_watch', 'forum_post', 'assignment_view']),
                    'duration_minutes': random.randint(5, 120)
                })
    
    save_submissions(pd.DataFrame(submissions_data))
    save_grading(pd.DataFrame(grading_data))
    save_activity(pd.DataFrame(activity_data))
    
    extensions_data = [
        {
            'extension_id': 'EXT_S001_A003_001',
            'assignment_id': 'A003',
            'student_id': 'S001',
            'student_name': '小明',
            'reason': '生病请假，需要延期提交',
            'original_due_date': '2026-06-05',
            'extended_due_date': '2026-06-12',
            'approval_status': 'approved',
            'created_at': '2026-06-03 10:00:00'
        },
        {
            'extension_id': 'EXT_S003_A002_001',
            'assignment_id': 'A002',
            'student_id': 'S003',
            'student_name': '小刚',
            'reason': '参加比赛，时间冲突',
            'original_due_date': '2026-05-20',
            'extended_due_date': '2026-05-25',
            'approval_status': 'approved',
            'created_at': '2026-05-18 14:30:00'
        },
        {
            'extension_id': 'EXT_S005_A004_001',
            'assignment_id': 'A004',
            'student_id': 'S005',
            'student_name': '小华',
            'reason': '家里有事，申请延期',
            'original_due_date': '2026-05-25',
            'extended_due_date': '2026-06-01',
            'approval_status': 'pending',
            'created_at': '2026-05-24 09:15:00'
        },
        {
            'extension_id': 'EXT_S007_A005_001',
            'assignment_id': 'A005',
            'student_id': 'S007',
            'student_name': '小美',
            'reason': '项目赶工，需要更多时间',
            'original_due_date': '2026-06-10',
            'extended_due_date': '2026-06-17',
            'approval_status': 'pending',
            'created_at': '2026-06-08 16:45:00'
        },
        {
            'extension_id': 'EXT_S002_A001_001',
            'assignment_id': 'A001',
            'student_id': 'S002',
            'student_name': '小红',
            'reason': '申请延期但理由不充分',
            'original_due_date': '2026-05-10',
            'extended_due_date': '2026-05-17',
            'approval_status': 'rejected',
            'created_at': '2026-05-09 11:20:00'
        }
    ]
    save_extensions(pd.DataFrame(extensions_data))
    
    print("✅ 示例数据已生成")

def simulate_daily_import():
    ensure_data_dir()
    
    today = datetime.now()
    print(f"🔄 模拟 {today.strftime('%Y-%m-%d')} 的数据导入...")
    
    new_submissions = []
    new_grading = []
    new_activity = []
    
    students = [
        ('S001', '小明'), ('S002', '小红'), ('S003', '小刚'), ('S004', '小丽'),
        ('S005', '小华'), ('S006', '小强'), ('S007', '小美'), ('S008', '小军'),
        ('S009', '小芳'), ('S010', '小伟')
    ]
    
    for student_id, student_name in students:
        if random.random() < 0.3:
            assign_id = random.choice(['A001', 'A002', 'A003', 'A004', 'A005', 'A006'])
            new_submissions.append({
                'submission_id': f'SUB_{student_id}_{assign_id}_{today.strftime("%Y%m%d")}',
                'assignment_id': assign_id,
                'student_id': student_id,
                'student_name': student_name,
                'submission_date': today.strftime('%Y-%m-%d'),
                'content': f'{student_name}的{assign_id}作业内容'
            })
        
        if random.random() < 0.5:
            new_activity.append({
                'activity_id': f'ACT_{student_id}_{today.strftime("%Y%m%d")}',
                'student_id': student_id,
                'student_name': student_name,
                'activity_date': today.strftime('%Y-%m-%d'),
                'activity_type': random.choice(['login', 'video_watch', 'forum_post', 'assignment_view']),
                'duration_minutes': random.randint(5, 120)
            })
    
    if new_submissions:
        from utils.data_processor import load_submissions, save_submissions
        existing = load_submissions()
        updated = pd.concat([existing, pd.DataFrame(new_submissions)], ignore_index=True)
        save_submissions(updated)
        print(f"  📝 导入了 {len(new_submissions)} 条新提交记录")
    
    if new_activity:
        from utils.data_processor import load_activity, save_activity
        existing = load_activity()
        updated = pd.concat([existing, pd.DataFrame(new_activity)], ignore_index=True)
        save_activity(updated)
        print(f"  👥 导入了 {len(new_activity)} 条活跃记录")
    
    report_path = generate_daily_report(today.strftime('%Y-%m-%d'))
    print(f"  📊 生成日报: {report_path}")
    
    return report_path

def generate_sample_csv_files():
    if not os.path.exists(SAMPLES_DIR):
        os.makedirs(SAMPLES_DIR)
    
    courses_sample = pd.DataFrame([
        {'course_id': 'C001', 'course_name': 'Python基础编程', 'instructor': '张老师', 'start_date': '2026-05-01', 'end_date': '2026-07-31'},
        {'course_id': 'C002', 'course_name': '数据分析实战', 'instructor': '李老师', 'start_date': '2026-05-15', 'end_date': '2026-08-15'},
    ])
    courses_sample.to_csv(os.path.join(SAMPLES_DIR, 'courses_sample.csv'), index=False, encoding='utf-8-sig')
    
    assignments_sample = pd.DataFrame([
        {'assignment_id': 'A001', 'course_id': 'C001', 'assignment_name': 'Python环境搭建', 'due_date': '2026-05-10', 'total_score': 100},
        {'assignment_id': 'A002', 'course_id': 'C001', 'assignment_name': '基础语法练习', 'due_date': '2026-05-20', 'total_score': 100},
    ])
    assignments_sample.to_csv(os.path.join(SAMPLES_DIR, 'assignments_sample.csv'), index=False, encoding='utf-8-sig')
    
    submissions_sample = pd.DataFrame([
        {'submission_id': 'SUB_S001_A001', 'assignment_id': 'A001', 'student_id': 'S001', 'student_name': '小明', 'submission_date': '2026-05-08', 'content': '作业内容...'},
        {'submission_id': 'SUB_S002_A001', 'assignment_id': 'A001', 'student_id': 'S002', 'student_name': '小红', 'submission_date': '2026-05-09', 'content': '作业内容...'},
    ])
    submissions_sample.to_csv(os.path.join(SAMPLES_DIR, 'submissions_sample.csv'), index=False, encoding='utf-8-sig')
    
    grading_sample = pd.DataFrame([
        {'grading_id': 'GRD_S001_A001', 'assignment_id': 'A001', 'student_id': 'S001', 'grader_id': 'TA001', 'grader_name': '李助教', 'score': 90, 'status': 'graded', 'graded_date': '2026-05-12', 'feedback': '完成良好'},
        {'grading_id': 'GRD_S002_A001', 'assignment_id': 'A001', 'student_id': 'S002', 'grader_id': 'TA001', 'grader_name': '李助教', 'score': None, 'status': 'pending', 'graded_date': None, 'feedback': None},
    ])
    grading_sample.to_csv(os.path.join(SAMPLES_DIR, 'grading_sample.csv'), index=False, encoding='utf-8-sig')
    
    activity_sample = pd.DataFrame([
        {'activity_id': 'ACT_S001_001', 'student_id': 'S001', 'student_name': '小明', 'activity_date': '2026-06-01', 'activity_type': 'login', 'duration_minutes': 30},
        {'activity_id': 'ACT_S002_001', 'student_id': 'S002', 'student_name': '小红', 'activity_date': '2026-06-01', 'activity_type': 'video_watch', 'duration_minutes': 60},
    ])
    activity_sample.to_csv(os.path.join(SAMPLES_DIR, 'activity_sample.csv'), index=False, encoding='utf-8-sig')
    
    extensions_sample = pd.DataFrame([
        {'extension_id': 'EXT_S001_A001_001', 'assignment_id': 'A001', 'student_id': 'S001', 'student_name': '小明', 'reason': '生病请假，需要延期提交', 'original_due_date': '2026-05-10', 'extended_due_date': '2026-05-17', 'approval_status': 'approved', 'created_at': '2026-05-08 10:00:00'},
        {'extension_id': 'EXT_S002_A001_001', 'assignment_id': 'A001', 'student_id': 'S002', 'student_name': '小红', 'reason': '家里有事，申请延期', 'original_due_date': '2026-05-10', 'extended_due_date': '2026-05-15', 'approval_status': 'pending', 'created_at': '2026-05-09 14:30:00'},
    ])
    extensions_sample.to_csv(os.path.join(SAMPLES_DIR, 'extensions_sample.csv'), index=False, encoding='utf-8-sig')
    
    print(f"✅ 示例CSV文件已生成到 {SAMPLES_DIR}")
