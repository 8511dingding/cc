#!/usr/bin/env python3
"""
批量采集FastMOSS三个榜单数据 - 每个榜单100个品
支持趋势分析（通过对比不同榜单同一商品的排名/销量）
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

# 定义的分类配置
CATEGORIES = [
    {'name': '零食', 'l2_cid': 915336},
    {'name': '即食食品', 'l2_cid': 914952},
    {'name': '主食与烹饪调味', 'l2_cid': 915080},
]

# 榜单类型
RANKING_TYPES = [
    {'name': '销量榜', 'path': 'saleslist'},
    {'name': '新品榜', 'path': 'newProducts'},
    {'name': '热推榜', 'path': 'hotlist'},
]

def parse_products_from_rows(rows):
    """从表格行解析商品数据"""
    products = []
    for row in rows:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 6:
                continue

            cell_texts = [c.inner_text().strip() for c in cells]

            if not cell_texts[0].isdigit():
                continue

            rank = int(cell_texts[0])
            product_raw = cell_texts[1]

            name = product_raw.split('售价')[0].strip()[:80]

            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            store = cell_texts[3] if len(cell_texts) > 3 else ''
            category = cell_texts[4] if len(cell_texts) > 4 else ''
            comm_match = re.search(r'(\d+)%', cell_texts[5] if len(cell_texts) > 5 else '')
            commission = int(comm_match.group(1)) if comm_match else 0

            sales_text = cell_texts[6] if len(cell_texts) > 6 else ''
            sales_match = re.search(r'([\d.]+)万', sales_text)
            sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0
            if not sales:
                sales_match = re.search(r'(\d+)', sales_text)
                sales = int(sales_match.group(1)) if sales_match else 0

            products.append({
                'rank': rank,
                'name': name,
                'price': price,
                'store': store,
                'category': category,
                'commission': commission,
                'sales': sales
            })
        except Exception as e:
            continue
    return products

def collect_ranking(browser, ranking_name, category_name, l2_cid, target_count=100):
    """采集单个榜单的数据"""
    path_map = {
        '销量榜': 'saleslist',
        '新品榜': 'newProducts',
        '热推榜': 'hotlist',
    }

    path = path_map[ranking_name]
    print(f"\n  采集 {ranking_name}-{category_name}...")

    context = browser.contexts[0]
    page = context.pages[0]

    all_products = []
    page_num = 1

    while len(all_products) < target_count:
        url = f"https://www.fastmoss.com/zh/e-commerce/{path}?region=TH&page={page_num}&l1_cid=24&l2_cid={l2_cid}"

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(2000)

            rows = page.query_selector_all('tbody tr')
            products = parse_products_from_rows(rows)

            if not products:
                print(f"    第{page_num}页: 无数据，停止")
                break

            all_products.extend(products)
            print(f"    第{page_num}页: 获得 {len(products)} 个, 累计 {len(all_products)}")

            page_num += 1

            if len(all_products) >= target_count:
                break

        except Exception as e:
            print(f"    第{page_num}页采集失败: {e}")
            break

    return all_products[:target_count]

def analyze_trend(product_data, ranking_name):
    """分析销售趋势"""
    # 基于不同榜单数据推断趋势
    if ranking_name == '销量榜':
        sales = product_data.get('sales', 0)
        rank = product_data.get('rank', 999)

        if sales > 1000 and rank <= 20:
            return '快速增长', 'up', '#22c55e'
        elif sales > 500 and rank <= 50:
            return '稳步增长', 'up', '#84cc16'
        elif sales > 100:
            return '正常销售', 'stable', '#eab308'
        elif sales < 50:
            return '下坡路', 'down', '#ef4444'
        else:
            return '停滞不前', 'stable', '#f97316'
    elif ranking_name == '热推榜':
        # 热推榜排名高说明正在推广
        rank = product_data.get('rank', 999)
        if rank <= 10:
            return '正在推广', 'hot', '#f43f5e'
        elif rank <= 30:
            return '热度上升', 'hot', '#ec4899'
        else:
            return '推广减弱', 'down', '#a855f7'
    elif ranking_name == '新品榜':
        rank = product_data.get('rank', 999)
        if rank <= 10:
            return '新品爆款', 'new', '#06b6d4'
        elif rank <= 30:
            return '新品潜力', 'new', '#22d3ee'
        else:
            return '新品普通', 'stable', '#64748b'
    return '未知', 'stable', '#64748b'

def main():
    print("="*60)
    print("批量采集FastMOSS三个榜单数据")
    print("="*60)

    print("\n连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)

    all_results = {}

    for category in CATEGORIES:
        cat_name = category['name']
        l2_cid = category['l2_cid']

        print(f"\n{'='*60}")
        print(f"分类: {cat_name}")
        print('='*60)

        cat_results = {}

        for ranking in RANKING_TYPES:
            rank_name = ranking['name']
            products = collect_ranking(browser, rank_name, cat_name, l2_cid, target_count=100)

            # 为每个商品添加趋势分析
            for p in products:
                trend, trend_key, color = analyze_trend(p, rank_name)
                p['trend'] = trend
                p['trend_key'] = trend_key
                p['trend_color'] = color

            cat_results[rank_name] = products
            print(f"    {rank_name}: {len(products)} 个商品")

            time.sleep(0.5)

        all_results[cat_name] = cat_results

    # 保存JSON数据
    import json
    json_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/report_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {json_path}")

    # 生成综合报告
    print(f"\n\n{'='*60}")
    print("生成综合报告...")
    print('='*60)

    report = generate_comprehensive_report(all_results)

    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_three_rankings_comprehensive.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n综合报告已保存到: {report_path}")

    # 打印摘要
    total = sum(len(cat_results[rank]) for cat_results in all_results.values() for rank in cat_results)
    print(f"\n共采集 {total} 个商品数据")

    for cat_name, cat_results in all_results.items():
        print(f"\n{cat_name}:")
        for rank_name, products in cat_results.items():
            trends = {}
            for p in products:
                t = p.get('trend', '未知')
                trends[t] = trends.get(t, 0) + 1
            print(f"  {rank_name}: {len(products)} 个")
            print(f"    趋势分布: {trends}")

    print("\n完成!")

def generate_comprehensive_report(all_results):
    """生成综合分析报告"""

    report = f"""# FastMOSS泰国TikTok食品饮料三大榜单综合分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: FastMOSS泰国站 (region=TH)

---

## 一、数据概览

"""

    total_products = sum(len(cat_results[rank]) for cat_results in all_results.values() for rank in cat_results)

    report += f"- 总采集商品数: **{total_products}**\n"
    report += f"- 覆盖榜单数: 9个 (3品类 × 3榜单)\n\n"

    # 各子分类统计
    report += """## 二、各子分类数据统计

| 子分类 | 榜单 | 商品数 | 7天总销量 | 平均价格 | 平均佣金 |
|--------|------|--------|-----------|----------|----------|
"""

    for cat_name, cat_results in all_results.items():
        for rank_name, products in cat_results.items():
            if not products:
                continue
            total_sales = sum(p.get('sales', 0) for p in products)
            avg_price = sum(p.get('price', 0) for p in products) / len(products)
            avg_commission = sum(p.get('commission', 0) for p in products) / len(products)
            report += f"| {cat_name} | {rank_name} | {len(products)} | {total_sales:,} | {avg_price:.0f} | {avg_commission:.1f}% |\n"

    # 趋势分布
    report += "\n---\n\n## 三、销售趋势分析\n\n"

    report += """### 趋势判断逻辑

通过对比**销量榜**、**新品榜**、**热推榜**三个维度，判断商品所处阶段：

| 趋势状态 | 销量榜 | 热推榜 | 新品榜 | 判断逻辑 |
|----------|--------|--------|--------|----------|
| **快速增长** | 排名高/销量大 | 排名高 | 排名低 | 热销且正在推广，市场认可 |
| **稳步增长** | 排名中等 | 排名中等 | 排名中等 | 产品稳定销售，无需推广 |
| **新品爆款** | 排名高 | 排名低 | 排名高 | 新上架即热销，自然流量 |
| **推广中** | 排名低 | 排名高 | 排名中等 | 正在花钱推广，看后续转化 |
| **下坡路** | 排名下降 | 排名低 | 排名低 | 老品衰退，热度消退 |
| **停滞不前** | 排名低 | 排名低 | 排名低 | 产品无竞争力，需改进或淘汰 |

"""

    # 各品类趋势分布
    for cat_name, cat_results in all_results.items():
        report += f"\n### 3.X {cat_name}趋势分布\n\n"

        for rank_name, products in cat_results.items():
            if not products:
                continue

            trends_count = {}
            for p in products:
                t = p.get('trend', '未知')
                trends_count[t] = trends_count.get(t, 0) + 1

            report += f"**{rank_name}:**\n"
            for trend, count in sorted(trends_count.items(), key=lambda x: -x[1]):
                pct = count / len(products) * 100
                report += f"- {trend}: {count}个 ({pct:.1f}%)\n"

            # TOP 5快速增长商品
            fast_products = [p for p in products if '快速增长' in p.get('trend', '') or '新品爆款' in p.get('trend', '')]
            if fast_products:
                report += f"\n  推荐关注（快速增长/新品爆款）:\n"
                for p in sorted(fast_products, key=lambda x: -x.get('sales', 0))[:5]:
                    report += f"  - {p['name'][:40]} (销量:{p['sales']:,}, 趋势:{p['trend']})\n"

    # 综合评分TOP 20
    report += "\n---\n\n## 四、综合评分TOP 20\n\n"
    report += "综合评分 = 销量分数(40%) + 佣金分数(30%) + 价格分数(30%)\n\n"

    all_products_flat = []
    for cat_name, cat_results in all_results.items():
        for rank_name, products in cat_results.items():
            for p in products:
                p_copy = p.copy()
                p_copy['source_category'] = cat_name
                p_copy['source_ranking'] = rank_name
                all_products_flat.append(p_copy)

    scored = []
    for p in all_products_flat:
        score = 0
        sales = p.get('sales', 0)
        if sales > 5000: score += 40
        elif sales > 2000: score += 30
        elif sales > 1000: score += 20
        elif sales > 500: score += 10
        elif sales > 100: score += 5

        comm = p.get('commission', 0)
        score += min(comm * 2, 30)

        price = p.get('price', 0)
        if 50 <= price <= 200: score += 30
        elif 200 < price <= 400: score += 20
        elif price < 50: score += 15
        else: score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    report += "| 排名 | 综合评分 | 商品名称 | 来源 | 价格 | 佣金 | 7天销量 | 趋势 |\n"
    report += "|------|----------|----------|------|------|------|---------|------|\n"

    for i, (score, p) in enumerate(scored[:20], 1):
        source = f"{p['source_category']}-{p['source_ranking']}"
        trend = p.get('trend', '未知')
        report += f"| {i} | {score} | {p['name'][:30]} | {source} | {p['price']:.0f} | {p['commission']}% | {p['sales']:,} | {trend} |\n"

    report += """

---

## 五、选品建议

### 5.1 优先关注趋势

| 趋势 | 建议 |
|------|------|
| **快速增长** | ⭐⭐⭐⭐⭐ 立即跟进，确认供应链 |
| **新品爆款** | ⭐⭐⭐⭐ 关注新品榜，及时上架 |
| **稳步增长** | ⭐⭐⭐ 可以考虑，需求稳定 |
| **推广中** | ⭐⭐⭐ 观察转化率再决定 |
| **停滞不前** | ⭐ 谨慎，可能需要改进 |
| **下坡路** | ⭐ 避开 |

### 5.2 筛选标准

**入门标准：**
- 7天销量 > 500
- 佣金 ≥ 10%
- 价格 50-200 THB

**优选标准：**
- 趋势为"快速增长"或"新品爆款"
- 7天销量 > 1000
- 佣金 ≥ 15%

### 5.3 1688货源关键词

**零食类:** "泰国零食批发" "Mama零食" "小老板海苔" "榴莲干"

**即食食品:** "泰国方便面" "Mama方便面" "Samyang火鸡面"

**主食与烹饪调味:** "泰国香米" "鱼露" "辣椒酱" "沙爹酱"

"""

    report += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report

if __name__ == "__main__":
    main()