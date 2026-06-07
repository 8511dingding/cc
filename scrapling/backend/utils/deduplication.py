# -*- coding: utf-8 -*-
"""
去重工具模块
基于内容指纹进行去重
"""

import hashlib
from typing import Dict, Any

def generate_fingerprint(item: Dict[str, Any]) -> str:
    """
    生成内容指纹用于去重
    
    指纹基于以下字段生成：
    - 标题
    - 链接
    - 作者名称
    - 内容描述
    """
    # 收集用于生成指纹的字段
    fingerprint_fields = [
        item.get('title', '').strip(),
        item.get('url', '').strip(),
        item.get('author_name', '').strip(),
        item.get('description', '').strip()[:500]  # 描述只取前500字符
    ]
    
    # 拼接字段生成指纹
    fingerprint_str = '|||'.join(fingerprint_fields)
    
    # 使用 SHA-256 生成指纹
    return hashlib.sha256(fingerprint_str.encode('utf-8')).hexdigest()

def is_duplicate(new_item: Dict[str, Any], existing_items: list) -> bool:
    """
    检查是否为重复项
    
    Args:
        new_item: 新抓取的项目
        existing_items: 已存在的项目列表
    
    Returns:
        bool: 是否重复
    """
    new_fingerprint = generate_fingerprint(new_item)
    
    for item in existing_items:
        existing_fingerprint = item.get('fingerprint')
        if existing_fingerprint and existing_fingerprint == new_fingerprint:
            return True
    
    return False

def deduplicate_items(items: list) -> list:
    """
    对抓取的项目进行去重
    
    Args:
        items: 原始项目列表
    
    Returns:
        list: 去重后的项目列表
    """
    seen_fingerprints = set()
    unique_items = []
    
    for item in items:
        fingerprint = generate_fingerprint(item)
        item['fingerprint'] = fingerprint
        
        if fingerprint not in seen_fingerprints:
            seen_fingerprints.add(fingerprint)
            unique_items.append(item)
    
    return unique_items

def calculate_duplicate_rate(items: list) -> float:
    """
    计算重复率
    
    Args:
        items: 项目列表
    
    Returns:
        float: 重复率 (0-1)
    """
    if not items:
        return 0.0
    
    fingerprints = [generate_fingerprint(item) for item in items]
    unique_count = len(set(fingerprints))
    
    return 1.0 - (unique_count / len(fingerprints))
