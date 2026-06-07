# -*- coding: utf-8 -*-
"""
数据库操作模块
使用 SQLite 存储爬虫数据
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, BigInteger, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()

class CrawlItem(Base):
    """爬虫数据模型"""
    __tablename__ = 'crawl_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(20), nullable=False)  # douyin, xiaohongshu
    type = Column(String(20))  # video, note
    url = Column(Text, nullable=False)
    title = Column(Text)
    description = Column(Text)
    cover_url = Column(Text)
    author_name = Column(String(255))
    author_url = Column(Text)
    author_avatar = Column(Text)
    publish_time = Column(String(100))
    like_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    share_count = Column(BigInteger, default=0)
    play_count = Column(BigInteger, default=0)
    fingerprint = Column(String(64), unique=True)  # 用于去重
    crawl_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        UniqueConstraint('fingerprint', name='uq_fingerprint'),
    )

class CommentItem(Base):
    """评论数据模型"""
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer)  # 关联的内容ID
    platform = Column(String(20), nullable=False)
    user_name = Column(String(255))
    avatar_url = Column(Text)
    content = Column(Text)
    comment_time = Column(String(100))
    like_count = Column(BigInteger, default=0)
    crawl_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

class CrawlTask(Base):
    """抓取任务记录"""
    __tablename__ = 'crawl_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(500), nullable=False)
    platform = Column(String(20), nullable=False)
    limit = Column(Integer, default=100)
    status = Column(String(20), default='pending')  # pending, running, completed, failed
    total_count = Column(Integer, default=0)
    saved_count = Column(Integer, default=0)
    skipped_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)

def get_db_path():
    """获取数据库路径"""
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    return f'sqlite:///{data_dir / "scrapling.db"}'

def init_db():
    """初始化数据库"""
    engine = create_engine(get_db_path(), connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)

def get_session():
    """获取数据库会话"""
    engine = create_engine(get_db_path(), connect_args={'check_same_thread': False})
    Session = sessionmaker(bind=engine)
    return Session()

def save_items(items: list, platform: str) -> tuple:
    """保存抓取的数据，自动去重"""
    session = get_session()
    saved_count = 0
    skipped_count = 0
    
    try:
        for item in items:
            # 检查是否已存在（通过fingerprint）
            existing = session.query(CrawlItem).filter_by(fingerprint=item.get('fingerprint')).first()
            
            if existing:
                skipped_count += 1
                continue
            
            # 创建新记录
            crawl_item = CrawlItem(
                platform=platform,
                type=item.get('type'),
                url=item.get('url', ''),
                title=item.get('title', ''),
                description=item.get('description', ''),
                cover_url=item.get('cover_url', ''),
                author_name=item.get('author_name', ''),
                author_url=item.get('author_url', ''),
                author_avatar=item.get('author_avatar', ''),
                publish_time=item.get('publish_time', ''),
                like_count=item.get('like_count', 0),
                comment_count=item.get('comment_count', 0),
                share_count=item.get('share_count', 0),
                play_count=item.get('play_count', 0),
                fingerprint=item.get('fingerprint', ''),
                crawl_time=datetime.fromisoformat(item.get('crawl_time', datetime.now().isoformat()))
            )
            
            session.add(crawl_item)
            saved_count += 1
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    return saved_count, skipped_count

def save_comments(comments: list, item_id: int, platform: str):
    """保存评论数据"""
    session = get_session()
    
    try:
        for comment in comments:
            comment_item = CommentItem(
                item_id=item_id,
                platform=platform,
                user_name=comment.get('user_name', ''),
                avatar_url=comment.get('avatar_url', ''),
                content=comment.get('content', ''),
                comment_time=comment.get('comment_time', ''),
                like_count=comment.get('like_count', 0),
                crawl_time=datetime.fromisoformat(comment.get('crawl_time', datetime.now().isoformat()))
            )
            session.add(comment_item)
        
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_item_count(platform: str = None) -> int:
    """获取数据总数"""
    session = get_session()
    try:
        query = session.query(CrawlItem)
        if platform:
            query = query.filter_by(platform=platform)
        return query.count()
    finally:
        session.close()

def get_items(platform: str = None, limit: int = None, order_by: str = 'like_count') -> list:
    """获取数据列表"""
    session = get_session()
    try:
        query = session.query(CrawlItem)
        if platform:
            query = query.filter_by(platform=platform)
        
        # 根据字段排序
        order_column = getattr(CrawlItem, order_by, CrawlItem.like_count)
        query = query.order_by(order_column.desc())
        
        if limit:
            query = query.limit(limit)
        
        items = query.all()
        return [item.__dict__ for item in items]
    finally:
        session.close()

def get_comments(item_id: int = None, platform: str = None) -> list:
    """获取评论列表"""
    session = get_session()
    try:
        query = session.query(CommentItem)
        if item_id:
            query = query.filter_by(item_id=item_id)
        if platform:
            query = query.filter_by(platform=platform)
        
        comments = query.all()
        return [comment.__dict__ for comment in comments]
    finally:
        session.close()

def export_data(output_path: Path, format_type: str = 'csv'):
    """导出数据"""
    import pandas as pd
    
    session = get_session()
    try:
        # 获取内容数据
        items = session.query(CrawlItem).all()
        if not items:
            print("⚠️ 数据库中没有数据")
            return
        
        # 转换为DataFrame
        data = []
        for item in items:
            data.append({
                '平台': item.platform,
                '类型': item.type,
                '标题': item.title,
                '描述': item.description,
                '链接': item.url,
                '封面图': item.cover_url,
                '作者名称': item.author_name,
                '作者链接': item.author_url,
                '作者头像': item.author_avatar,
                '发布时间': item.publish_time,
                '点赞数': item.like_count,
                '评论数': item.comment_count,
                '分享数': item.share_count,
                '播放量': item.play_count,
                '抓取时间': item.crawl_time
            })
        
        df = pd.DataFrame(data)
        
        # 根据格式导出
        if format_type == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        elif format_type == 'json':
            df.to_json(output_path, orient='records', force_ascii=False)
        elif format_type == 'xlsx':
            df.to_excel(output_path, index=False)
        
    finally:
        session.close()
