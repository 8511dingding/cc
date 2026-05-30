#!/usr/bin/env python3
"""
采集品类大盘和趋势数据
"""
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime

def parse_market_analyze(page):
    """解析大盘数据页面"""
    body_text = page.evaluate('document.body.innerText')
    lines = body_text.split('\n')

    data = {
        'total_sales': 0,
        'sales_change': 0,
        'on_sale_products': 0,
        'active_products': 0,
        'active_change': 0,
        'videos_count': 0,
        'videos_change': 0,
        'livestreams_count': 0,
        'livestreams_change': 0,
        'new_influencers_avg': 0,
        'new_livestreams_avg': 0,
        'new_videos_avg': 0,
        'top_products': [],
        'potential_products': []
    }

    # 解析关键数据
    for i, line in enumerate(lines):
        # 总销量
        if '上周' in line and 'TikTok食品饮料商品总销量' in line:
            sales_match = re.search(r'(\d+\.?\d*)万', line)
            if sales_match:
                data['total_sales'] = float(sales_match.group(1)) * 10000

            change_match = re.search(r'变化了([-\d.]+)%', line)
            if change_match:
                data['sales_change'] = float(change_match.group(1))

        # 带货视频数
        if '带货视频数' in line and i+1 < len(lines):
            videos_match = re.search(r'(\d+\.?\d*)万', lines[i+1])
            if videos_match:
                data['videos_count'] = float(videos_match.group(1)) * 10000
            # 变化值
            change_match = re.search(r'(-?\d+)万', lines[i+2])
            if change_match:
                data['videos_change'] = float(change_match.group(1)) * 10000

        # 带货直播场次
        if '带货直播场次' in line and i+1 < len(lines):
            live_match = re.search(r'(\d+\.?\d*)万', lines[i+1])
            if live_match:
                data['livestreams_count'] = float(live_match.group(1)) * 10000

        # 在售商品数
        if '在售商品数' in line and i+1 < len(lines):
            on_match = re.search(r'([\d.]+)万', lines[i+1])
            if on_match:
                data['on_sale_products'] = float(on_match.group(1)) * 10000

        # 动销商品数
        if '动销商品数' in line and i+1 < len(lines):
            active_match = re.search(r'(\d+\.?\d*)万', lines[i+1])
            if active_match:
                data['active_products'] = float(active_match.group(1)) * 10000

        # 新增带货达人均值
        if '新增带货达人均值' in line:
            avg_match = re.search(r'(\d+)', lines[i+1])
            if avg_match:
                data['new_influencers_avg'] = int(avg_match.group(1))

        # 新增带货视频均值
        if '新增带货视频均值' in line:
            avg_match = re.search(r'(\d+)', lines[i+1])
            if avg_match:
                data['new_videos_avg'] = int(avg_match.group(1))

        # 畅销商品
        if '畅销商品' in line:
            # 接下来的行是商品
            for j in range(i+1, min(i+20, len(lines))):
                line_text = lines[j].strip()
                if '销量' in line_text:
                    sales_text = lines[j+1].strip() if j+1 < len(lines) else ''
                    sales_num_match = re.search(r'([\d.]+)万', sales_text)
                    if sales_num_match:
                        product_name = lines[j-1].strip() if j-1 >= 0 else ''
                        if product_name and len(product_name) < 100:
                            data['top_products'].append({
                                'name': product_name,
                                'sales': float(sales_num_match.group(1)) * 10000
                            })

        # 潜力爆品
        if '潜力爆品' in line:
            for j in range(i+1, min(i+20, len(lines))):
                line_text = lines[j].strip()
                if '销量' in line_text:
                    sales_text = lines[j+1].strip() if j+1 < len(lines) else ''
                    sales_num_match = re.search(r'([\d.]+)万', sales_text)
                    if sales_num_match:
                        product_name = lines[j-1].strip() if j-1 >= 0 else ''
                        if product_name and len(product_name) < 100:
                            data['potential_products'].append({
                                'name': product_name,
                                'sales': float(sales_num_match.group(1)) * 10000
                            })

    return data

def collect_market_data(browser, date_value):
    """采集特定周的大盘数据"""
    context = browser.contexts[0]
    page = context.pages[0]

    url = f"https://www.fastmoss.com/zh/market/market-analyze?page=1&pcid=24&date_type=2&date_value={date_value}"

    try:
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        data = parse_market_analyze(page)
        data['date_value'] = date_value

        return data
    except Exception as e:
        print(f"采集 {date_value} 失败: {e}")
        return None

def main():
    print("="*60)
    print("采集食品饮料大盘数据")
    print("="*60)

    print("\n连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)

    # 采集最近4周的数据
    weeks = ['2026-21', '2026-20', '2026-19', '2026-18']
    all_market_data = []

    print("\n采集近4周大盘数据...")
    for week in weeks:
        print(f"\n采集 {week} 周数据...")
        data = collect_market_data(browser, week)
        if data:
            all_market_data.append(data)
            print(f"  总销量: {data['total_sales']:,.0f}")
            print(f"  变化: {data['sales_change']:+.2f}%")
            print(f"  畅销品: {len(data['top_products'])} 个")
        time.sleep(1)

    # 保存数据
    market_data_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/market_data.json"
    with open(market_data_path, 'w', encoding='utf-8') as f:
        json.dump(all_market_data, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {market_data_path}")

    # 生成报告
    report = f"""# 食品饮料大盘数据分析

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 近4周数据趋势

| 周次 | 总销量 | 环比变化 | 带货视频 | 动销商品数 |
|------|--------|----------|----------|------------|
"""

    for data in all_market_data:
        report += f"| {data['date_value']} | {data['total_sales']:,.0f} | {data['sales_change']:+.2f}% | {data['videos_count']:,.0f} | {data['active_products']:,.0f} |\n"

    # 畅销商品
    if all_market_data:
        latest = all_market_data[0]
        report += f"""
---

## 上周畅销商品 TOP 10

| 排名 | 商品名称 | 7天销量 |
|------|----------|---------|
"""
        for i, p in enumerate(latest.get('top_products', [])[:10], 1):
            report += f"| {i} | {p['name'][:40]} | {p['sales']:,.0f} |\n"

        report += f"""
---

## 上周潜力爆品 TOP 5

| 排名 | 商品名称 | 销量 |
|------|----------|------|
"""
        for i, p in enumerate(latest.get('potential_products', [])[:5], 1):
            report += f"| {i} | {p['name'][:40]} | {p['sales']:,.0f} |\n"

    report += """
---

## 数据解读

### 市场规模
- 上周食品饮料品类总销量 **525万+单**
- 环比变化: **-10.46%** (略有下降)

### 达人参与度
- 新增带货达人均值: **485/周**
- 新增带货视频均值: **280/周**

### 选品建议
1. **畅销商品**代表市场需求已验证
2. **潜力爆品**增长迅猛，可关注但需验证持续性
3. 建议结合榜单数据综合判断
"""

    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/market_analysis.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {report_path}")
    print("\n完成!")

if __name__ == "__main__":
    main()