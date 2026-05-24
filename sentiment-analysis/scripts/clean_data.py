"""
舆情分析 - 数据清洗脚本
用于清洗抖音/小红书原始数据，提取有效内容
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime


# 内容数据需要保留的列（前半部分）
CONTENT_COLUMNS = [
    '内容', '内容id', '作品id', '标题', '发布时间', '点赞数', '评论数', '转发数',
    '分享数', '收藏数', '作者', '作者昵称', 'ip_location'
]

# 评论数据需要保留的列（后半部分）- 7列
COMMENT_COLUMNS = [
    '评论id\ncomment_id',
    '评论时间\ncreate_time',
    'ip_location',
    '评论内容 content',
    'user_id',
    'short_user_id',
    '昵称\nnickname',
    '二级评论数\nsub_comment',
    '评论获赞\nlike_count'
]


def is_valid_content(text: str) -> bool:
    """
    判断内容是否有效可分析
    返回 True 表示有效，False 表示应过滤
    """
    if pd.isna(text) or not isinstance(text, str):
        return False

    # 去除空白后为空
    if not text.strip():
        return False

    # 检测乱码比例（简单判断：非中文非英文非数字的字符占比过高）
    cleaned = re.sub(r'[一-鿿　-〿\w\s]', '', text)
    if len(text) > 0 and len(cleaned) / len(text) > 0.7:
        return False

    # 检测纯表情/符号（评论中常见的无意义内容）
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    removed_emoji = emoji_pattern.sub('', text).strip()
    if not removed_emoji:
        return False

    # 去除表情后剩余字符过少
    if len(removed_emoji) < 3:
        return False

    return True


def clean_text(text: str) -> str:
    """
    清洗文本内容
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""

    # 去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def convert_timestamp(timestamp) -> str:
    """
    将Unix时间戳转换为可读时间格式 "2026-05-04 19:49:10"
    如果已是字符串或无法转换则返回原值
    """
    if pd.isna(timestamp):
        return ""

    try:
        # 如果是浮点数或整数
        if isinstance(timestamp, (int, float)):
            # 抖音使用的是10位时间戳（秒级）
            ts = int(timestamp)
            if ts > 1e12:  # 13位毫秒级
                ts = ts // 1000
            return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        # 如果是字符串
        elif isinstance(timestamp, str):
            # 尝试解析字符串
            try:
                ts = int(float(timestamp))
                if ts > 1e12:
                    ts = ts // 1000
                return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return timestamp
        return str(timestamp)
    except Exception:
        return str(timestamp)


def find_matching_columns(df_columns: List[str], target_columns: List[str]) -> List[str]:
    """
    在DataFrame列中查找与目标列匹配或包含的列
    支持模糊匹配（部分列名包含目标关键词）
    """
    available_cols = []
    for target in target_columns:
        target_lower = target.lower().replace('\n', ' ')
        matched = False
        for col in df_columns:
            col_lower = col.lower().replace('\n', ' ')
            # 完全匹配
            if col_lower == target_lower:
                available_cols.append(col)
                matched = True
                break
            # 包含匹配
            if target_lower in col_lower or col_lower in target_lower:
                available_cols.append(col)
                matched = True
                break
        if not matched:
            # 尝试关键词匹配
            keywords = target_lower.split()
            if all(kw in col_lower for kw in keywords if len(kw) > 2):
                available_cols.append(col)

    return available_cols


def clean_data(
    content_file: str,
    comment_file: str,
    output_file: str,
    content_text_column: str = '内容',
    comment_text_column: str = '评论内容 content'
):
    """
    清洗数据主函数 - 同时处理内容和评论数据

    Args:
        content_file: 内容数据文件路径
        comment_file: 评论数据文件路径
        output_file: 清洗后输出文件路径
        content_text_column: 内容文本列名
        comment_text_column: 评论文本列名
    """
    print(f"=== 开始数据清洗 ===")

    # 读取内容数据
    print(f"\n读取内容数据: {content_file}")
    if content_file.endswith('.xlsx'):
        content_df = pd.read_excel(content_file)
    elif content_file.endswith('.csv'):
        content_df = pd.read_csv(content_file)
    else:
        raise ValueError("不支持的内容文件格式，请使用 .xlsx 或 .csv")

    print(f"内容数据原始行数: {len(content_df)}")
    print(f"内容数据列名: {list(content_df.columns)}")

    # 读取评论数据
    print(f"\n读取评论数据: {comment_file}")
    if comment_file.endswith('.xlsx'):
        comment_df = pd.read_excel(comment_file)
    elif comment_file.endswith('.csv'):
        comment_df = pd.read_csv(comment_file)
    else:
        raise ValueError("不支持的评论文件格式，请使用 .xlsx 或 .csv")

    print(f"评论数据原始行数: {len(comment_df)}")
    print(f"评论数据列名: {list(comment_df.columns)}")

    # 过滤内容数据中的无效内容
    if content_text_column in content_df.columns:
        content_df['is_valid'] = content_df[content_text_column].apply(is_valid_content)
        valid_content_df = content_df[content_df['is_valid']].copy()
        valid_content_df['cleaned_text'] = valid_content_df[content_text_column].apply(clean_text)
        valid_content_df = valid_content_df.drop(columns=['is_valid'])
    else:
        # 尝试查找文本列
        possible_text_cols = ['内容', 'text', 'content', '评论', '正文']
        found_col = None
        for col in possible_text_cols:
            if col in content_df.columns:
                found_col = col
                break
        if found_col:
            content_text_column = found_col
            content_df['is_valid'] = content_df[content_text_column].apply(is_valid_content)
            valid_content_df = content_df[content_df['is_valid']].copy()
            valid_content_df['cleaned_text'] = valid_content_df[content_text_column].apply(clean_text)
            valid_content_df = valid_content_df.drop(columns=['is_valid'])
        else:
            valid_content_df = content_df.copy()
            valid_content_df['cleaned_text'] = ''

    print(f"有效内容数据行数: {len(valid_content_df)}")

    # 过滤评论数据中的无效内容
    if comment_text_column in comment_df.columns:
        comment_df['is_valid'] = comment_df[comment_text_column].apply(is_valid_content)
        valid_comment_df = comment_df[comment_df['is_valid']].copy()
        valid_comment_df['cleaned_text'] = valid_comment_df[comment_text_column].apply(clean_text)
        valid_comment_df = valid_comment_df.drop(columns=['is_valid'])
    else:
        # 尝试查找文本列
        possible_text_cols = ['评论内容', 'content', 'comment', '评论', 'text']
        found_col = None
        for col in possible_text_cols:
            if col in comment_df.columns:
                found_col = col
                break
        if found_col:
            comment_text_column = found_col
            comment_df['is_valid'] = comment_df[comment_text_column].apply(is_valid_content)
            valid_comment_df = comment_df[comment_df['is_valid']].copy()
            valid_comment_df['cleaned_text'] = valid_comment_df[comment_text_column].apply(clean_text)
            valid_comment_df = valid_comment_df.drop(columns=['is_valid'])
        else:
            valid_comment_df = comment_df.copy()
            valid_comment_df['cleaned_text'] = ''

    print(f"有效评论数据行数: {len(valid_comment_df)}")

    # 转换评论时间为可读格式 "2026-05-04 19:49:10"
    if '评论时间\ncreate_time' in valid_comment_df.columns:
        valid_comment_df['评论时间\ncreate_time'] = valid_comment_df['评论时间\ncreate_time'].apply(convert_timestamp)
    elif 'create_time' in valid_comment_df.columns:
        valid_comment_df['create_time'] = valid_comment_df['create_time'].apply(convert_timestamp)

    # 选择内容数据需要的列
    content_cols_to_keep = []
    for target in CONTENT_COLUMNS:
        matched = find_matching_columns(list(valid_content_df.columns), [target])
        content_cols_to_keep.extend(matched)

    # 去重但保持顺序
    content_cols_to_keep = list(dict.fromkeys(content_cols_to_keep))

    # 确保 cleaned_text 在内容列中
    if 'cleaned_text' not in content_cols_to_keep:
        content_cols_to_keep.append('cleaned_text')

    # 选择评论数据需要的列（7列）
    comment_cols_to_keep = []
    for target in COMMENT_COLUMNS:
        matched = find_matching_columns(list(valid_comment_df.columns), [target])
        comment_cols_to_keep.extend(matched)

    # 去重但保持顺序
    comment_cols_to_keep = list(dict.fromkeys(comment_cols_to_keep))

    # 确保 cleaned_text 在评论列中
    if 'cleaned_text' not in comment_cols_to_keep:
        comment_cols_to_keep.append('cleaned_text')

    print(f"\n内容数据保留列: {content_cols_to_keep}")
    print(f"评论数据保留列: {comment_cols_to_keep}")

    # 准备最终数据
    content_final = valid_content_df[content_cols_to_keep].copy()
    comment_final = valid_comment_df[comment_cols_to_keep].copy()

    # 添加数据来源标记
    content_final['数据来源'] = '内容'
    comment_final['数据来源'] = '评论'

    # 保存到同一个Excel的不同sheet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 第一个sheet：内容数据
        content_final.to_excel(writer, sheet_name='内容数据', index=False)
        # 第二个sheet：评论数据
        comment_final.to_excel(writer, sheet_name='评论数据', index=False)

    print(f"\n=== 清洗完成 ===")
    print(f"内容数据: {len(content_final)} 行")
    print(f"评论数据: {len(comment_final)} 行")
    print(f"输出文件: {output_file}")
    print(f"  - Sheet1: 内容数据")
    print(f"  - Sheet2: 评论数据")

    return content_final, comment_final


def clean_single_file(
    input_file: str,
    output_file: str,
    text_column: str = '内容',
    columns_to_keep: List[str] = None
):
    """
    清洗单个数据文件

    Args:
        input_file: 原始数据文件路径
        output_file: 清洗后输出文件路径
        text_column: 文本列名
        columns_to_keep: 需要保留的列名列表，None则保留所有
    """
    print(f"读取原始数据: {input_file}")

    if input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    elif input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        raise ValueError("不支持的文件格式，请使用 .xlsx 或 .csv")

    print(f"原始数据行数: {len(df)}")
    print(f"原始数据列名: {list(df.columns)}")

    # 过滤无效内容
    if text_column in df.columns:
        df['is_valid'] = df[text_column].apply(is_valid_content)
        valid_df = df[df['is_valid']].copy()
        valid_df['cleaned_text'] = valid_df[text_column].apply(clean_text)
        valid_df = valid_df.drop(columns=['is_valid'])
    else:
        # 尝试查找文本列
        possible_cols = ['内容', '评论', 'text', 'content', 'comment']
        found_col = None
        for col in possible_cols:
            if col in df.columns:
                found_col = col
                break
        if found_col:
            text_column = found_col
            print(f"使用列名: {text_column}")
            df['is_valid'] = df[text_column].apply(is_valid_content)
            valid_df = df[df['is_valid']].copy()
            valid_df['cleaned_text'] = valid_df[text_column].apply(clean_text)
            valid_df = valid_df.drop(columns=['is_valid'])
        else:
            valid_df = df.copy()
            valid_df['cleaned_text'] = ''

    # 选择保留的列
    if columns_to_keep:
        cols_to_use = []
        for target in columns_to_keep:
            matched = find_matching_columns(list(valid_df.columns), [target])
            cols_to_use.extend(matched)
        cols_to_use = list(dict.fromkeys(cols_to_use))
        if 'cleaned_text' not in cols_to_use:
            cols_to_use.append('cleaned_text')
        valid_df = valid_df[cols_to_use]
        print(f"保留列: {cols_to_use}")

    print(f"有效数据行数: {len(valid_df)}")
    print(f"过滤掉: {len(df) - len(valid_df)} 行无效内容")

    # 保存结果 - 第一个sheet
    valid_df.to_excel(output_file, index=False, sheet_name='清洗后数据')
    print(f"清洗完成，保存至: {output_file}")

    return valid_df


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法:")
        print("  单独文件清洗: python clean_data.py <输入文件> <输出文件> [文本列名]")
        print("  内容和评论合并: python clean_data.py <内容文件> <评论文件> <输出文件> --merge")
    else:
        if '--merge' in sys.argv:
            # 合并模式
            argv = [a for a in sys.argv if a != '--merge']
            if len(argv) < 4:
                print("合并模式用法: python clean_data.py <内容文件> <评论文件> <输出文件> --merge")
            else:
                content_f = argv[1]
                comment_f = argv[2]
                output_f = argv[3]
                clean_data(content_f, comment_f, output_f)
        else:
            # 单文件模式
            input_f = sys.argv[1]
            output_f = sys.argv[2]
            col = sys.argv[3] if len(sys.argv) > 3 else '内容'
            clean_single_file(input_f, output_f, col)