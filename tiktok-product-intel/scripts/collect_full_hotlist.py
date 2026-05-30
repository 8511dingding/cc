#!/usr/bin/env python3
"""
采集FastMOSS食品饮料完整热推榜数据
"""
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime
import json

def collect_all_pages():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    # 访问热推榜泰国站 - 食品饮料
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 点击食品饮料分类
    print("\n选择食品饮料分类...")
    page.evaluate("""
        () => {
            const elements = document.querySelectorAll('span');
            for (let el of elements) {
                if (el.innerText === '食品饮料') {
                    el.click();
                    break;
                }
            }
        }
    """)
    page.wait_for_timeout(2000)

    all_products = []

    # 采集第1页
    print("\n采集第1页...")
    products = extract_page_data(page)
    all_products.extend(products)
    print(f"第1页: {len(products)} 个商品")
    page.wait_for_timeout(1000)

    # 点击第2页
    print("\n跳转第2页...")
    page.click('text=2')
    page.wait_for_timeout(3000)
    products = extract_page_data(page)
    all_products.extend(products)
    print(f"第2页: {len(products)} 个商品")
    page.wait_for_timeout(1000)

    # 点击第3页
    print("\n跳转第3页...")
    page.click('text=3')
    page.wait_for_timeout(3000)
    products = extract_page_data(page)
    all_products.extend(products)
    print(f"第3页: {len(products)} 个商品")

    return all_products

def extract_page_data(page):
    """从当前页面提取商品数据"""
    products = []

    rows = page.query_selector_all('tbody tr')

    for row in rows:
        try:
            cells = row.query_selector_all('td')
            if len(cells) < 8:
                continue

            cell_texts = [c.inner_text().strip() for c in cells]

            rank_text = cell_texts[0]
            if not rank_text.isdigit():
                continue

            rank = int(rank_text)
            product_raw = cell_texts[1]

            # 提取名称和价格
            name = product_raw.split('售价')[0].strip()[:80]
            price_match = re.search(r'฿([\d,]+\.?\d*)', product_raw)
            price = float(price_match.group(1).replace(',', '')) if price_match else 0

            country = cell_texts[2]
            store = cell_texts[3]
            category = cell_texts[4]

            # 佣金
            comm_match = re.search(r'(\d+)%', cell_texts[5])
            commission = int(comm_match.group(1)) if comm_match else 0

            # 销量
            sales_match = re.search(r'([\d.]+)万', cell_texts[6])
            sales = int(float(sales_match.group(1)) * 10000) if sales_match else 0
            if not sales:
                sales_match = re.search(r'(\d+)', cell_texts[6])
                sales = int(sales_match.group(1)) if sales_match else 0

            # 销售额
            revenue_match = re.search(r'฿([\d.]+)万', cell_texts[7])
            revenue = float(revenue_match.group(1)) * 10000 if revenue_match else 0

            products.append({
                'rank': rank,
                'name': name,
                'price': price,
                'country': country,
                'store': store,
                'category': category,
                'commission': commission,
                'sales': sales,
                'revenue': revenue
            })

        except Exception as e:
            continue

    return products

def analyze_and_generate_report(products):
    """生成完整的分析报告"""
    print(f"\n\n共采集 {len(products)} 个商品")

    # 按销量排序
    sorted_products = sorted(products, key=lambda x: x.get('sales', 0), reverse=True)

    # 统计分析
    categories = {}
    price_ranges = {'0-100': 0, '100-200': 0, '200-500': 0, '500+': 0}
    commission_rates = {0: 0, 5: 0, 10: 0, 15: 0, 20: 0}

    total_sales = 0
    total_revenue = 0

    for p in products:
        cat = p.get('category', '未知')
        categories[cat] = categories.get(cat, 0) + 1

        price = p.get('price', 0)
        if price < 100:
            price_ranges['0-100'] += 1
        elif price < 200:
            price_ranges['100-200'] += 1
        elif price < 500:
            price_ranges['200-500'] += 1
        else:
            price_ranges['500+'] += 1

        comm = p.get('commission', 0)
        if comm <= 5:
            commission_rates[5] += 1
        elif comm <= 10:
            commission_rates[10] += 1
        elif comm <= 15:
            commission_rates[15] += 1
        else:
            commission_rates[20] += 1

        total_sales += p.get('sales', 0)
        total_revenue += p.get('revenue', 0)

    # 综合评分
    scored = []
    for p in products:
        score = 0

        # 销量分数 (最高40分)
        sales = p.get('sales', 0)
        if sales > 5000:
            score += 40
        elif sales > 2000:
            score += 30
        elif sales > 1000:
            score += 20
        elif sales > 500:
            score += 10
        elif sales > 100:
            score += 5

        # 佣金分数 (最高30分)
        comm = p.get('commission', 0)
        score += min(comm * 2, 30)

        # 价格适中分数 (最高30分)
        price = p.get('price', 0)
        if 80 <= price <= 200:
            score += 30
        elif 200 < price <= 400:
            score += 20
        elif price < 80:
            score += 15
        else:
            score += 5

        scored.append((score, p))

    scored.sort(key=lambda x: -x[0])

    # 生成报告
    report = f"""# FastMOSS泰国TikTok热推榜 食品饮料分析报告

采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH&l1_cid=24
采集页数: 3页 | 商品总数: {len(products)}

---

## 一、数据概览

- **总商品数**: {len(products)}
- **7天总销量**: {total_sales:,}
- **7天总销售额**: ฿{total_revenue/10000:.2f}万 ({total_revenue*4.7/10000:.2f}万 CNY)
- **平均销量**: {total_sales/len(products):,.0f}/商品
- **平均销售额**: ฿{total_revenue/len(products)/10000:.2f}万/商品

---

## 二、分类分布

"""

    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        report += f"- **{cat}**: {count}个 ({count/len(products)*100:.1f}%)\n"

    report += f"""
---

## 三、价格区间分布

| 价格区间 | 商品数 | 占比 |
|----------|--------|------|
"""

    for range_name, count in price_ranges.items():
        report += f"| {range_name} THB | {count} | {count/len(products)*100:.1f}% |\n"

    report += f"""
---

## 四、佣金比例分布

| 佣金比例 | 商品数 | 占比 |
|----------|--------|------|
"""

    for comm, count in commission_rates.items():
        label = f"{comm-5}%~{comm}%" if comm > 0 else "0~5%"
        report += f"| {label} | {count} | {count/len(products)*100:.1f}% |\n"

    report += """
---

## 五、TOP 20 爆款商品

| 排名 | 商品名称 | 价格 | 分类 | 佣金 | 7天销量 |
|------|----------|------|------|------|---------|
"""

    for i, p in enumerate(sorted_products[:20], 1):
        report += f"| {i} | {p['name'][:35]} | {p['price']:.0f} | {p['category'][:15]} | {p['commission']}% | {p['sales']:,} |\n"

    report += """
---

## 六、综合评分TOP 15（选品推荐）

综合评分维度：
- 销量权重40%（周销量越高分数越高）
- 佣金权重30%（佣金越高分数越高）
- 价格权重30%（80-200THB为最佳区间）

| 排名 | 商品名称 | 评分 | 价格 | 销量 | 佣金 | 综合评价 |
|------|----------|------|------|------|------|----------|
"""

    for i, (score, p) in enumerate(scored[:15], 1):
        # 综合评价
        if score >= 70:
           评价 = "⭐⭐⭐ 强烈推荐"
        elif score >= 50:
           评价 = "⭐⭐ 推荐"
        else:
           评价 = "⭐ 可关注"

        report += f"| {i} | {p['name'][:30]} | {score} | {p['price']:.0f} | {p['sales']:,} | {p['commission']}% | {评价} |\n"

    report += """
---

## 七、爆款产品筛选方法论

### 1. 核心筛选指标

#### （1）销量指标（权重40%）
- **周销量 > 2000**: 爆款标准，进入推荐名单
- **周销量 1000-2000**: 潜力款，重点观察
- **周销量 500-1000**: 普通款，需结合其他指标
- **周销量 < 500**: 冷门款，谨慎选择

#### （2）佣金指标（权重30%）
- **佣金 ≥ 15%**: 高利润款，优先推荐
- **佣金 10-15%**: 中高利润，可考虑
- **佣金 5-10%**: 中等利润，需要量支撑
- **佣金 < 5%**: 低利润，避开

#### （3）价格指标（权重30%）
- **最佳区间 80-200 THB**: 大众消费，转化率高
- **200-400 THB**: 中高端，销量会受限
- **< 80 THB**: 低价冲量，利润空间有限
- **> 400 THB**: 高价商品，谨慎

### 2. 加分项（额外权重）

- **商品名称含促销信息**：如"[แถม1]"买一送一，表示商家在推
- **多规格可选**：价格区间大（如฿230-861），说明有不同档次
- **本土店铺**：店铺销量高（>100万），说明是本地爆款
- **关联达人少但销量高**：竞争度低，容易切入

### 3. 筛除项（黑名单）

- **国际大牌**：可口可乐、百事可乐等，供应链被大玩家垄断
- **知名进口品牌**：品牌方已有官方渠道，新进入者难竞争
- **保质期短**：生鲜、冷藏食品，库存风险大
- **重量/体积大**：海运成本高，压舱位

### 4. 筛选流程图

```
输入：FastMOSS热推榜食品饮料分类
  ↓
第一步：周销量 > 500？
  ↓ 否 → 筛除
  ↓ 是 → 第二步
  ↓
第二步：佣金 ≥ 5%？
  ↓ 否 → 筛除
  ↓ 是 → 第三步
  ↓
第三步：价格 50-500 THB？
  ↓ 否 → 筛除
  ↓ 是 → 第四步
  ↓
第四步：是否黑名单商品？
  ↓ 是 → 筛除
  ↓ 否 → 进入备选名单
  ↓
输出：重点选品名单
```

---

## 八、选品建议

### 8.1 优先关注品类（按潜力排序）

| 品类 | 推荐理由 | 价格区间 | 佣金区间 |
|------|----------|----------|----------|
| **咖啡类** | 泰国人咖啡消费量大，复购率高 | 150-300 THB | 10-20% |
| **饼干/薯片** | 零食属性，冲动消费高 | 50-150 THB | 5-15% |
| **干粮零食** | 易保存，海运风险低 | 80-200 THB | 5-15% |
| **坚果种子** | 健康概念，客单价高 | 150-400 THB | 10-20% |
| **蛋白质/代餐** | 健身风潮，泰国女性市场大 | 300-800 THB | 8-15% |

### 8.2 具体商品推荐

"""

    # 从评分中找出推荐商品
    top_picks = [p for score, p in scored[:10] if score >= 50]

    for i, p in enumerate(top_picks, 1):
        report += f"""
**{i}. {p['name'][:50]}**
- 价格: {p['price']:.0f} THB ({p['price']*4.7:.1f} CNY)
- 7天销量: {p['sales']:,}
- 佣金: {p['commission']}%
- 分类: {p['category']}
- 店铺: {p['store']}
"""

    report += """

---

## 九、1688货源建议

根据以上选品，推荐以下1688搜索关键词：

### 咖啡/代餐类
- "泰国咖啡" "越南咖啡" "拿铁咖啡"
- "代餐粉" "蛋白粉" "素食代餐"

### 零食类
- "薯片批发" "饼干批发" "小零食"
- "海苔零食" "芒果干" "榴莲干"

### 坚果类
- "每日坚果" "混合坚果" "腰果"
- "奇亚籽" "亚麻籽"

### 调味品
- "泰式调味" "辣椒酱" "鱼露"

---

*报告生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*"

    # 保存报告
    report_path = "/Users/jianing/Ning's Git/tiktok-product-intel/reports/fastmoss_food_selection_methodology.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {report_path}")

    # 打印摘要
    print("\n" + "="*80)
    print("【选品方法论摘要】")
    print("="*80)
    print("\n爆款筛选三要素:")
    print("  1. 周销量 > 1000")
    print("  2. 佣金 ≥ 10%")
    print("  3. 价格 80-300 THB")
    print("\n优先品类:")
    print("  - 咖啡类 (高佣金10-20%)")
    print("  - 干粮零食 (易保存)")
    print("  - 坚果种子 (健康概念)")
    print("\nTOP 5 推荐商品:")
    for i, (score, p) in enumerate(scored[:5], 1):
        print(f"  {i}. {p['name'][:40]}")
        print(f"     价格:{p['price']:.0f} THB | 销量:{p['sales']:,} | 佣金:{p['commission']}%")

if __name__ == "__main__":
    products = collect_all_pages()
    if products:
        analyze_and_generate_report(products)
    print("\n完成!")