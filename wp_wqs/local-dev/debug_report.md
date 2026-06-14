# OrbStack + WordPress 本地开发环境问题报告

## 一、环境概况

### 1.1 目录结构
```
/Users/jianing/Ning's Git/
├── wp_wqs/                                    ← 项目主目录（用户定义的）
│   └── local-dev/
│       └── wordpress/                         ← 新的开发环境目标目录（刚迁移完成）
│           ├── wp-content/plugins/wq-archive/ ← MoMA风格艺术档案库插件
│           ├── wp-content/themes/wqs-archive/ ← 独立主题
│           ├── wp-config.php                  ← 数据库连接配置
│           └── [完整 WordPress 文件]
│
└── sentiment-web-product/
    └── local_portal/
        └── wp_wqs/                            ← 旧站目录（目前线上运行）
            ├── wp-config.php
            └── [完整 WordPress 文件]

OrbStack (macOS 应用)
├── MySQL 容器 → 端口 3306/3307
└── Web 服务 → 端口 8080（当前已映射到旧站）
```

### 1.2 当前访问方式
- **旧站**: http://localhost:8080/wp_wqs/ （正常工作）
- **新站**: http://localhost:8081/ （启动失败，无法访问）

### 1.3 数据库
- OrbStack MySQL，端口 3306
- 数据库名: `wqs_wordpress`
- 用户: root / 密码: GM3750-jm
- 两个站点的 wp-config.php 都配置连接同一个 OrbStack MySQL

---

## 二、问题描述

### 问题一：OrbStack 端口 8080 映射到旧站
- OrbStack 监听 port 8080
- `lsof -i :8080` 显示 OrbStack 进程绑定 `*:http-alt (LISTEN)`
- 旧站 `sentiment-web-product/local_portal/wp_wqs/` 通过 OrbStack 正常访问
- 新站 `wp_wqs/local-dev/wordpress/` 文件已迁移完成，但无法通过 OrbStack 访问

### 问题二：PHP 内置服务器无法在 8081 端口启动
- 执行 `cd /Users/jianing/Ning's Git/wp_wqs/local-dev/wordpress && php -S localhost:8081 -t .`
- 日志文件 `/tmp/php8081.log` 为空
- `lsof -i :8081` 无输出，进程未启动
- `curl http://localhost:8081/` 返回 HTTP 000（连接失败）
- 原因不明

---

## 三、已完成的操作

### 迁移完成
- 执行 `cp -r "/Users/jianing/Ning's Git/sentiment-web-product/local_portal/wp_wqs/"* "/Users/jianing/Ning's Git/wp_wqs/local-dev/wordpress/"`
- 新目录文件完整（27个主要文件和目录）
- 插件 `wq-archive` 和主题 `wqs-archive` 均已复制到新目录
- wp-config.php 数据库配置保持不变（连接 OrbStack MySQL）

### PHP 版本
- `php -v` 显示 PHP 版本正常

---

## 四、期望目标

1. **短期**：让新站 `wp_wqs/local-dev/wordpress/` 能够通过某个 URL 访问（如 localhost:8081）
2. **长期**：替换 OrbStack 的 Web 路由，从旧站切换到新站，让 `localhost:8080` 指向新目录

---

## 五、关键文件路径

| 项目 | 路径 |
|------|------|
| 新站目录 | `/Users/jianing/Ning's Git/wp_wqs/local-dev/wordpress/` |
| 旧站目录 | `/Users/jianing/Ning's Git/sentiment-web-product/local_portal/wp_wqs/` |
| OrbStack 配置 | `~/Library/Group Containers/HUAQ24HBR6.dev.orbstack/` |
| OrbStack 进程 | `lsof -i :8080` 显示 PID 13791 |
| MySQL 连接 | `mysql -u root -p'GM3750-jm' -h 127.0.0.1 -P 3306` |

---

## 六、需要研究解决的问题

1. OrbStack 的 Web 路由配置文件在哪里？如何修改 `localhost:8080` 的文档根目录？
2. PHP 内置服务器为什么无法在 8081 端口启动（无日志无报错）？
3. 如何让两个 WordPress 站点同时访问（一个通过 OrbStack 8080，一个通过其他端口或方式）？

---

## 七、相关命令备忘

```bash
# 检查 OrbStack 端口占用
lsof -i :8080

# 检查 8081 端口
lsof -i :8081

# 启动 PHP 服务器（当前失败）
cd "/Users/jianing/Ning's Git/wp_wqs/local-dev/wordpress"
php -S localhost:8081 -t .

# 查看 PHP 服务器日志
cat /tmp/php8081.log

# 检查 MySQL 连接
mysql -u root -p'GM3750-jm' -h 127.0.0.1 -P 3306 -e "SELECT VERSION();"

# 查看 OrbStack 配置目录
ls ~/Library/Group\ Containers/HUAQ24HBR6.dev.orbstack/
```