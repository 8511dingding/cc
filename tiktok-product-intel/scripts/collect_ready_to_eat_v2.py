#!/usr/bin/env python3
"""
采集FastMOSS即食食品分类数据 - 通过销量榜访问
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def collect_from_sales_rank():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    # 访问销量榜而非热推榜
    print("\n访问销量榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/product?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    print(f"当前URL: {page.url}")

    # 获取页面文本来了解分类结构
    body_text = page.evaluate('document.body.innerText')
    lines = body_text.split('\n')

    print("\n查找即食食品相关的分类选项:")
    for i, line in enumerate(lines):
        if ('即食' in line or '即时' in line or '方便' in line or '调料' in line or '调味' in line):
            print(f"  行{i}: {line.strip()}")

    # 尝试点击分类筛选器
    print("\n尝试展开分类筛选...")

    # 查找所有分类标签
    category_labels = page.query_selector_all('.ant-radio-button-wrapper, .ant-tag, [class*="category"]')

    print(f"找到 {len(category_labels)} 个可能的分类元素")

    # 尝试通过点击展开分类
    for label in category_labels[:20]:
        try:
            text = label.inner_text().strip()
            if text and len(text) < 20:
                print(f"  分类选项: {text}")
        except:
            pass

    # 通过JavaScript点击"食品饮料"展开子分类
    print("\n点击食品饮料分类...")
    page.evaluate("""
        () => {
            const elements = document.querySelectorAll('label, span, div');
            for (let el of elements) {
                if (el.innerText === '食品饮料') {
                    el.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(2000)

    print(f"点击后URL: {page.url}")

    # 再次获取页面内容，查找级联菜单
    page.wait_for_timeout(1000)

    # 尝试直接访问即食食品 - 通过l2_cid参数
    # 从之前的探索中，我们知道即食食品可能在某个特定的分类ID下
    # 先尝试l2_cid=947080（之前在食品饮料下点击即食食品时的ID）

    print("\n尝试通过分类参数访问...")

    # 先点击食品饮料
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

    # 获取当前URL
    print(f"当前URL: {page.url}")

    # 如果URL中有l2_cid参数，说明已经选中了某个子分类
    if 'l2_cid=' in page.url:
        current_l2 = page.url.split('l2_cid=')[1].split('&')[0]
        print(f"当前l2_cid: {current_l2}")

    # 提取当前页面的数据
    print("\n提取页面数据...")
    rows = page.query_selector_all('tbody tr')

    products = []
    for row in rows[:30]:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 6: continue

            cell_texts = [c.inner_text().strip() for c in cells]

            # 检查是否是数据行
            if not cell_texts[0].isdigit(): continue

            rank = int(cell_texts[0])
            product_raw = cell_texts[1]

            name = product_raw.split('售价')[0].strip()[:80]

            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            comm_match = re.search(r'(\d+)%', cell_texts[4])
            commission = int(comm_match.group(1)) if comm_match else 0

            sales_match = re.search(r'([\d.]+)万', cell_texts[5])
            sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0

            products.append({
                'rank': rank,
                'name': name,
                'price': price,
                'commission': commission,
                'sales': sales,
                'category': cell_texts[3] if len(cell_texts) > 3 else ''
            })

            print(f"  {rank}. {name[:45]} | {price:.0f} THB | 销量:{sales:,} | 分类:{cell_texts[3] if len(cell_texts) > 3 else 'N/A'}")

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
    print("【即食食品 TOP 10】")
    print("="*80)

    for i, p in enumerate(sorted_products[:10], 1):
        print(f"\n{i:2d}. {p['name'][:50]}")
        print(f"     价格: {p['price']:.0f} THB | 分类: {p['category']} | 佣金: {p['commission']}% | 销量: {p['sales']:,}")

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
数据来源: https://www.fastmoss.com/zh/e-commerce/product?region=TH

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
    products = collect_from_sales_rank()
    if products:
        analyze_and_report(products)
    print("\n完成!")