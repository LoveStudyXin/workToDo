# 工作 Todo + 报告生成应用

一个跨端的工作任务管理应用，支持 Todo 记录、工作进度追踪，并能自动生成日报、周报、月报、年度绩效报告。

## 技术栈

### 前端
- Vue 3 + TypeScript + Vite
- Vant 4 (移动端 UI 组件库)
- Pinia (状态管理)
- Capacitor (跨端构建)

### 后端
- Python FastAPI
- SQLAlchemy (ORM)
- SQLite/PostgreSQL
- JWT 认证
- 国产大模型集成 (DeepSeek/通义千问/文心一言)

## 快速开始

### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env  # 或直接编辑 .env 文件

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档: http://localhost:8000/docs

### 2. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端访问地址: http://localhost:3000

### 3. 移动端构建 (可选)

```bash
cd frontend

# 构建 Web 资源
npm run build

# 添加平台
npm run cap:add:ios      # iOS
npm run cap:add:android  # Android

# 同步资源
npm run cap:sync

# 打开原生项目
npm run cap:open:ios     # 在 Xcode 中打开
npm run cap:open:android # 在 Android Studio 中打开
```

## 功能特性

### Todo 管理
- 创建、编辑、删除任务
- 任务分类 (开发/测试/会议/文档等)
- 优先级设置 (1-5)
- 进度追踪 (0-100%)
- 截止日期设置
- 今日任务快捷视图

### 工作日志
- 每日工作内容记录
- 关联已有任务
- 工时统计
- 问题记录

### 报告生成
- **日报**: 当天任务完成情况
- **周报**: 本周工作汇总与下周计划
- **月报**: 月度工作量统计与分析
- **年度绩效**: 全年工作成果与数据统计

### 模板管理
- 系统预置模板
- 自定义模板
- 支持变量占位符:
  - `{{date_range}}` - 日期范围
  - `{{completed_tasks}}` - 已完成任务
  - `{{in_progress_tasks}}` - 进行中任务
  - `{{total_hours}}` - 工作时长
  - `{{highlights}}` - 工作亮点
  - `{{issues}}` - 问题记录
  - `{{next_plans}}` - 下一步计划

### AI 润色
支持多种国产大模型:
- DeepSeek
- 通义千问 (Qwen)
- 文心一言 (Wenxin)

在 `.env` 文件中配置 API Key 即可使用。

## 项目结构

```
工作todo/
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   ├── stores/        # Pinia 状态
│   │   ├── api/           # API 接口
│   │   ├── router/        # 路由配置
│   │   └── utils/         # 工具函数
│   └── capacitor.config.ts
│
├── backend/               # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 应用入口
│   │   ├── models/       # 数据模型
│   │   ├── routers/      # API 路由
│   │   ├── services/     # 业务逻辑
│   │   └── core/         # 核心配置
│   └── requirements.txt
│
└── README.md
```

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户

### 任务
- `GET /api/todos` - 获取任务列表
- `GET /api/todos/today` - 获取今日任务
- `POST /api/todos` - 创建任务
- `PUT /api/todos/{id}` - 更新任务
- `DELETE /api/todos/{id}` - 删除任务

### 工作日志
- `GET /api/work-logs` - 获取日志列表
- `POST /api/work-logs` - 创建日志
- `PUT /api/work-logs/{id}` - 更新日志
- `DELETE /api/work-logs/{id}` - 删除日志

### 报告
- `POST /api/reports/generate` - 生成报告
- `POST /api/reports/preview` - 预览报告
- `GET /api/reports` - 获取报告列表
- `GET /api/reports/{id}/export/markdown` - 导出 Markdown

### 模板
- `GET /api/templates` - 获取模板列表
- `POST /api/templates` - 创建模板
- `PUT /api/templates/{id}` - 更新模板
- `DELETE /api/templates/{id}` - 删除模板

## 环境变量配置

在 `backend/.env` 文件中配置:

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./work_todo.db

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI 服务 (选择一个)
AI_PROVIDER=deepseek  # deepseek, qwen, wenxin

# DeepSeek
DEEPSEEK_API_KEY=your-api-key

# 通义千问
QWEN_API_KEY=your-api-key

# 文心一言
WENXIN_API_KEY=your-api-key
WENXIN_SECRET_KEY=your-secret-key
```

## 许可证

MIT
