#!/usr/bin/env python3
"""
采集FastMOSS商品数据、图片URL和产品链接
"""

import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

# 配置
FASTMOSS_EMAIL = "16293163036"
FASTMOSS_PASSWORD = "aa661188"
PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_DIR / "orbstack-www" / "ning_mac" / "FastMOSS-Report"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PRIVATE_DIR = PROJECT_DIR / "data" / "private"
PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
COOKIES_FILE = PRIVATE_DIR / "fastmoss_cookies.json"
IMAGES_DIR = OUTPUT_DIR / "images"
IMAGES_DIR.mkdir(exist_ok=True)

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

def save_cookies(context):
    """保存cookies到文件"""
    cookies = context.cookies()
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)
    print(f"已保存 {len(cookies)} 个cookies到文件")

def load_cookies(context):
    """从文件加载cookies"""
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print(f"已加载 {len(cookies)} 个cookies")
        return True
    return False

def login_fastmoss(page, context):
    """登录FastMOSS，保存cookies"""
    print("访问FastMOSS...")
    page.goto("https://www.fastmoss.com/zh", timeout=60000)
    page.wait_for_timeout(2000)

    #尝试加载已保存的cookies
    if COOKIES_FILE.exists():
        load_cookies(context)
        page.goto("https://www.fastmoss.com/zh/e-commerce/saleslist?region=TH&page=1&l1_cid=24&l2_cid=915336", timeout=60000)
        page.wait_for_timeout(2000)
        if "login" not in page.url:
            print("使用cookies登录成功!")
            return True

    # 检查登录状态
    current_url = page.url
    if "login" in current_url or page.inner_text('body').find('登录') > -1:
        print("需要登录...")
        # 使用索引找到输入框
        inputs = page.query_selector_all('input')
        for inp in inputs:
            if inp.get_attribute('type') == 'text' and inp.is_visible():
                inp.fill(FASTMOSS_EMAIL)
                page.wait_for_timeout(500)
                break

        # 找到密码框
        password_inputs = page.query_selector_all('input[type="password"]')
        for inp in password_inputs:
            if inp.is_visible():
                inp.fill(FASTMOSS_PASSWORD)
                page.wait_for_timeout(500)
                break

        # 点击提交
        buttons = page.query_selector_all('button[type="submit"]')
        for btn in buttons:
            if btn.is_visible():
                btn.click()
                page.wait_for_timeout(5000)
                break

    # 保存cookies
    save_cookies(context)
    print(f"当前URL: {page.url}")
    return "dashboard" in page.url or "e-commerce" in page.url

def extract_product_data(row, page):
    """从行元素提取商品完整数据"""
    try:
        cells = row.query_selector_all('td')
        if len(cells) < 12:
            return None

        # 检查是否为空行（第一行是占位符）
        first_cell_text = cells[0].inner_text().strip()
        if not first_cell_text and cells[1].inner_text().strip() == '':
            return None

        # 获取行HTML来分析结构
        row_html = row.inner_html()

        # 提取图片URL
        img_match = re.search(r'<img[^>]+src="([^"]+)"', row_html)
        image_url = img_match.group(1) if img_match else ''

        # 提取产品链接
        links = row.query_selector_all('a')
        product_url = ''
        tiktok_url = ''
        for link in links:
            href = link.get_attribute('href') or ''
            if 'product' in href or 'item' in href:
                if href.startswith('http'):
                    product_url = href
                else:
                    product_url = 'https://www.fastmoss.com' + href
                break

        # td1: 商品名称 + 售价
        name_cell_text = cells[1].inner_text()
        name = name_cell_text.split('售价')[0].strip()[:150]

        # 价格 - 从售价提取
        price_match = re.search(r'฿([\d,]+\.?\d*)', name_cell_text)
        price = float(price_match.group(1).replace(',', '')) if price_match else 0

        # td2: 国家
        country = cells[2].inner_text().strip()

        # td3: 店铺名 + 店铺销量
        store_cell = cells[3].inner_text()
        store_match = re.search(r'^(.+?)\|店铺销量', store_cell)
        store = store_match.group(1).strip() if store_match else store_cell.strip()

        # td4: 分类
        category = cells[4].inner_text().strip()

        # td5: 佣金比例
        comm_text = cells[5].inner_text().strip()
        comm_match = re.search(r'(\d+)%', comm_text)
        commission = int(comm_match.group(1)) if comm_match else 0

        # td6: 7天销量
        sales_text = cells[6].inner_text().strip()
        try:
            sales = int(sales_text.replace(',', ''))
        except:
            sales = 0

        # td7: 销量环比
        change_text = cells[7].inner_text().strip()

        # 趋势判断 - 根据销量环比
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
            'rank': 0,
            'name': name,
            'price': price,
            'store': store,
            'category': category,
            'commission': commission,
            'sales': sales,
            'trend': trend_name,
            'trend_key': trend_key,
            'trend_color': trend_color,
            'image_url': image_url,
            'product_url': product_url,
            'tiktok_url': tiktok_url,
        }
    except Exception as e:
        print(f"提取数据错误: {e}")
        return None

def collect_ranking(page, category_name, l2_cid, ranking_name, path):
    """采集单个榜单"""
    products = []

    print(f"\n  采集 {ranking_name}-{category_name}...")
    page.goto(f"https://www.fastmoss.com/zh/e-commerce/{path}?region=TH&page=1&l1_cid=24&l2_cid={l2_cid}", timeout=60000)
    page.wait_for_timeout(3000)

    # 采集多页
    for page_num in range(1, 11):
        if page_num > 1:
            page.goto(f"https://www.fastmoss.com/zh/e-commerce/{path}?region=TH&page={page_num}&l1_cid=24&l2_cid={l2_cid}", timeout=60000)
            page.wait_for_timeout(2000)

        rows = page.query_selector_all('tbody tr')
        if not rows:
            break

        print(f"    第{page_num}页: {len(rows)}行")
        for row in rows:
            product = extract_product_data(row, page)
            if product:
                products.append(product)

        # 检查下一页
        try:
            next_btn = page.query_selector('button:has-text("下一页")')
            if not next_btn or next_btn.is_disabled():
                break
        except:
            break

    print(f"    共 {len(products)} 个商品")
    return products

def main():
    print("=" * 70)
    print("FastMOSS 商品数据采集")
    print("=" * 70)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, args=['--remote-debugging-port=9222'])
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # 登录（不要关闭浏览器）
    login_fastmoss(page, context)

    all_data = {}

    # 采集
    for cat in CATEGORIES:
        cat_name = cat['name']
        l2_cid = cat['l2_cid']
        print(f"\n{'='*50}")
        print(f"采集分类: {cat_name}")
        print(f"{'='*50}")

        all_data[cat_name] = {}

        for ranking in RANKING_TYPES:
            ranking_name = ranking['name']
            path = ranking['path']

            products = collect_ranking(page, cat_name, l2_cid, ranking_name, path)
            all_data[cat_name][ranking_name] = products

            page.wait_for_timeout(1500)

    # 保存
    output_file = OUTPUT_DIR / "report_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到: {output_file}")

    # 统计
    total = sum(len(products) for cats in all_data.values() for products in cats.values())
    with_images = sum(1 for cats in all_data.values() for products in cats.values() for p in products if p.get('image_url'))
    with_links = sum(1 for cats in all_data.values() for products in cats.values() for p in products if p.get('product_url'))

    print(f"总计: {total} 个商品")
    print(f"有图片URL: {with_images}")
    print(f"有产品链接: {with_links}")

    # 保存商品名列表用于翻译
    all_names = []
    for cat_name, rankings in all_data.items():
        for rank_name, products in rankings.items():
            for p in products:
                if p['name'] not in all_names:
                    all_names.append(p['name'])

    names_file = OUTPUT_DIR / "product_names.txt"
    with open(names_file, 'w', encoding='utf-8') as f:
        for i, name in enumerate(all_names, 1):
            f.write(f"{i}|{name}\n")
    print(f"商品名列表已保存到: {names_file}")

    # 保存cookies供下次使用
    save_cookies(context)

    print("\n采集完成!浏览器保持打开状态。")
    # 不要关闭浏览器，让用户可以继续操作
    # browser.close()
    # playwright.stop()

if __name__ == "__main__":
    main()
