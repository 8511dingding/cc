#!/usr/bin/env python3
"""
FastMOSS 交互式登录和数据采集脚本

使用方法:
1. 运行脚本
2. 在打开的浏览器窗口中手动登录FastMOSS
3. 登录成功后回到终端按回车
4. 脚本会自动采集数据
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))

from playwright.sync_api import sync_playwright
from fastmoss_parser import FastMossParser
from product_intel import ProductIntelDB, MarketData


class FastMossInteractive:
    """FastMOSS交互式采集器"""

    def __init__(self, db_path=None):
        self.db = ProductIntelDB(db_path)
        self.browser = None
        self.context = None
        self.page = None

    def start_browser(self):
        """启动浏览器"""
        self.browser = sync_playwright().start().chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        print("浏览器已启动")

    def wait_for_manual_login(self):
        """等待手动登录"""
        print("\n" + "=" * 60)
        print("请在浏览器窗口中完成FastMOSS登录")
        print("登录成功后，回到终端按回车键继续...")
        print("=" * 60)
        input()
        print("检测登录状态...")

        # 验证是否登录成功
        self.page.goto("https://www.fastmoss.com/zh/dashboard", wait_until='networkidle', timeout=30000)
        page_text = self.page.evaluate('document.body.innerText')

        if "登录/注册" in page_text or "登录" in page_text:
            print("⚠️ 检测到可能未登录，请确保已成功登录")
            return False
        else:
            print("✅ 检测到已登录")
            return True

    def get_product_page(self):
        """访问商品页面"""
        print("\n访问商品发现页面...")
        self.page.goto("https://www.fastmoss.com/zh/e-commerce/product", wait_until='networkidle', timeout=30000)
        self.page.wait_for_timeout(3000)
        print(f"当前URL: {self.page.url}")

    def search_keyword(self, keyword):
        """搜索关键词"""
        print(f"\n搜索关键词: {keyword}")

        # 找到搜索框并输入
        try:
            # 尝试多种搜索框定位方式
            search_box = self.page.locator('input[type="search"]').first
            if not search_box.is_visible():
                search_box = self.page.locator('input[placeholder*="搜索"]').first
            if not search_box.is_visible():
                search_box = self.page.locator('input[type="text"]').first

            search_box.fill(keyword)
            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(3000)
            print(f"✅ 搜索 '{keyword}' 完成")
            return True
        except Exception as e:
            print(f"搜索失败: {e}")
            return False

    def extract_product_data(self):
        """提取当前页面的商品数据"""
        products = []

        try:
            # 等待商品列表加载
            self.page.wait_for_timeout(2000)

            # 查找商品行 - FastMOSS使用表格形式展示数据
            # 尝试查找表格行
            rows = self.page.locator('tr, [class*="row"], [class*="item"]').all()

            for row in rows[:100]:  # 限制数量
                try:
                    cells = row.locator('td, [class*="cell"]').all()

                    if len(cells) >= 5:
                        # 提取商品名称（通常第一个单元格）
                        name = cells[0].inner_text().strip()
                        # 价格
                        price = cells[1].inner_text().strip() if len(cells) > 1 else ""
                        # 销量
                        sales = cells[2].inner_text().strip() if len(cells) > 2 else ""

                        if name and name not in ["商品", "商品名称", ""]:
                            products.append({
                                "name": name,
                                "price": price,
                                "sales": sales
                            })
                except:
                    continue

        except Exception as e:
            print(f"提取数据失败: {e}")

        print(f"提取到 {len(products)} 个商品数据")
        return products

    def click_export_button(self, output_path=None):
        """点击导出按钮并保存数据"""
        print("\n尝试点击导出按钮...")

        try:
            # 查找导出相关按钮
            export_btn = None
            btn_texts = ["导出", "Export", "下载", "download"]

            for text in btn_texts:
                btns = self.page.locator(f'button:has-text("{text}"), [role="button"]:has-text("{text}")').all()
                for btn in btns:
                    if btn.is_visible():
                        export_btn = btn
                        break
                if export_btn:
                    break

            if export_btn:
                export_btn.click()
                print("✅ 导出按钮已点击")
                return True
            else:
                print("⚠️ 未找到导出按钮")
                return False

        except Exception as e:
            print(f"点击导出按钮失败: {e}")
            return False

    def get_page_html(self):
        """获取当前页面完整HTML"""
        return self.page.content()

    def save_cookies(self, path):
        """保存cookies以便后续使用"""
        cookies = self.context.cookies()
        with open(path, 'w') as f:
            json.dump(cookies, f)
        print(f"Cookies已保存到: {path}")

    def load_cookies(self, path):
        """加载cookies"""
        with open(path, 'r') as f:
            cookies = json.load(f)
        self.context.add_cookies(cookies)
        print(f"Cookies已加载: {path}")

    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            print("浏览器已关闭")


def main():
    """主函数"""
    scraper = FastMossInteractive()

    try:
        # 1. 启动浏览器
        scraper.start_browser()

        # 2. 等待手动登录
        if not scraper.wait_for_manual_login():
            print("登录失败，退出")
            return

        # 3. 访问商品页面
        scraper.get_product_page()

        # 4. 搜索测试关键词
        test_keywords = ["鹰嘴豆", "板栗", "地瓜干"]
        for kw in test_keywords:
            scraper.search_keyword(kw)
            # 提取数据
            products = scraper.extract_product_data()

            # 保存到数据库
            for product in products:
                market_data = MarketData(
                    platform="tiktok_th_fastmoss",
                    product_name=product["name"],
                    price=_parse_price(product["price"]),
                    currency="THB",
                    sales_volume=_parse_sales(product["sales"]),
                    store_name="",
                    url="",
                    scraped_at=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                scraper.db.save_market_data(market_data)

        print("\n" + "=" * 60)
        print("数据采集完成!")
        print("=" * 60)

        # 5. 保存cookies供后续使用
        cookie_path = Path(__file__).parent.parent / "data" / "fastmoss_cookies.json"
        scraper.save_cookies(str(cookie_path))

    finally:
        input("按回车键关闭浏览器...")
        scraper.close()


def _parse_price(price_str):
    """解析价格"""
    import re
    match = re.search(r'[\d,]+\.?\d*', str(price_str))
    return float(match.group().replace(',', '')) if match else 0.0


def _parse_sales(sales_str):
    """解析销量"""
    import re
    match = re.search(r'(\d+)', str(sales_str))
    return int(match.group(1)) if match else 0


if __name__ == "__main__":
    main()