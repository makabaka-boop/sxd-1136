import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="课程作业报表系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 课程作业报表生成系统")
st.markdown("---")

st.header("系统介绍")
st.write("""
本系统用于分析课程作业提交率、批改进度、学员活跃度和风险提醒。
系统按角色划分为三个功能模块：
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🔧 管理员")
    st.write("- 上传课程与作业记录")
    st.write("- 管理学员活跃度数据")
    st.write("- 生成示例数据")
    st.write("- 下载示例CSV文件")

with col2:
    st.markdown("### 📝 助教")
    st.write("- 查看待批改作业列表")
    st.write("- 补充批改状态与评分")
    st.write("- 查看批改统计")
    st.write("- 批量导入批改数据")

with col3:
    st.markdown("### 📊 主管")
    st.write("- 查看核心指标看板")
    st.write("- **调整阈值预警线**（拖动滑块）")
    st.write("- 实时刷新风险清单")
    st.write("- 生成与下载日报HTML")
    st.write("- 模拟定时任务报表生成")

st.markdown("---")

st.header("核心功能特性")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 数据分析")
    st.write("- 作业提交率统计")
    st.write("- 批改进度追踪")
    st.write("- 学员活跃度分析")
    st.write("- 多维度趋势图表")

with col2:
    st.subheader("⚠️ 风险预警")
    st.write("- **可拖动阈值设置**")
    st.write("- 实时风险清单刷新")
    st.write("- 高/中风险分级")
    st.write("- 多维度风险识别")

st.markdown("---")

st.subheader("🚀 快速开始")

st.write("1. **首次使用**: 点击左侧「管理员 - 数据管理」，然后在「快速操作」标签页生成示例数据")
st.write("2. **查看报表**: 点击左侧「主管 - 数据看板」查看各项指标和风险预警")
st.write("3. **调整阈值**: 在「主管 - 数据看板」的「阈值设置」标签页拖动滑块调整预警线")
st.write("4. **生成日报**: 在「主管 - 数据看板」的「日报管理」标签页生成并下载HTML报告")
st.write("5. **模拟定时任务**: 点击「模拟每日数据导入」体验定时报表生成")

st.markdown("---")

st.sidebar.success("👈 请在左侧选择角色模块")

st.sidebar.info("""
**项目结构:**
- `pages/` - Streamlit 页面
- `utils/` - 核心功能模块
- `data/` - 数据存储 (CSV + 缓存)
- `reports/` - 生成的日报
- `samples/` - 示例CSV文件
""")
