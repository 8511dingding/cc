# 舆情分析产品 Docker 运行方案

## 本地运行

推荐安装 OrbStack：

https://orbstack.dev/

安装并启动 OrbStack 后，在项目根目录运行：

```bash
./run-local.sh
```

访问：

```text
http://localhost:8501
```

默认账号：

```text
admin / admin123
```

## 常用命令

```bash
# 后台启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f sentiment-web

# 停止
docker compose down

# 重启
docker compose restart sentiment-web
```

## 数据持久化

本地 `docker-compose.yml` 会把 `./web_system` 挂载到容器内 `/app/web_system`。

因此这些文件会留在本机：

- `web_system/sentiment.db`
- `web_system/brand_rules.json`
- `web_system/exports/`
- `web_system/uploads/`

## 腾讯云轻量服务器部署

服务器推荐安装 Docker Engine 和 Docker Compose Plugin。上传整个项目后运行：

```bash
cd /opt/sentiment-web-product
docker compose up -d --build
```

验证：

```bash
docker compose ps
curl -I http://127.0.0.1:8501/
```

Nginx 反向代理到：

```text
http://127.0.0.1:8501/
```

## 后续 WordPress 迁移思路

ServBay 里的 WordPress 可以迁移到同一个 Docker 体系，但建议单独一个 `wordpress-compose.yml`：

- WordPress 容器
- MySQL/MariaDB 容器
- `wp-content` 挂载目录
- 数据库 dump 导入
- Nginx 按域名或路径反代

这样舆情产品和 WordPress 互不污染，但都可以由 Docker 管理。
