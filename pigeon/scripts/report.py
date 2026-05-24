#!/usr/bin/env python3
"""
贝亲舆情分析系统 - 报告生成脚本
功能：生成Word/Excel格式的舆情分析报告
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# 报告模板配置
REPORT_TITLE = "贝亲（Pigeon）抖音舆情分析报告"

TAG_CATEGORIES = {
    'Buying_Drivers': '关注点标签（Buying Drivers）',
    'Pain_Points': '吐槽点标签（Pain Points）',
    'Brand_Value': '卖点心智标签（Brand Value）'
}

SENTIMENT_LABELS = {
    'Positive': '正面',
    'Neutral': '中性',
    'Negative': '负面'
}


def format_percentage(value, total):
    """计算百分比"""
    if total == 0:
        return "0%"
    return f"{value / total * 100:.1f}%"


def generate_summary_section(results):
    """生成摘要部分"""
    total = results['total_comments']
    sentiment = results['sentiment_distribution']

    summary = {
        '分析时间': results['timestamp'],
        '数据总量': f"{total} 条评论",
        '情感分布': {
            '正面': f"{sentiment.get('Positive', 0)} 条 ({format_percentage(sentiment.get('Positive', 0), total)})",
            '中性': f"{sentiment.get('Neutral', 0)} 条 ({format_percentage(sentiment.get('Neutral', 0), total)})",
            '负面': f"{sentiment.get('Negative', 0)} 条 ({format_percentage(sentiment.get('Negative', 0), total)})"
        }
    }

    return summary


def generate_tag_section(results):
    """生成标签分布部分"""
    tag_distribution = results['tag_distribution']

    tag_report = []
    for category_key, category_name in TAG_CATEGORIES.items():
        tag_report.append(f"\n【{category_name}】")
        tags = tag_distribution.get(category_key, {})
        for tag, count in sorted(tags.items(), key=lambda x: -x[1]):
            tag_report.append(f"  - {tag}: {count} 条")

    return "\n".join(tag_report)


def generate_word_cloud_section(results):
    """生成高频词部分"""
    top_words = results['top_words']

    lines = ["\n【高频词汇 TOP 30】"]
    for i, (word, count) in enumerate(top_words, 1):
        lines.append(f"  {i}. {word} ({count}次)")

    return "\n".join(lines)


def generate_topic_cluster_section(results):
    """生成热点聚类部分"""
    clusters = results['topic_clusters']

    lines = ["\n【热点话题聚类】"]
    for i, cluster in enumerate(clusters, 1):
        lines.append(f"\n  话题 {i}: {cluster['topic']}")
        lines.append(f"  讨论量: {cluster['count']} 条")
        lines.append(f"  代表评论:")
        for sample in cluster['samples'][:2]:
            sample_text = sample[:50] + "..." if len(sample) > 50 else sample
            lines.append(f"    - {sample_text}")

    return "\n".join(lines)


def generate_alert_section(results):
    """生成负面预警部分"""
    alerts = results.get('alerts', [])

    if not alerts:
        return "\n【负面预警】无预警触发"

    lines = ["\n【⚠️ 负面预警】"]
    for alert in alerts:
        lines.append(f"  [{alert['alert_level'].upper()}] {alert['message']}")

    return "\n".join(lines)


def generate_text_report(results):
    """生成文本格式报告（用于直接输出）"""
    report = []

    report.append("=" * 60)
    report.append(f"{REPORT_TITLE}")
    report.append("=" * 60)

    # 摘要
    summary = generate_summary_section(results)
    report.append("\n【一、数据概览】")
    report.append(f"  分析时间: {summary['分析时间']}")
    report.append(f"  数据总量: {summary['数据总量']}")
    report.append("  情感分布:")
    for label, value in summary['情感分布'].items():
        report.append(f"    {label}: {value}")

    # 标签分布
    report.append("\n【二、标签分布】")
    report.append(generate_tag_section(results))

    # 高频词
    report.append(generate_word_cloud_section(results))

    # 热点聚类
    report.append(generate_topic_cluster_section(results))

    # 预警
    report.append(generate_alert_section(results))

    report.append("\n" + "=" * 60)
    report.append("报告生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    report.append("=" * 60)

    return "\n".join(report)


def generate_excel_report(results, output_path):
    """生成Excel格式报告"""

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

        # Sheet 1: 总览
        summary_data = {
            '指标': ['分析时间', '数据总量', '正面评论', '中性评论', '负面评论'],
            '数值': [
                results['timestamp'],
                results['total_comments'],
                results['sentiment_distribution'].get('Positive', 0),
                results['sentiment_distribution'].get('Neutral', 0),
                results['sentiment_distribution'].get('Negative', 0)
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='总览', index=False)

        # Sheet 2: 情感分布
        sentiment_df = pd.DataFrame([
            {'情感': k, '数量': v}
            for k, v in results['sentiment_distribution'].items()
        ])
        sentiment_df.to_excel(writer, sheet_name='情感分布', index=False)

        # Sheet 3: 标签分布
        all_tags = []
        for category, tags in results['tag_distribution'].items():
            for tag, count in tags.items():
                all_tags.append({'标签类别': category, '标签名称': tag, '数量': count})
        pd.DataFrame(all_tags).to_excel(writer, sheet_name='标签分布', index=False)

        # Sheet 4: 高频词
        word_df = pd.DataFrame(results['top_words'], columns=['词汇', '频次'])
        word_df.to_excel(writer, sheet_name='高频词', index=False)

        # Sheet 5: 热点聚类
        cluster_data = []
        for cluster in results['topic_clusters']:
            cluster_data.append({
                '话题': cluster['topic'],
                '讨论量': cluster['count']
            })
        pd.DataFrame(cluster_data).to_excel(writer, sheet_name='热点聚类', index=False)

        # Sheet 6: 预警（如果有）
        if results.get('alerts'):
            alert_df = pd.DataFrame(results['alerts'])
            alert_df.to_excel(writer, sheet_name='负面预警', index=False)

    print(f"Excel报告已保存至: {output_path}")


def generate_report(analysis_results, output_path=None, format='text'):
    """
    生成报告主函数

    Args:
        analysis_results: analyze.py 返回的分析结果
        output_path: 输出路径（若为None，则只返回报告文本）
        format: 报告格式 ('text' 或 'excel')

    Returns:
        str: 报告内容
    """
    print("正在生成报告...")

    # 生成文本报告
    text_report = generate_text_report(analysis_results)

    # 保存到文件
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'excel':
            generate_excel_report(analysis_results, output_path)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_report)
            print(f"文本报告已保存至: {output_path}")

    return text_report


if __name__ == "__main__":
    # 读取分析结果并生成报告
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    report_dir = Path(__file__).parent.parent / "reports" / "final"

    results_file = data_dir / "analysis_results.xlsx"

    if results_file.exists():
        # 从结果文件重新构建结果（实际应用中应该直接传入results字典）
        df = pd.read_excel(results_file)

        # 简化示例：直接生成示例报告
        sample_results = {
            'total_comments': 1000,
            'sentiment_distribution': {'Positive': 450, 'Neutral': 350, 'Negative': 200},
            'tag_distribution': {
                'Buying_Drivers': {'Material_Safety': 120, 'Functionality': 95, 'Convenience': 80, 'Price_Channel': 65},
                'Pain_Points': {'Product_Defect': 85, 'Intolerance': 45, 'Service_Logistics': 30, 'Price_Dissatisfaction': 25},
                'Brand_Value': {'Official_USP': 60, 'Emotional_Trust': 55}
            },
            'top_words': [('漏奶', 89), ('贝亲', 76), ('胀气', 65), ('奶嘴', 54), ('回购', 43)],
            'topic_clusters': [
                {'topic': 'Product_Defect', 'count': 85, 'samples': ['奶嘴漏奶问题', '用了一周就漏奶', '密封不好']},
                {'topic': 'Material_Safety', 'count': 120, 'samples': ['PPSU材质安全', '没有异味', '高温消毒没问题']}
            ],
            'alerts': [
                {'tag': 'Product_Defect', 'negative_count': 45, 'negative_ratio': 0.225, 'alert_level': 'yellow', 'message': '标签 Product_Defect 负面占比 22.5%，超过阈值 20.0%'}
            ],
            'timestamp': datetime.now().isoformat()
        }

        # 生成报告
        report_path = report_dir / f"舆情报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report = generate_report(sample_results, report_path, format='text')
        print("\n" + report)
    else:
        print("未找到分析结果文件，请先运行 analyze.py")