# 部署指南

## 本地开发测试

### 1. 启动后端

```bash
cd /Users/xieyuxin/Downloads/工作todo/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 2. 启动前端

```bash
cd /Users/xieyuxin/Downloads/工作todo/frontend
npm run dev
```

### 3. 访问测试

打开浏览器访问：http://localhost:5173

---

## 上传到服务器

### 方式一：使用脚本（推荐）

```bash
cd /Users/xieyuxin/Downloads/工作todo
./deploy/upload.sh
```

选择对应选项即可。

### 方式二：手动命令

#### 1. 编译前端

```bash
cd /Users/xieyuxin/Downloads/工作todo/frontend
npx vite build
```

#### 2. 上传前端

```bash
cd /Users/xieyuxin/Downloads/工作todo
rsync -avz --delete \
    -e "ssh -i ~/.ssh/id_work" \
    frontend/dist/ root@106.14.148.230:/www/wwwroot/work-todo/frontend/dist/
```

#### 3. 上传后端

```bash
cd /Users/xieyuxin/Downloads/工作todo
rsync -avz \
    --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude '*.db' \
    -e "ssh -i ~/.ssh/id_work" \
    backend/ root@106.14.148.230:/www/wwwroot/work-todo/backend/
```

#### 4. 重启后端服务

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "pkill -f 'uvicorn.*8001' && cd /www/wwwroot/work-todo/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/work-todo.log 2>&1 &"
```

#### 5. 验证服务状态

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "netstat -tlnp | grep 8001"
```

---

## 服务器信息

| 项目 | 值 |
|-----|-----|
| 服务器 IP | 106.14.148.230 |
| SSH 密钥 | ~/.ssh/id_work |
| 域名 | https://todo.forstar.store |
| 前端路径 | /www/wwwroot/work-todo/frontend/dist |
| 后端路径 | /www/wwwroot/work-todo/backend |
| 后端端口 | 8001 |

---

## 常用运维命令

### 查看后端日志

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "tail -100 /tmp/work-todo.log"
```

### 查看后端进程

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "ps aux | grep uvicorn"
```

### 重启后端

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "pkill -f 'uvicorn.*8001' && cd /www/wwwroot/work-todo/backend && source venv/bin/activate && nohup uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/work-todo.log 2>&1 &"
```

### 安装新依赖后重启

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "cd /www/wwwroot/work-todo/backend && source venv/bin/activate && pip install -r requirements.txt && pkill -f 'uvicorn.*8001' && nohup uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/work-todo.log 2>&1 &"
```

### 执行数据库迁移

```bash
ssh -i ~/.ssh/id_work root@106.14.148.230 "cd /www/wwwroot/work-todo/backend && source venv/bin/activate && python -m alembic upgrade head"
```
