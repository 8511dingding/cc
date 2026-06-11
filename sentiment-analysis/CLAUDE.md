# 舆情分析项目 (Sentiment Analysis Project)

## 项目概述

用于对抖音、小红书等平台的内容和评论进行舆情分析，通过语义分析推测消费者和粉丝对品牌/产品的口碑和反馈，为营销决策提供支持。

## gstack 工作流集成

本项目集成 gstack 技能集，使用以下工作流：

### 可用技能

| 技能 | 用途 |
|------|------|
| `/spec` | 需求规格化、创建任务issue |
| `/investigate` | 排查问题、调试代码 |
| `/qa` | 测试脚本功能、验证分析结果 |
| `/review` | 代码审查 |
| `/ship` | 提交变更、创建PR |
| `/benchmark` | 性能基准测试（处理大数据时） |
| `/document-generate` | 生成文档和报告 |

### 开发规范

1. 数据分析脚本修改前先 `/spec` 明确需求
2. 使用 `/qa` 验证数据清洗和分析逻辑
3. 报告模板变更后用 `/qa` 测试生成流程
4. 使用 `/investigate` 排查数据处理问题

## gstack 技能路径

技能目录: `/Users/jianing/Ning's Git/gstack/`

核心技能: `/Users/jianing/Ning's Git/gstack/SKILL.md`

## 工作流程

### 第一步：数据清洗
- 读取原始数据（抖音/小红书评论、内容数据）
- 过滤完全无效的内容（如乱码、无意义字符等）
- 整理可分析内容到新的Excel文档第一个sheet

### 第二步：定性定量分析
根据提供的分析逻辑和背景知识进行：
- 情感倾向分析（正面/负面/中性）
- 话题聚类分析
- 品牌/产品提及分析
- 竞品对比分析
- 专业术语识别和正误判断

### 第三步：报告生成
- 按历史格式或新要求生成Word/Excel报告
- 包含统计结果和分析结论

## 分析内容来源

`analysis_logic/` 目录存放：
- `vocabulary.md` - 专业词汇表（持续更新）
- `brands_products.md` - 品牌旗下产品及竞品信息
- `analysis_rules.md` - 分析规则和注意事项
- `context.md` - 客户背景和品牌信息

## 数据目录结构

```
data/
├── raw/           # 原始数据（用户提供）
├── cleaned/       # 清洗后的数据
└── processed/     # 处理后的分析素材

reports/
├── final/         # 最终报告
└── interim/       # 中间分析结果

scripts/
├── clean_data.py  # 数据清洗脚本
├── analyze.py     # 分析脚本
└── report.py      # 报告生成脚本
```

## 关键词汇（核心识别对象）

具体词汇在 `analysis_logic/vocabulary.md` 中定义，定期更新。