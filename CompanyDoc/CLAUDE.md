# CompanyDoc - Claude Code 配置

## 项目概述
CompanyDoc 是企业文档管理系统，用于处理公司日常文书，支持中英泰三语。

## 核心功能
1. 文档管理 - 创建、编辑、删除、分类管理
2. 多语言 - 中英泰三语存储和翻译
3. 模板系统 - 合同、通知、会议纪要等模板
4. 术语库 - 专业术语统一管理
5. 审批流程 - 多级审批链

## 技术栈
- 后端: Python FastAPI + SQLite
- 前端: React + TypeScript + Vite (可选)

## 常用命令

### 启动后端
```bash
cd "/Users/jianing/Ning's Git/CompanyDoc/backend"
pip install -r requirements.txt
python app/main.py
```

### API 测试
启动后访问: http://localhost:8000/docs

### 快速操作

查看统计:
```bash
curl http://localhost:8000/api/stats
```

创建文档:
```bash
curl -X POST http://localhost:8000/api/documents \
  -H "Content-Type: application/json" \
  -d '{"title": "文档标题", "content": "文档内容", "category": "合同"}'
```

## 数据库结构
- documents: 文档表
- templates: 模板表
- terms: 术语库
- approvals: 审批记录

## 术语分类
- 合同、通知、报告、会议、通用

## 文档状态
- draft: 草稿
- approved: 已审批
- rejected: 已驳回

## 常用术语（中英泰）
- 经销商授权书 / Dealer Authorization / จดหมายอนุญาตตัวแทนจำหน่าย
- 有效期 / Valid Period / ช่วงเวลาที่มีผล法律效力
- 甲方 / Party A / ฝ่ายที่หนึ่ง
- 乙方 / Party B / ฝ่ายที่สอง
