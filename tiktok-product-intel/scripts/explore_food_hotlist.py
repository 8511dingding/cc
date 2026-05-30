#!/usr/bin/env python3
"""
深入探索FastMOSS泰国TikTok热推榜 - 食品饮料分类
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def parse_price(price_text):
    """从价格文本提取价格"""
    if not price_text:
        return 0.0
    # 匹配 ฿230.00 - 861.00 格式
    match = re.search(r'฿([\d,]+\.?\d*)', price_text)
    if match:
        return float(match.group(1).replace(',', ''))
    return 0.0

def parse_sales(sales_text):
    """解析销量"""
    if not sales_text:
        return 0
    sales_text = str(sales_text).replace(',', '')
    # 移除万
    if '万' in sales_text:
        match = re.search(r'([\d.]+)', sales_text)
        if match:
            return int(float(match.group(1)) * 10000)
    match = re.search(r'(\d+)', sales_text)
    if match:
        return int(match.group())
    return 0

def explore_food_hotlist():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print(f"当前URL: {page.url}")

    # 访问热推榜泰国站
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 点击食品饮料分类
    print("\n点击食品饮料分类...")
    page.click('text=食品饮料')
    page.wait_for_timeout(2000)

    # 切换到周榜
    print("切换到周榜...")
    page.click('text=周榜')
    page.wait_for_timeout(2000)

    print(f"当前URL: {page.url}")

    # 获取页面文本
    body_text = page.evaluate('document.body.innerText')

    # 提取所有商品数据（从纯文本解析）
    products = []

    # 使用正则提取商品块
    # 模式: 排名 + 商品名 + 售价 + 国家 + 店铺 + 分类 + 佣金 + 销量
    lines = body_text.split('\n')

    current_product = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 排名行 (单独的1,2,3...数字)
        rank_match = re.match(r'^(\d+)$', line)
        if rank_match and not current_product.get('rank'):
            # 检查下一行是否是商品
            continue

        # 商品名称和价格行
        if '售价：' in line or '฿' in line:
            if current_product.get('name'):
                products.append(current_product)
            current_product = {}

            # 提取价格
            price = parse_price(line)
            current_product['price'] = price

            # 提取商品名称 (售价之前的内容)
            name_part = line.split('售价')[0].strip()
            if name_part:
                current_product['name'] = name_part[:100]

            # 提取价格范围
            price_range_match = re.search(r'฿([\d,]+\.?\d*)\s*-\s*฿([\d,]+\.?\d*)', line)
            if price_range_match:
                current_product['price_min'] = float(price_range_match.group(1).replace(',', ''))
                current_product['price_max'] = float(price_range_match.group(2).replace(',', ''))
                current_product['price'] = (current_product['price_min'] + current_product['price_max']) / 2

        # 国家/地区 (泰国)
        if current_product.get('name') and not current_product.get('country'):
            if '泰国' in line and len(line) < 10:
                current_product['country'] = '泰国'

        # 店铺销量行 (如 "店铺销量：245.61万")
        store_match = re.search(r'店铺销量[:：]\s*([\d.]+)万', line)
        if store_match and current_product.get('name'):
            current_product['store_sales'] = int(float(store_match.group(1)) * 10000)

        # 店铺名称 (在店铺销量之后)
        if current_product.get('store_sales') and not current_product.get('store'):
            if '泰国' not in line and '售价' not in line and '店铺销量' not in line and len(line) < 50:
                current_product['store'] = line[:50]

        # 商品分类
        categories = ['咖啡', '碳酸饮料', '干粮零食', '代餐与蛋白质饮料', '乳代饮品', '灭菌奶', '不含酒精的饮料', '健身保健食品', '调味品', '茶']
        for cat in categories:
            if cat in line and current_product.get('name') and not current_product.get('category'):
                current_product['category'] = cat

        # 佣金比例 (如 "15%")
        commission_match = re.search(r'(\d+)%', line)
        if commission_match and current_product.get('name') and not current_product.get('commission'):
            current_product['commission'] = int(commission_match.group(1))

        # 销量数字 (大的数字可能是销量)
        sales_match = re.match(r'^([\d,]+)$', line.replace(',', ''))
        if sales_match and current_product.get('name') and 'store' in current_product and not current_product.get('sales'):
            num = int(sales_match.group(1).replace(',', ''))
            if num > 100:  # 销量通常大于100
                current_product['sales'] = num

    # 保存最后一个
    if current_product.get('name'):
        products.append(current_product)

    return products

def analyze_products(products):
    """分析产品特征"""
    print(f"\n共提取 {len(products)} 个商品")

    # 按销量排序
    sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

    print("\n" + "="*80)
    print("【FastMOSS泰国TikTok热推榜 食品饮料 TOP 20】")
    print("="*80)

    for i, p in enumerate(sorted_products[:20], 1):
        name = p.get('name', 'N/A')[:50]
        price = p.get('price', 0)
        store = p.get('store', 'N/A')
        category = p.get('category', 'N/A')
        commission = p.get('commission', 0)
        sales = p.get('sales', 0)

        print(f"\n{i:2d}. {name}")
        print(f"     价格: {price:.0f} THB | 店铺: {store} | 分类: {category}")
        print(f"     佣金: {commission}% | 7天销量: {sales:,}")

    # 分析特征
    print("\n\n" + "="*80)
    print("【食品饮料爆款特征分析】")
    print("="*80)

    categories = {}
    price_ranges = {'0-200': 0, '200-500': 0, '500-1000': 0, '1000+': 0}
    commission_rates = {}

    for p in products:
        cat = p.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1

        price = p.get('price', 0)
        if price < 200:
            price_ranges['0-200'] += 1
        elif price < 500:
            price_ranges['200-500'] += 1
        elif price < 1000:
            price_ranges['500-1000'] += 1
        else:
            price_ranges['1000+'] += 1

        comm = p.get('commission', 0)
        if comm > 0:
            commission_rates[comm] = commission_rates.get(comm, 0) + 1

    print("\n分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}个 ({count/len(products)*100:.1f}%)")

    print("\n价格区间分布:")
    for range_name, count in price_ranges.items():
        print(f"  {range_name} THB: {count}个 ({count/len(products)*100:.1f}%)")

    print("\n佣金比例分布:")
    for comm, count in sorted(commission_rates.items()):
        print(f"  {comm}%: {count}个")

    # 选品建议
    print("\n\n" + "="*80)
    print("【选品建议】")
    print("="*80)

    high_sales_products = [p for p in products if p.get('sales', 0) > 1000]
    high_commission_products = [p for p in products if p.get('commission', 0) >= 10]

    print(f"\n高销量商品 (>1000): {len(high_sales_products)}个")
    for p in sorted(high_sales_products, key=lambda x: -x.get('sales', 0))[:5]:
        print(f"  - {p.get('name', '')[:40]} | 销量:{p.get('sales', 0):,} | 佣金:{p.get('commission', 0)}%")

    print(f"\n高佣金商品 (≥10%): {len(high_commission_products)}个")
    for p in sorted(high_commission_products, key=lambda x: -x.get('commission', 0))[:5]:
        print(f"  - {p.get('name', '')[:40]} | 佣金:{p.get('commission', 0)}% | 销量:{p.get('sales', 0):,}")

    return products

if __name__ == "__main__":
    products = explore_food_hotlist()

    if products:
        analyze_products(products)

    print("\n\n分析完成!")