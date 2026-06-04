# 舆情标注平台新版

新版平台采用前后端分离结构，旧 Streamlit 系统暂时保留在 `/sentiment/`，新版入口为 `/platform/`。

## 目录

- `backend/`：FastAPI API 服务，当前为种子数据和内存存储骨架。
- `frontend/`：React + Vite 前端工作台。
- 根目录 `docker-compose.yml`：本地 Docker/OrbStack 运行入口。
- 根目录 `nginx/local-portal.conf`：本地主机目录与子路径反向代理。

## 本地 Docker 运行

```bash
docker compose up -d --build sentiment-platform-api sentiment-platform-web local-portal
```

访问：

- 本地目录页：`http://localhost:8080/`
- 新版平台：`http://localhost:8080/platform/`
- 新版 API：`http://localhost:8080/api/platform/dashboard`

## 前端开发

```bash
cd platform/frontend
npm install
npm run dev
```

开发服务会把 `/api/platform` 代理到 `http://localhost:8000`。

## 后端开发

```bash
cd platform/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
```

本机不要依赖 ServBay Python；建议使用系统 Python、pyenv、uv、conda 或 Docker 容器。

## 部署预留

后续部署到宝塔或腾讯云轻量服务器时，建议保留同样的服务拆分：

- API：FastAPI + Uvicorn/Gunicorn
- Web：React 静态构建产物，由 Nginx 托管
- 网关：Nginx 统一处理 `/platform/` 和 `/api/platform/`
- 数据库：优先 PostgreSQL 或 MySQL；SQLite 只适合本地原型

正式部署前需要补齐认证、权限、持久化数据库、文件上传校验、报告导出队列和备份策略。
