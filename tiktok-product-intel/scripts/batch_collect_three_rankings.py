#!/usr/bin/env python3
"""
批量采集FastMOSS三个榜单数据 - 每个榜单100个品
销量榜、新品榜、热推榜

URL规律：
- 销量榜: /zh/e-commerce/saleslist?region=TH&page={page}&l1_cid=24&l2_cid={l2_cid}
- 新品榜: /zh/e-commerce/newProducts?region=TH&page={page}&l1_cid=24&l2_cid={l2_cid}
- 热推榜: /zh/e-commerce/hotlist?region=TH&page={page}&l1_cid=24&l2_cid={l2_cid}

翻页参数: page=1,2,3... pagesize=10(固定10个/页)
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

            # 检查是否是有效数据行
            if not cell_texts[0].isdigit():
                continue

            rank = int(cell_texts[0])
            product_raw = cell_texts[1]

            # 提取商品名称（去除价格部分）
            name = product_raw.split('售价')[0].strip()[:80]

            # 提取价格
            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            # 店铺
            store = cell_texts[3] if len(cell_texts) > 3 else ''

            # 分类
            category = cell_texts[4] if len(cell_texts) > 4 else ''

            # 佣金
            comm_match = re.search(r'(\d+)%', cell_texts[5] if len(cell_texts) > 5 else '')
            commission = int(comm_match.group(1)) if comm_match else 0

            # 7天销量/反应数
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

            # 提取数据
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

def main():
    print("="*60)
    print("批量采集FastMOSS三个榜单数据")
    print("销量榜、新品榜、热推榜 - 每个分类各100个品")
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
            cat_results[rank_name] = products

            print(f"    {rank_name}: {len(products)} 个商品")

            # 短暂延迟避免请求过快
            time.sleep(0.5)

        all_results[cat_name] = cat_results

    # 生成综合报告
    print(f"\n\n{'='*60}")
    print("生成综合分析报告...")
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
            avg_sales = sum(p.get('sales', 0) for p in products) / len(products) if products else 0
            print(f"  {rank_name}: {len(products)} 个, 平均销量 {avg_sales:,.0f}")

    print("\n完成!")

def generate_comprehensive_report(all_results):
    """生成综合分析报告"""

    report = f"""# FastMOSS泰国TikTok食品饮料三大榜单综合分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: FastMOSS泰国站 (region=TH)
采集范围: 零食、即食食品、主食与烹饪调味 × 销量榜、新品榜、热推榜

---

## 一、数据概览

"""

    # 统计各榜单商品数
    total_products = 0
    report += "| 榜单类型 | 零食 | 即食食品 | 主食与烹饪调味 | 合计 |\n"
    report += "|----------|------|----------|----------------|------|\n"

    for rank_name in ['销量榜', '新品榜', '热推榜']:
        counts = []
        for cat_name in ['零食', '即食食品', '主食与烹饪调味']:
            count = len(all_results.get(cat_name, {}).get(rank_name, []))
            counts.append(str(count))
            total_products += count
        report += f"| {rank_name} | {' | '.join(counts)} | {sum(int(c) for c in counts)} |\n"

    report += f"\n**总计采集商品数: {total_products}**\n"

    # 各子分类详细分析
    for cat_name in ['零食', '即食食品', '主食与烹饪调味']:
        report += f"\n---\n\n## 二、{cat_name}分析\n"

        for rank_name in ['销量榜', '新品榜', '热推榜']:
            products = all_results.get(cat_name, {}).get(rank_name, [])
            if not products:
                continue

            sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

            report += f"\n### 2.X {rank_name} TOP 10\n\n"
            report += "| 排名 | 商品名称 | 价格(THB) | 店铺 | 佣金 | 7天销量 |\n"
            report += "|------|----------|-----------|------|------|---------|\n"

            for i, p in enumerate(sorted_products[:10], 1):
                store = p.get('store', '')[:15]
                report += f"| {i} | {p['name'][:35]} | {p['price']:.0f} | {store} | {p['commission']}% | {p['sales']:,} |\n"

            # 统计特征
            avg_price = sum(p.get('price', 0) for p in products) / len(products)
            avg_commission = sum(p.get('commission', 0) for p in products) / len(products)
            avg_sales = sum(p.get('sales', 0) for p in products) / len(products)

            report += f"\n**{rank_name}特征:**\n"
            report += f"- 商品数: {len(products)}\n"
            report += f"- 平均价格: {avg_price:.0f} THB\n"
            report += f"- 平均佣金: {avg_commission:.1f}%\n"
            report += f"- 平均7天销量: {avg_sales:,.0f}\n"

    # 综合TOP 20（跨所有分类和榜单）
    report += "\n---\n\n## 三、综合评分TOP 20（所有榜单）\n\n"
    report += "综合评分 = 销量分数(40%) + 佣金分数(30%) + 价格分数(30%)\n\n"

    all_products_flat = []
    for cat_name, cat_results in all_results.items():
        for rank_name, products in cat_results.items():
            for p in products:
                p_copy = p.copy()
                p_copy['source_category'] = cat_name
                p_copy['source_ranking'] = rank_name
                all_products_flat.append(p_copy)

    # 计算综合评分
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

    report += "| 排名 | 综合评分 | 商品名称 | 来源 | 价格 | 佣金 | 7天销量 |\n"
    report += "|------|----------|----------|------|------|------|---------|\n"

    for i, (score, p) in enumerate(scored[:20], 1):
        source = f"{p['source_category']}-{p['source_ranking']}"
        report += f"| {i} | {score} | {p['name'][:30]} | {source} | {p['price']:.0f} | {p['commission']}% | {p['sales']:,} |\n"

    # 选品建议
    report += """

---

## 四、选品建议

### 4.1 各子分类潜力判断

| 子分类 | 推荐度 | 理由 |
|--------|--------|------|
| **零食** | ⭐⭐⭐⭐⭐ | 需求稳定，冲动消费高，复购率高 |
| **即食食品** | ⭐⭐⭐⭐ | 便利性强，泰国上班族多 |
| **主食与烹饪调味** | ⭐⭐⭐⭐ | 刚需产品，消耗快 |

### 4.2 榜单选择建议

| 榜单 | 用途 |
|------|------|
| **销量榜** | 确定哪些商品已经爆了，跑量为主 |
| **新品榜** | 发现新兴趋势，及时跟进 |
| **热推榜** | 了解商品热度，判断是否在推 |

### 4.3 选品标准

**入门标准（满足任一即可）：**
- 7天销量 > 500
- 佣金 ≥ 10%
- 价格 50-200 THB

**优选标准（满足两个以上）：**
- 7天销量 > 1000
- 佣金 ≥ 15%
- 有促销标签（如"[แถม1]"买一送一）
- 店铺销量 > 50万

### 4.4 1688货源关键词

**零食类:**
- "泰国零食批发" "Mama零食" "小老板海苔"
- "榴莲干" "芒果干" "椰子干"

**即食食品:**
- "泰国方便面" "Mama方便面" "yumyum方便面"
- "Samyang火鸡面"

**主食与烹饪调味:**
- "泰国香米" "泰国调味料"
- "鱼露" "辣椒酱" "沙爹酱"

"""

    report += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report

if __name__ == "__main__":
    main()