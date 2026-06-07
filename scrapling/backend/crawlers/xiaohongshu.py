# -*- coding: utf-8 -*-
"""
小红书爬虫模块
支持搜索、内容抓取、评论抓取
"""

import asyncio
import json
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime
import random
import time

class XiaohongshuCrawler:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.base_url = "https://www.xiaohongshu.com"
    
    async def _init_browser(self):
        """初始化浏览器"""
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
    
    async def _create_page(self):
        """创建新页面"""
        await self._init_browser()
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        await asyncio.sleep(random.uniform(1.5, 2.5))
    
    async def _close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def get_search_count(self, keyword: str) -> int:
        """获取搜索结果数量（预抓取）"""
        try:
            await self._create_page()
            
            search_url = f"{self.base_url}/search_result?keyword={keyword}"
            await self.page.goto(search_url, timeout=60000)
            
            # 等待页面加载
            await self.page.wait_for_selector('div.note-list', timeout=30000)
            
            # 获取结果数量
            count_selector = 'div.search-header-info span'
            if await self.page.query_selector(count_selector):
                count_text = await self.page.inner_text(count_selector)
                import re
                match = re.search(r'(\d+)', count_text)
                if match:
                    return int(match.group(1))
            
            return 0
        except Exception as e:
            print(f"❌ 获取数量失败: {e}")
            return 0
        finally:
            await self._close()
    
    async def search_and_crawl(self, keyword: str, limit: int = 100) -> List[Dict[str, Any]]:
        """搜索并抓取内容"""
        items = []
        try:
            await self._create_page()
            
            search_url = f"{self.base_url}/search_result?keyword={keyword}"
            await self.page.goto(search_url, timeout=60000)
            
            await self.page.wait_for_selector('div.note-list', timeout=30000)
            
            scroll_count = 0
            max_scroll = (limit // 12) + 5
            
            while len(items) < limit and scroll_count < max_scroll:
                note_cards = await self.page.query_selector_all('div.note-item')
                
                for card in note_cards[:limit - len(items)]:
                    item = await self._extract_note_info(card)
                    if item:
                        items.append(item)
                        print(f"📥 已抓取: {len(items)}/{limit}")
                
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(2, 4))
                scroll_count += 1
            
            print(f"🔄 滚动次数: {scroll_count}")
            
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
        finally:
            await self._close()
        
        return items
    
    async def _extract_note_info(self, card) -> Dict[str, Any]:
        """提取笔记信息"""
        try:
            # 获取笔记链接
            link_elem = await card.query_selector('a')
            note_url = await link_elem.get_attribute('href') if link_elem else ''
            if note_url and not note_url.startswith('http'):
                note_url = self.base_url + note_url
            
            # 获取封面图
            cover_elem = await card.query_selector('img')
            cover_url = await cover_elem.get_attribute('src') if cover_elem else ''
            
            # 获取标题
            title_elem = await card.query_selector('div.note-title')
            title = await title_elem.inner_text() if title_elem else ''
            
            # 获取内容摘要
            desc_elem = await card.query_selector('div.note-desc')
            description = await desc_elem.inner_text() if desc_elem else ''
            
            # 获取互动数据
            stats_elems = await card.query_selector_all('div.note-stats span')
            stats = {'like': 0, 'comment': 0, 'share': 0}
            
            for i, stat in enumerate(stats_elems):
                text = await stat.inner_text()
                num = self._parse_number(text)
                if i == 0:
                    stats['like'] = num
                elif i == 1:
                    stats['comment'] = num
                elif i == 2:
                    stats['share'] = num
            
            # 获取作者信息
            author_elem = await card.query_selector('div.user-name')
            author_name = await author_elem.inner_text() if author_elem else ''
            
            author_avatar_elem = await card.query_selector('img.user-avatar')
            author_avatar = await author_avatar_elem.get_attribute('src') if author_avatar_elem else ''
            
            # 获取发布时间
            time_elem = await card.query_selector('div.note-time')
            publish_time = await time_elem.inner_text() if time_elem else ''
            
            return {
                'platform': 'xiaohongshu',
                'type': 'note',
                'url': note_url,
                'title': title,
                'description': description,
                'cover_url': cover_url,
                'author_name': author_name,
                'author_avatar': author_avatar,
                'publish_time': publish_time,
                'like_count': stats['like'],
                'comment_count': stats['comment'],
                'share_count': stats['share'],
                'crawl_time': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ 提取笔记信息失败: {e}")
            return None
    
    async def crawl_comments(self, note_url: str, limit: int = 100) -> List[Dict[str, Any]]:
        """抓取笔记评论"""
        comments = []
        try:
            await self._create_page()
            await self.page.goto(note_url, timeout=60000)
            
            await self.page.wait_for_selector('div.comment-list', timeout=30000)
            
            scroll_count = 0
            max_scroll = (limit // 20) + 3
            
            while len(comments) < limit and scroll_count < max_scroll:
                comment_items = await self.page.query_selector_all('div.comment-item')
                
                for item in comment_items[:limit - len(comments)]:
                    comment = await self._extract_comment(item)
                    if comment:
                        comments.append(comment)
                
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(1.5, 2.5))
                scroll_count += 1
            
        except Exception as e:
            print(f"❌ 抓取评论失败: {e}")
        finally:
            await self._close()
        
        return comments
    
    async def _extract_comment(self, item) -> Dict[str, Any]:
        """提取评论信息"""
        try:
            user_elem = await item.query_selector('div.user-name')
            user_name = await user_elem.inner_text() if user_elem else ''
            
            avatar_elem = await item.query_selector('img.user-avatar')
            avatar_url = await avatar_elem.get_attribute('src') if avatar_elem else ''
            
            content_elem = await item.query_selector('div.comment-content')
            content = await content_elem.inner_text() if content_elem else ''
            
            time_elem = await item.query_selector('div.comment-time')
            comment_time = await time_elem.inner_text() if time_elem else ''
            
            like_elem = await item.query_selector('div.comment-like')
            like_count = self._parse_number(await like_elem.inner_text()) if like_elem else 0
            
            return {
                'user_name': user_name,
                'avatar_url': avatar_url,
                'content': content,
                'comment_time': comment_time,
                'like_count': like_count,
                'crawl_time': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ 提取评论失败: {e}")
            return None
    
    async def crawl_by_url(self, url: str) -> Dict[str, Any]:
        """
        直接通过URL抓取单个笔记内容
        
        Args:
            url: 小红书笔记链接
            
        Returns:
            笔记信息字典，失败返回None
        """
        try:
            await self._create_page()
            
            # 确保URL完整
            if not url.startswith('http'):
                if url.startswith('/'):
                    url = self.base_url + url
                else:
                    url = self.base_url + '/' + url
            
            await self.page.goto(url, timeout=60000)
            
            # 等待页面加载
            await self.page.wait_for_selector('div.note-detail', timeout=30000)
            
            # 获取笔记标题
            title_elem = await self.page.query_selector('h1.note-title')
            title = await title_elem.inner_text() if title_elem else ''
            
            # 获取内容描述
            desc_elem = await self.page.query_selector('div.note-content')
            description = await desc_elem.inner_text() if desc_elem else ''
            
            # 获取封面图
            cover_elem = await self.page.query_selector('img.note-cover')
            cover_url = await cover_elem.get_attribute('src') if cover_elem else ''
            
            # 获取作者信息
            author_name_elem = await self.page.query_selector('span.user-name')
            author_name = await author_name_elem.inner_text() if author_name_elem else ''
            
            author_url_elem = await self.page.query_selector('a.user-link')
            author_url = await author_url_elem.get_attribute('href') if author_url_elem else ''
            if author_url and not author_url.startswith('http'):
                author_url = self.base_url + author_url
            
            author_avatar_elem = await self.page.query_selector('img.user-avatar')
            author_avatar = await author_avatar_elem.get_attribute('src') if author_avatar_elem else ''
            
            # 获取互动数据
            stats_elems = await self.page.query_selector_all('div.note-stats span')
            stats = {'like': 0, 'comment': 0, 'share': 0}
            
            for i, stat in enumerate(stats_elems):
                text = await stat.inner_text()
                num = self._parse_number(text)
                if i == 0:
                    stats['like'] = num
                elif i == 1:
                    stats['comment'] = num
                elif i == 2:
                    stats['share'] = num
            
            # 获取发布时间
            time_elem = await self.page.query_selector('span.note-time')
            publish_time = await time_elem.inner_text() if time_elem else ''
            
            result = {
                'platform': 'xiaohongshu',
                'type': 'note',
                'url': url,
                'title': title,
                'description': description,
                'cover_url': cover_url,
                'author_name': author_name,
                'author_url': author_url,
                'author_avatar': author_avatar,
                'publish_time': publish_time,
                'like_count': stats['like'],
                'comment_count': stats['comment'],
                'share_count': stats['share'],
                'play_count': 0,
                'crawl_time': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 抓取URL失败 {url}: {e}")
            return None
        finally:
            await self._close()
    
    def _parse_number(self, text: str) -> int:
        """解析数字字符串"""
        if not text:
            return 0
        
        text = text.strip()
        try:
            if '万' in text:
                return int(float(text.replace('万', '')) * 10000)
            elif '亿' in text:
                return int(float(text.replace('亿', '')) * 100000000)
            else:
                return int(''.join(filter(str.isdigit, text)))
        except:
            return 0
