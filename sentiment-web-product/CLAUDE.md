# 舆情Web产品 (sentiment-web-product)

## 项目概述

用于研发和迭代在线舆情分析报告产品。

## gstack 工作流集成

本项目集成 gstack 技能集，使用以下工作流：

### 可用技能

| 技能 | 用途 |
|------|------|
| `/spec` | 需求规格化、创建任务issue |
| `/investigate` | 排查问题、调试代码 |
| `/qa` | 测试网站功能、UI验证 |
| `/design-review` | 审查前端设计和用户体验 |
| `/review` | 代码审查 |
| `/ship` | 提交变更、创建PR |
| `/cso` | 安全审计 |
| `/benchmark` | 性能基准测试 |
| `/canary` | 部署后监控验证 |

### 开发规范

1. 新功能开发前先 `/spec` 明确需求
2. 使用 `/qa` 测试 Streamlit 应用功能
3. UI 变更后用 `/design-review` 审查
4. 重要修改前 `/review` 代码审查
5. 部署后用 `/canary` 验证运行状态

## gstack 技能路径

技能目录: `/Users/jianing/Ning's Git/gstack/`

核心技能: `/Users/jianing/Ning's Git/gstack/SKILL.md`

## 运行

```bash
cd "/Users/jianing/Ning's Git/sentiment-web-product/web_system"
streamlit run app.py
```

## 默认账号

- admin / admin123

## 技术栈

- Streamlit + 自定义CSS（科技风格深色主题）
- SQLite + SQLAlchemy ORM
- Plotly 图表
- python-docx 报告生成

## 核心功能

- 多用户认证
- 数据导入与清洗
- 四层标签体系（认知/情绪/行动/品牌竞品）
- 自动/手动标注
- 报告模板与导出管理