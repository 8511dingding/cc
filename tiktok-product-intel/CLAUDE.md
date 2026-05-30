# TikTok Product Intelligence - 选品与品类监控

## 项目目标

帮助泰国TikTok卖家进行**数据驱动的选品决策**和**品类销量监控**。

## 核心功能

1. **竞品分析** - 输入品牌/产品名，分析同类产品销量竞争格局
2. **关键词挖掘** - 从FastMoss数据中发现高潜力关键词
3. **选品推荐** - 结合销量、价格、竞争度给出选品建议
4. **趋势监控** - 定期导入数据，跟踪品类趋势变化

## 选品评估维度

| 维度 | 说明 |
|------|------|
| 售价 | 最终零售价（THB） |
| 面向消费者 | 目标用户群体 |
| 产地 | 货源地（中国→泰国） |
| 海运成本 | 单件海运费 |
| 保质期 | 对库存周转的要求 |
| 利润率 | 综合成本核算后的利润率 |
| 竞争度 | 关键词下产品数量和销量分布 |

## 数据来源

- **FastMoss导出** - 关键词相关产品销量表
- **内部销售数据** - tiktok-analytics项目中的订单和成本数据

## 技术栈

- Python 3.x (pandas, plotly, streamlit)
- SQLite (数据持久化)
- Playwright (浏览器自动化扩大搜索面)

## 快速开始

```bash
cd tiktok-product-intel
pip install pandas plotly streamlit playwright
playwright install chromium
```

## 项目结构

```
tiktok-product-intel/
├── CLAUDE.md              # 本文件
├── data/                  # 数据目录
│   └── fastmoss/          # FastMoss导出的原始数据
├── scripts/
│   ├── lib/               # 工具函数
│   ├── analyze.py         # 分析脚本
│   └── scrape.py          # 浏览器采集脚本
├── skills/
│   └── tiktok-product-intel/
│       └── SKILL.md       # 技能定义
├── notebooks/             # Jupyter notebooks
└── reports/               # 生成的分析报告
```