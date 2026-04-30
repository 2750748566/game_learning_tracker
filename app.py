import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd
from task_system import GameLearningSystem, TaskType, TaskStatus

# 页面配置
st.set_page_config(
    page_title="游戏化学习任务系统",
    page_icon="🎮",
    layout="wide"
)

# 初始化系统
@st.cache_resource
def init_system():
    return GameLearningSystem()

system = init_system()

# 自定义CSS样式
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    }
    .task-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid;
    }
    .main-task {
        border-left-color: #FF6B6B;
    }
    .side-task {
        border-left-color: #4ECDC4;
    }
    .daily-task {
        border-left-color: #FFEAA7;
    }
    .achievement-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 5px;
    }
    .level-progress {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏 - 玩家信息
with st.sidebar:
    st.title("🎮 玩家信息")
    
    player_data = system.get_task_tree_data()["player"]
    
    # 玩家等级和经验条
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"### Lv.{player_data['level']}")
    with col2:
        st.markdown(f"**XP**: {player_data['xp']}/{player_data['next_level_xp']}")
    
    xp_progress = player_data['xp'] / player_data['next_level_xp']
    st.progress(xp_progress)
    
    st.markdown("---")
    
    # 成就展示
    st.subheader("🏆 已获得成就")
    if player_data['achievements']:
        for ach in player_data['achievements']:
            with st.container():
                st.markdown(f"""
                <div class="achievement-badge">
                    🎖️ **{ach['name']}**<br>
                    <small>{ach['description']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("完成更多任务来获得成就吧！")
    
    st.markdown("---")
    
    # 创建自定义支线任务
    st.subheader("✨ 创建自定义任务")
    with st.form("custom_task"):
        task_name = st.text_input("任务名称")
        task_desc = st.text_area("任务描述")
        est_time = st.number_input("预计时间（小时）", min_value=0.5, step=0.5)
        xp_reward = st.number_input("经验奖励", min_value=10, step=10)
        parent_task = st.selectbox(
            "关联主线任务（可选）",
            ["无"] + [t.name for t in system.tasks.values() 
                     if t.type == TaskType.MAIN and t.status != TaskStatus.COMPLETED]
        )
        
        if st.form_submit_button("创建任务"):
            parent_id = None
            if parent_task != "无":
                for t in system.tasks.values():
                    if t.name == parent_task:
                        parent_id = t.id
                        break
            
            new_task = system.create_side_task(
                task_name, task_desc, est_time, xp_reward, parent_id
            )
            st.success(f"✅ 支线任务「{task_name}」已创建！")
            st.rerun()

# 主页面
st.title("🎯 游戏化学习任务系统")

# 统计卡片
col1, col2, col3, col4 = st.columns(4)

tasks_data = system.get_task_tree_data()
main_tasks = tasks_data["main"]
side_tasks = tasks_data["side"]
daily_tasks = tasks_data["daily"]

completed_main = sum(1 for t in main_tasks if t["status"] == "completed")
completed_side = sum(1 for t in side_tasks if t["status"] == "completed")
in_progress = sum(1 for t in system.tasks.values() 
                 if t.status == TaskStatus.IN_PROGRESS)

with col1:
    st.metric("📖 主线进度", f"{completed_main}/{len(main_tasks)}")
with col2:
    st.metric("🔀 支线完成", f"{completed_side}/{len(side_tasks)}")
with col3:
    st.metric("⚡ 进行中任务", in_progress)
with col4:
    total_hours = sum(t.actual_time for t in system.tasks.values())
    st.metric("⏰ 总学习时长", f"{total_hours:.1f}小时")

st.markdown("---")

# 任务树可视化（主线）
st.subheader("🌳 主线任务树")

# 创建任务树的可视化
def create_task_tree(main_tasks):
    """创建任务树的可视化图表"""
    fig = go.Figure()
    
    # 布局位置
    levels = {}
    for task in main_tasks:
        # 根据任务ID确定层级
        if "main_1" in task["id"]:
            y_pos = 0
        elif "main_2" in task["id"]:
            y_pos = -1
        elif "main_3" in task["id"]:
            y_pos = -2
        elif "main_4" in task["id"]:
            y_pos = -3
        elif "main_5" in task["id"]:
            y_pos = -4
        else:
            y_pos = -5
        
        # 状态颜色
        if task["status"] == "completed":
            color = "#00FF00"
            symbol = "star"
            size = 30
        elif task["status"] == "in_progress":
            color = "#FFA500"
            symbol = "circle"
            size = 25
        elif task["status"] == "available":
            color = "#4ECDC4"
            symbol = "circle"
            size = 20
        else:
            color = "#808080"
            symbol = "circle"
            size = 15
        
        fig.add_trace(go.Scatter(
            x=[task["id"]],
            y=[y_pos],
            mode='markers+text',
            name=task["name"],
            marker=dict(
                size=size,
                color=color,
                symbol=symbol,
                line=dict(width=2, color='white')
            ),
            text=task["name"],
            textposition="top center",
            hovertext=f"{task['name']}<br>进度: {task['progress']}%<br>奖励: {task['xp_reward']}XP",
            hoverinfo='text'
        ))
        
        # 添加连接线
        for prereq in task["prerequisites"]:
            prereq_task = next((t for t in main_tasks if t["id"] == prereq), None)
            if prereq_task:
                prereq_y = - (int(prereq_task["id"].split("_")[1]) - 1)
                current_y = - (int(task["id"].split("_")[1]) - 1)
                fig.add_trace(go.Scatter(
                    x=[prereq_task["id"], task["id"]],
                    y=[prereq_y, current_y],
                    mode='lines',
                    line=dict(color='white', width=2),
                    showlegend=False,
                    hoverinfo='none'
                ))
    
    fig.update_layout(
        title="主线任务树状图",
        xaxis=dict(
            title="任务",
            showgrid=False,
            showticklabels=False
        ),
        yaxis=dict(
            title="难度层级",
            showgrid=True,
            gridcolor='#333333'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        hovermode='closest'
    )
    
    return fig

st.plotly_chart(create_task_tree(main_tasks), use_container_width=True)

st.markdown("---")

# 任务展示区域（使用选项卡）
tab1, tab2, tab3 = st.tabs(["📖 主线任务", "🔀 支线任务", "⚡ 每日任务"])

with tab1:
    for task in main_tasks:
        with st.container():
            status_emoji = {
                "completed": "✅",
                "in_progress": "⚡",
                "available": "🔓",
                "locked": "🔒"
            }.get(task["status"], "❓")
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="task-card main-task">
                    <h4>{status_emoji} {task['name']}</h4>
                    <p>{task['description']}</p>
                    <small>⏰ 预计: {task['estimated_time']}小时 | ✨ 奖励: {task['xp_reward']}XP</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if task["status"] == "in_progress":
                    st.write(f"进度: {task['progress']}%")
                    st.progress(task["progress"] / 100)
            
            with col3:
                if task["status"] == "available":
                    if st.button("▶️ 开始", key=f"start_{task['id']}"):
                        system.start_task(task["id"])
                        st.rerun()
                elif task["status"] == "in_progress":
                    # 更新进度
                    progress_increment = st.number_input(
                        "增加进度 (%)", 
                        min_value=0, max_value=100-task["progress"],
                        key=f"progress_{task['id']}"
                    )
                    time_spent = st.number_input(
                        "学习时长 (小时)", 
                        min_value=0.0, step=0.5,
                        key=f"time_{task['id']}"
                    )
                    if st.button("📝 更新", key=f"update_{task['id']}"):
                        system.update_task_progress(task["id"], progress_increment, time_spent)
                        st.rerun()
                elif task["status"] == "completed":
                    st.success("已完成！")

with tab2:
    # 支线任务
    for task in side_tasks:
        with st.expander(f"🔀 {task['name']}"):
            st.write(f"**描述**: {task['description']}")
            st.write(f"**预计时间**: {task['estimated_time']}小时")
            st.write(f"**经验奖励**: {task['xp_reward']}XP")
            
            if task["status"] == "completed":
                st.success("✅ 已完成")
            elif task["status"] == "available":
                if st.button("开始任务", key=f"start_side_{task['id']}"):
                    system.start_task(task["id"])
                    st.rerun()
            elif task["status"] == "in_progress":
                st.progress(task["progress"] / 100)
                col1, col2 = st.columns(2)
                with col1:
                    progress_add = st.number_input("进度增加 (%)", key=f"side_prog_{task['id']}")
                with col2:
                    time_add = st.number_input("学习时长 (小时)", key=f"side_time_{task['id']}")
                if st.button("更新进度", key=f"update_side_{task['id']}"):
                    system.update_task_progress(task["id"], progress_add, time_add)
                    st.rerun()
            else:
                st.info("🔒 需要完成前置任务")

with tab3:
    # 每日任务（可以每日重置）
    st.warning("💡 每日任务每天更新，持续完成可获得稳定经验！")
    
    today = datetime.now().date()
    
    for task in daily_tasks:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="task-card daily-task">
                    <b>⚡ {task['name']}</b><br>
                    <small>{task['description']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if task["status"] == "in_progress":
                    st.write(f"进度: {task['progress']}%")
                    st.progress(task["progress"] / 100)
            
            with col3:
                if task["status"] == "available":
                    if st.button("今日挑战", key=f"daily_start_{task['id']}"):
                        system.start_task(task["id"])
                        st.rerun()
                elif task["status"] == "in_progress":
                    progress = st.number_input("进度", key=f"daily_prog_{task['id']}", min_value=0, max_value=100)
                    if st.button("记录", key=f"daily_update_{task['id']}"):
                        system.update_task_progress(task["id"], progress, 0)
                        st.rerun()
                elif task["status"] == "completed":
                    st.success("今日已完成！")

st.markdown("---")

# 统计和数据分析
st.subheader("📊 学习数据分析")

col1, col2 = st.columns(2)

with col1:
    # 任务完成统计饼图
    status_counts = {
        "已完成": sum(1 for t in system.tasks.values() 
                     if t.status == TaskStatus.COMPLETED),
        "进行中": sum(1 for t in system.tasks.values() 
                     if t.status == TaskStatus.IN_PROGRESS),
        "未开始": sum(1 for t in system.tasks.values() 
                     if t.status in [TaskStatus.LOCKED, TaskStatus.AVAILABLE])
    }
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(status_counts.keys()),
        values=list(status_counts.values()),
        marker_colors=['#00FF00', '#FFA500', '#808080']
    )])
    fig_pie.update_layout(title="任务完成情况")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # 学习时间分布
    task_times = []
    for task in system.tasks.values():
        if task.actual_time > 0:
            task_times.append({
                "任务": task.name[:20],
                "实际用时": task.actual_time,
                "预计用时": task.estimated_time
            })
    
    if task_times:
        df_times = pd.DataFrame(task_times)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="预计用时",
            x=df_times["任务"],
            y=df_times["预计用时"],
            marker_color="#4ECDC4"
        ))
        fig_bar.add_trace(go.Bar(
            name="实际用时",
            x=df_times["任务"],
            y=df_times["实际用时"],
            marker_color="#FF6B6B"
        ))
        fig_bar.update_layout(
            title="学习时间对比",
            barmode='group',
            xaxis_title="任务",
            yaxis_title="时长（小时）"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 学习笔记记录
st.subheader("📝 学习笔记")

with st.form("learning_note"):
    note_content = st.text_area("记录今天的学习心得", height=100)
    related_task = st.selectbox(
        "关联任务",
        [t.name for t in system.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
    )
    
    if st.form_submit_button("保存笔记"):
        for task in system.tasks.values():
            if task.name == related_task:
                system.update_task_progress(task.id, 0, 0, note_content)
                st.success("笔记已保存！")
                break

# 最近学习动态
st.subheader("🎯 近期学习动态")
recent_notes = []
for task in system.tasks.values():
    for note in task.notes[-3:]:  # 最近3条笔记
        recent_notes.append({
            "任务": task.name,
            "内容": note["content"][:100],
            "时间": note["timestamp"][:10]
        })

if recent_notes:
    df_notes = pd.DataFrame(recent_notes)
    st.dataframe(df_notes, use_container_width=True)
else:
    st.info("开始学习并记录笔记吧！")
