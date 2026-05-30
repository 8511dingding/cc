#!/usr/bin/env python3
"""
深入探索FastMOSS泰国TikTok热推榜
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime

def explore_hotlist():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print(f"当前URL: {page.url}")

    # 访问热推榜泰国站
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    print(f"当前URL: {page.url}")

    # 等待页面加载
    page.wait_for_timeout(2000)

    # 打印页面文本概览
    body_text = page.evaluate('document.body.innerText')
    print("\n页面文本预览（前2000字符）:")
    print(body_text[:2000])

    # 查找所有分类筛选器
    print("\n\n查找分类筛选器...")
    # 尝试不同的选择器
    filters = page.query_selector_all('.filter-item, .category-item, [class*="filter"], [class*="category"]')

    for f in filters:
        try:
            text = f.inner_text().strip()
            if text:
                print(f"  筛选器: {text}")
        except:
            pass

    # 尝试点击食品饮料分类（使用更精确的选择器）
    print("\n\n尝试点击食品饮料分类...")
    food_selectors = [
        'text=食品饮料',
        '[class*="食品"]',
        '.category >> text=食品',
        '[data-category*="食品"]'
    ]

    for selector in food_selectors:
        try:
            elements = page.query_selector_all(selector)
            print(f"  选择器 '{selector}' 找到 {len(elements)} 个元素")
            if len(elements) == 1:
                print(f"  点击唯一元素: {elements[0].inner_text()}")
                elements[0].click()
                page.wait_for_timeout(2000)
                break
            elif len(elements) > 1:
                # 点击第一个
                print(f"  点击第一个匹配的: {elements[0].inner_text()}")
                elements[0].click()
                page.wait_for_timeout(2000)
                break
        except Exception as e:
            print(f"  选择器 '{selector}' 失败: {e}")

    # 打印当前页面内容
    print("\n点击后的页面内容（前1500字符）:")
    body_text = page.evaluate('document.body.innerText')
    print(body_text[:1500])

    # 提取表格数据
    print("\n\n提取热推榜表格数据...")
    rows = page.query_selector_all('tbody tr, .el-table__row, [class*="row"]')

    products = []
    for row in rows[:50]:
        try:
            cells = row.query_selector_all('td, [class*="cell"]')
            if len(cells) >= 6:
                rank = cells[0].inner_text().strip()
                name = cells[1].inner_text().strip()[:60]
                store = cells[3].inner_text().strip() if len(cells) > 3 else ""
                category = cells[4].inner_text().strip() if len(cells) > 4 else ""
                commission = cells[5].inner_text().strip() if len(cells) > 5 else ""
                sales = cells[6].inner_text().strip() if len(cells) > 6 else ""

                if rank.isdigit() and int(rank) <= 100:
                    products.append({
                        'rank': int(rank),
                        'name': name,
                        'store': store,
                        'category': category,
                        'commission': commission,
                        'sales': sales
                    })
        except Exception as e:
            continue

    print(f"\n找到 {len(products)} 个商品")

    # 打印TOP 20
    print("\n" + "="*80)
    print("【FastMOSS泰国TikTok热推榜 TOP 20】")
    print("="*80)

    for p in products[:20]:
        print(f"\n{p['rank']:2d}. {p['name']}")
        print(f"     店铺: {p['store']} | 分类: {p['category']} | 佣金: {p['commission']} | 销量: {p['sales']}")

    return products

def analyze_product_patterns(products):
    """分析爆款产品特征"""
    print("\n\n" + "="*80)
    print("【爆款产品特征分析】")
    print("="*80)

    categories = {}
    stores = {}
    name_keywords = {}

    for p in products:
        cat = p.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1

        store = p.get('store', '未知')
        stores[store] = stores.get(store, 0) + 1

    print("\n分类分布:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}个")

    print("\n热门店铺:")
    for store, count in sorted(stores.items(), key=lambda x: -x[1])[:10]:
        print(f"  {store}: {count}个")

    return categories, stores

if __name__ == "__main__":
    products = explore_hotlist()

    if products:
        categories, stores = analyze_product_patterns(products)

    print("\n\n探索完成!")