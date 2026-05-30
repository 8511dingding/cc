#!/bin/bash
# =========================================
# 舆情分析系统 - 腾讯云部署脚本
# 适用于: Ubuntu + Nginx + Gunicorn
# =========================================
set -e

# 配置区域
APP_NAME="sentiment"
APP_DIR="/opt/sentiment-web"
APP_PORT=8501
BASE_URL="/sentiment"
SYSTEMD_SERVICE="streamlit-sentiment"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检测是否以root运行
if [[ $EUID -ne 0 ]]; then
   log_warn "建议以root权限运行此脚本 (sudo)"
fi

echo "=========================================="
echo "  舆情分析系统 - 腾讯云部署脚本"
echo "=========================================="
echo ""

# ========== Step 1: 创建应用目录 ==========
log_info "Step 1: 创建应用目录..."
mkdir -p ${APP_DIR}
mkdir -p ${APP_DIR}/exports
log_info "应用目录: ${APP_DIR}"

# ========== Step 2: 上传代码 ==========
log_info "Step 2: 请将 web_system 目录下的文件上传到服务器..."
log_warn "在本地执行: scp -r ./web_system/* user@your-server:/opt/sentiment-web/"
echo ""
log_info "或使用 rsync: rsync -avz --exclude='__pycache__' ./web_system/* user@your-server:/opt/sentiment-web/"
echo ""

# ========== Step 3: 安装依赖 ==========
log_info "Step 3: 安装Python依赖..."
echo "请在服务器上执行以下命令:"
echo ""
echo "  cd ${APP_DIR}"
echo "  pip install -r requirements.txt"
echo ""

# ========== Step 4: 配置Systemd服务 ==========
log_info "Step 4: 配置Systemd服务..."
cat > /tmp/${SYSTEMD_SERVICE}.service << EOF
[Unit]
Description=Streamlit Sentiment Analysis Web Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
Restart=always
RestartSec=5
ExecStart=$(which python3) -m streamlit run ${APP_DIR}/app.py \
    --server.port=${APP_PORT} \
    --server.baseUrlPath=${BASE_URL} \
    --server.proxyMode=true \
    --server.headless=true \
    --browser.gatherUsageStats=false

[Install]
WantedBy=multi-user.target
EOF

echo "请将以下内容保存到 /etc/systemd/system/${SYSTEMD_SERVICE}.service:"
echo ""
cat /tmp/${SYSTEMD_SERVICE}.service
echo ""

# ========== Step 5: 配置Nginx ==========
log_info "Step 5: 配置Nginx反向代理..."
cat > /tmp/sentiment_nginx.conf << EOF
# 舆情分析系统 Nginx 配置
location ${BASE_URL}/ {
    proxy_pass http://127.0.0.1:${APP_PORT}/;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;

    # Streamlit WebSocket 支持
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";

    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}

# 静态资源缓存
location ${BASE_URL}/static/ {
    proxy_pass http://127.0.0.1:${APP_PORT}/static/;
    proxy_cache_valid 200 1d;
    expires 1d;
}

# WebSocket 长连接
location ${BASE_URL}/_stcore/ {
    proxy_pass http://127.0.0.1:${APP_PORT}/_stcore/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400s;
}
EOF

echo "请将以下内容保存到 /etc/nginx/sites-available/sentiment:"
echo ""
cat /tmp/sentiment_nginx.conf
echo ""

# ========== Step 6: 启动服务 ==========
log_info "Step 6: 启动服务..."
echo "请在服务器上执行以下命令:"
echo ""
echo "  # 重新加载systemd配置"
echo "  sudo systemctl daemon-reload"
echo ""
echo "  # 启用并启动服务"
echo "  sudo systemctl enable ${SYSTEMD_SERVICE}"
echo "  sudo systemctl start ${SYSTEMD_SERVICE}"
echo ""
echo "  # 检查服务状态"
echo "  sudo systemctl status ${SYSTEMD_SERVICE}"
echo ""
echo "  # 启用Nginx配置"
echo "  sudo ln -s /etc/nginx/sites-available/sentiment /etc/nginx/sites-enabled/"
echo "  sudo nginx -t"
echo "  sudo systemctl reload nginx"
echo ""

# ========== 完成 ==========
echo "=========================================="
log_info "部署完成!"
echo "=========================================="
echo ""
echo "访问地址: http://your-server-ip${BASE_URL}"
echo "默认账号: admin / admin123"
echo ""
echo "常用命令:"
echo "  查看服务状态: sudo systemctl status ${SYSTEMD_SERVICE}"
echo "  查看日志: sudo journalctl -u ${SYSTEMD_SERVICE} -f"
echo "  重启服务: sudo systemctl restart ${SYSTEMD_SERVICE}"
echo "  查看Nginx日志: tail -f /var/log/nginx/sentiment-access.log"
echo ""