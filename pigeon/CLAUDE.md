# 贝亲（Pigeon）抖音舆情分析系统

## 项目概述

针对母婴头部品牌"贝亲（Pigeon）"的抖音平台定期舆情分析系统，通过抓取、分类和分析抖音评论区数据，帮助营销团队提炼消费者关注点、痛点及卖点心智。

## 数据源（Data Sourcing）

1. **品牌自有阵地**：贝亲官方旗舰店及矩阵号视频评论、自播间实时弹幕
2. **竞品对比阵地**：世喜、可优比、布朗博士等竞品热门视频评论
3. **KOL/KOC 扩散阵地**：母婴达人、评测博主、种草视频下的评论
4. **公域搜索阵地**：抖音搜索关键词下的沉淀评论

## 分析维度与标签体系

### 关注点标签（Buying Drivers）
- `Material_Safety`：材质与安全性（PPSU、玻璃、硅胶、双酚A、耐高温、异味）
- `Functionality`：功能适配（防胀气、奶嘴流速、防漏水、呛奶、吐奶）
- `Convenience`：使用便利性（宽口径、清洗难易、刻度清晰度、便携度）
- `Price_Channel`：价格与渠道（大促优惠、正品鉴别、渠道真伪）

### 吐槽点标签（Pain Points）
- `Product_Defect`：产品缺陷（奶嘴塌陷、吸管难吸、漏奶、刻度磨损）
- `Intolerance`：个体不耐受（宝宝不吃/抗拒、胀气未缓解）
- `Service_Logistics`：服务与物流（客服态度、物流破损、赠品漏发）
- `Price_Dissatisfaction`：价格溢价（贵、控价混乱、直播间价差）

### 卖点心智标签（Brand Value）
- `Official_USP`：官方卖点渗透（"自然实感"、"母乳实感"、"触感真实"）
- `Emotional_Trust`：情绪与信任资产（"老牌子放心"、"无限回购"、"大宝二宝都用"）

## 数据处理流程

1. **关键词矩阵与规则匹配**：母婴行业词库检索，自动打标
2. **情感倾向分析**：Positive / Neutral / Negative + 负面飙升预警
3. **高频词云与热点聚类**：按月/周时间维度生成高频词统计，主题聚类

## 目录结构

```
pigeon/
├── analysis_logic/     # 分析规则和知识库
│   ├── vocabulary.md    # 母婴行业专业词汇表
│   ├── brands_products.md  # 品牌及竞品信息
│   ├── analysis_rules.md   # 分析规则和注意事项
│   └── context.md       # 客户背景和品牌信息
├── data/
│   ├── raw/            # 原始数据
│   ├── cleaned/        # 清洗后的数据
│   └── processed/      # 处理后的分析素材
├── reports/
│   ├── final/          # 最终报告
│   └── interim/        # 中间分析结果
├── scripts/
│   ├── clean_data.py   # 数据清洗脚本
│   ├── analyze.py      # 分析脚本
│   └── report.py       # 报告生成脚本
└── skills/             # 技能定义
```

## 运行方式

```bash
python scripts/clean_data.py    # 数据清洗
python scripts/analyze.py       # 舆情分析
python scripts/report.py        # 生成报告
```