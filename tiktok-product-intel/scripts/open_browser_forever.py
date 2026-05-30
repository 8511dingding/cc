#!/usr/bin/env python3
"""打开浏览器并保持运行"""
from playwright.sync_api import sync_playwright

print("启动浏览器...")
browser = sync_playwright().start().chromium.launch(headless=False)
page = browser.new_page(viewport={'width': 1400, 'height': 900})

print("打开FastMOSS登录页...")
page.goto('https://www.fastmoss.com/zh/login')

print("=" * 50)
print("浏览器已打开!")
print("请在浏览器中登录 FastMOSS")
print("账号: 16293163036")
print("密码: aa661188")
print("=" * 50)
print("\n登录完成后告诉我，我会继续采集数据")

# 无限等待，让用户操作
import time
while True:
    time.sleep(10)
    print("等待中...")