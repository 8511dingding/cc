# 舆情Web产品 (sentiment-web-product)

## 项目定位

本项目是在线舆情分析与标注平台，目标是形成“数据导入 -> 清洗报告 -> 自动打标签 -> 人工校正 -> 规则学习 -> 在线报告确认 -> Word/PDF/PPT/Excel 导出”的长期产品闭环。

## 当前主架构

新版平台采用前后端分离结构，旧 Streamlit 系统暂时保留但不再作为主开发方向。

- 新版入口：`http://localhost:8080/platform/`
- 本地目录页：`http://localhost:8080/`
- 新版 API：`http://localhost:8080/api/platform/dashboard`
- 旧 Streamlit 入口：`http://localhost:8501/` 或经 Nginx 代理的 `/sentiment/`

核心服务由 Docker Compose 管理：

- `local-portal`：Nginx 本地总入口，监听 `8080`。
- `sentiment-platform-web`：React + Vite 前端。
- `sentiment-platform-api`：FastAPI 后端。
- `sentiment-web`：旧 Streamlit 系统，暂时保留。
- `wqs-mysql`：WordPress 迁移/本地站点使用的 MySQL。

## 环境决策记忆

长期主方案：`OrbStack + Docker Compose`。

选择原因：

- 本地环境和腾讯云/宝塔服务器更接近，方便长期部署和同步。
- 避免 Homebrew/系统 Python/本机 Node 版本漂移影响产品运行。
- 未来可以通过 GitHub 同步到服务器后用 Docker Compose 刷新服务。

本地工具边界：

- Homebrew 只作为辅助工具来源，例如 Git、CLI、Node 临时命令。
- ServBay 不再作为本项目默认运行环境。
- ServBay 文件和目录保留，便于其他旧项目临时使用，但不得默认注入 PATH。
- 已从 `~/.zshrc` 和 `~/.bash_profile` 移除 ServBay 默认 PATH 注入，并保留备份：
  - `/Users/jianing/.zshrc.before-servbay-cleanup`
  - `/Users/jianing/.bash_profile.before-servbay-cleanup`

## 本地运行与刷新容器

生产式本地运行：

```bash
make platform-up
```

高频前端开发，使用热更新模式：

```bash
make platform-dev
```

环境体检：

```bash
tools/platform-doctor.sh
```

查看容器状态：

```bash
docker compose ps
```

查看关键服务日志：

```bash
docker compose logs -f sentiment-platform-api sentiment-platform-web local-portal
```

强制重建并刷新新版平台容器：

```bash
docker compose up -d --build --force-recreate sentiment-platform-api sentiment-platform-web local-portal
```

重要约定：每次完成代码部署、容器刷新或本地服务更新后，助手都必须提醒用户以上常用刷新/验证命令，并说明访问地址 `http://localhost:8080/platform/`。

## 开发模式结构

新增开发 Compose：

- `docker-compose.dev.yml`
- `nginx/local-portal.dev.conf`

开发模式会让 `/platform/` 代理到容器内 Vite dev server，减少每次 UI 修改都重建生产镜像的等待。

生产模式仍然使用 `platform/frontend/Dockerfile` 构建静态产物，再由 Nginx 托管。

## 部署方向

未来腾讯云轻量服务器/宝塔部署建议保持同构：

- API：FastAPI + Uvicorn/Gunicorn。
- Web：React 静态构建产物，由 Nginx 托管。
- 网关：Nginx 统一处理 `/platform/` 和 `/api/platform/`。
- 数据库：正式环境优先 PostgreSQL 或 MySQL；当前内存/种子数据只适合原型阶段。
- WordPress：应单独 Docker 化，建议独立 `wordpress-compose.yml`，避免和舆情平台互相污染。

## 当前产品重点

- 数据导入不做文件评分。
- 上传后生成直观的数据整理/清洗报告。
- 有效数据口径：内容/评论内容列非空、非空格、非乱码。
- 用户确认有效数据后进入自动打标签。
- 自动标签结果允许人工校正；人工确认数据后续不可被自动规则覆盖。
- 系统后续要根据人工修改沉淀规则学习建议。
- 词云编辑器是独立页面 `wordcloud`，入口在人工标注页；模板按客户名跨项目保存，当前前端原型使用浏览器本地存储，后续正式版应迁入后端模板表。

## 默认账号

- admin / admin123

## 历史说明

旧版 `web_system/` 是 Streamlit + SQLite + SQLAlchemy + Plotly + python-docx 实现，仍保留作迁移参考；新版平台开发应优先在 `platform/` 下进行。
