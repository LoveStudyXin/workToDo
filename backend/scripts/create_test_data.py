"""
创建测试账号和一年的测试数据
"""
import asyncio
import random
from datetime import datetime, date, timedelta
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 导入模型
import sys
sys.path.insert(0, '/Users/xieyuxin/Downloads/工作todo/backend')

from app.database import Base
from app.models.user import User
from app.models.todo import Todo
from app.models.work_log import WorkLog
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 测试数据配置
TEST_USER = {
    "username": "test",
    "email": "test@example.com",
    "password": "test123"
}

# 任务分类
CATEGORIES = ["开发", "设计", "测试", "文档", "会议", "学习", "运维", "其他"]

# 任务模板
TASK_TEMPLATES = [
    # 开发
    ("完成用户登录模块开发", "开发", 4),
    ("修复订单页面bug", "开发", 5),
    ("优化数据库查询性能", "开发", 3),
    ("实现支付接口对接", "开发", 4),
    ("重构用户中心代码", "开发", 3),
    ("添加数据导出功能", "开发", 3),
    ("实现消息推送功能", "开发", 4),
    ("完成API文档编写", "开发", 2),
    ("修复移动端适配问题", "开发", 4),
    ("实现搜索功能优化", "开发", 3),
    # 设计
    ("设计新版首页UI", "设计", 4),
    ("制作产品宣传图", "设计", 3),
    ("优化用户体验流程", "设计", 3),
    ("设计活动页面", "设计", 4),
    ("制作图标素材", "设计", 2),
    # 测试
    ("执行回归测试", "测试", 4),
    ("编写测试用例", "测试", 3),
    ("性能压力测试", "测试", 4),
    ("兼容性测试", "测试", 3),
    ("安全测试", "测试", 5),
    # 文档
    ("编写技术方案", "文档", 3),
    ("更新API文档", "文档", 2),
    ("编写用户手册", "文档", 2),
    ("整理会议纪要", "文档", 1),
    # 会议
    ("参加需求评审会", "会议", 3),
    ("团队周会", "会议", 2),
    ("客户沟通会议", "会议", 4),
    ("技术分享会", "会议", 2),
    # 学习
    ("学习新框架", "学习", 2),
    ("阅读技术文章", "学习", 1),
    ("参加线上课程", "学习", 2),
    ("研究竞品功能", "学习", 2),
    # 运维
    ("服务器维护", "运维", 4),
    ("数据库备份", "运维", 3),
    ("监控告警处理", "运维", 5),
    ("部署新版本", "运维", 4),
    # 其他
    ("处理用户反馈", "其他", 3),
    ("协助同事解决问题", "其他", 2),
    ("整理工作台", "其他", 1),
]


async def create_test_data():
    """创建测试数据"""
    # 创建数据库连接
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # 1. 创建测试用户
        print("创建测试用户...")
        hashed_password = pwd_context.hash(TEST_USER["password"])
        user = User(
            username=TEST_USER["username"],
            email=TEST_USER["email"],
            password_hash=hashed_password
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"  用户创建成功: {user.username} (ID: {user.id})")

        # 2. 创建一年的任务数据
        print("创建任务数据...")
        today = date.today()
        start_date = today - timedelta(days=365)

        todos = []
        work_logs = []

        # 生成任务
        current_date = start_date
        task_id_counter = 0

        while current_date <= today:
            # 每天随机创建 0-3 个任务
            num_tasks = random.randint(0, 3)

            for _ in range(num_tasks):
                template = random.choice(TASK_TEMPLATES)
                title_base, category, priority = template

                # 添加日期后缀使标题唯一
                title = f"{title_base} - {current_date.strftime('%m%d')}-{task_id_counter}"
                task_id_counter += 1

                # 随机生成任务属性
                estimated_hours = random.choice([1, 2, 4, 8, 16])

                # 根据日期决定任务状态
                days_ago = (today - current_date).days
                if days_ago > 30:
                    # 30天前的任务大部分已完成
                    status = random.choices(
                        ["completed", "in_progress", "pending"],
                        weights=[85, 10, 5]
                    )[0]
                elif days_ago > 7:
                    # 7-30天的任务
                    status = random.choices(
                        ["completed", "in_progress", "pending"],
                        weights=[70, 20, 10]
                    )[0]
                else:
                    # 最近7天的任务
                    status = random.choices(
                        ["completed", "in_progress", "pending"],
                        weights=[30, 40, 30]
                    )[0]

                # 根据状态设置进度
                if status == "completed":
                    progress = 100
                    actual_hours = estimated_hours * random.uniform(0.8, 1.5)
                    completed_at = datetime.combine(
                        current_date + timedelta(days=random.randint(1, 7)),
                        datetime.min.time()
                    )
                    if completed_at.date() > today:
                        completed_at = datetime.combine(today, datetime.min.time())
                elif status == "in_progress":
                    progress = random.choice([25, 50, 75])
                    actual_hours = estimated_hours * progress / 100 * random.uniform(0.8, 1.2)
                    completed_at = None
                else:
                    progress = 0
                    actual_hours = 0
                    completed_at = None

                # 设置截止日期
                due_date = current_date + timedelta(days=random.randint(3, 14))

                todo = Todo(
                    user_id=user.id,
                    title=title,
                    description=f"这是{title}的详细描述",
                    category=category,
                    priority=priority,
                    status=status,
                    progress=progress,
                    due_date=due_date,
                    estimated_hours=estimated_hours,
                    actual_hours=round(actual_hours, 1) if actual_hours else None,
                    completed_at=completed_at,
                    created_at=datetime.combine(current_date, datetime.min.time())
                )
                todos.append(todo)

            current_date += timedelta(days=1)

        # 批量添加任务
        db.add_all(todos)
        await db.commit()
        print(f"  创建了 {len(todos)} 个任务")

        # 刷新获取ID
        for todo in todos:
            await db.refresh(todo)

        # 3. 创建工作日志
        print("创建工作日志...")

        # 为已完成和进行中的任务创建工作日志
        for todo in todos:
            if todo.status in ["completed", "in_progress"]:
                # 每个任务创建 1-5 条日志
                num_logs = random.randint(1, 5)
                log_date = todo.created_at.date()

                for i in range(num_logs):
                    if log_date > today:
                        break

                    hours = round(random.uniform(0.5, 4), 1)

                    # 进度更新
                    if i == num_logs - 1 and todo.status == "completed":
                        progress_update = 100
                    else:
                        progress_update = min(100, (i + 1) * 100 // num_logs)

                    content_templates = [
                        f"完成了{todo.title}的部分工作",
                        f"继续推进{todo.title}",
                        f"处理{todo.title}相关事项",
                        f"{todo.title}进展顺利",
                        f"解决了{todo.title}中遇到的问题",
                    ]

                    log = WorkLog(
                        user_id=user.id,
                        todo_id=todo.id,
                        date=log_date,
                        content=random.choice(content_templates),
                        hours_spent=hours,
                        progress_update=progress_update,
                        notes=random.choice([None, "顺利完成", "遇到一些问题已解决", "需要进一步跟进"]),
                        created_at=datetime.combine(log_date, datetime.min.time())
                    )
                    work_logs.append(log)

                    log_date += timedelta(days=random.randint(1, 3))

        # 批量添加工作日志
        db.add_all(work_logs)
        await db.commit()
        print(f"  创建了 {len(work_logs)} 条工作日志")

        print("\n" + "="*50)
        print("测试数据创建完成！")
        print("="*50)
        print(f"账号: {TEST_USER['username']}")
        print(f"密码: {TEST_USER['password']}")
        print(f"任务数: {len(todos)}")
        print(f"日志数: {len(work_logs)}")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(create_test_data())
