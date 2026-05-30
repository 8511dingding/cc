#!/usr/bin/env python3
"""
完整采集市场数据 - 包括大盘、品类分类
"""
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime

def parse_market_analyze_page(page):
    """解析大盘数据页面"""
    body_text = page.evaluate('document.body.innerText')

    data = {
        'total_sales': 0,
        'sales_change': 0,
        'on_sale_products': 0,
        'active_products': 0,
        'videos_count': 0,
        'livestreams_count': 0,
        'new_influencers_avg': 0,
        'new_videos_avg': 0,
        'top_products': [],
        'potential_products': [],
        'raw_text': body_text[:5000]
    }

    # 提取数值
    # 总销量 525万+
    sales_match = re.search(r'上周.*?商品总销量(\d+\.?\d*)万', body_text)
    if sales_match:
        data['total_sales'] = float(sales_match.group(1)) * 10000

    # 变化 -10.46%
    change_match = re.search(r'变化了([-\d.]+)%', body_text)
    if change_match:
        data['sales_change'] = float(change_match.group(1))

    # 带货视频数 24万
    videos_match = re.search(r'带货视频数\s+(\d+\.?\d*)万', body_text)
    if videos_match:
        data['videos_count'] = float(videos_match.group(1)) * 10000

    # 在售商品数 90万
    on_sale_match = re.search(r'在售商品数\s+(\d+\.?\d*)万', body_text)
    if on_sale_match:
        data['on_sale_products'] = float(on_sale_match.group(1)) * 10000

    # 动销商品数 10万
    active_match = re.search(r'动销商品数\s+(\d+\.?\d*)万', body_text)
    if active_match:
        data['active_products'] = float(active_match.group(1)) * 10000

    # 新增带货达人均值 485/周
    influencer_match = re.search(r'新增带货达人均值\s+(\d+)\s*/\s*周', body_text)
    if influencer_match:
        data['new_influencers_avg'] = int(influencer_match.group(1))

    # 新增带货视频均值 280/周
    video_avg_match = re.search(r'新增带货视频均值\s+(\d+)\s*/\s*周', body_text)
    if video_avg_match:
        data['new_videos_avg'] = int(video_avg_match.group(1))

    return data

def collect_weekly_data(browser, date_value):
    """采集特定周的大盘数据"""
    context = browser.contexts[0]
    page = context.pages[0]

    url = f"https://www.fastmoss.com/zh/market/market-analyze?page=1&pcid=24&date_type=2&date_value={date_value}"

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        data = parse_market_analyze_page(page)
        data['date_value'] = date_value
        return data
    except Exception as e:
        print(f"采集 {date_value} 失败: {e}")
        return None

def collect_category_data(browser):
    """采集品类分类数据"""
    context = browser.contexts[0]
    page = context.pages[0]

    url = "https://www.fastmoss.com/zh/market/market-category?page=1&l1_cid=24"

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        # 获取页面内容
        body_text = page.evaluate('document.body.innerText')

        # 查找价格带分布等数据
        data = {
            'date_range': '',
            'categories': []
        }

        # 提取日期范围
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}\s*~\s*\d{4}-\d{2}-\d{2})', body_text)
        if date_match:
            data['date_range'] = date_match.group(1)

        # 提取子分类数据
        # 寻找 "美妆个护", "女装与女士内衣" 等分类
        category_pattern = r'(美妆个护|女装与女士内衣|保健|时尚配件|运动与户外|手机与数码|居家日用|食品饮料)[^\d]*(\d+\.?\d*万)'

        # 查找市场规模数据
        market_scale_match = re.search(r'市场规模\s+([\d.]+万)', body_text)
        if market_scale_match:
            data['market_scale'] = market_scale_match.group(1)

        return data
    except Exception as e:
        print(f"采集品类数据失败: {e}")
        return None

def main():
    print("="*60)
    print("采集食品饮料完整市场数据")
    print("="*60)

    print("\n连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)

    # 1. 采集近4周大盘数据
    print("\n1. 采集近4周大盘数据...")
    weeks = ['2026-21', '2026-20', '2026-19', '2026-18']
    all_market_data = []

    for week in weeks:
        print(f"\n  采集 {week} 周数据...")
        data = collect_weekly_data(browser, week)
        if data:
            all_market_data.append(data)
            print(f"    总销量: {data['total_sales']:,.0f}, 变化: {data['sales_change']:+.2f}%")
        time.sleep(0.5)

    # 2. 采集品类分类数据
    print("\n2. 采集品类分类数据...")
    category_data = collect_category_data(browser)
    print(f"    品类数据: {json.dumps(category_data, ensure_ascii=False)[:200]}")

    # 3. 保存综合数据
    all_data = {
        'weekly_data': all_market_data,
        'category_data': category_data,
        '采集时间': datetime.now().isoformat()
    }

    full_data_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/full_market_data.json"
    with open(full_data_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {full_data_path}")

    # 打印摘要
    if all_market_data:
        print("\n近4周销量趋势:")
        for data in all_market_data:
            print(f"  {data['date_value']}: {data['total_sales']:,.0f} ({data['sales_change']:+.2f}%)")

    print("\n完成!")

if __name__ == "__main__":
    main()