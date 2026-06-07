#!/usr/bin/env python3
"""
采集FastMOSS商品数据 - 完整版
9个榜单 x100个商品
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

def login_and_collect(page, context):
    """登录并采集数据"""
    print("=" * 70)
    print("Step 1: 登录 FastMOSS")
    print("=" * 70)

    # 清除旧cookies，确保持续新鲜登录
    if COOKIES_FILE.exists():
        COOKIES_FILE.unlink()

    # 访问登录页面
    print("访问登录页面...")
    page.goto("https://www.fastmoss.com/zh/login", timeout=60000)
    page.wait_for_timeout(3000)

    # 截图看登录页
    page.screenshot(path='/tmp/login_debug.png')

    # 1. 先尝试点击"邮箱登录"标签切换到邮箱模式
    print("查找登录表单...")
    tabs = page.query_selector_all('div[role="tab"], button, div')
    for tab in tabs:
        text = tab.inner_text()
        if '邮箱' in text and tab.is_visible():
            print(f"  点击邮箱登录标签: {text}")
            tab.click()
            page.wait_for_timeout(1000)
            break

    # 2. 找到正确的输入框
    all_inputs = page.query_selector_all('input')
    email_input = None
    password_input = None

    for i, inp in enumerate(all_inputs):
        if not inp.is_visible():
            continue
        placeholder = inp.get_attribute('placeholder') or ''
        inp_type = inp.get_attribute('type') or 'text'

        if '手机' in placeholder and inp_type == 'text':
            email_input = inp
            print(f"  找到手机号输入框: index={i}, placeholder={placeholder}")
        elif inp_type == 'password' and '密码' in placeholder:
            password_input = inp
            print(f"  找到密码输入框: index={i}")
        elif i == 16 and inp_type == 'text' and not email_input:
            email_input = inp
            print(f"  使用index 16作为手机号输入框")
        elif i == 17 and inp_type == 'password' and not password_input:
            password_input = inp
            print(f"  使用index 17作为密码输入框")

    if not email_input or not password_input:
        print("ERROR: 无法找到登录输入框!")
        page.screenshot(path='/tmp/login_error.png')
        return False

    # 填写登录信息
    print("填写用户名...")
    email_input.fill(FASTMOSS_EMAIL)
    page.wait_for_timeout(500)

    print("填写密码...")
    password_input.fill(FASTMOSS_PASSWORD)
    page.wait_for_timeout(500)

    # 找提交按钮
    submit_btn = None
    btn_selectors = ['button[type="submit"]', 'button:has-text("登录")', 'button:has-text("登入")']
    for sel in btn_selectors:
        btns = page.query_selector_all(sel)
        for btn in btns:
            if btn.is_visible():
                submit_btn = btn
                print(f"  找到提交按钮: {sel}")
                break
        if submit_btn:
            break

    if not submit_btn:
        print("ERROR: 无法找到提交按钮!")
        return False

    # 点击登录
    print("点击登录...")
    submit_btn.click()
    page.wait_for_timeout(8000)  # 等待登录完成

    # 检查登录是否成功
    current_url = page.url
    print(f"登录后URL: {current_url}")

    if "login" in current_url:
        print("WARNING: 可能登录失败，仍然在登录页面")

    # 保存cookies
    cookies = context.cookies()
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)
    print(f"已保存 {len(cookies)} 个cookies")

    return True


def extract_product_data(row):
    """从行元素提取商品数据"""
    try:
        cells = row.query_selector_all('td')
        if len(cells) < 12:
            return None

        if not cells[1].inner_text().strip():
            return None

        row_html = row.inner_html()

        # 图片URL
        img_match = re.search(r'<img[^>]+src="([^"]+)"', row_html)
        image_url = img_match.group(1) if img_match else ''

        # 产品链接
        links = row.query_selector_all('a')
        product_url = ''
        for link in links:
            href = link.get_attribute('href') or ''
            if 'product' in href or 'item' in href:
                product_url = href if href.startswith('http') else 'https://www.fastmoss.com' + href
                break

        # 商品名称和价格
        name_cell_text = cells[1].inner_text()
        name = name_cell_text.split('售价')[0].strip()[:150]
        price_match = re.search(r'฿([\d,]+\.?\d*)', name_cell_text)
        price = float(price_match.group(1).replace(',', '')) if price_match else 0

        # 店铺
        store_cell = cells[3].inner_text()
        store_match = re.search(r'^(.+?)\|店铺销量', store_cell)
        store = store_match.group(1).strip() if store_match else store_cell.strip()

        # 分类
        category = cells[4].inner_text().strip()

        # 佣金
        comm_text = cells[5].inner_text().strip()
        comm_match = re.search(r'(\d+)%', comm_text)
        commission = int(comm_match.group(1)) if comm_match else 0

        # 7天销量
        sales_text = cells[6].inner_text().strip()
        try:
            sales = int(sales_text.replace(',', ''))
        except:
            sales = 0

        # 销量环比 - 判断趋势
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
            'image_url': image_url, 'product_url': product_url, 'tiktok_url': '',
        }
    except Exception as e:
        return None


def collect_ranking(page, category_name, l2_cid, ranking_name, path):
    """采集单个榜单 - 采集前100个商品"""
    products = []
    print(f"\n  采集 {ranking_name}-{category_name}...")

    # 每页10个，需要访问10页
    for page_num in range(1, 11):
        url = f"https://www.fastmoss.com/zh/e-commerce/{path}?region=TH&page={page_num}&l1_cid=24&l2_cid={l2_cid}"
        page.goto(url, timeout=60000)
        page.wait_for_timeout(2000)

        rows = page.query_selector_all('tbody tr')
        if not rows:
            break

        for row in rows:
            product = extract_product_data(row)
            if product:
                products.append(product)

        print(f"    第{page_num}页: {len(rows)}行, 累计{len(products)}个")

        # 检查是否到达100个
        if len(products) >= 100:
            products = products[:100]
            break

        # 检查下一页按钮
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
    print("FastMOSS 商品数据采集 - 完整版")
    print("目标: 9个榜单 x 100个商品 = 900个商品")
    print("=" * 70)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, args=['--remote-debugging-port=9222'])
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()

    # Step 1: 登录
    if not login_and_collect(page, context):
        print("登录失败，退出")
        browser.close()
        return

    # Step 2: 采集数据
    print("\n" + "=" * 70)
    print("Step 2: 采集商品数据")
    print("=" * 70)

    all_data = {}

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

    # Step 3: 保存数据
    print("\n" + "=" * 70)
    print("Step 3: 保存数据")
    print("=" * 70)

    # 保存报告数据
    output_file = OUTPUT_DIR / "report_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到: {output_file}")

    # 统计
    total = sum(len(products) for cats in all_data.values() for products in cats.values())
    with_images = sum(1 for cats in all_data.values() for products in cats.values() for p in products if p.get('image_url'))
    with_links = sum(1 for cats in all_data.values() for products in cats.values() for p in products if p.get('product_url'))

    print(f"\n总计: {total} 个商品")
    print(f"有图片URL: {with_images}")
    print(f"有产品链接: {with_links}")

    # 保存商品名列表用于翻译
    all_names = []
    name_to_product = {}
    for cat_name, rankings in all_data.items():
        for rank_name, products in rankings.items():
            for p in products:
                name = p.get('name', '')
                if name and name not in name_to_product:
                    all_names.append(name)
                    name_to_product[name] = p

    names_file = OUTPUT_DIR / "product_names.txt"
    with open(names_file, 'w', encoding='utf-8') as f:
        for i, name in enumerate(all_names, 1):
            f.write(f"{i}|{name}\n")
    print(f"商品名列表已保存到: {names_file}")

    print("\n" + "=" * 70)
    print("采集完成!")
    print(f"请访问 http://192.168.31.18/web_report.html 查看报告")
    print("浏览器将保持打开状态")
    print("=" * 70)

    # 保持浏览器打开
    input("按回车键关闭浏览器...")
    browser.close()
    playwright.stop()


if __name__ == "__main__":
    main()
