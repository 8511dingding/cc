#!/usr/bin/env python3
"""
发现即食食品各子分类的正确ID
"""
from playwright.sync_api import sync_playwright
import json

def discover_category_ids():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 1. 选择食品饮料分类
    print("\n1. 选择食品饮料分类...")
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

    # 2. 点击商品分类标签展开级联菜单
    print("\n2. 展开级联菜单...")
    page.evaluate("""
        () => {
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.innerText === '商品分类：食品饮料') {
                    if (el.click) el.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(1500)

    # 3. 获取所有级联菜单项
    print("\n3. 获取级联菜单项...")
    menu_items = page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            const result = [];
            items.forEach((item, index) => {
                const rect = item.getBoundingClientRect();
                result.push({
                    index: index,
                    text: item.innerText,
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2)
                });
            });
            return JSON.stringify(result);
        }
    """)

    menu_items = json.loads(menu_items)
    print(f"  找到 {len(menu_items)} 个菜单项")

    for i, item in enumerate(menu_items):
        print(f"    {i}: {item['text']} at ({item['x']}, {item['y']})")

    # 4. 点击即食食品展开第二层
    print("\n4. 点击即食食品展开第二层...")
    for item in menu_items:
        if item['text'] == '即食食品':
            page.mouse.click(item['x'], item['y'])
            page.wait_for_timeout(2000)
            break

    # 5. 获取第二层菜单项
    print("\n5. 获取第二层级联菜单项...")
    menu_items_l2 = page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            const result = [];
            items.forEach((item, index) => {
                const rect = item.getBoundingClientRect();
                result.push({
                    index: index,
                    text: item.innerText,
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2)
                });
            });
            return JSON.stringify(result);
        }
    """)

    menu_items_l2 = json.loads(menu_items_l2)
    print(f"  找到 {len(menu_items_l2)} 个第二层菜单项")

    # 过滤出y坐标大于500的（第二层）
    l2_items = [item for item in menu_items_l2 if item['y'] > 500]
    print(f"  第二层子分类: {len(l2_items)} 个")

    for i, item in enumerate(l2_items):
        print(f"    {i}: {item['text']} at ({item['x']}, {item['y']})")

    # 6. 逐一获取每个子分类的l2_cid
    print("\n6. 获取各子分类的ID...")

    category_ids = {}

    for item in l2_items:
        name = item['text']
        x, y = item['x'], item['y']

        # 点击该子分类
        page.mouse.click(x, y)
        page.wait_for_timeout(3000)

        # 获取URL中的l2_cid
        url = page.url
        print(f"  {name}: {url}")

        if 'l2_cid=' in url:
            l2_cid = url.split('l2_cid=')[1].split('&')[0]
            category_ids[name] = l2_cid
            print(f"    -> l2_cid = {l2_cid}")

        # 返回重新获取菜单
        page.evaluate("""
            () => {
                const allElements = document.querySelectorAll('*');
                for (let el of allElements) {
                    if (el.innerText === '商品分类：食品饮料') {
                        if (el.click) el.click();
                        break;
                    }
                }
            }
        """)
        page.wait_for_timeout(1500)

        # 重新展开即食食品
        for m in menu_items:
            if m['text'] == '即食食品':
                page.mouse.click(m['x'], m['y'])
                page.wait_for_timeout(2000)
                break

    # 打印最终结果
    print("\n" + "="*60)
    print("即食食品子分类ID:")
    print("="*60)
    for name, cid in category_ids.items():
        print(f"  '{name}': {cid},")

    return category_ids

if __name__ == "__main__":
    ids = discover_category_ids()
    print("\n完成!")