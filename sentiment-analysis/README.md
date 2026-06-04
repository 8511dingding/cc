# A2舆情分析项目

用于对抖音、小红书等平台内容和评论进行清洗、分类标记和报告生成。当前主流程以 `scripts/monthly_pipeline.py` 为入口，支持每月重复分析。

## 环境准备

```bash
pip install -r requirements.txt
```

如需启用 LLM 辅助分类：

```bash
pip install -r requirements-llm.txt
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=你的密钥
```

默认不启用 LLM，以保证每月分析口径稳定。

## 每月运行

从原始内容文件和评论文件开始：

```bash
python scripts/monthly_pipeline.py \
  --month 2026-06 \
  --compare-month 2026-05 \
  --content-file data/raw/内容文件.xlsx \
  --comment-file data/raw/评论文件.xlsx
```

如果已经有清洗后的 Excel：

```bash
python scripts/monthly_pipeline.py \
  --month 2026-06 \
  --compare-month 2026-05 \
  --cleaned-file data/processed/2026-06_a2舆情_清洗后.xlsx
```

默认输出：

- 清洗数据：`data/processed/<month>_a2舆情_清洗后.xlsx`
- 标记数据：`reports/final/<month>_a2舆情_数据.xlsx`
- Word报告：`reports/final/<month>_a2舆情_报告.docx`

## 分母口径

`report_v11.py` 默认从标记后的数据中计算分母：

- 第一阶段：`--compare-month` 对应月份的数据行数
- 第二阶段：`--month` 对应月份的数据行数

只有当业务明确要求使用外部分母时，才传入：

```bash
python scripts/monthly_pipeline.py \
  --month 2026-06 \
  --compare-month 2026-05 \
  --cleaned-file data/processed/2026-06_a2舆情_清洗后.xlsx \
  --phase1-total 1234 \
  --phase2-total 5678
```

## 单独运行步骤

只做分类标记：

```bash
python scripts/tag_comments_v11.py \
  data/processed/2026-06_a2舆情_清洗后.xlsx \
  reports/final/2026-06_a2舆情_数据.xlsx \
  --month 2026-06 \
  --compare-month 2026-05
```

只生成 Word 报告：

```bash
python scripts/report_v11.py \
  reports/final/2026-06_a2舆情_数据.xlsx \
  reports/final/2026-06_a2舆情_报告.docx \
  --month 2026-06 \
  --compare-month 2026-05
```

## 规则维护

核心分类规则在 `scripts/rules/`：

- `a2_sentiment_rules.yaml`：认知层、情绪层、行动层、评论类型规则
- `a2_brand_rules.yaml`：品牌和产品识别规则
- `a2_emoji_rules.yaml`：Emoji增强规则

每次修改规则后，建议用一小批人工标注样本复核分类结果，再进入月度正式报告。
