# CompanyDoc - 企业文档管理系统

## 项目简介
CompanyDoc 是一个企业级文档管理和处理系统，专注于公司日常文书的创建、编辑、翻译、审批和归档管理。

## 核心功能

### 1. 文档管理
- 创建、编辑、删除文档
- 按分类组织（合同、通知、报告等）
- 草稿/审批状态管理
- 版本历史记录

### 2. 多语言支持
- 中英文泰三语存储
- 自动翻译（集成 DeepL/Google API）
- 术语库统一管理

### 3. 模板系统
- 预置合同、通知、报告等模板
- 支持自定义模板
- 模板变量替换

### 4. 审批流程
- 多级审批链
- 审批意见记录
- 状态流转追踪

### 5. 文档归档
- 全文搜索
- 按部门/项目分类
- 权限管理

## 快速开始

### 后端启动
```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

访问：http://localhost:8000/docs 查看 API 文档

### 前端启动（可选）
```bash
cd frontend
npm install
npm run dev
```

## 项目结构
```
CompanyDoc/
├── backend/              # Python FastAPI 后端
│   ├── app/
│   │   └── main.py       # 主入口
│   └── requirements.txt
├── frontend/             # React 前端（可选）
├── shared/
│   └── templates/        # 文档模板
└── README.md
```

## 使用示例

### 方式一：通过 Claude Code 对话
直接在对话中描述需求，例如：
- "帮我创建一份经销商授权书，中英泰三语"
- "翻译这份文档的第2段"
- "将文档状态改为审批中"

### 方式二：直接调用 API
```bash
# 创建文档
curl -X POST http://localhost:8000/api/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "测试文档", "content": "文档内容...", "category": "合同"}'

# 获取文档列表
curl http://localhost:8000/api/documents
```
