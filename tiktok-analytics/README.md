# TikTok Shop 数据分析项目

## 项目概述

专注于 TikTok 店铺的电商数据分析，包括：
- 订单利润分析
- 产品利润分析
- GMV 投放分析
- 店铺运营指标监控

## 技术栈

- **Python 3.11+** - 数据处理和分析
- **pandas** - 数据处理
- **matplotlib/seaborn** - 数据可视化
- **Jupyter Notebook** - 交互式分析

## 目录结构

```
tiktok-analytics/
├── data/           # 原始数据和处理后数据
├── notebooks/      # Jupyter 分析笔记本
├── scripts/        # Python 分析脚本
├── reports/        # 生成的报告和图表
├── CLAUDE.md      # 项目文档
└── README.md      # 项目说明
```

## 数据来源

支持以下数据格式：
- TikTok Seller Center 导出的 CSV/Excel
- 第三方 ERP 数据
- 自定义 JSON/CSV 格式

## 分析模块

1. **订单分析** - 订单量、退款率、客单价、发货时效
2. **利润分析** - 产品成本、佣金、物流费、广告费计算利润
3. **GMV 分析** - 销售额目标追踪、投放 ROI 分析
4. **产品分析** - 爆款分析、滞销分析、品类分析

## 运行方式

```bash
# 数据分析
python scripts/analyze.py

# 生成报告
python scripts/generate_report.py
```