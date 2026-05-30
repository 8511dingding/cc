#!/usr/bin/env python3
"""
探索FastMOSS分类层级结构
"""
from playwright.sync_api import sync_playwright
import time
import re

def explore_category_structure():
    print("连接到Chrome...")
    browser = sync_playwright().start().chromium.connect_over_cdp("http://localhost:9222", timeout=10000)
    context = browser.contexts[0]
    page = context.pages[0]

    # 访问热推榜页面
    print("\n访问热推榜页面...")
    page.goto("https://www.fastmoss.com/zh/e-commerce/hotlist?region=TH", timeout=60000)
    page.wait_for_timeout(3000)

    # 获取页面文本，找到分类相关的内容
    body_text = page.evaluate('document.body.innerText')
    lines = body_text.split('\n')

    print("\n查找所有分类相关的行:")
    categories = []
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # 查找可能是一级或二级分类的行
        if ('食品' in line or '饮料' in line or '即食' in line or '生鲜' in line or
            '调味' in line or '咖啡' in line or '茶' in line or '零食' in line or
            '母婴' in line or '保健' in line or '美妆' in line or '个护' in line):
            if len(line) < 20 and line.strip():
                print(f"  行{i}: '{line.strip()}'")
                categories.append((i, line.strip()))

    # 查看URL参数变化
    print("\n当前URL:", page.url)

    # 尝试直接访问即食食品的URL
    # 根据之前的URL结构: l1_cid=24 是一级分类(食品饮料)
    # 尝试查找即食食品的二级分类ID

    print("\n尝试访问即食食品分类...")

    # 先获取一级分类ID
    page.wait_for_timeout(1000)

    # 打印所有一级分类的链接
    print("\n打印页面中的链接...")

    # 尝试找到"食品饮料"然后展开子分类
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)

    # 查找商品分类标签附近的所有可点击元素
    print("\n尝试查找分类层级结构...")

    # 使用JavaScript获取分类信息
    category_info = page.evaluate("""
        () => {
            const result = [];
            // 查找所有包含分类文本的元素
            const allElements = document.querySelectorAll('*');
            const seen = new Set();

            for (let el of allElements) {
                const text = el.innerText?.trim();
                if (text && text.length > 0 && text.length < 30) {
                    // 检查是否是分类名称
                    if (!seen.has(text) && (
                        text.includes('食品') || text.includes('饮料') ||
                        text.includes('即食') || text.includes('生鲜') ||
                        text.includes('咖啡') || text.includes('茶') ||
                        text.includes('母婴') || text.includes('保健')
                    )) {
                        seen.add(text);
                        // 获取父元素信息
                        let parent = el.parentElement;
                        let level = 'unknown';
                        let id = '';

                        // 判断层级
                        if (el.tagName === 'SPAN' || el.tagName === 'DIV') {
                            // 检查是否有radio或checkbox样式
                            const className = el.className || '';
                            if (className.includes('radio') || className.includes('check')) {
                                level = 'category';
                            }
                        }

                        result.push({
                            text: text,
                            tag: el.tagName,
                            class: el.className?.substring(0, 50),
                            level: level
                        });
                    }
                }
            }
            return result;
        }
    """)

    print(f"\n找到 {len(category_info)} 个分类相关元素:")
    for info in category_info[:20]:
        print(f"  [{info['level']}] <{info['tag']}> {info['text']} (class: {info['class']})")

    return category_info

if __name__ == "__main__":
    explore_category_structure()
    print("\n完成!")