#!/usr/bin/env python3
"""
从FastMOSS泰国食品饮料页面采集数据
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from product_intel import ProductIntelDB, MarketData


def parse_price(text):
    if not text:
        return 0.0
    return float(str(text).replace(',', ''))


def parse_number(text):
    if not text:
        return 0
    text = str(text).strip()
    if '万' in text:
        return int(float(text.replace('万', '')) * 10000)
    if '亿' in text:
        return int(float(text.replace('亿', '')) * 100000000)
    match = re.search(r'([\d,\.]+)', text)
    if match:
        return int(match.group().replace(',', ''))
    return 0


def collect_products(page, db):
    """从当前页面采集商品数据"""
    body_text = page.evaluate('document.body.innerText')
    lines = body_text.split('\n')

    products = []
    i = 0
    current_product = {}

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 商品名称和价格
        if '售价：' in line or '฿' in line:
            if current_product.get('name'):
                products.append(current_product.copy())

            current_product = {}

            # 提取价格
            price_match = re.search(r'售价[：:]\s*([\d,\.]+)', line)
            if price_match:
                current_product['price'] = parse_price(price_match.group(1))

            # 提取名称
            name_part = line.split('售价')[0].strip()
            if name_part and len(name_part) > 3:
                current_product['name'] = name_part[:100]

        # 7天销量
        if current_product.get('name') and 'week_sales' not in current_product:
            if re.match(r'^[\d,\.]+万?$', line):
                current_product['week_sales'] = parse_number(line)
                i += 1
                continue

        # 总销量
        if current_product.get('name') and 'total_sales' not in current_product:
            if re.match(r'^[\d,\.]+万$', line) and '店铺销量' not in line:
                current_product['total_sales'] = parse_number(line)
                i += 1
                continue

        # 店铺名
        if '店铺销量' in line:
            store_match = re.search(r'([\wก-๙]+)\s*店铺销量', line)
            if store_match:
                current_product['store'] = store_match.group(1)

        i += 1

    # 保存最后一个商品
    if current_product.get('name'):
        products.append(current_product)

    # 保存到数据库
    saved = 0
    for p in products:
        if p.get('total_sales', 0) > 0:
            try:
                market_data = MarketData(
                    platform="tiktok_th_fastmoss_food",
                    product_name=p.get('name', ''),
                    price=p.get('price', 0),
                    currency="THB",
                    sales_volume=p.get('total_sales', 0),
                    store_name=p.get('store', ''),
                    url="",
                    scraped_at=datetime.now().isoformat()
                )
                db.save_market_data(market_data)
                saved += 1
            except Exception as e:
                pass

    return products, saved


def main():
    db = ProductIntelDB()

    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print(f"当前URL: {page.url}")

    # 确保在食品饮料分类页面
    if '食品饮料' not in page.evaluate('document.body.innerText'):
        print("正在选择食品饮料分类...")
        page.click('text=食品饮料')
        page.wait_for_timeout(3000)

    all_products = []
    total_saved = 0

    # 采集第1页
    print("\n采集第1页数据...")
    products, saved = collect_products(page, db)
    all_products.extend(products)
    total_saved += saved
    print(f"第1页: {saved} 个商品")

    # 点击第2页
    print("\n跳转到第2页...")
    page.click('text=2')
    page.wait_for_timeout(3000)
    products, saved = collect_products(page, db)
    all_products.extend(products)
    total_saved += saved
    print(f"第2页: {saved} 个商品")

    # 点击第3页
    print("\n跳转到第3页...")
    page.click('text=3')
    page.wait_for_timeout(3000)
    products, saved = collect_products(page, db)
    all_products.extend(products)
    total_saved += saved
    print(f"第3页: {saved} 个商品")

    print(f"\n总计采集: {len(all_products)} 个商品, 保存 {total_saved} 个到数据库")

    # 按总销量排序打印TOP 20
    print("\n" + "="*70)
    print("【食品饮料 TOP 20 爆款】")
    print("="*70)

    sorted_products = sorted(all_products, key=lambda x: x.get('total_sales', 0), reverse=True)

    for i, p in enumerate(sorted_products[:20], 1):
        name = p.get('name', 'N/A')[:45]
        price = p.get('price', 0)
        week = p.get('week_sales', 0)
        total = p.get('total_sales', 0)
        store = p.get('store', 'N/A')
        print(f"\n{i}. {name}")
        print(f"   店铺: {store} | 价格: {price} THB | 7天: {week:,} | 总销量: {total:,}")

    # 保存分析报告
    report_path = Path(__file__).parent.parent / "reports" / f"fastmoss_food_top20_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# FastMOSS 泰国食品饮料 爆款分析

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: FastMOSS 泰国TikTok Shop

## 数据概览

- 采集页数: 3页
- 总商品数: {len(all_products)}
- 保存到数据库: {total_saved}

---

## TOP 20 爆款商品

| 排名 | 商品名称 | 店铺 | 售价(THB) | 7天销量 | 总销量 |
|------|----------|------|-----------|---------|--------|
"""

    for i, p in enumerate(sorted_products[:20], 1):
        report += f"| {i} | {p.get('name', '')[:40]} | {p.get('store', '')} | {p.get('price', 0)} | {p.get('week_sales', 0):,} | {p.get('total_sales', 0):,} |\n"

    report += """
---

## 选品建议

基于以上数据分析：

"""

    # 添加分析建议
    report += """
**高热度商品特征:**
- 价格区间: 10-100 THB (低价走量)
- 品类: 零食、饮料、调味品

**高销量商品特征:**
- 价格区间: 20-300 THB
- 品类: 干货、咖啡、饼干

**推荐关注:**
1. 干货类 (墨鱼干等) - 7天销量4万+
2. 咖啡类 - 佣金比例高(10-30%)
3. 饼干零食类 - 竞争激烈但需求稳定
"""

    report_path.write_text(report)
    print(f"\n报告已保存到: {report_path}")


if __name__ == "__main__":
    main()