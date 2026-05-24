#!/usr/bin/env python3
"""
贝亲舆情分析系统 - 数据清洗脚本
功能：读取原始抖音评论数据，清洗无效内容，输出可分析的干净数据
"""

import pandas as pd
import re
import os
from pathlib import Path

# 停用词表
STOPWORDS = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '也', '都', '很',
    '要', '会', '能', '对', '与', '为', '但', '这', '那', '就', '都', '还',
    '个', '以', '及', '等', '着', '过', '说', '到', '去', '来', '上', '下',
    '么', '之', '从', '被', '给', '让', '把', '用', '做', '当', '却', '却'
}

# 品牌名称统一映射
BRAND_MAPPING = {
    '贝亲': ['贝亲', 'pigeon', 'Pigeon', 'PIGEON'],
    '世喜': ['世喜', 'shisei', 'Shisei', 'SHISEI'],
    '可优比': ['可优比', 'kub', 'Kub'],
    '布朗博士': ['布朗博士', 'Dr.Brown', 'Dr. Brown', 'dr brown']
}

def clean_text(text):
    """清洗单条评论文本"""
    if pd.isna(text) or not isinstance(text, str):
        return ""

    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)

    # 去除特殊字符（保留中文、英文、数字、常用标点）
    text = re.sub(r'[^一-龥a-zA-Z0-9\s.,!?！？。，、；；：：""''（）()【】\[\]]', '', text)

    # 去除URL
    text = re.sub(r'http[s]?://\S+', '', text)

    return text.strip()

def remove_stopwords(text):
    """分词并去除停用词"""
    # 简单按字符级处理，实际应用应用 jieba 分词
    words = text.split()
    return ' '.join([w for w in words if w not in STOPWORDS and len(w) > 1])

def normalize_brands(text):
    """统一品牌名称"""
    for brand, aliases in BRAND_MAPPING.items():
        for alias in aliases:
            text = re.sub(re.escape(alias), brand, text, flags=re.IGNORECASE)
    return text

def load_raw_data(file_path):
    """加载原始数据"""
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")

def clean_data(input_path, output_path):
    """
    数据清洗主函数

    Args:
        input_path: 原始数据路径（CSV/Excel/JSON）
        output_path: 清洗后数据输出路径
    """
    print(f"正在读取数据: {input_path}")
    df = load_raw_data(input_path)

    print(f"原始数据量: {len(df)} 条")

    # 清洗文本
    if 'comment' in df.columns:
        df['cleaned_comment'] = df['comment'].apply(clean_text)
    elif 'text' in df.columns:
        df['cleaned_comment'] = df['text'].apply(clean_text)
    else:
        # 尝试第一列
        first_col = df.columns[0]
        df['cleaned_comment'] = df[first_col].apply(clean_text)

    # 过滤空评论
    df = df[df['cleaned_comment'].str.len() > 0]
    print(f"清洗后数据量: {len(df)} 条")

    # 统一品牌名称
    df['normalized_comment'] = df['cleaned_comment'].apply(normalize_brands)

    # 保存清洗后的数据
    df.to_excel(output_path, index=False)
    print(f"清洗后数据已保存至: {output_path}")

    return df

if __name__ == "__main__":
    # 示例用法
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir = Path(__file__).parent.parent / "data" / "cleaned"

    # 查找原始数据文件
    raw_files = list(data_dir.glob("*.csv")) + list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*.json"))

    if raw_files:
        input_file = raw_files[0]
        output_file = output_dir / f"cleaned_{input_file.stem}.xlsx"
        clean_data(input_file, output_file)
    else:
        print("未找到原始数据文件，请将数据放入 data/raw 目录")