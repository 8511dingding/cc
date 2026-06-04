# 舆情分析系统 v2.0

## 概述

基于 Streamlit 的在线舆情分析报告产品，支持多用户、数据清洗、自动标注、模板管理和报告导出。

## 功能模块

### 1️⃣ 用户与认证
- 多用户登录（admin/user/viewer 角色）
- 默认账号: `admin` / `admin123`
- 支持部署到云服务器（SQLite + Streamlit）

### 2️⃣ 项目管理
- 创建项目（含子集项目）
- 从原始数据通过筛选条件创建子集（如2万条筛选8000条）
- 项目状态管理（active/archived）

### 3️⃣ 数据导入
- 上传 Excel 文件（.xlsx/.xls）
- 自动执行所有清洗规则检测
- 实时显示统计（总数据量、有效数据、阶段分布）

### 4️⃣ 数据总览
- 顶部统计卡片（总量、有效、无效、已标注）
- 阶段分布（4月/5月）
- 清洗规则统计（各规则检出数量和占比）
- 标签分布图表（认知/情绪/行动/品牌竞品四层）
- 完整数据表格（分页、筛选、搜索、批量操作）

### 5️⃣ 数据清洗
6条清洗规则，可单独开关，勾选后**实时预览**效果：
| 规则 | 说明 |
|------|------|
| 纯@无互动 | @后无有效文字；多人@ |
| 纯表情/emoji | 只有emoji无文字 |
| 无意义语气词 | 啊啊啊、哈哈、嗯嗯、666等 |
| 空内容 | 内容为空或NaN |
| 乱码/异常字符 | 包含乱码或异常字符 |
| 重复内容 | 与之前内容完全相同 |

### 6️⃣ 内容管理
- 多维度筛选（阶段、有效性、内容类型、模糊搜索）
- 表格展示
- **创建数据子集**：从筛选结果创建子集+项目

### 7️⃣ 数据子集管理
- 通过条件筛选创建子集（阶段+有效性+类型+关键词+IP地区）
- **同时创建新项目**来管理子集
- 子集列表管理

### 8️⃣ 品牌与竞品管理
- **品牌管理**：添加/编辑品牌（名称、别名、类别、优先级）
- **竞品产品管理**：按品牌管理竞品（名称、系列、识别关键词）
- 品牌识别：a2、爱他美、飞鹤、金领冠、贝拉米、美赞臣等

### 9️⃣ 规则管理
- **标签规则**：认知/情绪/行动/品牌竞品四层关键词配置
- **清洗规则**：启用/禁用各清洗规则
- **优先级配置**：各标签的匹配优先级说明

### 🔟 标签管理
- 四层统计（认知/情绪/行动/品牌竞品）
- 分母可配置
- 两阶段并列对比
- **自动打标签**：
  - 可选择"标注为空的内容"或"全部内容（重新打标）"
  - 可选择层级和阶段

### 1️⃣1️⃣ 手动标注（增强版）
- 多条件筛选：阶段/标注状态/内容类型/有效性
- **模糊搜索**：输入关键词实时筛选
- **排序**：默认/时间升序/时间降序/ID升序/ID降序
- 分页浏览，每页20条
- 6列标签同时编辑（S1认知/S2认知/S1情绪/S2情绪/S1行动/S2行动）
- 已标注状态标识
- 保存后实时生效

### 1️⃣2️⃣ 数据统计
- 选择层级（认知/情绪/行动/品牌竞品）和阶段
- 统计表格（数量+占比）
- 可视化图表（柱状图/饼图）

### 1️⃣3️⃣ 报告生成
- **模板选择**：可选择不同报告模板
- **板块勾选自定义**：选择生成哪些板块
- **文件名模板配置**：{project}_{date}_{version}
- 实时预览报告内容
- 导出 Word/PDF

### 1️⃣4️⃣ 模板管理
- 查看模板列表
- 创建新模板（名称、版本、描述、板块配置）
- 编辑已有模板
- 设置默认模板

### 1️⃣5️⃣ 导出记录管理
- 查看所有导出历史
- 文件名、模板、类型、大小、时间
- 包含板块记录
- 文件名模板配置

### 1️⃣6️⃣ 系统设置
- 个人信息管理
- 系统信息
- 数据库管理

### 1️⃣7️⃣ 用户管理（管理员）
- 查看用户列表
- 添加新用户
- 设置角色和状态

## 技术栈

- **前端**：Streamlit
- **数据处理**：Pandas
- **可视化**：Plotly
- **报告生成**：python-docx
- **数据库**：SQLite (SQLAlchemy ORM)
- **运行环境**：Python 3.9+

## 推荐安装与运行（Docker / OrbStack）

本项目现在推荐用 Docker 容器运行，避免依赖 ServBay、Conda 或系统 Python。

Mac 本地推荐先安装 OrbStack：

```text
https://orbstack.dev/
```

安装并启动 OrbStack 后，在项目根目录运行：

```bash
cd "/Users/jianing/Ning's Git/sentiment-web-product"
./run-local.sh
```

访问：

```text
http://localhost:8501
```

详细说明见项目根目录 `DOCKER_SETUP.md`。

## 旧版安装与运行（不推荐）

```bash
cd /Users/jianing/Ning\'s\ Git/sentiment-web-product/web_system

pip install -r requirements.txt

streamlit run app.py
```

## 云服务器部署 (Nginx + 子路径)

### 架构
```
用户请求 → Nginx (80/443) → 反代到 Streamlit (8501)
访问地址: http://server-ip/sentiment
```

### 部署文件
| 文件 | 说明 |
|------|------|
| `deploy_tencent.sh` | 自动化部署脚本 |
| `streamlit-sentiment.service` | Systemd 服务配置 |
| `sentiment_nginx.conf` | Nginx 反向代理配置 |

### 部署步骤

**Step 1: 上传代码到服务器**
```bash
scp -r ./web_system/* user@your-server:/opt/sentiment-web/
```

**Step 2: 安装依赖**
```bash
cd /opt/sentiment-web
pip install -r requirements.txt
```

**Step 3: 配置 Systemd 服务**
```bash
sudo cp streamlit-sentiment.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable streamlit-sentiment
sudo systemctl start streamlit-sentiment
```

**Step 4: 配置 Nginx**
```bash
sudo cp sentiment_nginx.conf /etc/nginx/sites-available/sentiment
sudo ln -s /etc/nginx/sites-available/sentiment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**Step 5: 验证访问**
```
http://your-server-ip/sentiment
```

### 常用命令
```bash
# 查看服务状态
sudo systemctl status streamlit-sentiment

# 查看日志
sudo journalctl -u streamlit-sentiment -f

# 重启服务
sudo systemctl restart streamlit-sentiment

# 查看Nginx日志
tail -f /var/log/nginx/sentiment-access.log
```

### 默认账号
- 用户名: `admin`
- 密码: `admin123`

### 故障排查
1. **服务无法启动**: 检查 `/opt/sentiment-web` 路径是否正确
2. **502 错误**: 确认 Streamlit 服务在 8501 端口运行
3. **静态资源加载失败**: 确认 `--server.proxyMode=true` 参数已添加

## 目录结构

```
web_system/
├── app.py              # 主应用
├── models.py           # 数据模型
├── requirements.txt    # 依赖包
├── sentiment.db        # 数据库文件（自动创建）
├── exports/            # 导出文件目录（自动创建）
└── README.md           # 本文件
```

## 数据库结构

- `users` - 用户表
- `projects` - 项目表
- `raw_data` - 原始数据表
- `data_subsets` - 数据子集表
- `brands` - 品牌表
- `competitor_products` - 竞品表
- `label_rules` - 标签规则表
- `clean_rules` - 清洗规则表
- `report_templates` - 报告模板表
- `export_records` - 导出记录表

## 默认数据

- 默认管理员账号: `admin` / `admin123`
- 默认清洗规则: 6条
- 默认品牌: a2、爱他美、飞鹤、金领冠、贝拉米、美赞臣、惠氏、皇家美素力
- 默认报告模板: 舆情分析报告模板 v1.0
