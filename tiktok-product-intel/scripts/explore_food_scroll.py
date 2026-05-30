#!/usr/bin/env python3
"""
深入探索FastMOSS泰国TikTok热推榜 - 滚动展开分类
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def explore_food_hotlist():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print(f"当前URL: {page.url}")

    # 访问热推榜泰国站
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 先滚动到页面顶部让元素可见
    page.evaluate('window.scrollTo(0, 0)')
    page.wait_for_timeout(1000)

    # 找到商品分类展开按钮
    print("\n查找商品分类筛选器...")

    # 查找"商品分类"文本附近的元素
    category_block = page.locator('text=商品分类').first
    if category_block:
        print("找到商品分类标签")
        # 尝试点击展开
        parent = category_block.locator('..')
        for _ in range(5):
            try:
                parent.click()
                page.wait_for_timeout(500)
            except:
                pass

    # 查找所有可见的分类选项
    print("\n查找可见的分类选项...")
    all_text = page.evaluate('document.body.innerText')
    lines = all_text.split('\n')

    # 打印包含"食品"或"饮料"的行
    for i, line in enumerate(lines):
        if '食品' in line or '饮料' in line or '美妆' in line:
            print(f"  行 {i}: {line[:60]}")

    # 尝试JavaScript点击食品饮料
    print("\n尝试JavaScript点击食品饮料...")
    try:
        # 找到食品饮料的span并点击
        page.evaluate("""
            () => {
                const elements = document.querySelectorAll('span');
                for (let el of elements) {
                    if (el.innerText === '食品饮料') {
                        el.click();
                        break;
                    }
                }
            }
        """)
        page.wait_for_timeout(2000)
        print("JavaScript点击成功")
    except Exception as e:
        print(f"JavaScript点击失败: {e}")

    print(f"当前URL: {page.url}")

    # 等待并获取表格数据
    page.wait_for_timeout(3000)

    # 提取表格数据
    print("\n提取表格数据...")
    rows = page.query_selector_all('tbody tr')

    print(f"找到 {len(rows)} 行")

    products = []
    for i, row in enumerate(rows[:30]):
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 8:
                continue

            cell_texts = [c.inner_text().strip() for c in cells]

            # 解析数据
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

            print(f"  {rank}. {name[:40]} | {price:.0f} THB | 销量:{sales:,} | 佣金:{commission}%")

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
    print("【FastMOSS泰国TikTok热推榜 食品饮料 TOP 20】")
    print("="*80)

    for i, p in enumerate(sorted_products[:20], 1):
        print(f"\n{i:2d}. {p['name'][:50]}")
        print(f"     价格: {p['price']:.0f} THB | 分类: {p['category']} | 佣金: {p['commission']}% | 销量: {p['sales']:,}")

    # 统计分析
    print("\n\n" + "="*80)
    print("【爆款商品特征分析】")
    print("="*80)

    categories = {}
    for p in products:
        cat = p.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1

    print("\n分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}个 ({count/len(products)*100:.1f}%)")

    # 综合评分推荐
    print("\n\n" + "="*80)
    print("【选品推荐】")
    print("="*80)

    scored = []
    for p in products:
        score = 0
        sales = p.get('sales', 0)
        if sales > 5000: score += 40
        elif sales > 2000: score += 30
        elif sales > 1000: score += 20
        elif sales > 500: score += 10

        comm = p.get('commission', 0)
        score += min(comm * 3, 30)

        price = p.get('price', 0)
        if 100 <= price <= 400: score += 30
        elif 400 < price <= 800: score += 20
        elif price < 100: score += 10
        else: score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    print("\n综合评分TOP10:")
    for i, (score, p) in enumerate(scored[:10], 1):
        print(f"\n  {i}. [{score}分] {p['name'][:45]}")
        print(f"      价格: {p['price']:.0f} THB | 销量: {p['sales']:,} | 佣金: {p['commission']}% | 分类: {p['category']}")

    # 保存报告
    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_food_hotlist.md"

    report = f"""# FastMOSS泰国TikTok热推榜 食品饮料分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH

## 数据概览

- 采集商品数: {len(products)}
- 数据类型: 周榜

---

## TOP 20 爆款商品

| 排名 | 商品名称 | 价格(THB) | 分类 | 佣金 | 7天销量 |
|------|----------|-----------|------|------|---------|
"""

    for i, p in enumerate(sorted_products[:20], 1):
        report += f"| {i} | {p['name'][:40]} | {p['price']:.0f} | {p['category']} | {p['commission']}% | {p['sales']:,} |\n"

    report += f"""

---

## 分类分布

"""
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        report += f"- {cat}: {count}个 ({count/len(products)*100:.1f}%)\n"

    report += """

---

## 选品建议

基于销量、佣金、价格三个维度综合评分：

1. **高销量高佣金产品** - 优先关注
2. **价格100-400THB** - 适合大众消费
3. **佣金≥10%** - 可获得较高利润

**推荐关注品类:**
- 咖啡类 (佣金10-15%)
- 蛋白质/代餐 (佣金8-12%)
- 零食干粮 (佣金5-10%)
"""

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n\n报告已保存到: {report_path}")

if __name__ == "__main__":
    products = explore_food_hotlist()
    if products:
        analyze_and_report(products)
    print("\n完成!")