import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid

class TaskType(Enum):
    MAIN = "main"      # 主线任务
    SIDE = "side"      # 支线任务
    DAILY = "daily"    # 每日任务
    ACHIEVEMENT = "achievement"  # 成就任务

class TaskStatus(Enum):
    LOCKED = "locked"      # 未解锁
    AVAILABLE = "available" # 可接取
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成

class LearningTask:
    """学习任务类"""
    def __init__(self, task_id: str, name: str, task_type: TaskType, 
                 description: str, estimated_time: float, xp_reward: int,
                 prerequisites: List[str] = None, sub_tasks: List[Dict] = None):
        self.id = task_id
        self.name = name
        self.type = task_type
        self.description = description
        self.estimated_time = estimated_time  # 预计完成时间（小时）
        self.xp_reward = xp_reward
        self.prerequisites = prerequisites or []  # 前置任务ID列表
        self.sub_tasks = sub_tasks or []  # 子任务列表
        self.status = TaskStatus.LOCKED
        self.progress = 0  # 进度 0-100
        self.actual_time = 0
        self.completed_at = None
        self.notes = []  # 学习笔记
        self.resources = []  # 学习资源链接
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "estimated_time": self.estimated_time,
            "xp_reward": self.xp_reward,
            "prerequisites": self.prerequisites,
            "sub_tasks": self.sub_tasks,
            "status": self.status.value,
            "progress": self.progress,
            "actual_time": self.actual_time,
            "completed_at": self.completed_at,
            "notes": self.notes,
            "resources": self.resources
        }

class GameLearningSystem:
    def __init__(self, data_file="learning_tasks/learning_data.json"):
        # 确保数据目录存在
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        self.data_file = data_file
        self.tasks: Dict[str, LearningTask] = {}
        self.player_level = 1
        self.player_xp = 0
        self.skill_tree = {}
        self.achievements = []
        self.load_data()
        
    def load_data(self):
        """加载任务数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.player_level = data.get("player_level", 1)
                self.player_xp = data.get("player_xp", 0)
                # 加载任务
                for task_data in data.get("tasks", []):
                    task = LearningTask(
                        task_data["id"],
                        task_data["name"],
                        TaskType(task_data["type"]),
                        task_data["description"],
                        task_data["estimated_time"],
                        task_data["xp_reward"],
                        task_data.get("prerequisites", []),
                        task_data.get("sub_tasks", [])
                    )
                    task.status = TaskStatus(task_data["status"])
                    task.progress = task_data["progress"]
                    task.actual_time = task_data["actual_time"]
                    task.completed_at = task_data.get("completed_at")
                    task.notes = task_data.get("notes", [])
                    task.resources = task_data.get("resources", [])
                    self.tasks[task.id] = task
        else:
            self.init_default_tasks()
    
    def init_default_tasks(self):
        """初始化默认任务（以Python学习为例）"""
        # 主线任务 - 使用明确参数传递
        main_task_1 = LearningTask(
            task_id="main_1",
            name="Python基础语法",
            task_type=TaskType.MAIN,
            description="学习变量、数据类型、控制流",
            estimated_time=10,
            xp_reward=100,
            prerequisites=[]
        )
        self.add_task(main_task_1)
        
        main_task_2 = LearningTask(
            task_id="main_2",
            name="函数与模块",
            task_type=TaskType.MAIN,
            description="学习函数定义、模块导入",
            estimated_time=8,
            xp_reward=150,
            prerequisites=["main_1"]
        )
        self.add_task(main_task_2)
        
        main_task_3 = LearningTask(
            task_id="main_3",
            name="面向对象编程",
            task_type=TaskType.MAIN,
            description="学习类、继承、多态",
            estimated_time=12,
            xp_reward=200,
            prerequisites=["main_2"]
        )
        self.add_task(main_task_3)
        
        main_task_4 = LearningTask(
            task_id="main_4",
            name="文件与异常处理",
            task_type=TaskType.MAIN,
            description="学习文件读写、异常捕获",
            estimated_time=6,
            xp_reward=120,
            prerequisites=["main_3"]
        )
        self.add_task(main_task_4)
        
        main_task_5 = LearningTask(
            task_id="main_5",
            name="数据结构与算法",
            task_type=TaskType.MAIN,
            description="学习列表、字典、集合、基础算法",
            estimated_time=20,
            xp_reward=300,
            prerequisites=["main_3"]
        )
        self.add_task(main_task_5)
        
        main_task_6 = LearningTask(
            task_id="main_6",
            name="Web开发入门",
            task_type=TaskType.MAIN,
            description="学习Flask/Django基础",
            estimated_time=25,
            xp_reward=400,
            prerequisites=["main_5"]
        )
        self.add_task(main_task_6)
        
        # 支线任务
        side_task_1 = LearningTask(
            task_id="side_1",
            name="代码规范",
            task_type=TaskType.SIDE,
            description="学习PEP8编码规范",
            estimated_time=3,
            xp_reward=50,
            prerequisites=["main_1"]
        )
        self.add_task(side_task_1)
        
        side_task_2 = LearningTask(
            task_id="side_2",
            name="Git版本控制",
            task_type=TaskType.SIDE,
            description="学习Git基础命令",
            estimated_time=5,
            xp_reward=80,
            prerequisites=["main_2"]
        )
        self.add_task(side_task_2)
        
        side_task_3 = LearningTask(
            task_id="side_3",
            name="单元测试",
            task_type=TaskType.SIDE,
            description="学习unittest/pytest",
            estimated_time=6,
            xp_reward=90,
            prerequisites=["main_3"]
        )
        self.add_task(side_task_3)
        
        side_task_4 = LearningTask(
            task_id="side_4",
            name="正则表达式",
            task_type=TaskType.SIDE,
            description="学习正则表达式应用",
            estimated_time=4,
            xp_reward=70,
            prerequisites=["main_2"]
        )
        self.add_task(side_task_4)
        
        side_task_5 = LearningTask(
            task_id="side_5",
            name="装饰器与生成器",
            task_type=TaskType.SIDE,
            description="学习高级Python特性",
            estimated_time=5,
            xp_reward=100,
            prerequisites=["main_3"]
        )
        self.add_task(side_task_5)
        
        # 每日任务
        daily_task_1 = LearningTask(
            task_id="daily_1",
            name="每日编码",
            task_type=TaskType.DAILY,
            description="至少编写30行代码",
            estimated_time=1,
            xp_reward=30,
            prerequisites=[]
        )
        self.add_task(daily_task_1)
        
        daily_task_2 = LearningTask(
            task_id="daily_2",
            name="学习笔记",
            task_type=TaskType.DAILY,
            description="整理今日学习笔记",
            estimated_time=0.5,
            xp_reward=20,
            prerequisites=[]
        )
        self.add_task(daily_task_2)
        
        daily_task_3 = LearningTask(
            task_id="daily_3",
            name="代码阅读",
            task_type=TaskType.DAILY,
            description="阅读开源代码30分钟",
            estimated_time=0.5,
            xp_reward=25,
            prerequisites=[]
        )
        self.add_task(daily_task_3)
        
        self.save_data()
    
    def add_task(self, task: LearningTask):
        """添加新任务"""
        self.tasks[task.id] = task
        self.update_task_availability()
        self.save_data()
    
    def update_task_availability(self):
        """更新任务可用性（检查前置任务）"""
        for task in self.tasks.values():
            if task.status == TaskStatus.COMPLETED:
                continue
            
            # 检查前置任务是否完成
            if task.prerequisites:
                all_prereqs_completed = all(
                    self.tasks.get(prereq_id) and 
                    self.tasks[prereq_id].status == TaskStatus.COMPLETED
                    for prereq_id in task.prerequisites
                )
                if all_prereqs_completed and task.status == TaskStatus.LOCKED:
                    task.status = TaskStatus.AVAILABLE
            elif task.status == TaskStatus.LOCKED:
                task.status = TaskStatus.AVAILABLE
        
        self.save_data()
    
    def start_task(self, task_id: str):
        """开始任务"""
        if task_id in self.tasks and self.tasks[task_id].status == TaskStatus.AVAILABLE:
            self.tasks[task_id].status = TaskStatus.IN_PROGRESS
            self.save_data()
            return True
        return False
    
    def update_task_progress(self, task_id: str, progress_increment: int, 
                            time_spent: float = 0, notes: str = ""):
        """更新任务进度"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != TaskStatus.IN_PROGRESS:
            return False
        
        task.progress = min(100, task.progress + progress_increment)
        task.actual_time += time_spent
        
        if notes:
            task.notes.append({
                "content": notes,
                "timestamp": datetime.now().isoformat()
            })
        
        # 任务完成
        if task.progress >= 100:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            # 获得经验值
            self.add_xp(task.xp_reward)
            # 检查成就
            self.check_achievements()
            # 更新其他任务的可用性
            self.update_task_availability()
        
        self.save_data()
        return True
    
    def add_xp(self, xp: int):
        """添加经验值并升级"""
        self.player_xp += xp
        # 简单的升级公式：每500经验升一级
        new_level = 1 + self.player_xp // 500
        if new_level > self.player_level:
            self.player_level = new_level
            return True  # 升级了
        return False
    
    def create_side_task(self, name: str, description: str, 
                        estimated_time: float, xp_reward: int,
                        parent_task_id: Optional[str] = None):
        """创建自定义支线任务"""
        task_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        prerequisites = [parent_task_id] if parent_task_id else []
        
        new_task = LearningTask(
            task_id=task_id,
            name=name,
            task_type=TaskType.SIDE,
            description=description,
            estimated_time=estimated_time,
            xp_reward=xp_reward,
            prerequisites=prerequisites
        )
        self.add_task(new_task)
        return new_task
    
    def check_achievements(self):
        """检查成就"""
        completed_count = sum(1 for t in self.tasks.values() 
                            if t.status == TaskStatus.COMPLETED)
        
        main_completed = all(t.status == TaskStatus.COMPLETED 
                            for t in self.tasks.values() 
                            if t.type == TaskType.MAIN)
        
        achievements_to_check = [
            ("first_blood", "首战告捷", "完成第一个任务", completed_count >= 1),
            ("task_master", "任务大师", "完成10个任务", completed_count >= 10),
            ("main_story", "主线通关", "完成所有主线任务", main_completed),
        ]
        
        new_achievements = []
        for ach_id, ach_name, ach_desc, achieved in achievements_to_check:
            if achieved and ach_id not in [a["id"] for a in self.achievements]:
                new_achievements.append({
                    "id": ach_id,
                    "name": ach_name,
                    "description": ach_desc,
                    "earned_at": datetime.now().isoformat()
                })
        
        self.achievements.extend(new_achievements)
        if new_achievements:
            self.save_data()
    
    def get_task_tree_data(self) -> Dict:
        """获取任务树结构数据"""
        main_tasks = [t for t in self.tasks.values() if t.type == TaskType.MAIN]
        side_tasks = [t for t in self.tasks.values() if t.type == TaskType.SIDE]
        daily_tasks = [t for t in self.tasks.values() if t.type == TaskType.DAILY]
        
        return {
            "main": [t.to_dict() for t in sorted(main_tasks, key=lambda x: x.id)],
            "side": [t.to_dict() for t in side_tasks],
            "daily": [t.to_dict() for t in daily_tasks],
            "player": {
                "level": self.player_level,
                "xp": self.player_xp,
                "next_level_xp": self.player_level * 500,
                "achievements": self.achievements
            }
        }
    
    def save_data(self):
        """保存数据"""
        data = {
            "player_level": self.player_level,
            "player_xp": self.player_xp,
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "achievements": self.achievements
        }
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
