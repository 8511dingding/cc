#!/bin/bash
# deploy.sh - WordPress 部署脚本
# 用法: ./deploy.sh

set -e

# ============================================
# 配置区 - 根据实际修改
# ============================================
SERVER_HOST="43.154.159.91"
SERVER_USER="root"
SERVER_PATH="/www/wwwroot/2026.wangqingsong.com"
SSH_KEY="$HOME/.ssh/tencent_cloud_jianing"
LOCAL_WP_PATH="./local-dev/wordpress"

# 线上数据库配置
DB_NAME="26_wangqingsong"
DB_USER="26_wangqingsong"
DB_PASSWORD="4cNR1wxtEYTRkcEc"
DB_HOST="43.154.159.91"

# 线上 URL 配置
WP_HOME="https://2026.wangqingsong.com"
WP_SITEURL="https://2026.wangqingsong.com"
WP_CONTENT_URL="https://2026.wangqingsong.com/wp-content"

# ============================================
# 函数定义
# ============================================

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# 1. 同步代码文件（排除环境相关文件）
sync_code() {
    log "同步代码文件到服务器..."

    rsync -avz -e "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i $SSH_KEY" \
        --exclude='wp-config.php' \
        --exclude='wp-content/uploads' \
        --exclude='.htaccess' \
        --exclude='.user.ini' \
        --exclude='wp-content/object-cache.php' \
        --exclude='wp-content/advanced-cache.php' \
        "$LOCAL_WP_PATH/" \
        "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"
}

# 2. 替换 wp-config.php 占位符
update_wp_config() {
    log "更新 wp-config.php..."

    ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i $SSH_KEY \
        "$SERVER_USER@$SERVER_HOST" \
        "sed -i \
            -e 's|__DB_NAME__|$DB_NAME|g' \
            -e 's|__DB_USER__|$DB_USER|g' \
            -e 's|__DB_PASSWORD__|$DB_PASSWORD|g' \
            -e 's|__DB_HOST__|$DB_HOST|g' \
            -e 's|__WP_HOME__|$WP_HOME|g' \
            -e 's|__WP_SITEURL__|$WP_SITEURL|g' \
            -e 's|__WP_CONTENT_URL__|$WP_CONTENT_URL|g' \
            $SERVER_PATH/wp-config.php"
}

# 3. 同步用户上传文件（可选）
sync_uploads() {
    log "同步用户上传文件..."
    rsync -avz -e "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i $SSH_KEY" \
        "$LOCAL_WP_PATH/wp-content/uploads/" \
        "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/wp-content/uploads/"
}

# 4. 重载 PHP-FPM
reload_php() {
    log "重载 PHP-FPM..."
    ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i $SSH_KEY \
        "$SERVER_USER@$SERVER_HOST" \
        "php-fpm -t && php-fpm reload 2>/dev/null || systemctl reload php-fpm 2>/dev/null || service php-fpm reload 2>/dev/null || echo 'PHP reload skipped'" \
        || true
}

# 5. 验证网站
verify() {
    log "验证网站状态..."
    STATUS=$(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i $SSH_KEY \
        "$SERVER_USER@$SERVER_HOST" \
        "curl -s -o /dev/null -w '%{http_code}' https://2026.wangqingsong.com/" 2>/dev/null || echo "000")
    log "网站返回状态码: $STATUS"
    if [ "$STATUS" = "200" ]; then
        log "验证通过 ✓"
    else
        log "验证失败，请检查！"
    fi
}

# ============================================
# 主流程
# ============================================

main() {
    log "========== 开始部署 =========="

    sync_code
    update_wp_config
    reload_php
    verify

    log "========== 部署完成 =========="
}

main "$@"
