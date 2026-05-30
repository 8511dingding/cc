#!/usr/bin/env python3
"""
采集FastMOSS即食食品分类 - 精确版
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

    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    print(f"当前URL: {page.url}")

    # 1. 点击"食品饮料"一级分类
    print("\n1. 选择食品饮料分类...")
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

    print(f"选择后URL: {page.url}")

    # 2. 等待并点击级联选择器展开二级分类
    print("\n2. 展开二级分类...")

    # 找到级联选择器并点击
    page.evaluate("""
        () => {
            // 查找ant-cascader组件
            const cascader = document.querySelector('.ant-cascader-menus');
            if (cascader) {
                cascader.style.display = 'block';
            }

            // 同时尝试点击分类标签本身来触发下拉
            const filterLabels = document.querySelectorAll('.filter-label, [class*="filter"]');
            for (let el of filterLabels) {
                if (el.innerText && el.innerText.includes('商品分类')) {
                    el.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(1000)

    # 3. 尝试展开"饮料"子分类，然后选择"即食食品"
    print("\n3. 查找并点击即食食品...")

    # 通过JavaScript直接操作级联菜单
    page.evaluate("""
        () => {
            // 首先找到所有的级联菜单项
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            console.log('Found ' + items.length + ' cascader items');

            // 找到"饮料"分类并点击展开
            for (let item of items) {
                if (item.innerText === '饮料') {
                    console.log('Found 饮料, clicking...');
                    item.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(1000)

    # 检查是否有新的菜单项出现（即食食品）
    page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            console.log('After clicking 饮料, found ' + items.length + ' items');
            items.forEach(item => {
                console.log('Item: ' + item.innerText);
            });
        }
    """)

    # 查找并点击即食食品
    page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            for (let item of items) {
                if (item.innerText === '即食食品') {
                    console.log('Found 即食食品, clicking...');
                    item.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(3000)

    print(f"\n最终URL: {page.url}")

    # 提取数据
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
        if sales > 5000: score += 40
        elif sales > 2000: score += 30
        elif sales > 1000: score += 20
        elif sales > 500: score += 10

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

### 即食食品子分类
1. **方便面/杯面** - 东南亚传统品类，需求稳定
2. **速溶饮品** - 咖啡、奶茶、果汁粉
3. **肉干/鱼干零食** - 泰国特色，符合当地口味
4. **调味方便食品** - 肉松、调味包、酱料
5. **罐头食品** - 保鲜时间长
6. **微波炉食品** - 城市上班族青睐

### 选品建议

**推荐关注品类（按潜力排序）：**
1. **方便面/杯面** - 群众基础大，泰国方便食品传统
2. **咖啡/奶茶速溶** - 泰国咖啡文化浓厚，复购率高
3. **肉干零食** - 冲动消费属性强，泰国口味偏好
4. **调味酱料** - 泰国料理常用，消耗快

**1688货源关键词：**
- "泰国方便面" "杯面批发" "即食面条"
- "泰国咖啡" "速溶咖啡" "咖啡粉"
- "猪肉干" "鱼干零食" "即食肉干"
- "泰国调味酱" "辣椒酱" "鱼露"

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