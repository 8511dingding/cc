#!/usr/bin/env python3
"""
采集FastMOSS即食食品分类 - 使用Playwright Locator
"""
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime

def collect_ready_to_eat():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 1. 点击"食品饮料"一级分类
    print("\n1. 选择食品饮料分类...")
    page.click('label:has-text("食品饮料")')
    page.wait_for_timeout(2000)

    print(f"选择后URL: {page.url}")

    # 2. 点击商品分类展开级联菜单
    print("\n2. 展开级联菜单...")
    page.click('text=商品分类：食品饮料')
    page.wait_for_timeout(1500)

    # 3. 使用Playwright Locator精确找到即食食品并点击
    print("\n3. 查找并点击即食食品...")

    # 等待级联菜单出现
    page.wait_for_selector('.ant-cascader-menus', timeout=5000)
    page.wait_for_timeout(500)

    # 找到级联菜单中的即食食品
    # 方法：使用 nth() 选择第二个菜单项（第一个是饮料，第二个是即食食品）
    try:
        # 找到所有菜单项
        menu_items = page.locator('.ant-cascader-menu-item')
        count = menu_items.count()
        print(f"  找到 {count} 个菜单项")

        # 打印所有菜单项
        for i in range(count):
            text = menu_items.nth(i).inner_text()
            print(f"    {i}: {text}")

        # 找到即食食品
        for i in range(count):
            text = menu_items.nth(i).inner_text()
            if '即食食品' in text:
                print(f"  点击菜单项 {i}: {text}")
                menu_items.nth(i).click()
                page.wait_for_timeout(3000)
                break

    except Exception as e:
        print(f"  使用Locator点击失败: {e}")

        # 备用方法：直接通过坐标点击
        print("\n  使用备用坐标点击...")
        result = page.evaluate("""
            () => {
                const items = document.querySelectorAll('.ant-cascader-menu-item');
                for (let i = 0; i < items.length; i++) {
                    if (items[i].innerText.includes('即食食品')) {
                        const rect = items[i].getBoundingClientRect();
                        return {
                            index: i,
                            text: items[i].innerText,
                            x: Math.round(rect.left + rect.width / 2),
                            y: Math.round(rect.top + rect.height / 2)
                        };
                    }
                }
                return null;
            }
        """)

        if result:
            print(f"  找到即食食品: index={result['index']},坐标=({result['x']},{result['y']})")
            page.mouse.click(result['x'], result['y'])
            page.wait_for_timeout(3000)

    print(f"\n点击后URL: {page.url}")

    # 4. 提取数据
    print("\n4. 提取数据...")
    rows = page.query_selector_all('tbody tr')

    print(f"找到 {len(rows)} 行")

    products = []
    for row in rows[:50]:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 8: continue

            cell_texts = [c.inner_text().strip() for c in cells]

            if not cell_texts[0].isdigit(): continue

            rank = int(cell_texts[0])
            product_raw = cell_texts[1]

            name = product_raw.split('售价')[0].strip()[:80]
            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            country = cell_texts[2]
            store = cell_texts[3]
            category = cell_texts[4]

            comm_match = re.search(r'(\d+)%', cell_texts[5])
            commission = int(comm_match.group(1)) if comm_match else 0

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

            print(f"  {rank}. {name[:45]}")
            print(f"      价格: {price:.0f} THB | 分类: {category} | 佣金: {commission}% | 销量: {sales:,}")

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
    print("【即食食品爆款特征分析】")
    print("="*80)

    # 价格分布
    price_ranges = {'0-100': 0, '100-200': 0, '200-500': 0, '500+': 0}
    for p in products:
        price = p.get('price', 0)
        if price < 100: price_ranges['0-100'] += 1
        elif price < 200: price_ranges['100-200'] += 1
        elif price < 500: price_ranges['200-500'] += 1
        else: price_ranges['500+'] += 1

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

## 即食食品选品建议

### 即食食品品类特点
- **便利性**: 无需烹饪，开封即食，适合泰国上班族/学生
- **保质期**: 通常6-12个月，库存风险相对较低
- **重量**: 多为小包装/单份装，海运成本可控
- **价格**: 50-300 THB大众消费为主，转化率高

### 即食食品子分类（根据FastMOSS分类结构）
1. **即食泡面** - 东南亚传统品类，需求稳定
2. **罐装与包装食品** - 保鲜时间长
3. **即食饭与粥** - 方便速食
4. **即食火锅** - 网红新品类

### 选品建议

**推荐关注品类（按潜力排序）：**
1. **即食泡面/杯面** - 群众基础大，泰国方便食品传统
2. **罐装与包装食品** - 易保存，海运风险低
3. **即食饭与粥** - 上班族午餐需求

**1688货源关键词：**
- "泰国方便面" "即食泡面" "杯面批发"
- "泰国罐装食品" "包装食品批发"
- "即食米饭" "方便粥"

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