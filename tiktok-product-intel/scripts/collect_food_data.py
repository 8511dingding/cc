#!/usr/bin/env python3
"""
FastMOSS食品品类数据采集脚本
假设用户已经登录了浏览器
"""
from playwright.sync_api import sync_playwright
import time
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from product_intel import ProductIntelDB, MarketData
from datetime import datetime


class FastMossFoodScraper:
    """FastMOSS食品品类采集器"""

    def __init__(self):
        self.db = ProductIntelDB()
        self.platform = "tiktok_th_fastmoss"

    def extract_products_from_page(self, page):
        """从页面提取商品数据"""
        products = []

        # 获取页面HTML
        html = page.content()

        # 方法1: 尝试提取表格数据
        rows = page.query_selector_all('tbody tr, .el-table__row, [class*="row"]')

        for row in rows[:100]:
            try:
                cells = row.query_selector_all('td, [class*="cell"]')
                if len(cells) >= 5:
                    name = cells[0].inner_text().strip()[:100]
                    price_text = cells[1].inner_text().strip() if len(cells) > 1 else ""
                    sales_text = cells[2].inner_text().strip() if len(cells) > 2 else ""

                    if name and not name.startswith("商品"):
                        products.append({
                            "name": name,
                            "price": self.parse_price(price_text),
                            "price_raw": price_text,
                            "sales": self.parse_sales(sales_text),
                            "sales_raw": sales_text
                        })
            except:
                continue

        # 方法2: 从页面文本中搜索商品信息
        if not products:
            print("方法1未找到数据，尝试方法2...")
            page_text = page.evaluate('document.body.innerText')

            # 提取 ฿价格格式的商品
            price_pattern = r'(฿[\d,]+\.?\d*)\s*\n\s*(.+?)\s*\n'
            matches = re.findall(price_pattern, page_text)

            for price, name in matches:
                if len(name) > 5 and len(name) < 200:
                    products.append({
                        "name": name.strip(),
                        "price": self.parse_price(price),
                        "price_raw": price,
                        "sales": 0,
                        "sales_raw": ""
                    })

        return products

    def parse_price(self, price_str):
        """解析泰铢价格"""
        if not price_str:
            return 0.0
        match = re.search(r'[\d,]+\.?\d*', str(price_str))
        if match:
            return float(match.group().replace(',', ''))
        return 0.0

    def parse_sales(self, sales_str):
        """解析销量"""
        if not sales_str:
            return 0
        # 移除千分位
        sales_str = str(sales_str).replace(',', '')
        match = re.search(r'(\d+)', sales_str)
        if match:
            return int(match.group())
        return 0

    def save_products(self, products, keyword):
        """保存商品到数据库"""
        saved = 0
        for p in products:
            try:
                market_data = MarketData(
                    platform=self.platform,
                    product_name=p["name"],
                    price=p["price"],
                    currency="THB",
                    sales_volume=p["sales"],
                    store_name=p.get("store", ""),
                    url=p.get("url", ""),
                    scraped_at=datetime.now().isoformat()
                )
                self.db.save_market_data(market_data)
                saved += 1
            except Exception as e:
                print(f"保存失败: {e}")

        print(f"已保存 {saved}/{len(products)} 个商品 (关键词: {keyword})")
        return saved


def main():
    scraper = FastMossFoodScraper()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("打开FastMOSS商品页面...")
        page.goto("https://www.fastmoss.com/zh/e-commerce/product", wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(3000)

        print(f"当前URL: {page.url}")

        # 食品类关键词列表
        food_keywords = [
            "零食", "小吃", "坚果", "糖果", "饼干", "巧克力",
            "方便面", "速食", "调味品", "酱料",
            "咖啡", "茶", "饮料", "果汁",
            "蜂蜜", "燕窝", "保健品",
            "大米", "面粉", "面条",
            "肉类", "海鲜", "干货",
            "水果干", "果脯", "蜜饯",
            "网红食品", "泰国食品", "日本食品"
        ]

        total_saved = 0
        searched_keywords = []

        for keyword in food_keywords:
            print(f"\n搜索: {keyword}")
            try:
                # 找到搜索框
                search_box = page.locator('input[type="search"], input[placeholder*="搜索"]').first
                if search_box.is_visible():
                    search_box.fill(keyword)
                    page.keyboard.press("Enter")
                    page.wait_for_timeout(3000)

                    # 提取数据
                    products = scraper.extract_products_from_page(page)
                    if products:
                        saved = scraper.save_products(products, keyword)
                        total_saved += saved
                        searched_keywords.append(keyword)

                    # 清除搜索框继续下一个
                    search_box.fill("")
                    page.wait_for_timeout(500)

            except Exception as e:
                print(f"搜索 '{keyword}' 失败: {e}")
                continue

        print("\n" + "=" * 60)
        print(f"采集完成!")
        print(f"搜索关键词: {len(searched_keywords)}/{len(food_keywords)}")
        print(f"总采集商品: {total_saved}")
        print("=" * 60)

        browser.close()


if __name__ == "__main__":
    main()