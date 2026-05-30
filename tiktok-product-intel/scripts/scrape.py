#!/usr/bin/env python3
"""
FastMOSS 浏览器自动化采集脚本
用于登录和采集关键词下的产品数据
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# 添加lib目录到路径
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from product_intel import ProductIntelDB, MarketData


class FastMossScraper:
    """FastMOSS数据采集器"""

    def __init__(self, username, password, db_path=None):
        self.username = username
        self.password = password
        self.db = ProductIntelDB(db_path)
        self.platform = "tiktok_th_fastmoss"

    def login(self, page):
        """登录FastMOSS"""
        print("正在打开FastMOSS登录页...")
        page.goto("https://www.fastmoss.com/zh/login")
        page.wait_for_load_state("networkidle")

        time.sleep(2)

        # 输入用户名和密码
        print(f"输入用户名: {self.username}")
        page.fill('input[type="text"]', self.username)
        page.fill('input[type="password"]', self.password)

        # 点击登录
        print("点击登录...")
        page.click('button[type="submit"]')

        # 等待登录完成
        time.sleep(3)

        # 检查是否登录成功
        if "login" in page.url.lower():
            print("⚠️ 登录可能失败，URL仍显示登录页")
        else:
            print("✅ 登录成功")

    def search_keyword(self, page, keyword):
        """搜索关键词"""
        print(f"\n正在搜索关键词: {keyword}")

        # 访问发现的商品页面
        page.goto("https://www.fastmoss.com/zh/e-commerce/product")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        # 找到搜索框并输入关键词
        search_input = page.locator('input[placeholder*="搜索"]').first
        if search_input.is_visible():
            search_input.fill(keyword)
            page.keyboard.press("Enter")
            time.sleep(3)
            print(f"✅ 搜索关键词 '{keyword}' 完成")
        else:
            print("⚠️ 未找到搜索框，尝试其他方式")
            # 尝试直接访问搜索结果URL
            search_url = f"https://www.fastmoss.com/zh/e-commerce/product?keyword={keyword}"
            page.goto(search_url)
            page.wait_for_load_state("networkidle")
            time.sleep(3)

    def get_product_list(self, page):
        """获取商品列表"""
        products = []

        # 等待商品列表加载
        time.sleep(2)

        # 查找商品条目
        product_cards = page.locator('.product-item, .product-card, [class*="product"]').all()

        print(f"找到 {len(product_cards)} 个商品元素")

        for i, card in enumerate(product_cards[:50]):  # 限制最多50个
            try:
                # 提取商品信息
                name_elem = card.locator('.name, .title, [class*="name"]').first
                price_elem = card.locator('.price, [class*="price"]').first
                sales_elem = card.locator('[class*="sales"], [class*="sold"]').first

                product = {
                    "name": name_elem.text_content() if name_elem.is_visible() else "",
                    "price": price_elem.text_content() if price_elem.is_visible() else "",
                    "sales": sales_elem.text_content() if sales_elem.is_visible() else ""
                }

                if product["name"]:
                    products.append(product)

            except Exception as e:
                continue

        return products

    def export_data(self, page, keyword, output_dir):
        """导出当前关键词的数据"""
        # 查找导出按钮
        export_btn = page.locator('button:has-text("导出"), button:has-text("Export")').first

        if export_btn.is_visible():
            print("点击导出按钮...")
            export_btn.click()
            time.sleep(3)
            print(f"✅ 关键词 '{keyword}' 数据导出完成")
        else:
            print("⚠️ 未找到导出按钮，请手动导出")

    def get_recommended_keywords(self, page, category="食品"):
        """获取推荐关键词"""
        print(f"\n获取 {category} 分类的推荐关键词...")

        # 访问商品发现页面
        page.goto("https://www.fastmoss.com/zh/e-commerce/product")
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        keywords = []

        # 尝试找到热门关键词标签
        tag_elements = page.locator('[class*="tag"], [class*="keyword"], .hot-word').all()

        for tag in tag_elements:
            try:
                text = tag.text_content()
                if text and len(text) < 20:
                    keywords.append(text.strip())
            except:
                continue

        print(f"找到 {len(keywords)} 个推荐关键词")
        return keywords[:30]  # 返回前30个

    def save_products_to_db(self, products, keyword):
        """保存商品数据到数据库"""
        saved_count = 0

        for product in products:
            try:
                market_data = MarketData(
                    platform=self.platform,
                    product_name=product.get("name", ""),
                    price=self._parse_price(product.get("price", "")),
                    currency="THB",
                    sales_volume=self._parse_sales(product.get("sales", "")),
                    store_name=product.get("store", ""),
                    url=product.get("url", ""),
                    scraped_at=datetime.now().isoformat()
                )
                self.db.save_market_data(market_data)
                saved_count += 1
            except Exception as e:
                print(f"保存商品失败: {e}")

        print(f"已保存 {saved_count}/{len(products)} 个商品到数据库")
        return saved_count

    def _parse_price(self, price_str):
        """解析价格"""
        import re
        match = re.search(r'[\d,]+\.?\d*', str(price_str))
        return float(match.group().replace(',', '')) if match else 0.0

    def _parse_sales(self, sales_str):
        """解析销量"""
        import re
        match = re.search(r'(\d+)', str(sales_str))
        return int(match.group(1)) if match else 0

    def update_keyword_tracking(self, keyword, product_count, sales_volume):
        """更新关键词追踪"""
        conn = self.db.db_path
        import sqlite3
        conn_db = sqlite3.connect(conn)
        cursor = conn_db.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO keyword_tracking
            (keyword, last_product_count, last_sales_volume, updated_at)
            VALUES (?, ?, ?, ?)
        """, (keyword, product_count, sales_volume, datetime.now().isoformat()))

        conn_db.commit()
        conn_db.close()


def main():
    """主函数 - 演示登录"""
    from playwright.sync_api import sync_playwright

    # 凭据
    USERNAME = "16293163036"
    PASSWORD = "aa661188"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        scraper = FastMossScraper(USERNAME, PASSWORD)

        # 1. 登录
        scraper.login(page)

        # 2. 获取推荐关键词
        keywords = scraper.get_recommended_keywords(page, "食品")
        print(f"\n推荐的食品类关键词: {keywords[:20]}")

        # 3. 搜索测试
        if keywords:
            test_keyword = keywords[0]
            scraper.search_keyword(page, test_keyword)

        browser.close()


if __name__ == "__main__":
    main()