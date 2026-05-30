#!/usr/bin/env python3
"""
深入探索FastMOSS泰国TikTok热推榜 - 使用表格结构提取
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def explore_food_table():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print(f"当前URL: {page.url}")

    # 访问热推榜泰国站
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 点击食品饮料分类
    print("\n点击食品饮料分类...")
    page.click('text=食品饮料')
    page.wait_for_timeout(2000)

    print(f"当前URL: {page.url}")

    # 等待表格加载
    page.wait_for_timeout(3000)

    # 直接提取表格数据
    products = []

    # 尝试多种表格选择器
    selectors = [
        'tbody tr',
        '.el-table__body tr',
        '[class*="table"] tr',
        'table tr'
    ]

    rows = []
    for sel in selectors:
        rows = page.query_selector_all(sel)
        print(f"选择器 '{sel}' 找到 {len(rows)} 行")
        if rows:
            break

    print(f"\n找到 {len(rows)} 行数据")

    # 逐行提取数据
    for i, row in enumerate(rows[:30]):
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 6:
                continue

            # 提取每个单元格文本
            cell_texts = []
            for cell in cells:
                cell_texts.append(cell.inner_text().strip())

            print(f"\n行 {i+1}: {cell_texts[:8]}")  # 最多显示8列

            # 解析关键字段
            # 假设列顺序: 排名, 商品, 国家, 店铺, 分类, 佣金, 销量, 销售额
            if len(cell_texts) >= 7:
                rank_text = cell_texts[0]
                product_text = cell_texts[1]
                country_text = cell_texts[2]
                store_text = cell_texts[3]
                category_text = cell_texts[4]
                commission_text = cell_texts[5]
                sales_text = cell_texts[6]

                # 检查是否是有效数据行
                if rank_text.isdigit():
                    rank = int(rank_text)

                    # 解析商品名称和价格
                    name = product_text.split('售价')[0].strip() if '售价' in product_text else product_text[:80]

                    # 解析价格
                    price_match = re.search(r'฿([\d,]+\.?\d*)', product_text)
                    price = float(price_match.group(1).replace(',', '')) if price_match else 0

                    # 解析佣金
                    comm_match = re.search(r'(\d+)%', commission_text)
                    commission = int(comm_match.group(1)) if comm_match else 0

                    # 解析销量
                    sales_match = re.search(r'([\d.]+)万', sales_text)
                    sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0
                    if not sales:
                        sales_match = re.search(r'(\d+)', sales_text)
                        sales = int(sales_match.group(1)) if sales_match else 0

                    products.append({
                        'rank': rank,
                        'name': name,
                        'price': price,
                        'price_raw': product_text,
                        'country': country_text,
                        'store': store_text,
                        'category': category_text,
                        'commission': commission,
                        'sales': sales,
                        'sales_raw': sales_text
                    })

                    print(f"  -> 商品: {name[:40]} | 价格: {price} | 佣金: {commission}% | 销量: {sales:,}")

        except Exception as e:
            print(f"  解析行 {i+1} 失败: {e}")
            continue

    return products

def analyze_products(products):
    """分析产品特征"""
    print(f"\n\n共提取 {len(products)} 个商品")

    # 按销量排序
    sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

    print("\n" + "="*80)
    print("【FastMOSS泰国TikTok热推榜 食品饮料 TOP 20】")
    print("="*80)

    for i, p in enumerate(sorted_products[:20], 1):
        name = p.get('name', 'N/A')[:50]
        price = p.get('price', 0)
        store = p.get('store', 'N/A')
        category = p.get('category', 'N/A')
        commission = p.get('commission', 0)
        sales = p.get('sales', 0)

        print(f"\n{i:2d}. {name}")
        print(f"     价格: {price:.0f} THB | 店铺: {store} | 分类: {category}")
        print(f"     佣金: {commission}% | 7天销量: {sales:,}")

    # 分类统计
    print("\n\n" + "="*80)
    print("【食品饮料爆款特征分析】")
    print("="*80)

    categories = {}
    price_ranges = {'0-200': 0, '200-500': 0, '500-1000': 0, '1000+': 0}
    commission_rates = {}

    for p in products:
        cat = p.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1

        price = p.get('price', 0)
        if price < 200:
            price_ranges['0-200'] += 1
        elif price < 500:
            price_ranges['200-500'] += 1
        elif price < 1000:
            price_ranges['500-1000'] += 1
        else:
            price_ranges['1000+'] += 1

        comm = p.get('commission', 0)
        if comm > 0:
            commission_rates[comm] = commission_rates.get(comm, 0) + 1

    print("\n分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}个 ({count/len(products)*100:.1f}%)")

    print("\n价格区间分布:")
    for range_name, count in price_ranges.items():
        print(f"  {range_name} THB: {count}个 ({count/len(products)*100:.1f}%)")

    print("\n佣金比例分布:")
    for comm, count in sorted(commission_rates.items()):
        print(f"  {comm}%: {count}个")

    # 选品建议
    print("\n\n" + "="*80)
    print("【选品建议】")
    print("="*80)

    # 高销量TOP5
    print("\n高销量TOP5:")
    for i, p in enumerate(sorted_products[:5], 1):
        print(f"  {i}. {p.get('name', '')[:40]}")
        print(f"     价格: {p.get('price', 0):.0f} THB | 分类: {p.get('category')} | 佣金: {p.get('commission')}% | 销量: {p.get('sales', 0):,}")

    # 高佣金商品
    high_comm_products = [p for p in products if p.get('commission', 0) >= 10]
    high_comm_products = sorted(high_comm_products, key=lambda x: -x.get('sales', 0))

    print(f"\n高佣金商品 (≥10%): {len(high_comm_products)}个")
    for p in high_comm_products[:5]:
        print(f"  - {p.get('name', '')[:40]} | 佣金:{p.get('commission')}% | 销量:{p.get('sales', 0):,}")

    # 推荐商品
    print("\n\n" + "="*80)
    print("【可关注商品】")
    print("="*80)

    # 综合评分: 销量(40%) + 佣金(30%) + 价格适中(30%)
    scored = []
    for p in products:
        score = 0
        # 销量分数 (最高40分)
        sales = p.get('sales', 0)
        if sales > 5000:
            score += 40
        elif sales > 2000:
            score += 30
        elif sales > 1000:
            score += 20
        elif sales > 500:
            score += 10

        # 佣金分数 (最高30分)
        comm = p.get('commission', 0)
        score += min(comm * 3, 30)

        # 价格适中分数 (100-500之间最好, 30分)
        price = p.get('price', 0)
        if 100 <= price <= 300:
            score += 30
        elif 300 < price <= 500:
            score += 20
        elif price < 100:
            score += 10
        else:
            score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    print("\n综合评分TOP10 (销量40% + 佣金30% + 价格30%):")
    for i, (score, p) in enumerate(scored[:10], 1):
        print(f"  {i}. [{score}分] {p.get('name', '')[:40]}")
        print(f"      价格: {p.get('price', 0):.0f} THB | 销量: {p.get('sales', 0):,} | 佣金: {p.get('commission')}%")

    return products, scored

if __name__ == "__main__":
    products = explore_food_table()

    if products:
        products, scored = analyze_products(products)

    print("\n\n分析完成!")