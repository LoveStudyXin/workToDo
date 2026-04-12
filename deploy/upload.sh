#!/bin/bash

# ============================================
# 代码上传脚本 - 本地执行
# 使用方法: ./upload.sh
# ============================================

set -e

# ========== 配置区域 - 请修改以下变量 ==========
SERVER_IP="106.14.148.230"        # 服务器IP地址
SERVER_USER="root"                 # SSH用户名
SERVER_PATH="/www/wwwroot/work-todo"   # 服务器上的项目路径
SSH_KEY="$HOME/.ssh/id_work"       # SSH密钥路径(可选)，例如: ~/.ssh/id_rsa
# =============================================

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[步骤]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查配置
if [ "$SERVER_IP" == "your_server_ip" ]; then
    print_error "请先编辑此脚本，配置 SERVER_IP 等变量"
    exit 1
fi

# SSH 选项
SSH_OPTS="-o StrictHostKeyChecking=no -o ConnectTimeout=10"
if [ -n "$SSH_KEY" ] && [ -f "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

# 构建 SSH/SCP 命令
SSH_CMD="ssh $SSH_OPTS $SERVER_USER@$SERVER_IP"
SCP_CMD="scp $SSH_OPTS"
RSYNC_CMD="rsync -avz --progress -e \"ssh $SSH_OPTS\""

echo ""
echo "=========================================="
echo "  工作 TODO 代码上传脚本"
echo "=========================================="
echo ""
print_info "服务器: $SERVER_USER@$SERVER_IP"
print_info "路径: $SERVER_PATH"
print_info "本地项目: $PROJECT_DIR"
echo ""

# 选择上传模式
echo "请选择操作："
echo "  1) 上传后端代码"
echo "  2) 上传前端代码（仅源码，服务器编译）"
echo "  3) 上传前端编译后的 dist"
echo "  4) 全部上传（后端 + 前端源码）"
echo "  5) 全部上传（后端 + 前端 dist）"
echo "  6) 仅同步更新（增量上传）"
echo ""
read -p "请输入选项 [1-6]: " choice

case $choice in
    1)
        print_step "上传后端代码..."
        $SSH_CMD "mkdir -p $SERVER_PATH/backend"
        eval $RSYNC_CMD \
            --exclude 'venv/' \
            --exclude '__pycache__/' \
            --exclude '*.pyc' \
            --exclude '.env' \
            --exclude '*.db' \
            --exclude '.pytest_cache/' \
            "$PROJECT_DIR/backend/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/backend/"
        print_step "后端上传完成"
        ;;
    2)
        print_step "上传前端源码..."
        $SSH_CMD "mkdir -p $SERVER_PATH/frontend"
        eval $RSYNC_CMD \
            --exclude 'node_modules/' \
            --exclude 'dist/' \
            --exclude '.env.local' \
            "$PROJECT_DIR/frontend/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/frontend/"
        print_step "前端源码上传完成"
        print_warn "请在服务器上执行 npm install && npx vite build"
        ;;
    3)
        print_step "本地构建前端..."
        cd "$PROJECT_DIR/frontend"
        npx vite build

        print_step "上传 dist 目录..."
        $SSH_CMD "mkdir -p $SERVER_PATH/frontend/dist"
        eval $RSYNC_CMD --delete --exclude '.user.ini' \
            "$PROJECT_DIR/frontend/dist/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/frontend/dist/" || true
        print_step "前端 dist 上传完成"
        ;;
    4)
        print_step "上传后端代码..."
        $SSH_CMD "mkdir -p $SERVER_PATH/backend"
        eval $RSYNC_CMD \
            --exclude 'venv/' \
            --exclude '__pycache__/' \
            --exclude '*.pyc' \
            --exclude '.env' \
            --exclude '*.db' \
            --exclude '.pytest_cache/' \
            "$PROJECT_DIR/backend/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/backend/"

        print_step "上传前端源码..."
        $SSH_CMD "mkdir -p $SERVER_PATH/frontend"
        eval $RSYNC_CMD \
            --exclude 'node_modules/' \
            --exclude 'dist/' \
            --exclude '.env.local' \
            "$PROJECT_DIR/frontend/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/frontend/"

        print_step "全部上传完成"
        ;;
    5)
        print_step "上传后端代码..."
        $SSH_CMD "mkdir -p $SERVER_PATH/backend"
        eval $RSYNC_CMD \
            --exclude 'venv/' \
            --exclude '__pycache__/' \
            --exclude '*.pyc' \
            --exclude '.env' \
            --exclude '*.db' \
            --exclude '.pytest_cache/' \
            "$PROJECT_DIR/backend/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/backend/"

        print_step "本地构建前端..."
        cd "$PROJECT_DIR/frontend"
        npx vite build

        print_step "上传 dist 目录..."
        $SSH_CMD "mkdir -p $SERVER_PATH/frontend/dist"
        eval $RSYNC_CMD --delete --exclude '.user.ini' \
            "$PROJECT_DIR/frontend/dist/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/frontend/dist/" || true

        print_step "全部上传完成"
        ;;
    6)
        print_step "增量同步所有文件..."
        $SSH_CMD "mkdir -p $SERVER_PATH"
        eval $RSYNC_CMD \
            --exclude 'venv/' \
            --exclude 'node_modules/' \
            --exclude '__pycache__/' \
            --exclude '*.pyc' \
            --exclude '.env' \
            --exclude '*.db' \
            --exclude '.pytest_cache/' \
            --exclude 'frontend-slides-main/' \
            "$PROJECT_DIR/" "$SERVER_USER@$SERVER_IP:$SERVER_PATH/"
        print_step "同步完成"
        ;;
    *)
        print_error "无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
print_step "上传完成！"
echo "=========================================="
echo ""
print_info "接下来在服务器上执行："
echo ""
echo "  # 后端重启"
echo "  cd $SERVER_PATH/backend"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  python -m alembic upgrade head"
echo "  pkill -f 'uvicorn.*8001' && nohup uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/work-todo.log 2>&1 &"
echo ""
echo "  # 如果上传的是前端源码"
echo "  cd $SERVER_PATH/frontend"
echo "  npm install && npx vite build"
echo ""

# 询问是否自动重启服务
read -p "是否自动重启后端服务? [y/N]: " restart
if [ "$restart" == "y" ] || [ "$restart" == "Y" ]; then
    print_step "重启后端服务..."
    $SSH_CMD "cd $SERVER_PATH/backend && source venv/bin/activate && pip install -r requirements.txt -q && python -m alembic upgrade head && pkill -f 'uvicorn.*8001'; nohup uvicorn app.main:app --host 127.0.0.1 --port 8001 > /tmp/work-todo.log 2>&1 &"
    sleep 2
    print_step "服务已重启"

    # 检查服务状态
    print_info "服务状态："
    $SSH_CMD "netstat -tlnp | grep 8001"
fi

echo ""
print_step "全部完成！"
