# 舆情Web产品 (sentiment-web-product)

## 项目概述

用于研发和迭代在线舆情分析报告产品。

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