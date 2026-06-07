#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScrapLing - 社交媒体爬虫主入口
支持抖音、小红书内容和评论抓取
支持三种模式：关键词搜索、链接抓取、混合模式
"""

import asyncio
import argparse
import json
from pathlib import Path
from typing import List, Tuple

from crawlers.douyin import DouyinCrawler
from crawlers.xiaohongshu import XiaohongshuCrawler
from utils.db import init_db, save_items, get_item_count, export_data
from utils.deduplication import generate_fingerprint

def detect_platform(url: str) -> str:
    """
    从URL检测平台类型
    
    Args:
        url: 内容链接
        
    Returns:
        平台名称 ('douyin' 或 'xiaohongshu')
    """
    if 'douyin' in url or 'dy' in url or 'douyin.com' in url:
        return 'douyin'
    elif 'xiaohongshu' in url or 'xiaohongshu.com' in url or 'xhs' in url:
        return 'xiaohongshu'
    else:
        return 'unknown'

def load_urls_from_file(file_path: str) -> List[str]:
    """
    从文件加载URL列表
    
    Args:
        file_path: URL文件路径，每行一个URL
        
    Returns:
        URL列表
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
    except Exception as e:
        print(f"❌ 读取URL文件失败: {e}")
    
    return urls

async def crawl_by_keyword(
    keyword: str, 
    platform_name: str, 
    crawler, 
    limit: int, 
    preview: bool
) -> Tuple[int, int, int]:
    """
    按关键词搜索抓取
    
    Returns:
        (预估数量/实际保存数, 跳过数, 总数)
    """
    if preview:
        count = await crawler.get_search_count(keyword)
        print(f"📊 {platform_name} 预估数据量: {count} 条")
        return count, 0, 0
    
    print(f"🔍 搜索关键词: {keyword}")
    print(f"📝 计划抓取: {limit} 条")
    
    items = await crawler.search_and_crawl(keyword, limit)
    
    for item in items:
        item['fingerprint'] = generate_fingerprint(item)
        item['source_type'] = 'keyword'
        item['source_value'] = keyword
    
    saved_count, skipped_count = save_items(items, platform_name)
    
    print(f"✅ 成功保存: {saved_count} 条")
    print(f"⏭️ 跳过重复: {skipped_count} 条")
    
    total = get_item_count(platform_name)
    print(f"📈 {platform_name} 数据库总计: {total} 条")
    
    return saved_count, skipped_count, total

async def crawl_by_urls(
    urls: List[str], 
    platform_name: str, 
    crawler
) -> Tuple[int, int, int]:
    """
    按URL列表抓取
    
    Returns:
        (保存数, 跳过数, 总数)
    """
    print(f"🔗 开始抓取 {len(urls)} 个链接...")
    
    items = []
    for i, url in enumerate(urls, 1):
        print(f"\r📥 正在处理: {i}/{len(urls)} - {url}", end='')
        
        try:
            item = await crawler.crawl_by_url(url)
            if item:
                item['fingerprint'] = generate_fingerprint(item)
                item['source_type'] = 'url'
                item['source_value'] = url
                items.append(item)
        except Exception as e:
            print(f"\n⚠️ 抓取失败 {url}: {e}")
    
    print()
    
    if items:
        saved_count, skipped_count = save_items(items, platform_name)
        
        print(f"✅ 成功保存: {saved_count} 条")
        print(f"⏭️ 跳过重复: {skipped_count} 条")
        
        total = get_item_count(platform_name)
        print(f"📈 {platform_name} 数据库总计: {total} 条")
        
        return saved_count, skipped_count, total
    
    return 0, 0, get_item_count(platform_name)

async def main():
    parser = argparse.ArgumentParser(description='ScrapLing - 社交媒体爬虫')
    
    # 搜索模式
    parser.add_argument('--keyword', '-k', type=str, default='', help='搜索关键词')
    
    # URL模式
    parser.add_argument('--url', '-u', type=str, action='append', default=[], 
                        help='单个内容链接（可多次使用）')
    parser.add_argument('--url-file', '-uf', type=str, default='', 
                        help='包含URL列表的文件路径（每行一个URL）')
    
    # 平台选择
    parser.add_argument('--platform', '-p', type=str, choices=['douyin', 'xiaohongshu', 'all'], 
                        default='all', help='目标平台')
    
    # 抓取参数
    parser.add_argument('--limit', '-l', type=int, default=100, help='关键词搜索时的抓取数量')
    parser.add_argument('--preview', '-pre', action='store_true', help='预抓取模式（仅统计数量）')
    
    # 导出参数
    parser.add_argument('--export', '-e', action='store_true', help='导出数据')
    parser.add_argument('--export-format', type=str, choices=['csv', 'json', 'xlsx'], default='csv')
    parser.add_argument('--output', '-o', type=str, default='output', help='输出文件名')
    
    args = parser.parse_args()
    
    # 初始化数据库
    init_db()
    
    # 导出模式
    if args.export:
        output_path = Path(f"../data/{args.output}.{args.export_format}")
        export_data(output_path, args.export_format)
        print(f"✅ 数据已导出到: {output_path}")
        return
    
    # 检查是否有输入
    has_keyword = bool(args.keyword.strip())
    has_urls = len(args.url) > 0 or bool(args.url_file.strip())
    
    if not has_keyword and not has_urls:
        print("❌ 请提供关键词(--keyword)或URL(--url/--url-file)")
        parser.print_help()
        return
    
    # 加载URL列表
    urls: List[str] = []
    if args.url:
        urls.extend(args.url)
    if args.url_file:
        urls.extend(load_urls_from_file(args.url_file))
    
    # 根据URL自动检测平台（如果没有指定平台）
    platforms = []
    if args.platform == 'all':
        platforms.append(('douyin', DouyinCrawler()))
        platforms.append(('xiaohongshu', XiaohongshuCrawler()))
    elif args.platform == 'douyin':
        platforms.append(('douyin', DouyinCrawler()))
    elif args.platform == 'xiaohongshu':
        platforms.append(('xiaohongshu', XiaohongshuCrawler()))
    
    for platform_name, crawler in platforms:
        print(f"\n🚀 开始处理 {platform_name}...")
        
        # 关键词搜索模式
        if has_keyword:
            await crawl_by_keyword(args.keyword, platform_name, crawler, args.limit, args.preview)
        
        # URL抓取模式（非预览模式）
        if has_urls and not args.preview:
            # 过滤当前平台的URL
            platform_urls = [url for url in urls if detect_platform(url) == platform_name]
            
            if platform_urls:
                await crawl_by_urls(platform_urls, platform_name, crawler)
            else:
                print(f"ℹ️ 没有属于 {platform_name} 的链接")
    
    print("\n🎉 抓取任务完成！")

if __name__ == '__main__':
    asyncio.run(main())
