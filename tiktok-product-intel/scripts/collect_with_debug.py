#!/usr/bin/env python3
"""
采集FastMOSS即食食品分类 - 截图调试版
"""
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime

def collect_with_screenshot():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 截图保存当前状态
    page.screenshot(path='/Users/jianing/Ning\'s Git/tiktok-product-intel/scripts/debug1_initial.png')
    print("截图1: 初始页面")

    # 点击食品饮料
    print("\n点击食品饮料分类...")
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
    page.screenshot(path='/Users/jianing/Ning\'s Git/tiktok-product-intel/scripts/debug2_after_food.png')
    print("截图2: 点击食品饮料后")

    # 获取页面上所有可点击元素的信息
    clickable_info = page.evaluate("""
        () => {
            const result = [];
            const elements = document.querySelectorAll('*');
            const seen = new Set();

            for (let el of elements) {
                const text = el.innerText?.trim();
                const tag = el.tagName.toLowerCase();
                const className = el.className || '';

                if (text && (text.includes('即食') || text.includes('饮料') ||
                    text.includes('生鲜') || text.includes('食品')) &&
                    !seen.has(text) && text.length < 20) {

                    seen.add(text);
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    result.push({
                        text: text,
                        tag: tag,
                        class: className.substring(0, 80),
                        visible: style.display !== 'none' && style.visibility !== 'hidden',
                        rect: { top: Math.round(rect.top), left: Math.round(rect.left), width: Math.round(rect.width), height: Math.round(rect.height) }
                    });
                }
            }
            return JSON.stringify(result);
        }
    """)

    print(f"\n页面中的分类相关元素:")
    items = json.loads(clickable_info)
    for item in items[:15]:
        visible_mark = "✓" if item['visible'] else "✗"
        print(f"  [{visible_mark}] <{item['tag']}> {item['text']} (rect: {item['rect']['top']},{item['rect']['left']})")

    # 尝试通过坐标点击级联菜单中的即食食品
    print("\n尝试通过坐标点击...")

    # 先点击展开级联菜单
    page.evaluate("""
        () => {
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.innerText === '商品分类：食品饮料') {
                    if (el.click) el.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(1500)
    page.screenshot(path='/Users/jianing/Ning\'s Git/tiktok-product-intel/scripts/debug3_after_cascader.png')
    print("截图3: 点击商品分类后")

    # 获取所有级联菜单项的位置
    menu_items = page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item, [class*="cascader"] [class*="menu"] [class*="item"]');
            const result = [];

            items.forEach(item => {
                const rect = item.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    result.push({
                        text: item.innerText,
                        x: Math.round(rect.left + rect.width / 2),
                        y: Math.round(rect.top + rect.height / 2),
                        visible: window.getComputedStyle(item).display !== 'none'
                    });
                }
            });

            return JSON.stringify(result);
        }
    """)

    print(f"\n级联菜单项:")
    try:
        menu_list = json.loads(menu_items)
        for item in menu_list:
            vis = "✓" if item.get('visible', False) else "✗"
            print(f"  [{vis}] {item.get('text', 'N/A')} at ({item.get('x', 0)}, {item.get('y', 0)})")
    except Exception as e:
        print(f"  解析错误: {e}")
        print(f"  原始数据: {menu_items[:200]}")

    # 尝试通过坐标点击即食食品
    print("\n通过坐标点击即食食品...")
    for item in menu_list:
        if '即食' in item.get('text', ''):
            x, y = item.get('x', 0), item.get('y', 0)
            print(f"  点击坐标: ({x}, {y})")
            page.mouse.click(x, y)
            page.wait_for_timeout(2000)
            break

    page.screenshot(path='/Users/jianing/Ning\'s Git/tiktok-product-intel/scripts/debug4_final.png')
    print("截图4: 最终状态")

    print(f"\n最终URL: {page.url}")

    # 提取数据
    print("\n提取数据...")
    rows = page.query_selector_all('tbody tr')

    products = []
    for row in rows[:30]:
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
                'category': category,
                'commission': commission,
                'sales': sales
            })

            print(f"  {rank}. {name[:45]} | {price:.0f} THB | {category} | 销量:{sales:,}")

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
        else: score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    print("\n\n综合评分TOP10:")
    for i, (score, p) in enumerate(scored[:10], 1):
        print(f"  {i}. [{score}分] {p['name'][:40]} | {p['price']:.0f} THB | 销量:{p['sales']:,} | 佣金:{p['commission']}%")

    # 保存报告
    report = f"""# FastMOSS即食食品分类分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 即食食品分析结果

共采集 {len(products)} 个商品

"""

    for i, p in enumerate(sorted_products[:20], 1):
        report += f"| {i} | {p['name'][:40]} | {p['price']:.0f} | {p['category']} | {p['commission']}% | {p['sales']:,} |\n"

    report += """

### 即食食品选品建议

**品类特点:**
- 便利性高，无需烹饪
- 保质期6-12个月，库存风险低
- 小包装为主，海运成本可控

**推荐关注品类:**
- 方便面/杯面
- 速溶咖啡/奶茶
- 肉干/鱼干零食
- 调味酱料

**1688货源关键词:**
- "泰国方便面" "杯面批发"
- "泰国咖啡" "速溶咖啡"
- "猪肉干" "鱼干零食"
"""

    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_ready_to_eat.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {report_path}")

if __name__ == "__main__":
    products = collect_with_screenshot()
    if products:
        analyze_and_report(products)
    print("\n完成!")