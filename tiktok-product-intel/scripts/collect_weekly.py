#!/usr/bin/env python3
"""
FastMOSS 周榜数据采集脚本

URL格式:
https://www.fastmoss.com/zh/e-commerce/{path}?region=TH&page={页数}&l1_cid=24&l2_cid={分类}&date_type=2&date_value={2026-周数}&pagesize=10

参数:
- path: saleslist(销量榜), newProducts(新品榜), hotlist(热推榜)
- l2_cid: 915336(零食), 914952(即食食品), 915080(主食与烹饪调味)
- date_value: 2026-21(第21周), 2026-20(第20周), ... 2026-16(第16周)
- pagesize=10: 每页10条,翻10页=100个商品

使用:
1. 先打开浏览器登录FastMOSS
2. 运行: python3 scripts/collect_weekly.py
"""

import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("/Applications/ServBay/www/ning_mac")

CATEGORIES = [
    {'name': '零食', 'l2_cid': 915336},
    {'name': '即食食品', 'l2_cid': 914952},
    {'name': '主食与烹饪调味', 'l2_cid': 915080},
]

RANKING_TYPES = [
    {'name': '销量榜', 'path': 'saleslist'},
    {'name': '新品榜', 'path': 'newProducts'},
    {'name': '热推榜', 'path': 'hotlist'},
]

WEEKS = ['2026-21', '2026-20', '2026-19', '2026-18', '2026-17', '2026-16']

def extract_product_data(row):
    try:
        cells = row.query_selector_all('td')
        if len(cells) < 12:
            return None
        if not cells[1].inner_text().strip():
            return None

        row_html = row.inner_html()
        img_match = re.search(r'<img[^>]+src="([^"]+)"', row_html)
        image_url = img_match.group(1) if img_match else ''

        links = row.query_selector_all('a')
        product_url = ''
        tiktok_url = ''
        for link in links:
            href = link.get_attribute('href') or ''
            if 'product' in href and 'fastmoss' in href:
                product_url = href if href.startswith('http') else 'https://www.fastmoss.com' + href
            elif 'tiktok' in href or 'item' in href:
                tiktok_url = href if href.startswith('http') else 'https://www.tiktok.com' + href

        name_cell_text = cells[1].inner_text()
        name = name_cell_text.split('售价')[0].strip()[:150]
        price_match = re.search(r'฿([\d,]+\.?\d*)', name_cell_text)
        price = float(price_match.group(1).replace(',', '')) if price_match else 0

        store_cell = cells[3].inner_text()
        store_match = re.search(r'^(.+?)\|店铺销量', store_cell)
        store = store_match.group(1).strip() if store_match else store_cell.strip()

        category = cells[4].inner_text().strip()

        comm_text = cells[5].inner_text().strip()
        comm_match = re.search(r'(\d+)%', comm_text)
        commission = int(comm_match.group(1)) if comm_match else 0

        sales_text = cells[6].inner_text().strip()
        try:
            sales = int(sales_text.replace(',', ''))
        except:
            sales = 0

        change_text = cells[7].inner_text().strip()
        trend_key = 'unknown'
        trend_name = '未知'
        trend_color = '#9ca3af'
        try:
            change_val = float(change_text.replace('%', '').replace('+', ''))
            if change_val > 10:
                trend_key = 'up'
                trend_name = '快速增长'
                trend_color = '#22c55e'
            elif change_val > 0:
                trend_key = 'stable'
                trend_name = '稳步增长'
                trend_color = '#eab308'
            elif change_val < -10:
                trend_key = 'down'
                trend_name = '下坡路'
                trend_color = '#ef4444'
            else:
                trend_key = 'stable'
                trend_name = '持平'
                trend_color = '#9ca3af'
        except:
            pass

        return {
            'rank': 0, 'name': name, 'price': price, 'store': store,
            'category': category, 'commission': commission, 'sales': sales,
            'trend': trend_name, 'trend_key': trend_key, 'trend_color': trend_color,
            'image_url': image_url, 'product_url': product_url, 'tiktok_url': tiktok_url,
        }
    except:
        return None


def main():
    print("=" * 70)
    print("FastMOSS 周榜数据采集")
    print("目标: 6周 x 900个商品 = 5400个商品")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()

        all_data = {}

        for week in WEEKS:
            week_file = OUTPUT_DIR / f'report_data_{week}.json'
            if week_file.exists():
                print(f"\n{week} 已存在，跳过")
                with open(week_file, 'r', encoding='utf-8') as f:
                    all_data[week] = json.load(f)
                continue

            print(f"\n{'='*60}")
            print(f"采集周次: {week}")
            print(f"{'='*60}")

            week_data = {}

            for cat in CATEGORIES:
                cat_name = cat['name']
                l2_cid = cat['l2_cid']
                print(f"\n  {cat_name}:")
                week_data[cat_name] = {}

                for ranking in RANKING_TYPES:
                    ranking_name = ranking['name']
                    path = ranking['path']
                    print(f"\n    {ranking_name}...")

                    products = []

                    for page_num in range(1, 11):
                        url = f"https://www.fastmoss.com/zh/e-commerce/{path}?region=TH&page={page_num}&l1_cid=24&l2_cid={l2_cid}&date_type=2&date_value={week}&pagesize=10"
                        page.goto(url, timeout=60000)
                        page.wait_for_timeout(2000)

                        rows = page.query_selector_all('tbody tr')
                        if not rows:
                            print(f"      第{page_num}页无数据")
                            break

                        for row in rows:
                            product = extract_product_data(row)
                            if product:
                                products.append(product)

                        print(f"      第{page_num}页: {len(rows)}行, 累计{len(products)}个")
                        time.sleep(2)

                    week_data[cat_name][ranking_name] = products[:100]
                    print(f"    完成: {len(products[:100])}个")
                    time.sleep(2)

            with open(OUTPUT_DIR / f'report_data_{week}.json', 'w', encoding='utf-8') as f:
                json.dump(week_data, f, ensure_ascii=False, indent=2)

            all_data[week] = week_data

        # 合并所有数据
        with open(OUTPUT_DIR / 'report_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        # 收集所有商品名
        all_names = []
        for week, week_data in all_data.items():
            for cat, rankings in week_data.items():
                for rank, products in rankings.items():
                    for p in products:
                        if p['name'] not in all_names:
                            all_names.append(p['name'])

        with open(OUTPUT_DIR / 'product_names.txt', 'w', encoding='utf-8') as f:
            for i, name in enumerate(all_names, 1):
                f.write(f"{i}|{name}\n")

        total = sum(len(p) for w in all_data.values() for cats in w.values() for p in cats.values())
        print(f"\n{'='*70}")
        print(f"采集完成! 总计: {total} 个商品, {len(all_names)} 个唯一商品名")


if __name__ == "__main__":
    main()