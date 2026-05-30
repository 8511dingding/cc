#!/usr/bin/env python3
"""
批量采集FastMOSS即食食品各子类数据
使用已知的分类ID直接访问
"""
from playwright.sync_api import sync_playwright
import time
import re
import json
from datetime import datetime

# 已知的分类ID
CATEGORY_IDS = {
    '食品饮料': 24,
    '即食泡面': 914952,
    '罐装与包装食品': 947080,
    '即食饭与粥': 947081,
    '即食火锅': 947082,
}

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

def collect_subcategory(browser, subcategory_name, l2_cid, max_pages=5):
    """采集单个子分类的数据"""
    print(f"\n  采集子分类: {subcategory_name} (l2_cid={l2_cid})")

    context = browser.contexts[0]
    page = context.pages[0]

    all_products = []

    # 访问带分类参数的页面
    url = f"https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH&l1_cid=24&l2_cid={l2_cid}"
    page.goto(url, timeout=60000)
    page.wait_for_timeout(3000)

    for page_num in range(1, max_pages + 1):
        if page_num > 1:
            # 点击页码按钮
            try:
                page.click(f'text="{page_num}"')
                page.wait_for_timeout(3000)
            except:
                try:
                    # 尝试使用Ant Design的分页器
                    page_num_element = page.locator(f'.ant-pagination-item >> text={page_num}')
                    if page_num_element.is_visible():
                        page_num_element.click()
                        page.wait_for_timeout(3000)
                except:
                    # 尝试使用JavaScript直接点击
                    page.evaluate(f"""
                        () => {{
                            const pagination = document.querySelector('.ant-pagination');
                            if (pagination) {{
                                const page{page_num} = pagination.querySelector('[title="{page_num}"]');
                                if (page{page_num}) page{page_num}.click();
                            }}
                        }}
                    """)
                    page.wait_for_timeout(3000)

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

def main():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)

    all_results = {}

    for subcategory_name, l2_cid in CATEGORY_IDS.items():
        if subcategory_name == '食品饮料':
            continue  # 跳过一级分类

        print(f"\n{'='*60}")
        print(f"采集: {subcategory_name}")
        print('='*60)

        products = collect_subcategory(browser, subcategory_name, l2_cid, max_pages=10)
        all_results[subcategory_name] = products

        print(f"  共采集 {len(products)} 个商品")

        # 短暂等待
        time.sleep(1)

    # 生成综合报告
    print(f"\n\n{'='*60}")
    print("生成综合分析报告...")
    print('='*60)

    report = generate_comprehensive_report(all_results)

    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_ready_to_eat_comprehensive.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n综合报告已保存到: {report_path}")

    # 打印摘要
    total = sum(len(v) for v in all_results.values())
    print(f"\n共采集 {total} 个商品")

    for name, products in all_results.items():
        avg_sales = sum(p.get('sales', 0) for p in products) / len(products) if products else 0
        print(f"  {name}: {len(products)} 个, 平均销量 {avg_sales:,.0f}")

    print("\n完成!")

def generate_comprehensive_report(all_results):
    """生成综合分析报告"""

    report = f"""# FastMOSS即食食品分类综合分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH
分类路径: 食品饮料 → 即食食品

---

## 一、数据概览

"""

    total_products = sum(len(v) for v in all_results.values())

    report += f"- 总采集商品数: **{total_products}**\n"
    report += f"- 覆盖子分类数: **{len(all_results)}**\n\n"

    # 子分类统计表
    report += """## 二、各子分类数据统计

| 子分类 | 商品数 | 7天总销量 | 平均价格(THB) | 平均佣金 |
|--------|--------|-----------|----------------|----------|
"""

    category_stats = {}
    for cat, products in all_results.items():
        if not products:
            continue
        total_sales = sum(p.get('sales', 0) for p in products)
        avg_price = sum(p.get('price', 0) for p in products) / len(products)
        avg_commission = sum(p.get('commission', 0) for p in products) / len(products)
        category_stats[cat] = {
            'count': len(products),
            'total_sales': total_sales,
            'avg_price': avg_price,
            'avg_commission': avg_commission,
            'products': products
        }
        report += f"| {cat} | {len(products)} | {total_sales:,} | {avg_price:.0f} | {avg_commission:.1f}% |\n"

    # 每个子分类的TOP 10
    report += "\n---\n\n## 三、各子分类爆款TOP 10\n"

    for cat, products in all_results.items():
        if not products:
            continue
        sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

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
    for cat, products in all_results.items():
        for p in products:
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
        pct = count / total_products * 100 if total_products > 0 else 0
        report += f"| {range_name} THB | {count} | {pct:.1f}% |\n"

    # 佣金分析
    report += "\n### 4.2 佣金比例分布\n\n"

    all_commissions = {'0-5%': 0, '5-10%': 0, '10-15%': 0, '15%+': 0}
    for cat, products in all_results.items():
        for p in products:
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
        pct = count / total_products * 100 if total_products > 0 else 0
        report += f"| {range_name} | {count} | {pct:.1f}% |\n"

    # 综合评分TOP 20
    report += "\n### 4.3 综合评分TOP 20（所有子分类）\n\n"
    report += "综合评分公式：销量分数(40%) + 佣金分数(30%) + 价格分数(30%)\n\n"

    all_products_flat = []
    for cat, products in all_results.items():
        for p in products:
            p_copy = p.copy()
            p_copy['subcategory'] = cat
            all_products_flat.append(p_copy)

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

    for cat, products in all_results.items():
        if not products:
            continue
        sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)
        top_products = sorted_products[:3]
        avg_sales = sum(p.get('sales', 0) for p in products) / len(products) if products else 0

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
- "印尼捞面" "越南方便面"

#### 罐装与包装食品
- "泰国辣椒酱" "鱼露" "酸梅酱" "沙爹酱"
- "泰国鱼罐头" "炸鱼干" "虾酱"

#### 即食饭与粥
- "泰国即食粥" "方便米饭" "微波米饭"
- "泰国粥罐头"

#### 即食火锅
- "泰国火锅底料" "冬阴功汤底" "麻辣火锅底料"
- "泰式火锅包"

### 5.3 筛选标准建议

**入门标准（满足任一即可）：**
- 7天销量 > 500
- 佣金 ≥ 10%
- 价格 50-200 THB

**优选标准（满足两个以上）：**
- 7天销量 > 1000
- 佣金 ≥ 15%
- 有促销信息（如"[แถม1]"买一送一）
- 本土店铺销量 > 50万

"""

    report += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report

if __name__ == "__main__":
    main()