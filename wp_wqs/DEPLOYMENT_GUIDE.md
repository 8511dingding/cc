# WordPress 部署指南

## 概述

WordPress 包含两类文件：
- **代码文件** - 主题、插件、WordPress 核心
- **环境相关文件** - 数据库配置、URL、用户上传内容

本方案解决：代码同步时保护环境特定的配置不被覆盖。

---

## 环境分类

| 环境 | 路径示例 | 说明 |
|------|----------|------|
| 本地开发 | `/Users/jianing/Ning's Git/wp_wqs/local-dev/wordpress/` | 本地开发环境 |
| 线上生产 | `/www/wwwroot/2026.wangqingsong.com/` | 腾讯云服务器 |

---

## 关键文件处理策略

### 1. wp-config.php - 使用占位符模板

**原理**: 把 `wp-config.php` 改成模板，部署时替换真实值。

```
// wp-config.php.template
define( 'DB_NAME', '__DB_NAME__' );
define( 'DB_USER', '__DB_USER__' );
define( 'DB_PASSWORD', '__DB_PASSWORD__' );
define( 'DB_HOST', '__DB_HOST__' );

define('WP_HOME', '__WP_HOME__' );
define('WP_SITEURL', '__WP_SITEURL__' );
define('WP_CONTENT_URL', '__WP_CONTENT_URL__' );
```

**部署时**: 脚本自动替换占位符为环境对应的值。

### 2. wp-content/uploads/ - 独立同步

**原理**: 用户上传的图片不走 Git，直接用 rsync 同步。

```bash
# 同步图片到服务器（不覆盖 wp-config.php 和数据库）
rsync -avz --exclude='wp-config.php' --exclude='wp-content/db.php' \
  local-dev/wordpress/wp-content/uploads/ \
  root@server:/www/wwwroot/2026.wangqingsong.com/wp-content/uploads/
```

### 3. Nginx 配置文件 - 服务器本地管理

**原理**: Nginx 配置在服务器上手动管理，不从 Git 同步。

需要关注时，手动检查并更新：
```bash
# 服务器上查看
cat /www/server/panel/vhost/nginx/extension/2026.wangqingsong.com/wordpress.conf
```

---

## 部署脚本

在项目根目录创建 `deploy.sh`：

```bash
#!/bin/bash
# deploy.sh - WordPress 部署脚本

set -e

# ============================================
# 配置区 - 根据实际修改
# ============================================
SERVER_HOST="43.154.159.91"
SERVER_USER="root"
SERVER_PATH="/www/wwwroot/2026.wangqingsong.com"
SSH_KEY="~/.ssh/tencent_cloud_jianing"
LOCAL_WP_PATH="./local-dev/wordpress"

# 线上数据库配置（这些值存在服务器上，不提交到 Git）
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

# 3. 同步用户上传文件
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
        "php-fpm -t && php-fpm reload 2>/dev/null || systemctl reload php-fpm 2>/dev/null || service php-fpm reload 2>/dev/null || echo 'PHP reload skipped'"
}

# 5. 验证网站
verify() {
    log "验证网站状态..."
    ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i $SSH_KEY \
        "$SERVER_USER@$SERVER_HOST" \
        "curl -s -o /dev/null -w '%{http_code}' https://2026.wangqingsong.com/"
}

# ============================================
# 主流程
# ============================================

main() {
    log "========== 开始部署 =========="

    sync_code
    update_wp_config
    # sync_uploads  # 暂时注释，上传已完成
    reload_php

    log "========== 部署完成 =========="
}

main "$@"
```

---

## 使用流程

### 日常开发 → 推送代码到 Git

```bash
cd /Users/jianing/Ning\'s\ Git/wp_wqs/
git add .
git commit -m "更新内容"
git push
```

### 部署到服务器

```bash
# 在本地项目目录执行
cd /Users/jianing/Ning\'s\ Git/wp_wqs/
./deploy.sh
```

### 仅同步图片

```bash
# 图片不需要每次都同步，只在有新图片时执行
rsync -avz -e "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -i ~/.ssh/tencent_cloud_jianing" \
    "./local-dev/wordpress/wp-content/uploads/" \
    "root@43.154.159.91:/www/wwwroot/2026.wangqingsong.com/wp-content/uploads/"
```

---

## Nginx 配置（服务器本地管理）

此文件在服务器上手动维护，不从 Git 同步：

**文件位置**: `/www/server/panel/vhost/nginx/extension/2026.wangqingsong.com/wordpress.conf`

**当前内容**:
```nginx
location / {
    try_files $uri $uri/ /index.php?$args;
}

location ~* ^/wp-json/ {
    rewrite ^/wp-json/(.*?)/?$ /?rest_route=/$1&$args last;
}

rewrite /wp-admin$ /wp-admin/ permanent;
```

如需修改 WordPress 伪静态规则，在服务器上编辑此文件。

---

## 数据库配置（服务器本地管理）

数据库连接信息存储在：
- `wp-config.php` 中的占位符（已在 Git 中模板化）
- 实际值在部署脚本 `deploy.sh` 中

如需修改数据库密码：
1. 在腾讯云控制台修改 MySQL 密码
2. 更新 `deploy.sh` 中的 `DB_PASSWORD`
3. 更新服务器上的 `wp-config.php`

---

## 常见问题

### Q: 如果本地 wp-config.php 有新的配置项需要加到线上？
A: 修改 `wp-config.php.template` 添加新占位符，修改 `deploy.sh` 添加替换命令。

### Q: 如何查看服务器上的 wp-config.php 当前内容？
```bash
ssh root@43.154.159.91 "cat /www/wwwroot/2026.wangqingsong.com/wp-config.php"
```

### Q: 如何回滚到旧版本代码？
```bash
# 在本地回滚 Git
git log
git revert <commit-id>  # 创建新提交抵消旧变更
# 或
git reset --hard <commit-id>  # 硬回滚（慎用）

# 然后重新部署
./deploy.sh
```
