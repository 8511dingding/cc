# A2舆情分析v11规则引擎

## 项目概述

A2奶粉舆情分析系统，基于规则引擎的自动化分类标注工具。

## 技术架构

### 核心文件

```
scripts/
├── lib/
│   ├── rules_engine.py       # 规则引擎核心（从YAML加载规则）
│   ├── llm_evaluator.py      # LLM辅助分类（置信度低时触发）
│   └── emoji_engine.py       # Emoji增强引擎
├── rules/
│   ├── a2_sentiment_rules.yaml  # 情绪/认知/行动层规则
│   ├── a2_brand_rules.yaml      # 40品牌识别规则
│   └── a2_emoji_rules.yaml      # Emoji元数据库
└── tag_comments_v11.py          # v11主脚本（直接使用）
```

### 规则引擎 (rules_engine.py)

从YAML配置文件加载所有分类规则，无需修改代码即可更新规则。

**加载配置**：
- `a2_sentiment_rules.yaml` - 情绪层5分类、认知层4分类、行动层4分类
- `a2_brand_rules.yaml` - 40个品牌识别（含错别字容错）

**核心方法**：
- `classify(text)` → 三维分类 (认知, 情绪, 行动)
- `extract_brands(text)` → 品牌提及
- `is_pure_at_no_interaction(text)` → 纯@无互动判断

### LLM辅助 (llm_evaluator.py)

置信度低的评论自动触发LLM二次判断。

**环境变量配置**：
```bash
# Anthropic
export ANTHROPIC_API_KEY=your_key

# 或 硅基流动
export SILICONFLOW_API_KEY=your_key
export LLM_PROVIDER=siliconflow
export LLM_BASE_URL=https://api.siliconflow.cn/v1
export LLM_MODEL=your-model
```

**功能**：
- 规则引擎置信度 < 0.6 时触发LLM
- 支持情绪/认知/行动三层单独评估
- 可配置化提示词

### Emoji增强 (emoji_engine.py)

从 `a2_emoji_rules.yaml` 加载100+emoji标准化分类。

**功能**：
- Emoji情绪分类（恐慌焦虑/愤怒背叛/庆幸旁观/正面/中性）
- Emoji组合增强（多个哭泣emoji → 恐慌焦虑增强）
- Emoji+关键词组合判断

## 使用方式

```bash
cd /Users/jianing/Ning's\ Git/sentiment-analysis

# 运行v11分类
python scripts/tag_comments_v11.py <输入文件> <输出文件>
```

**输入文件格式**：
- 列名兼容中英文：`评论内容`/`content`, `评论时间`/`create_time`

**输出**：
- 认知层/情绪层/行动层标签
- 品牌提及
- 评论类型

## 分类标准（v9标准）

### 情绪层5分类
1. **正面**：对a2品牌持信任态度
2. **中性**：普通讨论，无明显情绪
3. **恐慌焦虑**：担忧宝宝健康，害怕中招
4. **庆幸旁观**：庆幸自己没买/已换奶粉
5. **愤怒背叛**：感觉信任被辜负

### 认知层4分类
1. **无明确认知**：默认
2. **信息混淆**：分不清版本区别
3. **精准认知**：理解召回范围和批次
4. **泛化抵触**：认为所有奶粉都有问题

### 行动层4分类
1. **暂无行动**：默认
2. **寻求帮助**：询问怎么办/哪个安全
3. **转奶流失**：明确表示要换奶粉
4. **维权诉求**：提到12315/赔偿

### 数据基数
- 第一阶段（4月）：586条（剔除纯@无互动）
- 第二阶段（5月）：4093条（剔除纯@无互动）

## 品牌识别规则（v1.1）

覆盖40个品牌，含错别字容错：

| 品牌 | 错别字容错 |
|------|-----------|
| 美赞臣 | 美赞成 |
| 雀巢 | 雀勺、雀窠 |
| 君乐宝 | 君乐保 |
| 爱他美 | 爱他媒 |
| 飞鹤 | 飞榃 |

## 更新日志

- **2026-05-29**: v11发布，规则外部化到YAML，支持LLM辅助和Emoji增强
- **2026-05-26**: v9标准，5分类，情绪层取消"负面"大类

## 相关文档

- `MEMORY/a2-classification-standards-v9.md` - v9分类标准详细规则
- `MEMORY/a2-correction-rules.md` - 客户纠正规则（97+68条）
- `MEMORY/brand-recognition-rules.md` - 品牌识别规则详解