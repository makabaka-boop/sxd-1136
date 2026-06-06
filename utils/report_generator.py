import os
import pandas as pd
from datetime import datetime
from jinja2 import Template
from utils.data_processor import calculate_metrics, load_extensions, load_assignments
from utils.risk_analyzer import analyze_risks, get_risk_summary

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>课程作业日报 - {{ report_date }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        .metric-card h3 { font-size: 14px; color: #666; margin-bottom: 8px; }
        .metric-card .value { font-size: 32px; font-weight: bold; color: #333; }
        .metric-card .unit { font-size: 14px; color: #999; margin-left: 5px; }
        .section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        .section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        .risk-high { border-left: 4px solid #e74c3c; padding-left: 10px; }
        .risk-medium { border-left: 4px solid #f39c12; padding-left: 10px; }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-high { background: #fef0f0; color: #e74c3c; }
        .badge-medium { background: #fef6e7; color: #f39c12; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #f0f0f0;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            font-size: 13px;
            color: #555;
        }
        tr:hover { background: #f8f9fa; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .progress-good { background: #27ae60; }
        .progress-warning { background: #f39c12; }
        .progress-danger { background: #e74c3c; }
        .footer {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 30px;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 课程作业日报</h1>
            <p>生成时间: {{ generated_at }}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>总课程数</h3>
                <div class="value">{{ metrics.total_courses }}</div>
            </div>
            <div class="metric-card">
                <h3>总作业数</h3>
                <div class="value">{{ metrics.total_assignments }}</div>
            </div>
            <div class="metric-card">
                <h3>学员总数</h3>
                <div class="value">{{ metrics.total_students }}</div>
            </div>
            <div class="metric-card">
                <h3>作业提交率</h3>
                <div class="value">{{ metrics.submission_rate }}<span class="unit">%</span></div>
                <div class="progress-bar">
                    <div class="progress-fill {{ 'progress-danger' if metrics.submission_rate < 60 else 'progress-warning' if metrics.submission_rate < 80 else 'progress-good' }}" 
                         style="width: {{ metrics.submission_rate }}%"></div>
                </div>
            </div>
            <div class="metric-card">
                <h3>批改进度</h3>
                <div class="value">{{ metrics.grading_progress }}<span class="unit">%</span></div>
                <div class="progress-bar">
                    <div class="progress-fill {{ 'progress-danger' if metrics.grading_progress < 60 else 'progress-warning' if metrics.grading_progress < 80 else 'progress-good' }}" 
                         style="width: {{ metrics.grading_progress }}%"></div>
                </div>
            </div>
            <div class="metric-card">
                <h3>逾期作业</h3>
                <div class="value">{{ metrics.overdue_count }}<span class="unit">份</span></div>
            </div>
            <div class="metric-card">
                <h3>平均批改延迟</h3>
                <div class="value">{{ metrics.avg_grading_delay }}<span class="unit">天</span></div>
            </div>
            <div class="metric-card">
                <h3>活跃学员</h3>
                <div class="value">{{ metrics.active_students }}<span class="unit">/{{ metrics.total_students }}</span></div>
            </div>
            <div class="metric-card">
                <h3>延期申请</h3>
                <div class="value">{{ metrics.total_extensions }}<span class="unit">份</span></div>
            </div>
            <div class="metric-card">
                <h3>已批准延期</h3>
                <div class="value">{{ metrics.approved_extensions }}<span class="unit">份</span></div>
            </div>
            <div class="metric-card">
                <h3>待审批延期</h3>
                <div class="value">{{ metrics.pending_extensions }}<span class="unit">份</span></div>
            </div>
        </div>

        <div class="section">
            <h2>⚠️ 风险清单 ({{ risks.total_risks }} 项)</h2>
            {% if risks.total_risks > 0 %}
                <p>高风险: <span class="badge badge-high">{{ risks.high_risk_count }}</span> 项 | 
                   中风险: <span class="badge badge-medium">{{ risks.medium_risk_count }}</span> 项</p>
                <table>
                    <thead>
                        <tr>
                            <th>风险等级</th>
                            <th>风险类型</th>
                            <th>关联对象</th>
                            <th>指标</th>
                            <th>当前值</th>
                            <th>阈值</th>
                            <th>描述</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for risk in risks.all_risks %}
                        <tr>
                            <td>
                                {% if risk.level == 'high' %}
                                    <span class="badge badge-high">高风险</span>
                                {% else %}
                                    <span class="badge badge-medium">中风险</span>
                                {% endif %}
                            </td>
                            <td>{{ risk.type_name }}</td>
                            <td>{{ risk.object_name }}</td>
                            <td>{{ risk.metric }}</td>
                            <td>{{ risk.value }}</td>
                            <td>{{ risk.threshold }}</td>
                            <td>{{ risk.message }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="color: #27ae60;">✅ 当前无风险项，一切正常！</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>📅 延期申请详情</h2>
            {% if extensions_list %}
                <table>
                    <thead>
                        <tr>
                            <th>学员</th>
                            <th>作业</th>
                            <th>申请原因</th>
                            <th>原截止时间</th>
                            <th>延期后截止</th>
                            <th>审批状态</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ext in extensions_list %}
                        <tr>
                            <td>{{ ext.student_name }}</td>
                            <td>{{ ext.assignment_name }}</td>
                            <td>{{ ext.reason }}</td>
                            <td>{{ ext.original_due_date }}</td>
                            <td>{{ ext.extended_due_date }}</td>
                            <td>
                                {% if ext.approval_status == 'approved' %}
                                    <span class="badge badge-high" style="background: #e8f5e9; color: #27ae60;">已批准</span>
                                {% elif ext.approval_status == 'pending' %}
                                    <span class="badge badge-medium">待审批</span>
                                {% else %}
                                    <span class="badge badge-high">已拒绝</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="color: #666;">暂无延期申请记录</p>
            {% endif %}
        </div>

        <div class="section">
            <h2>🎯 阈值配置</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                <div>
                    <strong>提交率阈值:</strong> {{ thresholds.submission_rate }}%
                </div>
                <div>
                    <strong>逾期数阈值:</strong> {{ thresholds.overdue_count }} 个
                </div>
                <div>
                    <strong>批改延迟阈值:</strong> {{ thresholds.grading_delay }} 天
                </div>
            </div>
        </div>

        <div class="footer">
            <p>本报告由报表生成系统自动生成 | © 2026</p>
        </div>
    </div>
</body>
</html>
"""

def ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def generate_daily_report(report_date: str = None) -> str:
    if report_date is None:
        report_date = datetime.now().strftime('%Y-%m-%d')
    
    metrics = calculate_metrics(report_date)
    risks = analyze_risks()
    thresholds = risks.get('thresholds_used', {})
    
    risk_list = []
    for risk in risks.get('all_risks', []):
        risk_copy = risk.copy()
        risk_copy['type_name'] = _get_risk_type_name(risk['type'])
        risk_copy['object_name'] = _get_object_name(risk)
        risk_list.append(risk_copy)
    
    risks['all_risks'] = risk_list
    
    extensions = load_extensions()
    assignments = load_assignments()
    extensions_list = []
    if not extensions.empty:
        ext_with_assign = extensions.merge(
            assignments[['assignment_id', 'assignment_name']], 
            on='assignment_id', 
            how='left'
        )
        for _, ext in ext_with_assign.iterrows():
            extensions_list.append({
                'student_name': ext.get('student_name', ext['student_id']),
                'assignment_name': ext.get('assignment_name', ext['assignment_id']),
                'reason': ext.get('reason', ''),
                'original_due_date': ext['original_due_date'],
                'extended_due_date': ext['extended_due_date'],
                'approval_status': ext['approval_status']
            })
    
    template = Template(REPORT_TEMPLATE)
    html_content = template.render(
        report_date=report_date,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        metrics=metrics,
        risks=risks,
        thresholds=thresholds,
        extensions_list=extensions_list
    )
    
    ensure_reports_dir()
    filename = f"daily_report_{report_date}.html"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath

def _get_risk_type_name(risk_type: str) -> str:
    names = {
        'low_submission_rate': '课程提交率低',
        'student_overdue': '学员逾期过多',
        'grading_delay': '批改延迟过高',
        'inactive_student': '学员不活跃'
    }
    return names.get(risk_type, risk_type)

def _get_object_name(item: dict) -> str:
    if 'course_name' in item:
        return f"课程: {item['course_name']}"
    elif 'student_name' in item:
        return f"学员: {item['student_name']}"
    elif 'grader_name' in item:
        return f"助教: {item['grader_name']}"
    return '未知'

def list_reports() -> list:
    ensure_reports_dir()
    reports = []
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(REPORTS_DIR, filename)
            reports.append({
                'filename': filename,
                'filepath': filepath,
                'created_at': datetime.fromtimestamp(os.path.getctime(filepath))
            })
    return sorted(reports, key=lambda x: x['created_at'], reverse=True)

def get_report_path(report_date: str) -> str:
    filename = f"daily_report_{report_date}.html"
    return os.path.join(REPORTS_DIR, filename)
