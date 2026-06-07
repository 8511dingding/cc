# -*- coding: utf-8 -*-
"""
抖音爬虫模块
支持搜索、内容抓取、评论抓取
"""

import asyncio
import json
from typing import List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from datetime import datetime
import random
import time

class DouyinCrawler:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.base_url = "https://www.douyin.com"
    
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
        # 设置随机延迟模拟人类操作
        await asyncio.sleep(random.uniform(1.5, 2.5))
    
    async def _close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def _safe_click(self, selector: str, timeout: int = 30000):
        """安全点击元素"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            await self.page.click(selector)
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return True
        except Exception as e:
            print(f"⚠️ 点击失败: {selector} - {e}")
            return False
    
    async def _safe_input(self, selector: str, text: str):
        """安全输入文本"""
        try:
            await self.page.wait_for_selector(selector)
            await self.page.fill(selector, text)
            await asyncio.sleep(random.uniform(0.5, 1.0))
            return True
        except Exception as e:
            print(f"⚠️ 输入失败: {selector} - {e}")
            return False
    
    async def get_search_count(self, keyword: str) -> int:
        """获取搜索结果数量（预抓取）"""
        try:
            await self._create_page()
            
            # 访问抖音搜索页面
            search_url = f"{self.base_url}/search/{keyword}"
            await self.page.goto(search_url, timeout=60000)
            
            # 等待页面加载
            await self.page.wait_for_selector('div[data-e2e="search-result"]', timeout=30000)
            
            # 获取结果数量
            count_selector = 'span[data-e2e="search-result-count"]'
            if await self.page.query_selector(count_selector):
                count_text = await self.page.inner_text(count_selector)
                # 提取数字
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
            
            # 访问搜索页面
            search_url = f"{self.base_url}/search/{keyword}"
            await self.page.goto(search_url, timeout=60000)
            
            # 等待搜索结果
            await self.page.wait_for_selector('div[data-e2e="search-result-list"]', timeout=30000)
            
            # 滚动加载更多内容
            scroll_count = 0
            max_scroll = (limit // 10) + 5
            
            while len(items) < limit and scroll_count < max_scroll:
                # 提取当前页面的视频卡片
                video_cards = await self.page.query_selector_all('div[data-e2e="search-video-card"]')
                
                for card in video_cards[:limit - len(items)]:
                    item = await self._extract_video_info(card)
                    if item:
                        items.append(item)
                        print(f"📥 已抓取: {len(items)}/{limit}")
                
                # 滚动加载更多
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(random.uniform(2, 4))
                scroll_count += 1
            
            print(f"🔄 滚动次数: {scroll_count}")
            
        except Exception as e:
            print(f"❌ 抓取失败: {e}")
        finally:
            await self._close()
        
        return items
    
    async def _extract_video_info(self, card) -> Dict[str, Any]:
        """提取视频信息"""
        try:
            # 获取视频链接
            link_elem = await card.query_selector('a')
            video_url = await link_elem.get_attribute('href') if link_elem else ''
            
            # 获取封面图
            cover_elem = await card.query_selector('img')
            cover_url = await cover_elem.get_attribute('src') if cover_elem else ''
            
            # 获取标题
            title_elem = await card.query_selector('span[data-e2e="search-video-title"]')
            title = await title_elem.inner_text() if title_elem else ''
            
            # 获取互动数据
            stats_elems = await card.query_selector_all('span[data-e2e="video-stat"]')
            stats = {
                'like': 0,
                'comment': 0,
                'share': 0,
                'play': 0
            }
            
            for i, stat in enumerate(stats_elems):
                text = await stat.inner_text()
                num = self._parse_number(text)
                if i == 0:
                    stats['play'] = num
                elif i == 1:
                    stats['like'] = num
                elif i == 2:
                    stats['comment'] = num
                elif i == 3:
                    stats['share'] = num
            
            # 获取作者信息
            author_elem = await card.query_selector('span[data-e2e="search-video-author-name"]')
            author_name = await author_elem.inner_text() if author_elem else ''
            
            author_link_elem = await card.query_selector('a[data-e2e="search-video-author"]')
            author_url = await author_link_elem.get_attribute('href') if author_link_elem else ''
            
            # 获取发布时间
            time_elem = await card.query_selector('span[data-e2e="search-video-time"]')
            publish_time = await time_elem.inner_text() if time_elem else ''
            
            return {
                'platform': 'douyin',
                'type': 'video',
                'url': video_url,
                'title': title,
                'cover_url': cover_url,
                'author_name': author_name,
                'author_url': author_url,
                'publish_time': publish_time,
                'like_count': stats['like'],
                'comment_count': stats['comment'],
                'share_count': stats['share'],
                'play_count': stats['play'],
                'crawl_time': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ 提取视频信息失败: {e}")
            return None
    
    async def crawl_comments(self, video_url: str, limit: int = 100) -> List[Dict[str, Any]]:
        """抓取视频评论"""
        comments = []
        try:
            await self._create_page()
            await self.page.goto(video_url, timeout=60000)
            
            # 等待评论区加载
            await self.page.wait_for_selector('div[data-e2e="comment-list"]', timeout=30000)
            
            scroll_count = 0
            max_scroll = (limit // 20) + 3
            
            while len(comments) < limit and scroll_count < max_scroll:
                comment_items = await self.page.query_selector_all('div[data-e2e="comment-item"]')
                
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
            # 用户名
            user_elem = await item.query_selector('span[data-e2e="comment-user-name"]')
            user_name = await user_elem.inner_text() if user_elem else ''
            
            # 用户头像
            avatar_elem = await item.query_selector('img[data-e2e="comment-avatar"]')
            avatar_url = await avatar_elem.get_attribute('src') if avatar_elem else ''
            
            # 评论内容
            content_elem = await item.query_selector('span[data-e2e="comment-content"]')
            content = await content_elem.inner_text() if content_elem else ''
            
            # 评论时间
            time_elem = await item.query_selector('span[data-e2e="comment-time"]')
            comment_time = await time_elem.inner_text() if time_elem else ''
            
            # 点赞数
            like_elem = await item.query_selector('span[data-e2e="comment-like"]')
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
        直接通过URL抓取单个视频内容
        
        Args:
            url: 抖音视频链接
            
        Returns:
            视频信息字典，失败返回None
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
            await self.page.wait_for_selector('div[data-e2e="video-detail"]', timeout=30000)
            
            # 获取视频标题
            title_elem = await self.page.query_selector('h1[data-e2e="video-title"]')
            title = await title_elem.inner_text() if title_elem else ''
            
            # 获取封面图
            cover_elem = await self.page.query_selector('img[data-e2e="video-cover"]')
            cover_url = await cover_elem.get_attribute('src') if cover_elem else ''
            
            # 获取作者信息
            author_name_elem = await self.page.query_selector('span[data-e2e="user-name"]')
            author_name = await author_name_elem.inner_text() if author_name_elem else ''
            
            author_url_elem = await self.page.query_selector('a[data-e2e="user-link"]')
            author_url = await author_url_elem.get_attribute('href') if author_url_elem else ''
            if author_url and not author_url.startswith('http'):
                author_url = self.base_url + author_url
            
            author_avatar_elem = await self.page.query_selector('img[data-e2e="user-avatar"]')
            author_avatar = await author_avatar_elem.get_attribute('src') if author_avatar_elem else ''
            
            # 获取互动数据
            stats_elems = await self.page.query_selector_all('div[data-e2e="video-stats-item"]')
            stats = {'like': 0, 'comment': 0, 'share': 0, 'play': 0}
            
            for stat in stats_elems:
                text = await stat.inner_text()
                if '赞' in text:
                    stats['like'] = self._parse_number(text)
                elif '评论' in text:
                    stats['comment'] = self._parse_number(text)
                elif '分享' in text:
                    stats['share'] = self._parse_number(text)
                elif '播放' in text or '次观看' in text:
                    stats['play'] = self._parse_number(text)
            
            # 获取发布时间
            time_elem = await self.page.query_selector('span[data-e2e="upload-time"]')
            publish_time = await time_elem.inner_text() if time_elem else ''
            
            result = {
                'platform': 'douyin',
                'type': 'video',
                'url': url,
                'title': title,
                'cover_url': cover_url,
                'author_name': author_name,
                'author_url': author_url,
                'author_avatar': author_avatar,
                'publish_time': publish_time,
                'like_count': stats['like'],
                'comment_count': stats['comment'],
                'share_count': stats['share'],
                'play_count': stats['play'],
                'crawl_time': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 抓取URL失败 {url}: {e}")
            return None
        finally:
            await self._close()
    
    def _parse_number(self, text: str) -> int:
        """解析数字字符串（支持万/亿单位）"""
        if not text:
            return 0
        
        text = text.strip()
        try:
            if '万' in text:
                return int(float(text.replace('万', '')) * 10000)
            elif '亿' in text:
                return int(float(text.replace('亿', '')) * 100000000)
            elif 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            else:
                return int(''.join(filter(str.isdigit, text)))
        except:
            return 0
