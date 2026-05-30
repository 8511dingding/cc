#!/usr/bin/env python3
"""
探索FastMOSS页面结构
"""
from playwright.sync_api import sync_playwright
import time
import re

def explore_category_market():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print("\n" + "="*60)
    print("1. 探索品类大盘页面")
    print("="*60)

    page.goto("https://www.fastmoss.com/zh/market/market-category?page=1&l1_cid=24", timeout=60000)
    page.wait_for_timeout(3000)

    print(f"URL: {page.url}")

    # 截图
    page.screenshot(path='/Users/jianing/Ning\'s Git/tiktok-product-intel/scripts/cat_market.png', full_page=False)
    print("已截图: cat_market.png")

    # 获取页面文本
    body_text = page.evaluate('document.body.innerText')
    lines = body_text.split('\n')

    print("\n页面内容预览（前100行）:")
    for i, line in enumerate(lines[:100]):
        if line.strip():
            print(f"  {i}: {line[:80]}")

    # 查找表格数据
    rows = page.query_selector_all('tbody tr, .el-table__row')
    print(f"\n找到 {len(rows)} 行表格数据")

    if rows:
        print("\n第一行数据:")
        cells = rows[0].query_selector_all('td, [class*="cell"]')
        for j, cell in enumerate(cells[:10]):
            print(f"  列{j}: {cell.inner_text()[:50]}")

    print("\n" + "="*60)
    print("2. 探索食品饮料大盘数据页面")
    print("="*60)

    page.goto("https://www.fastmoss.com/zh/market/market-analyze?page=1&pcid=24&date_type=2&date_value=2026-21", timeout=60000)
    page.wait_for_timeout(3000)

    print(f"URL: {page.url}")

    # 截图
    page.screenshot(path='/Users/jianing/Ning\'s Git/tiktok-product-intel/scripts/market_analyze.png', full_page=False)
    print("已截图: market_analyze.png")

    # 获取页面文本
    body_text = page.evaluate('document.body.innerText')
    lines = body_text.split('\n')

    print("\n页面内容预览（前100行）:")
    for i, line in enumerate(lines[:100]):
        if line.strip():
            print(f"  {i}: {line[:80]}")

    # 查找数据图表
    print("\n查找图表元素...")
    charts = page.query_selector_all('canvas, svg, [class*="chart"]')
    print(f"找到 {len(charts)} 个图表元素")

    print("\n完成探索!")

if __name__ == "__main__":
    explore_category_market()