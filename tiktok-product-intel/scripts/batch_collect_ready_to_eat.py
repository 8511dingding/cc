#!/usr/bin/env python3
"""
批量采集FastMOSS即食食品各子类数据
每个子类采集100个商品
"""
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime
from pathlib import Path

def parse_products_from_rows(rows):
    """从表格行解析商品数据"""
    products = []
    for row in rows:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 8: continue

            cell_texts = [c.inner_text().strip() for c in cells]

            if not cell_texts[0].isdigit(): continue

            rank = int(cell_texts[0])
            product_raw = cell_texts[1]

            name = product_raw.split('售价')[0].strip()[:80]
            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            category = cell_texts[4]

            comm_match = re.search(r'(\d+)%', cell_texts[5])
            commission = int(comm_match.group(1)) if comm_match else 0

            sales_match = re.search(r'([\d.]+)万', cell_texts[6])
            sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0
            if not sales:
                sales_match = re.search(r'(\d+)', cell_texts[6])
                sales = int(sales_match.group(1)) if sales_match else 0

            products.append({
                'rank': rank,
                'name': name,
                'price': price,
                'category': category,
                'commission': commission,
                'sales': sales
            })
        except:
            continue
    return products

def collect_subcategory(page, subcategory_name, l2_cid, max_pages=5):
    """采集单个子分类的数据"""
    print(f"\n  采集子分类: {subcategory_name} (l2_cid={l2_cid})")

    all_products = []

    # 访问带分类参数的页面
    url = f"https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH&l1_cid=24&l2_cid={l2_cid}"
    page.goto(url, timeout=60000)
    page.wait_for_timeout(3000)

    for page_num in range(1, max_pages + 1):
        if page_num > 1:
            # 点击下一页
            try:
                page.click(f'text={page_num}')
                page.wait_for_timeout(3000)
            except:
                try:
                    # 尝试下一页按钮
                    next_btn = page.locator('.ant-pagination-next')
                    if next_btn.is_visible():
                        next_btn.click()
                        page.wait_for_timeout(3000)
                except:
                    break

        # 提取当前页数据
        rows = page.query_selector_all('tbody tr')
        products = parse_products_from_rows(rows)

        if not products:
            break

        all_products.extend(products)
        print(f"    第{page_num}页: 获得 {len(products)} 个商品, 累计: {len(all_products)}")

        if len(all_products) >= 100:
            break

    return all_products[:100]  # 最多返回100个

def explore_and_collect():
    """探索即食食品的子分类并批量采集"""
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    # 访问热推榜页面
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 1. 选择食品饮料分类
    print("\n1. 选择食品饮料分类...")
    page.click('label:has-text("食品饮料")')
    page.wait_for_timeout(2000)

    # 2. 展开级联菜单获取所有子分类
    print("\n2. 获取子分类列表...")

    # 点击商品分类标签展开级联菜单
    page.click('text=商品分类：食品饮料')
    page.wait_for_timeout(1500)

    # 获取所有子分类的信息
    subcategories = page.evaluate("""
        () => {
            const items = document.querySelectorAll('.ant-cascader-menu-item');
            const result = [];
            items.forEach((item, index) => {
                const rect = item.getBoundingClientRect();
                result.push({
                    index: index,
                    text: item.innerText,
                    x: Math.round(rect.left),
                    y: Math.round(rect.top)
                });
            });
            return JSON.stringify(result);
        }
    """)

    subcategories = json.loads(subcategories)
    print(f"  找到 {len(subcategories)} 个子分类:")

    # 获取每个子分类的坐标并记录
    category_info = []
    for i, item in enumerate(subcategories):
        print(f"    {i}: {item['text']} at ({item['x']}, {item['y']})")
        category_info.append({
            'index': i,
            'name': item['text'],
            'y': item['y']
        })

    # 3. 批量采集每个子分类的数据
    print("\n3. 批量采集各子分类数据...")

    # 子分类在级联菜单中的顺序（根据之前的探索）
    # 第一层: 饮料, 即食食品, 生鲜冷冻食品 (y ≈ 405)
    # 第二层: 即食泡面, 罐装与包装食品, 即食饭与粥, 即食火锅 (y ≈ 575)

    # 点击即食食品展开第二层
    for item in subcategories:
        if item['text'] == '即食食品':
            page.mouse.click(item['x'] + 100, item['y'])  # 点击右侧展开第二层
            page.wait_for_timeout(2000)
            break

    # 获取第二层子分类
    subcategories_l2 = page.evaluate("""
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

    subcategories_l2 = json.loads(subcategories_l2)

    # 过滤出即食食品的子分类
    ready_to_eat_subs = []
    for item in subcategories_l2:
        if item['y'] > 500:  # 第二层的位置
            ready_to_eat_subs.append(item)

    print(f"\n  即食食品子分类:")
    for item in ready_to_eat_subs:
        print(f"    - {item['text']}")

    # 为每个子分类获取l2_cid
    # 先点击一个子分类看URL变化
    print("\n  获取子分类ID...")

    results = {}

    for sub in ready_to_eat_subs:
        name = sub['text']
        x, y = sub['x'], sub['y']

        # 点击该子分类
        page.mouse.click(x, y)
        page.wait_for_timeout(3000)

        # 获取URL中的l2_cid
        url = page.url
        if 'l2_cid=' in url:
            l2_cid = url.split('l2_cid=')[1].split('&')[0]
            print(f"  {name}: l2_cid = {l2_cid}")
            results[name] = l2_cid

            # 采集数据
            products = collect_subcategory(page, name, l2_cid, max_pages=5)
            results[f'{name}_products'] = products

            print(f"    共采集 {len(products)} 个商品")

            # 返回重新获取菜单
            page.click('text=商品分类：食品饮料')
            page.wait_for_timeout(1500)

            # 重新展开即食食品
            for item in subcategories:
                if item['text'] == '即食食品':
                    page.mouse.click(item['x'] + 100, item['y'])
                    page.wait_for_timeout(2000)
                    break

    return results

def generate_comprehensive_report(all_results):
    """生成综合分析报告"""

    report = f"""# FastMOSS即食食品分类综合分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH
分类: 食品饮料 → 即食食品

---

## 一、数据概览

"""

    total_products = 0
    category_stats = {}

    for name, data in all_results.items():
        if name.endswith('_products'):
            category = name.replace('_products', '')
            products = data
            total_products += len(products)
            total_sales = sum(p.get('sales', 0) for p in products)
            avg_price = sum(p.get('price', 0) for p in products) / len(products) if products else 0
            avg_commission = sum(p.get('commission', 0) for p in products) / len(products) if products else 0

            category_stats[category] = {
                'count': len(products),
                'total_sales': total_sales,
                'avg_price': avg_price,
                'avg_commission': avg_commission,
                'products': products
            }

    report += f"- 总采集商品数: **{total_products}**\n"
    report += f"- 覆盖子分类数: **{len(category_stats)}**\n\n"

    # 子分类统计表
    report += """## 二、各子分类数据统计

| 子分类 | 商品数 | 7天总销量 | 平均价格(THB) | 平均佣金 |
|--------|--------|-----------|----------------|----------|
"""

    for cat, stats in category_stats.items():
        report += f"| {cat} | {stats['count']} | {stats['total_sales']:,} | {stats['avg_price']:.0f} | {stats['avg_commission']:.1f}% |\n"

    # 每个子分类的TOP 10
    report += "\n---\n\n## 三、各子分类爆款TOP 10\n"

    for cat, stats in category_stats.items():
        sorted_products = sorted(stats['products'], key=lambda x: x.get('sales', 0), reverse=True)

        report += f"\n### 3.1 {cat}\n\n"
        report += "| 排名 | 商品名称 | 价格(THB) | 佣金 | 7天销量 |\n"
        report += "|------|----------|-----------|------|---------|\n"

        for i, p in enumerate(sorted_products[:10], 1):
            report += f"| {i} | {p['name'][:40]} | {p['price']:.0f} | {p['commission']}% | {p['sales']:,} |\n"

    # 综合分析
    report += "\n---\n\n## 四、综合分析\n\n"

    # 价格区间分析
    report += "### 4.1 价格区间分布\n\n"

    all_prices = {'0-50': 0, '50-100': 0, '100-200': 0, '200-500': 0, '500+': 0}
    for cat, stats in category_stats.items():
        for p in stats['products']:
            price = p.get('price', 0)
            if price < 50:
                all_prices['0-50'] += 1
            elif price < 100:
                all_prices['50-100'] += 1
            elif price < 200:
                all_prices['100-200'] += 1
            elif price < 500:
                all_prices['200-500'] += 1
            else:
                all_prices['500+'] += 1

    report += "| 价格区间 | 商品数 | 占比 |\n"
    report += "|----------|--------|------|\n"
    for range_name, count in all_prices.items():
        pct = count / total_products * 100
        report += f"| {range_name} THB | {count} | {pct:.1f}% |\n"

    # 佣金分析
    report += "\n### 4.2 佣金比例分布\n\n"

    all_commissions = {'0-5%': 0, '5-10%': 0, '10-15%': 0, '15%+': 0}
    for cat, stats in category_stats.items():
        for p in stats['products']:
            comm = p.get('commission', 0)
            if comm < 5:
                all_commissions['0-5%'] += 1
            elif comm < 10:
                all_commissions['5-10%'] += 1
            elif comm < 15:
                all_commissions['10-15%'] += 1
            else:
                all_commissions['15%+'] += 1

    report += "| 佣金区间 | 商品数 | 占比 |\n"
    report += "|----------|--------|------|\n"
    for range_name, count in all_commissions.items():
        pct = count / total_products * 100
        report += f"| {range_name} | {count} | {pct:.1f}% |\n"

    # 综合评分TOP 20
    report += "\n### 4.3 综合评分TOP 20（所有子分类）\n\n"

    all_products_flat = []
    for cat, stats in category_stats.items():
        for p in stats['products']:
            p['subcategory'] = cat
            all_products_flat.append(p)

    # 计算综合评分
    scored = []
    for p in all_products_flat:
        score = 0
        sales = p.get('sales', 0)
        if sales > 5000: score += 40
        elif sales > 2000: score += 30
        elif sales > 1000: score += 20
        elif sales > 500: score += 10
        elif sales > 100: score += 5

        comm = p.get('commission', 0)
        score += min(comm * 2, 30)

        price = p.get('price', 0)
        if 50 <= price <= 200: score += 30
        elif 200 < price <= 400: score += 20
        elif price < 50: score += 15
        else: score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    report += "| 排名 | 综合评分 | 商品名称 | 子分类 | 价格 | 佣金 | 7天销量 |\n"
    report += "|------|----------|----------|--------|------|------|---------|\n"

    for i, (score, p) in enumerate(scored[:20], 1):
        report += f"| {i} | {score} | {p['name'][:35]} | {p['subcategory']} | {p['price']:.0f} | {p['commission']}% | {p['sales']:,} |\n"

    # 选品建议
    report += """

---

## 五、选品建议

### 5.1 各子分类推荐

"""

    for cat, stats in category_stats.items():
        top_products = sorted(stats['products'], key=lambda x: x.get('sales', 0), reverse=True)[:3]
        avg_sales = stats['total_sales'] / stats['count'] if stats['count'] > 0 else 0

        report += f"\n**{cat}:**\n"
        report += f"- 平均7天销量: {avg_sales:,.0f}\n"
        report += f"- 推荐商品:\n"
        for p in top_products:
            report += f"  - {p['name'][:40]} (销量:{p['sales']:,}, 佣金:{p['commission']}%)\n"

    # 1688货源建议
    report += """

### 5.2 1688货源关键词

根据各子分类爆款特征，推荐以下1688搜索关键词：

#### 即食泡面
- "泰国方便面" "Mama方便面" "Samyang火鸡面" "yumyum方便面"

#### 罐装与包装食品
- "泰国辣椒酱" "鱼露" "酸梅酱" "沙爹酱"
- "泰国鱼罐头" "炸鱼干"

#### 即食饭与粥
- "泰国即食粥" "方便米饭" "微波米饭"

#### 即食火锅
- "泰国火锅底料" "冬阴功汤底" "麻辣火锅底料"

### 5.3 筛选标准建议

**入门标准（满足任一即可）：**
- 7天销量 > 500
- 佣金 ≥ 10%
- 价格 50-200 THB

**优选标准（满足两个以上）：**
- 7天销量 > 1000
- 佣金 ≥ 15%
- 有促销信息（如"买一送一"）
- 本土店铺销量 > 50万

"""

    report += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report

if __name__ == "__main__":
    results = explore_and_collect()

    if results:
        report = generate_comprehensive_report(results)

        report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_ready_to_eat_comprehensive.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n\n综合报告已保存到: {report_path}")
        print(f"报告包含 {sum(len(v) for k, v in results.items() if k.endswith('_products'))} 个商品数据")
    else:
        print("采集失败")

    print("\n完成!")