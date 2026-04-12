#!/bin/bash

# 工作 TODO 部署脚本
# 使用方法: ./deploy.sh

set -e

echo "=========================================="
echo "  工作 TODO 部署脚本"
echo "=========================================="

# 配置变量 - 请根据实际情况修改
APP_DIR="/var/www/work-todo"
DOMAIN="your-domain.com"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${GREEN}[步骤]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    print_error "请使用 root 用户运行此脚本"
    exit 1
fi

# 1. 安装系统依赖
print_step "安装系统依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx mysql-server nodejs npm

# 2. 创建应用目录
print_step "创建应用目录..."
mkdir -p $APP_DIR
cd $APP_DIR

# 3. 复制文件（假设文件已上传到 /tmp/work-todo）
print_step "复制应用文件..."
if [ -d "/tmp/work-todo" ]; then
    cp -r /tmp/work-todo/* $APP_DIR/
else
    print_warn "请先将项目文件上传到 /tmp/work-todo"
    print_warn "或者使用 git clone 拉取代码"
fi

# 4. 配置后端
print_step "配置后端..."
cd $APP_DIR/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 检查 .env 文件
if [ ! -f ".env" ]; then
    print_warn "请复制 .env.production 为 .env 并修改配置"
    cp .env.production .env
    print_warn "修改完成后重新运行此脚本"
    exit 1
fi

# 5. 配置 MySQL 数据库
print_step "配置数据库..."
echo "请手动创建数据库："
echo "  mysql -u root -p"
echo "  CREATE DATABASE work_todo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "  CREATE USER 'worktodo'@'localhost' IDENTIFIED BY '你的密码';"
echo "  GRANT ALL PRIVILEGES ON work_todo.* TO 'worktodo'@'localhost';"
echo "  FLUSH PRIVILEGES;"

# 6. 构建前端
print_step "构建前端..."
cd $APP_DIR/frontend
npm install
npm run build

# 7. 配置 Nginx
print_step "配置 Nginx..."
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/work-todo
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/work-todo
sed -i "s|/var/www/work-todo|$APP_DIR|g" /etc/nginx/sites-available/work-todo
ln -sf /etc/nginx/sites-available/work-todo /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 8. 创建 systemd 服务
print_step "创建后端服务..."
cat > /etc/systemd/system/work-todo.service << EOF
[Unit]
Description=Work TODO Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/backend/venv/bin
ExecStart=$APP_DIR/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable work-todo
systemctl start work-todo

# 9. 配置 HTTPS（可选）
print_step "配置 HTTPS..."
echo "建议使用 certbot 配置 HTTPS："
echo "  apt install certbot python3-certbot-nginx"
echo "  certbot --nginx -d $DOMAIN"

echo ""
echo "=========================================="
echo -e "${GREEN}  部署完成！${NC}"
echo "=========================================="
echo "访问地址: http://$DOMAIN"
echo ""
echo "常用命令："
echo "  查看后端状态: systemctl status work-todo"
echo "  重启后端: systemctl restart work-todo"
echo "  查看日志: journalctl -u work-todo -f"
