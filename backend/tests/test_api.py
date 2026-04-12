"""
API 测试用例
运行方式: cd backend && pytest tests/test_api.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from datetime import date, timedelta

from app.main import app
from app.database import Base, engine, get_db
from app.models.report_template import ReportTemplate
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """每个测试前创建表，测试后删除"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建默认报告模板
    async with TestSessionLocal() as session:
        templates = [
            ReportTemplate(
                name="默认日报模板",
                type="daily",
                template_content="# 日报 {{ start_date }}\n\n## 完成的任务\n{% for todo in completed_todos %}\n- {{ todo.title }}\n{% endfor %}\n\n## 进行中的任务\n{% for todo in in_progress_todos %}\n- {{ todo.title }} ({{ todo.progress }}%)\n{% endfor %}",
                is_default=True,
                user_id=None
            ),
            ReportTemplate(
                name="默认周报模板",
                type="weekly",
                template_content="# 周报 {{ start_date }} ~ {{ end_date }}\n\n## 本周完成\n{% for todo in completed_todos %}\n- {{ todo.title }}\n{% endfor %}\n\n## 进行中\n{% for todo in in_progress_todos %}\n- {{ todo.title }}\n{% endfor %}",
                is_default=True,
                user_id=None
            ),
            ReportTemplate(
                name="默认月报模板",
                type="monthly",
                template_content="# 月报 {{ start_date }} ~ {{ end_date }}\n\n## 完成任务\n{% for todo in completed_todos %}\n- {{ todo.title }}\n{% endfor %}",
                is_default=True,
                user_id=None
            ),
        ]
        for template in templates:
            session.add(template)
        await session.commit()

    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(setup_database):
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client):
    """创建已登录的测试客户端"""
    # 先注册用户
    await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    # 登录获取 token
    response = await client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# ==================== 用户认证测试 ====================

class TestAuth:
    """用户认证相关测试"""

    async def test_register_success(self, client):
        """测试注册成功"""
        response = await client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"

    async def test_register_duplicate_username(self, client):
        """测试重复用户名注册"""
        # 先注册一个用户
        await client.post("/api/auth/register", json={
            "username": "existuser",
            "email": "exist@example.com",
            "password": "password123"
        })
        # 尝试用相同用户名注册
        response = await client.post("/api/auth/register", json={
            "username": "existuser",
            "email": "other@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "用户名已被使用" in response.json()["detail"]

    async def test_register_duplicate_email(self, client):
        """测试重复邮箱注册"""
        await client.post("/api/auth/register", json={
            "username": "user1",
            "email": "same@example.com",
            "password": "password123"
        })
        response = await client.post("/api/auth/register", json={
            "username": "user2",
            "email": "same@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "邮箱已被使用" in response.json()["detail"]

    async def test_login_success(self, client):
        """测试登录成功"""
        # 先注册
        await client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123"
        })
        # 登录
        response = await client.post("/api/auth/login", data={
            "username": "loginuser",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_username(self, client):
        """测试用户名不存在"""
        response = await client.post("/api/auth/login", data={
            "username": "nonexistent",
            "password": "password123"
        })
        assert response.status_code == 401
        assert "未注册" in response.json()["detail"]

    async def test_login_wrong_password(self, client):
        """测试密码错误"""
        # 先注册
        await client.post("/api/auth/register", json={
            "username": "pwduser",
            "email": "pwd@example.com",
            "password": "password123"
        })
        # 用错误密码登录
        response = await client.post("/api/auth/login", data={
            "username": "pwduser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "密码错误" in response.json()["detail"]

    async def test_get_current_user(self, auth_client):
        """测试获取当前用户信息"""
        response = await auth_client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"


# ==================== 任务管理测试 ====================

class TestTodos:
    """任务管理相关测试"""

    async def test_create_todo(self, auth_client):
        """测试创建任务"""
        response = await auth_client.post("/api/todos", json={
            "title": "测试任务",
            "description": "这是一个测试任务",
            "category": "开发",
            "priority": 4,
            "due_date": str(date.today() + timedelta(days=7))
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "测试任务"
        assert data["category"] == "开发"
        assert data["priority"] == 4
        assert data["status"] == "pending"

    async def test_get_todos(self, auth_client):
        """测试获取任务列表"""
        # 创建几个任务
        await auth_client.post("/api/todos", json={"title": "任务1", "category": "开发"})
        await auth_client.post("/api/todos", json={"title": "任务2", "category": "测试"})

        response = await auth_client.get("/api/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_todos_by_status(self, auth_client):
        """测试按状态筛选任务"""
        # 创建任务
        res = await auth_client.post("/api/todos", json={"title": "进行中任务"})
        todo_id = res.json()["id"]
        # 更新状态
        await auth_client.put(f"/api/todos/{todo_id}", json={"status": "in_progress"})

        response = await auth_client.get("/api/todos?status=in_progress")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "in_progress"

    async def test_get_today_todos(self, auth_client):
        """测试获取今日任务"""
        # 创建今天到期的任务
        await auth_client.post("/api/todos", json={
            "title": "今日任务",
            "due_date": str(date.today())
        })
        # 创建未来任务
        await auth_client.post("/api/todos", json={
            "title": "未来任务",
            "due_date": str(date.today() + timedelta(days=7))
        })

        response = await auth_client.get("/api/todos/today")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "今日任务"

    async def test_update_todo(self, auth_client):
        """测试更新任务"""
        # 创建任务
        res = await auth_client.post("/api/todos", json={"title": "原标题"})
        todo_id = res.json()["id"]

        # 更新
        response = await auth_client.put(f"/api/todos/{todo_id}", json={
            "title": "新标题",
            "status": "in_progress",
            "progress": 50
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"
        assert data["status"] == "in_progress"
        assert data["progress"] == 50

    async def test_delete_todo(self, auth_client):
        """测试删除任务"""
        # 创建任务
        res = await auth_client.post("/api/todos", json={"title": "待删除"})
        todo_id = res.json()["id"]

        # 删除
        response = await auth_client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 200

        # 确认已删除
        response = await auth_client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 404

    async def test_complete_todo(self, auth_client):
        """测试完成任务"""
        # 创建任务
        res = await auth_client.post("/api/todos", json={"title": "待完成"})
        todo_id = res.json()["id"]

        # 标记完成
        response = await auth_client.put(f"/api/todos/{todo_id}", json={
            "status": "completed",
            "progress": 100
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress"] == 100
        assert data["completed_at"] is not None


# ==================== 工作日志测试 ====================

class TestWorkLogs:
    """工作日志相关测试"""

    async def test_create_work_log(self, auth_client):
        """测试创建工作日志"""
        # 先创建任务
        res = await auth_client.post("/api/todos", json={"title": "日志任务"})
        todo_id = res.json()["id"]

        # 创建日志
        response = await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(date.today()),
            "content": "完成了部分工作",
            "hours_spent": 2.5,
            "progress_update": 30
        })
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "完成了部分工作"
        assert data["hours_spent"] == 2.5

    async def test_get_work_logs(self, auth_client):
        """测试获取工作日志列表"""
        # 创建任务
        res = await auth_client.post("/api/todos", json={"title": "日志任务"})
        todo_id = res.json()["id"]

        # 创建多条日志
        await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(date.today()),
            "content": "日志1",
            "hours_spent": 1
        })
        await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(date.today()),
            "content": "日志2",
            "hours_spent": 2
        })

        response = await auth_client.get("/api/work-logs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_get_work_logs_by_date(self, auth_client):
        """测试按日期筛选工作日志"""
        res = await auth_client.post("/api/todos", json={"title": "日志任务"})
        todo_id = res.json()["id"]

        today = date.today()
        yesterday = today - timedelta(days=1)

        await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(today),
            "content": "今天的日志",
            "hours_spent": 1
        })
        await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(yesterday),
            "content": "昨天的日志",
            "hours_spent": 1
        })

        response = await auth_client.get(f"/api/work-logs?start_date={today}&end_date={today}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "今天的日志"

    async def test_update_work_log(self, auth_client):
        """测试更新工作日志"""
        res = await auth_client.post("/api/todos", json={"title": "日志任务"})
        todo_id = res.json()["id"]

        res = await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(date.today()),
            "content": "原内容",
            "hours_spent": 1
        })
        log_id = res.json()["id"]

        response = await auth_client.put(f"/api/work-logs/{log_id}", json={
            "content": "更新后的内容",
            "hours_spent": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "更新后的内容"
        assert data["hours_spent"] == 3

    async def test_delete_work_log(self, auth_client):
        """测试删除工作日志"""
        res = await auth_client.post("/api/todos", json={"title": "日志任务"})
        todo_id = res.json()["id"]

        res = await auth_client.post("/api/work-logs", json={
            "todo_id": todo_id,
            "date": str(date.today()),
            "content": "待删除",
            "hours_spent": 1
        })
        log_id = res.json()["id"]

        response = await auth_client.delete(f"/api/work-logs/{log_id}")
        assert response.status_code == 200


# ==================== 报告测试 ====================

class TestReports:
    """报告相关测试"""

    async def test_preview_report(self, auth_client):
        """测试预览报告"""
        # 创建一些任务数据
        await auth_client.post("/api/todos", json={
            "title": "报告测试任务",
            "category": "开发"
        })

        response = await auth_client.post("/api/reports/preview", json={
            "type": "daily",
            "start_date": str(date.today()),
            "end_date": str(date.today()),
            "use_ai": False
        })
        assert response.status_code == 200
        data = response.json()
        assert "raw_content" in data

    async def test_generate_report(self, auth_client):
        """测试生成报告"""
        response = await auth_client.post("/api/reports/generate", json={
            "type": "weekly",
            "start_date": str(date.today() - timedelta(days=7)),
            "end_date": str(date.today()),
            "use_ai": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "weekly"
        assert "raw_content" in data

    async def test_get_reports(self, auth_client):
        """测试获取报告列表"""
        # 先生成一个报告
        gen_res = await auth_client.post("/api/reports/generate", json={
            "type": "daily",
            "start_date": str(date.today()),
            "end_date": str(date.today()),
            "use_ai": False
        })
        assert gen_res.status_code == 200

        response = await auth_client.get("/api/reports")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_presentation_styles(self, auth_client):
        """测试获取演示文稿风格列表"""
        response = await auth_client.get("/api/reports/presentation/styles")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0  # 应该有多种风格


# ==================== 模板测试 ====================

class TestTemplates:
    """模板相关测试"""

    async def test_get_templates(self, auth_client):
        """测试获取模板列表（应包含系统默认模板）"""
        response = await auth_client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # 至少有日报、周报、月报模板
        # 检查是否包含系统默认模板
        types = [t["type"] for t in data]
        assert "daily" in types
        assert "weekly" in types

    async def test_copy_template(self, auth_client):
        """测试复制模板到用户名下"""
        # 获取系统模板列表
        res = await auth_client.get("/api/templates?type=daily")
        templates = res.json()
        assert len(templates) > 0
        template_id = templates[0]["id"]

        # 复制模板
        response = await auth_client.post(f"/api/templates/{template_id}/copy")
        assert response.status_code == 200
        data = response.json()
        assert "副本" in data["name"]
        assert data["type"] == "daily"
        assert data["user_id"] is not None  # 归属于当前用户

    async def test_update_own_template(self, auth_client):
        """测试修改自己的模板"""
        # 先复制一个模板
        res = await auth_client.get("/api/templates?type=daily")
        template_id = res.json()[0]["id"]
        copy_res = await auth_client.post(f"/api/templates/{template_id}/copy")
        my_template_id = copy_res.json()["id"]

        # 修改自己的模板
        response = await auth_client.put(f"/api/templates/{my_template_id}", json={
            "name": "我的自定义日报",
            "template_content": "# 自定义内容"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "我的自定义日报"

    async def test_cannot_update_system_template(self, auth_client):
        """测试无法修改系统模板"""
        # 获取系统模板
        res = await auth_client.get("/api/templates?type=daily")
        templates = res.json()
        # 找到系统模板（user_id 为 None）
        system_template = next((t for t in templates if t.get("user_id") is None), None)
        assert system_template is not None

        # 尝试修改系统模板
        response = await auth_client.put(f"/api/templates/{system_template['id']}", json={
            "name": "尝试修改系统模板"
        })
        assert response.status_code == 404  # 应该无权修改

    async def test_delete_own_template(self, auth_client):
        """测试删除自己的模板"""
        # 先复制一个模板
        res = await auth_client.get("/api/templates?type=weekly")
        template_id = res.json()[0]["id"]
        copy_res = await auth_client.post(f"/api/templates/{template_id}/copy")
        my_template_id = copy_res.json()["id"]

        # 删除自己的模板
        response = await auth_client.delete(f"/api/templates/{my_template_id}")
        assert response.status_code == 200

        # 确认已删除
        get_res = await auth_client.get(f"/api/templates/{my_template_id}")
        assert get_res.status_code == 404


# ==================== 权限测试 ====================

class TestPermissions:
    """权限相关测试"""

    async def test_unauthorized_access(self, client):
        """测试未授权访问"""
        response = await client.get("/api/todos")
        assert response.status_code == 401

    async def test_access_other_user_todo(self, client, setup_database):
        """测试访问其他用户的任务"""
        # 创建用户1
        await client.post("/api/auth/register", json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123"
        })
        res = await client.post("/api/auth/login", data={
            "username": "user1",
            "password": "password123"
        })
        token1 = res.json()["access_token"]

        # 用户1创建任务
        client.headers["Authorization"] = f"Bearer {token1}"
        res = await client.post("/api/todos", json={"title": "用户1的任务"})
        todo_id = res.json()["id"]

        # 创建用户2
        await client.post("/api/auth/register", json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123"
        })
        res = await client.post("/api/auth/login", data={
            "username": "user2",
            "password": "password123"
        })
        token2 = res.json()["access_token"]

        # 用户2尝试访问用户1的任务
        client.headers["Authorization"] = f"Bearer {token2}"
        response = await client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 404  # 应该看不到
