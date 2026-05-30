#!/usr/bin/env python3
"""简单启动FastMOSS浏览器，不等待自动采集"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("正在打开FastMOSS登录页...")
    page.goto("https://www.fastmoss.com/zh/login")

    print("\n" + "="*50)
    print("浏览器已打开!")
    print("请在浏览器中登录FastMOSS")
    print("账号: 16293163036")
    print("密码: aa661188")
    print("="*50)
    print("\n登录后告诉我 '完成' ，我继续帮你采集数据")

    # 保持浏览器打开
    input("按回车键关闭浏览器...")

    browser.close()