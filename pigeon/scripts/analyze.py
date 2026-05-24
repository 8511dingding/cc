#!/usr/bin/env python3
"""
贝亲舆情分析系统 - 分析脚本
功能：情感分析、多标签分类、负面预警、高频词统计
"""

import pandas as pd
import re
from collections import Counter
from pathlib import Path
from datetime import datetime, timedelta

# ============== 标签关键词配置 ==============

BUYING_DRIVERS = {
    'Material_Safety': ['PPSU', '玻璃', '硅胶', '双酚A', '耐高温', '异味', '材质', '安全', '无毒', 'Tritan', '耐温'],
    'Functionality': ['防胀气', '奶嘴流速', '防漏', '呛奶', '吐奶', '流速', '吸管', '导气', '阀门', '吸吮'],
    'Convenience': ['宽口径', '清洗', '刻度', '便携', '轻', '组装', '方便', '好洗', '死角', '配件'],
    'Price_Channel': ['价格', '优惠', '促销', '正品', '渠道', '贵', '便宜', '性价比', '大促', '直播间', '囤货']
}

PAIN_POINTS = {
    'Product_Defect': ['塌陷', '漏奶', '吸管难吸', '刻度磨损', '发黄', '裂纹', '变形', '坏了', '质量', '破损', '瑕疵'],
    'Intolerance': ['不吃', '抗拒', '胀气', '吐奶', '不喝', '拒绝', '不适应', '抗拒', '厌奶'],
    'Service_Logistics': ['客服', '物流', '破损', '漏发', '退货', '态度', '少发', '错发', '包装'],
    'Price_Dissatisfaction': ['贵', '不值', '价差', '控价', '直播间', '溢价', '被刺']
}

BRAND_VALUE = {
    'Official_USP': ['自然实感', '母乳实感', '触感真实', '贝亲', '日本', '官方', '医学', '实感'],
    'Emotional_Trust': ['老牌子', '放心', '回购', '无限回购', '大宝二宝', '传承', '推荐', '种草', '信赖', '一直用']
}

# 情感关键词
POSITIVE_WORDS = ['好用', '喜欢', '回购', '推荐', '满意', '棒', '赞', '值', '放心', '安全', '宝宝喜欢', '奶量', '舒服', '方便', '赞', '好', '棒']
NEGATIVE_WORDS = ['难用', '差', '失望', '后悔', '烂', '垃圾', '漏奶', '胀气', '不吃', '抗拒', '假货', '欺骗', '坏', '破', '质量差', '坑', '黑']
NEGATION_WORDS = ['不', '没', '非', '别', '未', '无', '莫']

# ============== 分析函数 ==============

def classify_sentiment(text):
    """
    情感分类：Positive / Neutral / Negative

    Args:
        text: 评论文本

    Returns:
        str: 情感类别
    """
    text = text.lower() if text else ""

    # 统计正负面词出现次数
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text)
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text)

    # 处理否定词（简单逻辑）
    for neg_word in NEGATION_WORDS:
        if neg_word in text:
            # 检查是否有正面词跟在否定词后面
            for pos_word in POSITIVE_WORDS:
                if f"{neg_word}{pos_word}" in text:
                    neg_count += 1
                    pos_count -= 1

    if neg_count > pos_count:
        return 'Negative'
    elif pos_count > neg_count:
        return 'Positive'
    else:
        return 'Neutral'


def multi_label_classify(text):
    """
    多标签分类：对评论打上多个标签

    Args:
        text: 评论文本

    Returns:
        dict: 标签字典，格式 {'标签大类': [子标签列表]}
    """
    labels = {
        'Buying_Drivers': [],
        'Pain_Points': [],
        'Brand_Value': []
    }

    # 检查关注点标签
    for tag, keywords in BUYING_DRIVERS.items():
        for keyword in keywords:
            if keyword in text:
                if tag not in labels['Buying_Drivers']:
                    labels['Buying_Drivers'].append(tag)

    # 检查吐槽点标签
    for tag, keywords in PAIN_POINTS.items():
        for keyword in keywords:
            if keyword in text:
                if tag not in labels['Pain_Points']:
                    labels['Pain_Points'].append(tag)

    # 检查卖点心智标签
    for tag, keywords in BRAND_VALUE.items():
        for keyword in keywords:
            if keyword in text:
                if tag not in labels['Brand_Value']:
                    labels['Brand_Value'].append(tag)

    return labels


def check_negative_alert(labels_list, sentiment_list, window_days=7, threshold=0.2, growth_rate=0.3):
    """
    负面预警检测

    Args:
        labels_list: 标签列表（每个元素是multi_label_classify的返回值）
        sentiment_list: 情感列表
        window_days: 窗口天数
        threshold: 负面占比阈值
        growth_rate: 环比增长阈值

    Returns:
        dict: 预警信息
    """
    # 统计各标签的负面评论数
    tag_neg_counts = {}

    for labels, sentiment in zip(labels_list, sentiment_list):
        if sentiment == 'Negative':
            for tag in labels.get('Pain_Points', []):
                tag_neg_counts[tag] = tag_neg_counts.get(tag, 0) + 1

    # 计算负面占比
    total = len(sentiment_list)
    alerts = []

    for tag, neg_count in tag_neg_counts.items():
        neg_ratio = neg_count / total if total > 0 else 0

        if neg_ratio >= threshold:
            # 简单模拟环比增长计算
            # 实际应用中需要对比上周数据
            alert_level = 'yellow'
            if neg_ratio > 0.5:
                alert_level = 'red'
            elif neg_ratio > 0.3:
                alert_level = 'orange'

            alerts.append({
                'tag': tag,
                'negative_count': neg_count,
                'negative_ratio': neg_ratio,
                'alert_level': alert_level,
                'message': f"标签 {tag} 负面占比 {neg_ratio:.1%}，超过阈值 {threshold:.1%}"
            })

    return alerts


def word_frequency_stats(text_list, top_n=50):
    """
    高频词统计

    Args:
        text_list: 文本列表
        top_n: 返回前N个高频词

    Returns:
        list: 高频词及其频次
    """
    all_words = []

    for text in text_list:
        # 简单分词（实际应用应使用 jieba）
        words = re.findall(r'[一-龥]+', text)
        all_words.extend(words)

    # 过滤停用词
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '也', '都', '很', '要', '会', '能', '这', '那', '个', '都', '还', '着', '过', '说', '到', '上', '下', '么', '之', '从', '被', '给'}
    filtered_words = [w for w in all_words if len(w) > 1 and w not in stopwords]

    # 统计词频
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)


def topic_clustering(text_list, labels_list, top_n=10):
    """
    热点聚类（简化版）

    将相似主题的评论聚类在一起

    Returns:
        list: 主题聚类结果
    """
    # 简化实现：按标签组合聚类
    clusters = {}

    for text, labels in zip(text_list, labels_list):
        # 使用标签组合作为聚类key
        if labels['Pain_Points']:
            key = '+'.join(labels['Pain_Points'])
        elif labels['Buying_Drivers']:
            key = '+'.join(labels['Buying_Drivers'])
        elif labels['Brand_Value']:
            key = '+'.join(labels['Brand_Value'])
        else:
            key = 'Other'

        if key not in clusters:
            clusters[key] = []
        clusters[key].append(text)

    # 转换为列表格式
    result = [
        {'topic': k, 'count': len(v), 'samples': v[:3]}
        for k, v in sorted(clusters.items(), key=lambda x: -len(x[1]))
    ][:top_n]

    return result


# ============== 主分析函数 ==============

def analyze_data(input_path, output_dir=None):
    """
    分析主函数

    Args:
        input_path: 清洗后的数据路径
        output_dir: 输出目录

    Returns:
        dict: 分析结果
    """
    print(f"正在加载数据: {input_path}")
    df = pd.read_excel(input_path)

    comments = df['cleaned_comment'].tolist()

    print(f"正在分析 {len(comments)} 条评论...")

    # 情感分析
    sentiments = [classify_sentiment(c) for c in comments]

    # 多标签分类
    labels_list = [multi_label_classify(c) for c in comments]

    # 统计结果
    sentiment_counts = Counter(sentiments)

    # 标签统计
    tag_counts = {'Buying_Drivers': {}, 'Pain_Points': {}, 'Brand_Value': {}}
    for labels in labels_list:
        for category, tags in labels.items():
            for tag in tags:
                tag_counts[category][tag] = tag_counts[category].get(tag, 0) + 1

    # 高频词
    top_words = word_frequency_stats(comments)

    # 热点聚类
    clusters = topic_clustering(comments, labels_list)

    # 负面预警
    alerts = check_negative_alert(labels_list, sentiments)

    # 组装结果
    results = {
        'total_comments': len(comments),
        'sentiment_distribution': dict(sentiment_counts),
        'tag_distribution': tag_counts,
        'top_words': top_words[:30],
        'topic_clusters': clusters,
        'alerts': alerts,
        'timestamp': datetime.now().isoformat()
    }

    # 打印摘要
    print("\n========== 分析摘要 ==========")
    print(f"总评论数: {results['total_comments']}")
    print(f"情感分布: {results['sentiment_distribution']}")
    print(f"\n关注点标签分布:")
    for tag, count in results['tag_distribution']['Buying_Drivers'].items():
        print(f"  - {tag}: {count}")
    print(f"\n吐槽点标签分布:")
    for tag, count in results['tag_distribution']['Pain_Points'].items():
        print(f"  - {tag}: {count}")
    print(f"\n卖点心智标签分布:")
    for tag, count in results['tag_distribution']['Brand_Value'].items():
        print(f"  - {tag}: {count}")

    if alerts:
        print(f"\n⚠️  负面预警:")
        for alert in alerts:
            print(f"  [{alert['alert_level'].upper()}] {alert['message']}")

    # 保存结果
    if output_dir:
        output_path = Path(output_dir) / "analysis_results.xlsx"

        # 创建结果DataFrame
        results_df = pd.DataFrame([
            {'comment': c, 'sentiment': s, 'labels': str(l)}
            for c, s, l in zip(comments, sentiments, labels_list)
        ])
        results_df.to_excel(output_path, index=False)
        print(f"\n分析结果已保存至: {output_path}")

    return results


if __name__ == "__main__":
    # 示例用法
    data_dir = Path(__file__).parent.parent / "data" / "cleaned"
    output_dir = Path(__file__).parent.parent / "data" / "processed"

    cleaned_files = list(data_dir.glob("*.xlsx"))

    if cleaned_files:
        input_file = cleaned_files[0]
        results = analyze_data(input_file, output_dir)
    else:
        print("未找到清洗后的数据文件")