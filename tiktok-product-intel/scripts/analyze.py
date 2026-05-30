#!/usr/bin/env python3
"""
FastMoss数据分析脚本
生成选品和品类监控分析报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加lib目录到路径
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from fastmoss_parser import FastMossParser
from product_intel import ProductIntelligence, ProductIntelDB, MarketData


def df_to_markdown(df):
    """将DataFrame转换为markdown表格字符串"""
    if df.empty:
        return "（无数据）"

    # 获取列名
    headers = list(df.columns)
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"

    lines = [header_line, separator]

    for _, row in df.iterrows():
        values = [str(v)[:30] for v in row.values]  # 截断过长内容
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def main():
    data_dir = Path(__file__).parent.parent / "data" / "fastmoss"

    print("=" * 70)
    print("FastMoss 数据分析报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)

    # 1. 加载和解析数据
    parser = FastMossParser(str(data_dir))
    df = parser.load_all_files()

    if df.empty:
        print("No data loaded. Exiting.")
        return

    # 2. 数据库操作
    db = ProductIntelDB()

    # 3. 存储市场数据
    print("\n存储市场数据到数据库...")
    for _, row in df.iterrows():
        market_data = MarketData(
            platform="tiktok_th",
            product_name=str(row['商品名称']),
            price=row['售价_数值'],
            currency="THB",
            sales_volume=int(row['总销量_数值']),
            store_name=str(row['店铺名称']),
            url=str(row.get('TikTok商品落地页地址', '')),
            scraped_at=datetime.now().isoformat()
        )
        db.save_market_data(market_data)

    print(f"已存储 {len(df)} 条市场数据")

    # 4. 生成分析报告
    print("\n" + "=" * 70)
    print("品类分析")
    print("=" * 70)

    keyword_summary = parser.analyze_by_keyword(df)
    print("\n【按关键词汇总】")
    print(keyword_summary.to_string())

    print("\n【TOP 20 店铺】")
    store_summary = parser.analyze_by_store(df, top_n=20)
    print(store_summary.to_string())

    print("\n【价格区间分析】")
    price_dist = parser.analyze_price_distribution(df)
    for price_range, data in price_dist.items():
        pct = data['总销量_数值'] / df['总销量_数值'].sum() * 100
        print(f"  {price_range:>10} THB: {data['商品名称']:>3}个商品, "
              f"总销量{data['总销量_数值']:>6}, 占比{pct:>5.1f}%")

    # 5. 竞品分析 - 找出高销量产品
    print("\n" + "=" * 70)
    print("爆款产品分析（总销量TOP 10）")
    print("=" * 70)

    top_products = df.nlargest(10, '总销量_数值')[
        ['商品名称', '店铺名称', '售价_数值', '总销量_数值', '7天销量_数值', '带货达人总数_数值']
    ]

    for i, (_, row) in enumerate(top_products.iterrows(), 1):
        print(f"\n{i}. {row['商品名称'][:50]}")
        print(f"   店铺: {row['店铺名称']}")
        print(f"   售价: {row['售价_数值']:.0f} THB | 总销量: {row['总销量_数值']:,} | "
              f"7天: {row['7天销量_数值']} | 达人: {row['带货达人总数_数值']}")

    # 6. 计算品类吸引力评分
    print("\n" + "=" * 70)
    print("品类吸引力评分")
    print("=" * 70)

    intel = ProductIntelligence()

    category_scores = []

    for keyword in df['来源关键词'].unique():
        kw_data = df[df['来源关键词'] == keyword]
        total_sales = kw_data['总销量_数值'].sum()
        week_sales = kw_data['7天销量_数值'].sum()
        avg_price = kw_data['售价_数值'].mean()
        store_count = kw_data['店铺名称'].nunique()
        product_count = len(kw_data)

        # 竞争度评估
        if store_count / product_count < 0.3:
            competition = "低"
        elif store_count / product_count < 0.6:
            competition = "中"
        else:
            competition = "高"

        # 综合评分
        sales_score = min(week_sales / 1000 * 100, 100)  # 1000件/周满分
        competition_score = {"低": 100, "中": 60, "高": 30}.get(competition, 50)
        market_size_score = min(total_sales / 50000 * 100, 100)  # 5万件总分满分
        avg_score = (sales_score * 0.4 + competition_score * 0.3 + market_size_score * 0.3)

        category_scores.append({
            "keyword": keyword,
            "total_sales": total_sales,
            "week_sales": week_sales,
            "product_count": product_count,
            "store_count": store_count,
            "avg_price": avg_price,
            "competition": competition,
            "score": avg_score
        })

        print(f"\n【{keyword}】")
        print(f"  市场总销量: {total_sales:,} 件")
        print(f"  7天销量: {week_sales} 件 (热度)")
        print(f"  商品数: {product_count}, 店铺数: {store_count}")
        print(f"  均价: {avg_price:.0f} THB")
        print(f"  竞争度: {competition}")
        print(f"  综合评分: {avg_score:.0f}/100")

    # 7. 生成Markdown报告
    report = generate_markdown_report(df, keyword_summary, store_summary, price_dist, category_scores)
    report_path = Path(__file__).parent.parent / "reports" / f"fastmoss_analysis_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    print(f"\n报告已保存到: {report_path}")


def generate_markdown_report(df, keyword_summary, store_summary, price_dist, category_scores) -> str:
    """生成Markdown格式分析报告"""

    total_sales = df['总销量_数值'].sum()

    report = f"""# FastMoss 数据分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**数据来源**: FastMoss 泰国TikTok Shop

---

## 1. 数据概览

| 指标 | 数值 |
|------|------|
| 总商品数 | {len(df)} |
| 在售商品数 | {len(df[df['商品状态'] == '在售'])} |
| 总销量 | {df['总销量_数值'].sum():,} |
| 7天销量 | {df['7天销量_数值'].sum():,} |
| 涉及店铺数 | {df['店铺名称'].nunique()} |
| 涉及关键词 | {', '.join(df['来源关键词'].unique())} |

---

## 2. 关键词分析

{df_to_markdown(keyword_summary)}

---

## 3. 价格区间分布

| 价格区间(THB) | 商品数 | 总销量 | 占比 |
|---------------|--------|--------|------|
"""

    for price_range, data in price_dist.items():
        pct = data['总销量_数值'] / total_sales * 100
        report += f"| {price_range} | {data['商品名称']} | {data['总销量_数值']:,} | {pct:.1f}% |\n"

    report += f"""

---

## 4. TOP 20 店铺

{df_to_markdown(store_summary)}

---

## 5. 爆款产品 (TOP 10 总销量)

| 排名 | 商品名称 | 店铺 | 售价 | 总销量 | 7天销量 | 达人带量 |
|------|----------|------|------|--------|---------|----------|
"""

    top_products = df.nlargest(10, '总销量_数值')
    for i, (_, row) in enumerate(top_products.iterrows(), 1):
        report += f"| {i} | {str(row['商品名称'])[:40]} | {row['店铺名称']} | {row['售价_数值']:.0f} | {row['总销量_数值']:,} | {row['7天销量_数值']} | {row['带货达人总数_数值']} |\n"

    report += """

---

## 6. 品类吸引力评分

| 品类 | 总销量 | 7天销量 | 商品数 | 店铺数 | 均价 | 竞争度 | 评分 |
|------|--------|--------|--------|--------|------|--------|------|
"""

    for cat in sorted(category_scores, key=lambda x: x['score'], reverse=True):
        report += f"| {cat['keyword']} | {cat['total_sales']:,} | {cat['week_sales']} | {cat['product_count']} | {cat['store_count']} | {cat['avg_price']:.0f} | {cat['competition']} | {cat['score']:.0f} |\n"

    report += """

---

## 7. 选品建议

### 地瓜干 (Dried Sweet Potato)
- **市场规模**: 最大 (94,988件总销量)
- **竞争度**: 高 (108个店铺)
- **建议**: 红海市场，适合有差异化资源的卖家

### 鹰嘴豆 (Chickpeas)
- **市场规模**: 中等 (22,212件)
- **近期热度**: 最高 (7天647件)
- **竞争度**: 中等 (20个店铺)
- **建议**: ✅ 推荐关注，近期热度高且竞争适中

### 板栗 (Chestnuts)
- **市场规模**: 较小 (19,695件)
- **近期热度**: 低 (7天80件)
- **建议**: 观望，关注季节性需求

---

*报告由 TikTok Product Intelligence 自动生成*
"""

    return report


if __name__ == "__main__":
    main()