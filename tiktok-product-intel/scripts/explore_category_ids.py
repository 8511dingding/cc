#!/usr/bin/env python3
"""
通过URL参数直接访问即食食品分类
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def try_direct_category_access():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    # 尝试不同的分类ID组合
    # 食品饮料 l1_cid=24
    # 已知子分类ID: 915336(饮料), 914952(?), 915336(?)

    category_urls = [
        # 尝试即食食品可能的ID
        "https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH&l1_cid=24&l2_cid=914952",
        "https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH&l1_cid=24&l2_cid=915336",
        "https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH&l1_cid=24&l2_cid=947080",
    ]

    for url in category_urls:
        print(f"\n尝试访问: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        # 获取分类名称
        body_text = page.evaluate('document.body.innerText')
        lines = body_text.split('\n')

        print("当前页面包含的分类行:")
        category_lines = []
        for i, line in enumerate(lines):
            if ('食品' in line or '饮料' in line or '即食' in line or '生鲜' in line or
                '调味' in line or '咖啡' in line or '茶' in line) and len(line) < 20:
                print(f"  行{i}: {line.strip()}")
                category_lines.append(line.strip())

        # 打印前几行数据
        print("\n表格数据预览:")
        rows = page.query_selector_all('tbody tr')
        for i, row in enumerate(rows[:3]):
            cells = row.query_selector_all('td')
            if len(cells) >= 5:
                print(f"  行{i+1}: {cells[1].inner_text()[:60]}")

def explore_categories_with_api():
    """使用JavaScript探索分类层级"""
    print("\n\n使用JavaScript探索分类结构...")

    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 点击食品饮料展开一级分类
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

    # 获取当前页面的级联菜单内容
    menu_info = page.evaluate("""
        () => {
            // 找到级联选择器
            const cascader = document.querySelector('.ant-cascader-menus');
            if (!cascader) return 'No cascader found';

            const items = cascader.querySelectorAll('.ant-cascader-menu-item');
            const result = [];

            items.forEach(item => {
                result.push({
                    text: item.innerText,
                    level: item.classList.contains('ant-cascader-menu-item-active') ? 'active' : 'normal'
                });
            });

            return JSON.stringify(result);
        }
    """)

    print(f"\n级联菜单内容: {menu_info}")

    # 点击即食食品
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
    page.wait_for_timeout(3000)

    print(f"\n点击后的URL: {page.url}")

    # 解析URL中的分类参数
    url = page.url
    if 'l2_cid=' in url:
        l2_cid = url.split('l2_cid=')[1].split('&')[0]
        print(f"即食食品的l2_cid: {l2_cid}")

    # 提取数据
    rows = page.query_selector_all('tbody tr')
    print(f"\n找到 {len(rows)} 行数据")

    products = []
    for row in rows[:20]:
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

            comm_match = re.search(r'(\d+)%', cell_texts[5])
            commission = int(comm_match.group(1)) if comm_match else 0

            sales_match = re.search(r'([\d.]+)万', cell_texts[6])
            sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0

            products.append({
                'rank': rank,
                'name': name,
                'price': price,
                'commission': commission,
                'sales': sales,
                'category': cell_texts[4]
            })

            print(f"  {rank}. {name[:45]} | {price:.0f} THB | 销量:{sales:,}")

        except Exception as e:
            continue

    return products

if __name__ == "__main__":
    products = explore_categories_with_api()

    if products:
        sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

        print("\n\n" + "="*80)
        print("【即食食品 TOP 10】")
        print("="*80)

        for i, p in enumerate(sorted_products[:10], 1):
            print(f"\n{i:2d}. {p['name'][:50]}")
            print(f"     价格: {p['price']:.0f} THB | 分类: {p['category']} | 佣金: {p['commission']}% | 销量: {p['sales']:,}")

    print("\n完成!")

    # 如果找到了l2_cid，保存下来
    url = products[0] if products else None
    if url and 'l2_cid=' in str(url):
        print("\n记下即食食品的分类ID")