"""
A2舆情分析 - v11分类标记脚本
基于规则引擎：从YAML配置加载规则，支持LLM辅助和Emoji增强

使用方法：
    python tag_comments_v11.py <输入文件> <输出文件> --month 2026-06 --compare-month 2026-05

环境变量：
    ANTHROPIC_API_KEY - LLM API密钥（可选，启用时设置）
    LLM_PROVIDER - 提供商：anthropic/openai/siliconflow
    LLM_MODEL - 模型名称
"""

import pandas as pd
import sys
import os
import argparse
from pathlib import Path
from typing import Tuple, Optional

# 添加lib目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from lib.rules_engine import get_engine, RulesEngine
from lib.llm_evaluator import LLMEvaluator, calculate_confidence, get_evaluator as get_llm_evaluator
from lib.emoji_engine import EmojiEngine, get_emoji_engine


TIME_COLUMN_CANDIDATES = ['评论时间', '评论时间\ncreate_time', '评论时间 create_time', 'create_time']
CONTENT_COLUMN_CANDIDATES = ['评论内容', '评论内容 content', 'content', 'cleaned_text']


def _normalize_column_name(name: str) -> str:
    return str(name).lower().replace('\n', ' ').replace(' ', '')


def find_column(df: pd.DataFrame, explicit: Optional[str], candidates: list[str]) -> Optional[str]:
    """Find a column by explicit name, normalized name, or known candidates."""
    if explicit:
        if explicit in df.columns:
            return explicit
        explicit_norm = _normalize_column_name(explicit)
        for col in df.columns:
            if _normalize_column_name(col) == explicit_norm:
                return col
        return None

    normalized = {_normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        match = normalized.get(_normalize_column_name(candidate))
        if match:
            return match
    return None


def read_comment_sheet(input_file: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Read the intended comment sheet, preferring the cleaned pipeline's 评论数据 sheet."""
    excel = pd.ExcelFile(input_file)
    target_sheet = sheet_name
    if target_sheet is None:
        target_sheet = '评论数据' if '评论数据' in excel.sheet_names else excel.sheet_names[0]
    print(f"读取Sheet: {target_sheet}")
    return pd.read_excel(excel, sheet_name=target_sheet)


def month_series(values: pd.Series) -> pd.Series:
    """Normalize timestamp/string/datetime values to YYYY-MM month strings."""
    numeric_values = pd.to_numeric(values, errors='coerce')
    numeric_ratio = numeric_values.notna().mean() if len(values) else 0

    if numeric_ratio > 0.8:
        median_value = numeric_values.dropna().median()
        unit = 'ms' if median_value > 1e12 else 's'
        parsed = pd.to_datetime(numeric_values, unit=unit, errors='coerce')
    else:
        parsed = pd.to_datetime(values, errors='coerce')

    fallback = values.astype(str).str[:7]
    months = parsed.dt.strftime('%Y-%m')
    return months.fillna(fallback)


def previous_month(month: str) -> str:
    period = pd.Period(month, freq='M') - 1
    return str(period)


def infer_phase_months(months: pd.Series, compare_month: Optional[str], month: Optional[str]) -> tuple[str, str]:
    """Return (phase1/compare month, phase2/current month)."""
    valid_months = sorted(m for m in months.dropna().unique() if isinstance(m, str) and len(m) == 7)

    phase2_month = month
    phase1_month = compare_month

    if phase2_month is None:
        if not valid_months:
            raise ValueError("无法从评论时间推导月份，请传入 --month")
        phase2_month = valid_months[-1]

    if phase1_month is None:
        earlier_months = [m for m in valid_months if m < phase2_month]
        phase1_month = earlier_months[-1] if earlier_months else previous_month(phase2_month)

    return phase1_month, phase2_month


def run_tagging_v11(
    input_file: str,
    output_file: str = None,
    use_llm: bool = False,
    use_emoji: bool = True,
    sheet_name: Optional[str] = None,
    time_col: Optional[str] = None,
    content_col: Optional[str] = None,
    month: Optional[str] = None,
    compare_month: Optional[str] = None
) -> Tuple[Optional[pd.DataFrame], dict, int, int]:
    """
    运行v11标记流程

    Args:
        input_file: 输入Excel文件
        output_file: 输出Excel文件
        use_llm: 是否启用LLM辅助（置信度低时触发）
        use_emoji: 是否启用Emoji增强
        sheet_name: 输入Excel中的评论sheet，默认优先读取“评论数据”
        time_col: 评论时间列名，默认自动识别
        content_col: 评论内容列名，默认自动识别
        month: 当前分析月份，格式YYYY-MM，默认取数据中的最新月份
        compare_month: 对比月份，格式YYYY-MM，默认取当前月份之前的最新月份
    """
    print(f"读取数据: {input_file}")
    df = read_comment_sheet(input_file, sheet_name=sheet_name)
    print(f"原始数据: {len(df)}条")

    # 兼容中英文列名
    time_col = find_column(df, time_col, TIME_COLUMN_CANDIDATES)
    content_col = find_column(df, content_col, CONTENT_COLUMN_CANDIDATES)

    if not time_col or not content_col:
        print(f"错误：找不到评论时间或评论内容列")
        print(f"可用列: {df.columns.tolist()}")
        return None, {}, 0, 0

    # 获取规则引擎
    engine = get_engine()

    # 初始化增强模块
    llm_evaluator = None
    emoji_engine = None

    if use_llm:
        try:
            llm_evaluator = get_llm_evaluator()
            print("LLM辅助已启用（置信度<0.6时触发）")
        except Exception as e:
            print(f"[警告] LLM初始化失败: {e}")
            print("[警告] 将继续使用纯规则引擎")
            use_llm = False

    if use_emoji:
        try:
            emoji_engine = get_emoji_engine()
            print("Emoji增强已启用")
        except Exception as e:
            print(f"[警告] Emoji引擎初始化失败: {e}")
            use_emoji = False

    # 时间阶段 (兼容Unix时间戳、字符串和datetime格式)
    df['评论时间_str'] = month_series(df[time_col])
    phase1_month, phase2_month = infer_phase_months(df['评论时间_str'], compare_month, month)
    phase1_mask = df['评论时间_str'].eq(phase1_month)
    phase2_mask = df['评论时间_str'].eq(phase2_month)
    out_of_scope_count = (~(phase1_mask | phase2_mask)).sum()
    if out_of_scope_count:
        print(f"[提示] 有{out_of_scope_count}条评论不属于{phase1_month}/{phase2_month}，保留但不计入阶段统计")
    print(f"阶段月份：第一阶段={phase1_month}，第二阶段={phase2_month}")

    # 统计纯@无互动
    df['is_pure_at'] = df[content_col].apply(engine.is_pure_at_no_interaction)
    pure_at_p1 = (phase1_mask & df['is_pure_at']).sum()
    pure_at_p2 = (phase2_mask & df['is_pure_at']).sum()
    print(f"纯@无互动：第一阶段{pure_at_p1}条，第二阶段{pure_at_p2}条")

    # 需要分析的评论
    df_to_analyze = df[~df['is_pure_at']].copy()
    p1_count = (phase1_mask & ~df['is_pure_at']).sum()
    p2_count = (phase2_mask & ~df['is_pure_at']).sum()
    print(f"分析基数：第一阶段{p1_count}条，第二阶段{p2_count}条")

    # 初始化统计
    stats = {
        'cog': {'p1': {}, 'p2': {}},
        'emo': {'p1': {}, 'p2': {}},
        'act': {'p1': {}, 'p2': {}},
    }

    # 增强统计
    enhanced_stats = {
        'llm_calls': 0,
        'emoji_boosts': 0,
    }

    # 逐行处理
    for idx, row in df_to_analyze.iterrows():
        text = str(row[content_col]) if pd.notna(row[content_col]) else ''
        is_p1 = phase1_mask[idx]
        is_p2 = phase2_mask[idx]

        # 更新评论类型
        df_to_analyze.at[idx, '评论内容类型'] = engine.get_comment_type(text)

        # 更新品牌提及
        df_to_analyze.at[idx, '品牌提及'] = engine.extract_brands(text)

        # 三维分类（规则引擎）
        cog, emo, act = engine.classify(text)

        # Emoji增强
        if emoji_engine and use_emoji and emo:
            emo, _ = emoji_engine.enhance_emotion_classification(text, emo, 0.7)

        # LLM辅助（置信度低时触发）
        if llm_evaluator and use_llm:
            # 计算各层置信度
            emo_conf = calculate_confidence(text, 'emotion')
            cog_conf = calculate_confidence(text, 'cognitive')
            act_conf = calculate_confidence(text, 'action')

            # 如果情绪层置信度低，触发LLM
            if emo_conf < 0.6:
                enhanced_emo, _ = llm_evaluator.evaluate_emotion(text)
                if enhanced_emo != emo:
                    enhanced_stats['llm_calls'] += 1
                    emo = enhanced_emo

            # 如果认知层置信度低，触发LLM
            if cog_conf < 0.6:
                enhanced_cog, _ = llm_evaluator.evaluate_cognitive(text)
                if enhanced_cog != cog:
                    enhanced_stats['llm_calls'] += 1
                    cog = enhanced_cog

            # 如果行动层置信度低，触发LLM
            if act_conf < 0.6:
                enhanced_act, _ = llm_evaluator.evaluate_action(text)
                if enhanced_act != act:
                    enhanced_stats['llm_calls'] += 1
                    act = enhanced_act

        if is_p1:
            df_to_analyze.at[idx, '认知层阶段一'] = cog
            df_to_analyze.at[idx, '情绪层阶段一'] = emo
            df_to_analyze.at[idx, '行动层阶段一'] = act
            stats['cog']['p1'][cog] = stats['cog']['p1'].get(cog, 0) + 1
            stats['emo']['p1'][emo] = stats['emo']['p1'].get(emo, 0) + 1
            stats['act']['p1'][act] = stats['act']['p1'].get(act, 0) + 1
        elif is_p2:
            df_to_analyze.at[idx, '认知层阶段二'] = cog
            df_to_analyze.at[idx, '情绪层阶段二'] = emo
            df_to_analyze.at[idx, '行动层阶段二'] = act
            stats['cog']['p2'][cog] = stats['cog']['p2'].get(cog, 0) + 1
            stats['emo']['p2'][emo] = stats['emo']['p2'].get(emo, 0) + 1
            stats['act']['p2'][act] = stats['act']['p2'].get(act, 0) + 1

    # 删除临时列
    if '评论时间_str' in df_to_analyze.columns:
        df_to_analyze = df_to_analyze.drop(columns=['评论时间_str'])
    if 'is_pure_at' in df_to_analyze.columns:
        df_to_analyze = df_to_analyze.drop(columns=['is_pure_at'])

    # 打印统计
    print("\n" + "="*60)
    print("=== v11分类统计结果 ===")
    print("="*60)

    if llm_evaluator and use_llm:
        print(f"\n[增强统计]")
        print(f"  LLM调用次数: {enhanced_stats['llm_calls']}")

    print(f"\n【第一阶段】共{p1_count}条")
    print(f"  认知层: {dict(sorted(stats['cog']['p1'].items(), key=lambda x: -x[1]))}")
    print(f"  情绪层: {dict(sorted(stats['emo']['p1'].items(), key=lambda x: -x[1]))}")
    print(f"  行动层: {dict(sorted(stats['act']['p1'].items(), key=lambda x: -x[1]))}")

    print(f"\n【第二阶段】共{p2_count}条")
    print(f"  认知层: {dict(sorted(stats['cog']['p2'].items(), key=lambda x: -x[1]))}")
    print(f"  情绪层: {dict(sorted(stats['emo']['p2'].items(), key=lambda x: -x[1]))}")
    print(f"  行动层: {dict(sorted(stats['act']['p2'].items(), key=lambda x: -x[1]))}")

    # 保存
    if output_file:
        df_to_analyze.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df_to_analyze, stats, p1_count, p2_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A2舆情v11分类标记")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--sheet", dest="sheet_name", help="评论数据所在sheet，默认优先使用“评论数据”")
    parser.add_argument("--time-col", help="评论时间列名")
    parser.add_argument("--content-col", help="评论内容列名")
    parser.add_argument("--month", help="当前分析月份，格式YYYY-MM，默认取数据中的最新月份")
    parser.add_argument("--compare-month", help="对比月份，格式YYYY-MM，默认取当前月份之前的最新月份")
    parser.add_argument("--use-llm", action="store_true", help="启用LLM辅助；默认关闭以保证月度口径稳定")
    parser.add_argument("--no-emoji", action="store_true", help="禁用Emoji增强")
    args = parser.parse_args()

    run_tagging_v11(
        args.input_file,
        args.output_file,
        use_llm=args.use_llm,
        use_emoji=not args.no_emoji,
        sheet_name=args.sheet_name,
        time_col=args.time_col,
        content_col=args.content_col,
        month=args.month,
        compare_month=args.compare_month,
    )
