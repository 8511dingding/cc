# TikTok Product Intelligence

数据驱动的TikTok泰国选品决策和品类监控工具。

## 功能

- 选品评估：多维度综合评估产品可行性
- 竞品分析：分析竞争格局和差异化机会
- 关键词挖掘：从数据中发现高潜力关键词
- 品类监控：跟踪品类趋势变化

## 安装

```bash
pip install pandas plotly streamlit playwright
playwright install chromium
```

## 项目结构

```
tiktok-product-intel/
├── CLAUDE.md              # 项目指南
├── skills/               # 技能定义
├── scripts/
│   ├── lib/             # 核心库
│   │   └── product_intel.py
│   └── analyze.py        # 分析脚本
├── data/                 # 数据目录
│   └── fastmoss/        # FastMoss数据
└── reports/              # 输出报告
```