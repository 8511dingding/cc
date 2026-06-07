# ScrapLing - 社交媒体爬虫项目
# 支持抖音、小红书内容抓取

## 项目结构
```
scrapling/
├── backend/           # 后端爬虫模块
│   ├── crawlers/      # 爬虫实现
│   │   ├── douyin.py       # 抖音爬虫
│   │   └── xiaohongshu.py  # 小红书爬虫
│   ├── utils/         # 工具函数
│   │   ├── db.py           # 数据库操作
│   │   └── deduplication.py # 去重工具
│   ├── main.py        # 主入口
│   └── requirements.txt
├── frontend/          # 前端界面
│   ├── src/           # React组件
│   └── package.json
├── data/              # 数据库和导出文件
└── README.md
```

## 功能特性
- ✅ 支持抖音、小红书双平台
- ✅ 关键词搜索
- ✅ 预抓取（统计数量）
- ✅ 分批抓取（先100条验证）
- ✅ 智能去重（基于内容指纹）
- ✅ 多格式导出（CSV/JSON/Excel）
- ✅ 可视化前端界面

## 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt
playwright install

# 前端依赖
cd frontend
npm install
```

## 使用方式

### 命令行方式
```bash
cd backend

# 预抓取（统计数量）
python main.py --keyword "美妆产品" --platform all --preview

# 抓取100条数据
python main.py --keyword "美妆产品" --platform douyin --limit 100

# 导出数据
python main.py --export --export-format csv --output result
```

### 前端界面方式
```bash
# 启动后端服务（待实现）
cd backend
python api.py

# 启动前端
cd frontend
npm run dev
```

## 数据字段

### 内容数据
| 字段 | 说明 |
|------|------|
| platform | 平台（douyin/xiaohongshu） |
| type | 类型（video/note） |
| title | 标题 |
| description | 描述 |
| url | 内容链接 |
| cover_url | 封面图 |
| author_name | 作者名称 |
| author_url | 作者主页 |
| author_avatar | 作者头像 |
| publish_time | 发布时间 |
| like_count | 点赞数 |
| comment_count | 评论数 |
| share_count | 分享数 |
| play_count | 播放量（抖音） |

### 评论数据
| 字段 | 说明 |
|------|------|
| user_name | 评论者名称 |
| avatar_url | 评论者头像 |
| content | 评论内容 |
| comment_time | 评论时间 |
| like_count | 点赞数 |

## 注意事项
1. 请合理控制抓取频率，避免对目标网站造成压力
2. 使用前请确保遵守目标平台的使用条款
3. 建议使用代理IP避免被封禁
4. 数据库使用SQLite，数据存储在data目录下
