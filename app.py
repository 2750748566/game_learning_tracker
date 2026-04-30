import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from data_manager import LearningDataManager

# 页面配置
st.set_page_config(
    page_title="学习进度追踪器",
    page_icon="📚",
    layout="wide"
)

# 初始化数据管理器
@st.cache_resource
def init_manager():
    return LearningDataManager()

manager = init_manager()

# 自定义CSS样式
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4ECDC4;
    }
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏 - 添加学习记录
with st.sidebar:
    st.title("📝 添加学习记录")
    
    # 添加新科目
    with st.expander("➕ 添加新科目"):
        new_subject = st.text_input("科目名称")
        total_hours = st.number_input("总学习时长（小时）", min_value=0.0, step=0.5)
        if st.button("添加科目"):
            if new_subject and total_hours > 0:
                if manager.add_subject(new_subject, total_hours):
                    st.success(f"成功添加科目：{new_subject}")
                    st.rerun()
                else:
                    st.error("科目已存在！")
    
    # 添加学习记录
    st.subheader("📖 今日学习")
    subjects = list(manager.data["subjects"].keys())
    
    if subjects:
        selected_subject = st.selectbox("选择科目", subjects)
        hours = st.number_input("学习时长（小时）", min_value=0.0, max_value=24.0, step=0.5)
        notes = st.text_area("学习笔记（可选）", height=80)
        date = st.date_input("日期", datetime.now())
        
        if st.button("记录学习", type="primary"):
            if selected_subject and hours > 0:
                manager.add_learning_log(
                    date.strftime("%Y-%m-%d"),
                    selected_subject,
                    hours,
                    notes
                )
                st.success("✅ 学习记录已保存！")
                st.rerun()
    else:
        st.info("请先在左侧添加学习科目")
    
    # 设置目标
    with st.expander("🎯 设置学习目标"):
        if subjects:
            goal_subject = st.selectbox("选择科目", subjects, key="goal_select")
            goal_hours = st.number_input("目标时长（小时）", min_value=0.0, step=1.0)
            deadline = st.date_input("截止日期")
            if st.button("设置目标"):
                manager.set_goal(goal_subject, goal_hours, deadline.strftime("%Y-%m-%d"))
                st.success("目标已设置！")
        else:
            st.info("请先添加科目")

# 主页面
st.title("📊 学习进度可视化仪表板")

# 顶部概览指标
col1, col2, col3, col4 = st.columns(4)

# 计算总学习时长
total_study_hours = sum(log["hours"] for log in manager.data["daily_logs"])
total_subjects = len(manager.data["subjects"])
completed_subjects = sum(1 for data in manager.data["subjects"].values() 
                        if data["completed_hours"] >= data["total_hours"])

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📚 总学习时长</h3>
        <p class="big-font">{total_study_hours:.1f} 小时</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>📖 学习科目</h3>
        <p class="big-font">{total_subjects}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>✅ 已完成科目</h3>
        <p class="big-font">{completed_subjects}/{total_subjects}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    # 平均每日学习时长
    days_with_logs = len(set(log["date"] for log in manager.data["daily_logs"]))
    avg_daily = total_study_hours / days_with_logs if days_with_logs > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <h3>📅 日均学习</h3>
        <p class="big-font">{avg_daily:.1f} 小时/天</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 两列布局
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 各科目进度")
    progress_data = manager.get_progress_data()
    
    if progress_data:
        # 创建进度条图表
        fig = go.Figure()
        subjects_list = list(progress_data.keys())
        completed = [progress_data[s]["completed"] for s in subjects_list]
        remaining = [progress_data[s]["remaining"] for s in subjects_list]
        
        fig.add_trace(go.Bar(
            name="已完成",
            x=subjects_list,
            y=completed,
            marker_color="#4ECDC4"
        ))
        fig.add_trace(go.Bar(
            name="剩余",
            x=subjects_list,
            y=remaining,
            marker_color="#FF6B6B"
        ))
        
        fig.update_layout(
            barmode='stack',
            title="学习进度构成",
            xaxis_title="科目",
            yaxis_title="学习时长（小时）",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示百分比进度
        for subject, data in progress_data.items():
            st.write(f"**{subject}**")
            st.progress(data["percentage"] / 100)
            st.write(f"进度：{data['percentage']:.1f}% "
                    f"({data['completed']:.1f}/{data['completed']+data['remaining']:.1f}小时)")
    else:
        st.info("暂无学习数据，请添加学习记录")

with col2:
    st.subheader("📊 学习趋势分析")
    
    # 获取最近30天数据
    daily_stats = manager.get_daily_stats(30)
    
    if daily_stats:
        df = pd.DataFrame([
            {"日期": date, "学习时长": hours}
            for date, hours in daily_stats.items()
        ])
        df = df.sort_values("日期")
        
        # 折线图
        fig = px.line(
            df, 
            x="日期", 
            y="学习时长",
            title="每日学习时长趋势",
            markers=True
        )
        fig.update_layout(
            xaxis_title="日期",
            yaxis_title="学习时长（小时）",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 统计信息
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("最高单日", f"{df['学习时长'].max():.1f}小时")
        with col_b:
            st.metric("最近7天总计", f"{df.tail(7)['学习时长'].sum():.1f}小时")
        with col_c:
            st.metric("平均每日", f"{df['学习时长'].mean():.1f}小时")
    else:
        st.info("暂无学习记录")

st.markdown("---")

# 第三行：近期学习记录和目标进度
col3, col4 = st.columns(2)

with col3:
    st.subheader("📋 近期学习记录")
    if manager.data["daily_logs"]:
        # 显示最近10条记录
        recent_logs = manager.data["daily_logs"][-10:][::-1]
        for log in recent_logs:
            with st.container():
                col_date, col_subj, col_hours = st.columns([2, 2, 1])
                with col_date:
                    st.write(f"📅 {log['date']}")
                with col_subj:
                    st.write(f"📖 {log['subject']}")
                with col_hours:
                    st.write(f"⏰ {log['hours']}小时")
                if log.get('notes'):
                    st.caption(f"✏️ 笔记：{log['notes']}")
                st.divider()
    else:
        st.info("暂无学习记录")

with col4:
    st.subheader("🎯 学习目标追踪")
    if manager.data["goals"]:
        for subject, goal in manager.data["goals"].items():
            if subject in manager.data["subjects"]:
                completed = manager.data["subjects"][subject]["completed_hours"]
                target = goal["goal_hours"]
                progress_pct = min(100, (completed / target * 100)) if target > 0 else 0
                
                st.write(f"**{subject}**")
                st.write(f"目标：{target}小时 | 截止：{goal['deadline']}")
                st.progress(progress_pct / 100)
                st.write(f"已学习：{completed:.1f}小时 ({progress_pct:.1f}%)")
                
                # 距离截止日期的提醒
                deadline_date = datetime.strptime(goal['deadline'], "%Y-%m-%d").date()
                days_left = (deadline_date - datetime.now().date()).days
                if days_left > 0:
                    st.caption(f"⏰ 还剩 {days_left} 天")
                    daily_needed = (target - completed) / days_left if days_left > 0 else 0
                    if daily_needed > 0:
                        st.caption(f"📊 每天需要学习 {daily_needed:.1f} 小时")
                else:
                    st.warning("⚠️ 已超过截止日期！")
                st.divider()
    else:
        st.info("暂无学习目标，请在侧边栏设置")

# 页脚
st.markdown("---")
st.caption("💡 提示：持续记录学习时间，保持学习动力！")
