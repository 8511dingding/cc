# wp_wqs

王庆松个人网站的当前本地 WordPress 开发项目。仓库包含正在运行的
WordPress、迁移脚本、旧 Joomla 数据、数据库备份和设计资源。

## 当前本地环境

- 网站地址：`http://localhost:8081/wp_wqs/`
- WordPress 根目录：`local-dev/wordpress/`
- 数据库：`wqs_wordpress`
- MySQL：OrbStack，`127.0.0.1:3306`
- 当前主题：`local-dev/wordpress/wp-content/themes/wqs-portfolio/`
- MU 插件：`local-dev/wordpress/wp-content/mu-plugins/`
- PHP 路由：`local-dev/router.php`
- PHP 工作进程：4
- 运行日志：`local-dev/php8081.log`

ServBay、`wp_wqs.local`、`/Applications/ServBay/www/wqs_2026`、端口 80 和
MySQL 3307 均为已经停用的旧环境，不是当前部署目标。

## 启动网站

```bash
./local-dev/start-wp8081.sh
```

该脚本使用 PHP 内置服务器监听 `localhost:8081`，并通过
`local-dev/router.php` 处理 WordPress 固定链接。当前本地环境关闭了随网页访问
自动触发的 WP-Cron，避免 PHP 开发服务器的回环请求阻塞文章保存。

检查运行状态：

```bash
curl -I http://localhost:8081/wp_wqs/
lsof -nP -iTCP:8081 -sTCP:LISTEN
lsof -nP -iTCP:3306 -sTCP:LISTEN
tail -f local-dev/php8081.log
```

## URL 配置

`local-dev/wordpress/wp-config.php` 中的当前配置：

```php
define('WP_HOME', 'http://localhost:8081/wp_wqs');
define('WP_SITEURL', 'http://localhost:8081/wp_wqs');
define('WP_CONTENT_URL', 'http://localhost:8081/wp_wqs/wp-content');
```

## 目录说明

- `local-dev/wordpress/`：当前运行的 WordPress。
- `local-dev/router.php`：PHP 内置服务器路由。
- `local-dev/start-wp8081.sh`：启动或重启本地网站。
- `migration-scripts/`：Joomla 到 WordPress 的迁移和修复脚本。
- `database-export/`：旧数据库导出。
- `old-site/`：旧 Joomla 站点资料。
- `design/`：Logo 等设计资源。
- `local-dev/debug_report.md`：早期迁移故障记录，仅作历史参考。

## 修改与验证

网站修改应直接写入 `local-dev/wordpress/`。不需要同步到其他 Web 根目录。

完成修改后至少检查：

```bash
php -l path/to/changed-file.php
curl -I http://localhost:8081/wp_wqs/
```
