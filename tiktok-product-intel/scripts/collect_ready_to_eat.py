#!/usr/bin/env python3
"""
采集FastMOSS即食食品分类完整数据
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def collect_ready_to_eat():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print(f"当前URL: {page.url}")

    # 访问热推榜泰国站
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 1. 先点击"食品饮料"一级分类
    print("\n选择食品饮料分类...")
    page.evaluate("""
        () => {
            const elements = document.querySelectorAll('label');
            for (let el of elements) {
                if (el.innerText === '食品饮料') {
                    el.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(2000)

    # 2. 查找并点击级联选择器，展开二级分类
    print("\n展开二级分类菜单...")

    # 点击"食品饮料"标签来展开级联选择器
    page.evaluate("""
        () => {
            // 找到级联选择器并点击
            const cascader = document.querySelector('.ant-cascader');
            if (cascader) {
                cascader.click();
            }
        }
    """)
    page.wait_for_timeout(1000)

    # 3. 查找级联菜单中的"即食食品"并点击
    print("\n点击即食食品...")

    # 方法1：通过JavaScript点击
    page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            for (let item of items) {
                if (item.innerText === '即食食品') {
                    item.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(2000)

    print(f"当前URL: {page.url}")

    # 等待数据加载
    page.wait_for_timeout(3000)

    # 提取表格数据
    print("\n提取表格数据...")
    rows = page.query_selector_all('tbody tr')

    print(f"找到 {len(rows)} 行")

    products = []
    for i, row in enumerate(rows[:50]):
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 8:
                continue

            cell_texts = [c.inner_text().strip() for c in cells]

            rank_text = cell_texts[0]
            if not rank_text.isdigit():
                continue

            rank = int(rank_text)
            product_raw = cell_texts[1]

            # 提取名称和价格
            name = product_raw.split('售价')[0].strip()[:80]
            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            country = cell_texts[2]
            store = cell_texts[3]
            category = cell_texts[4]

            # 佣金
            comm_match = re.search(r'(\d+)%', cell_texts[5])
            commission = int(comm_match.group(1)) if comm_match else 0

            # 销量
            sales_match = re.search(r'([\d.]+)万', cell_texts[6])
            sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0
            if not sales:
                sales_match = re.search(r'(\d+)', cell_texts[6])
                sales = int(sales_match.group(1)) if sales_match else 0

            products.append({
                'rank': rank,
                'name': name,
                'price': price,
                'country': country,
                'store': store,
                'category': category,
                'commission': commission,
                'sales': sales
            })

            print(f"  {rank}. {name[:50]}")
            print(f"      价格: {price:.0f} THB | 销量: {sales:,} | 佣金: {commission}%")

        except Exception as e:
            continue

    return products

def analyze_and_report(products):
    if not products:
        print("没有找到商品数据")
        return

    print(f"\n\n共提取 {len(products)} 个商品")

    sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

    print("\n" + "="*80)
    print("【即食食品 TOP 20】")
    print("="*80)

    for i, p in enumerate(sorted_products[:20], 1):
        print(f"\n{i:2d}. {p['name'][:50]}")
        print(f"     价格: {p['price']:.0f} THB | 分类: {p['category']} | 佣金: {p['commission']}% | 销量: {p['sales']:,}")

    # 统计分析
    print("\n\n" + "="*80)
    print("【即食食品爆款特征】")
    print("="*80)

    # 价格区间
    price_ranges = {'0-100': 0, '100-200': 0, '200-500': 0, '500+': 0}
    for p in products:
        price = p.get('price', 0)
        if price < 100:
            price_ranges['0-100'] += 1
        elif price < 200:
            price_ranges['100-200'] += 1
        elif price < 500:
            price_ranges['200-500'] += 1
        else:
            price_ranges['500+'] += 1

    print("\n价格区间分布:")
    for r, c in price_ranges.items():
        print(f"  {r} THB: {c}个 ({c/len(products)*100:.1f}%)")

    # 综合评分
    scored = []
    for p in products:
        score = 0
        sales = p.get('sales', 0)
        if sales > 2000: score += 40
        elif sales > 1000: score += 30
        elif sales > 500: score += 20
        elif sales > 100: score += 10

        comm = p.get('commission', 0)
        score += min(comm * 2, 30)

        price = p.get('price', 0)
        if 50 <= price <= 200: score += 30
        elif 200 < price <= 400: score += 20
        elif price < 50: score += 15
        else: score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    print("\n\n" + "="*80)
    print("【选品推荐】")
    print("="*80)

    print("\n综合评分TOP10:")
    for i, (score, p) in enumerate(scored[:10], 1):
        print(f"\n  {i}. [{score}分] {p['name'][:45]}")
        print(f"      价格: {p['price']:.0f} THB | 销量: {p['sales']:,} | 佣金: {p['commission']}%")

    # 保存报告
    report = f"""# FastMOSS即食食品分类分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH

---

## 数据概览

- 总商品数: {len(products)}
- 7天总销量: {sum(p.get('sales',0) for p in products):,}

---

## TOP 20 爆款商品

| 排名 | 商品名称 | 价格(THB) | 分类 | 佣金 | 7天销量 |
|------|----------|-----------|------|------|---------|
"""

    for i, p in enumerate(sorted_products[:20], 1):
        report += f"| {i} | {p['name'][:40]} | {p['price']:.0f} | {p['category']} | {p['commission']}% | {p['sales']:,} |\n"

    report += """
---

## 价格区间分布

"""
    for r, c in price_ranges.items():
        report += f"- {r} THB: {c}个 ({c/len(products)*100:.1f}%)\n"

    report += """
---

## 选品建议

### 即食食品特点
- **便利性**：无需烹饪，适合泰国上班族
- **保质期**：通常6-12个月，海运风险低
- **重量**：多为小包装，海运成本低
- **价格**：50-300 THB大众消费为主

### 即食食品子分类
根据FastMOSS分类，即食食品可能包括：
- 方便面/杯面
- 即食调味包
- 速溶饮品（咖啡、奶茶）
- 肉干/鱼干零食
- 罐头食品
- 微波炉食品

### 推荐关注品类
1. **方便面/杯面** - 东南亚传统，需求稳定
2. **速溶咖啡/奶茶** - 泰国咖啡文化浓厚
3. **肉干零食** - 泰国特色，冲动消费
4. **调味方便食品** - 如肉松、调味包

### 1688货源关键词
- "泰国风味方便面" "杯面批发" "即食肉干"
- "速溶咖啡" "泰国咖啡" "即食调味包"

"""

    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_ready_to_eat.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n\n报告已保存到: {report_path}")

if __name__ == "__main__":
    products = collect_ready_to_eat()
    if products:
        analyze_and_report(products)
    print("\n完成!")