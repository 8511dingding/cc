"""
Monthly sentiment analysis pipeline.

This script provides one stable entry point for recurring monthly analysis:
clean raw exports when provided, tag comments with v11 rules, then generate the
customer Word report with data-derived denominators.
"""

import argparse
from pathlib import Path

from clean_data import clean_data
from report_v11 import generate_report_v11
from tag_comments_v11 import run_tagging_v11


def build_default_paths(month: str, prefix: str, output_dir: Path, work_dir: Path) -> dict[str, Path]:
    safe_month = month or "latest"
    return {
        "cleaned": work_dir / f"{safe_month}_{prefix}_清洗后.xlsx",
        "tagged": output_dir / f"{safe_month}_{prefix}_数据.xlsx",
        "report": output_dir / f"{safe_month}_{prefix}_报告.docx",
    }


def run_monthly_pipeline(args: argparse.Namespace) -> dict[str, Path]:
    output_dir = Path(args.output_dir)
    work_dir = Path(args.work_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    paths = build_default_paths(args.month, args.prefix, output_dir, work_dir)

    if args.cleaned_file:
        cleaned_file = Path(args.cleaned_file)
    else:
        if not args.content_file or not args.comment_file:
            raise ValueError("请提供 --cleaned-file，或同时提供 --content-file 和 --comment-file")
        cleaned_file = Path(args.cleaned_output) if args.cleaned_output else paths["cleaned"]
        clean_data(args.content_file, args.comment_file, str(cleaned_file))

    tagged_file = Path(args.tagged_output) if args.tagged_output else paths["tagged"]
    run_tagging_v11(
        str(cleaned_file),
        str(tagged_file),
        use_llm=args.use_llm,
        use_emoji=not args.no_emoji,
        sheet_name=args.sheet,
        time_col=args.time_col,
        content_col=args.content_col,
        month=args.month,
        compare_month=args.compare_month,
    )

    report_file = Path(args.report_output) if args.report_output else paths["report"]
    if not args.skip_report:
        generate_report_v11(
            str(tagged_file),
            str(report_file),
            phase1_total=args.phase1_total,
            phase2_total=args.phase2_total,
            month=args.month,
            compare_month=args.compare_month,
            time_col=args.time_col,
            template_file=args.template,
        )

    return {
        "cleaned": cleaned_file,
        "tagged": tagged_file,
        "report": report_file,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="每月舆情分析流水线")
    parser.add_argument("--month", help="当前分析月份，格式YYYY-MM；默认由数据推导")
    parser.add_argument("--compare-month", help="对比月份，格式YYYY-MM；默认取当前月份之前的最新月份")
    parser.add_argument("--prefix", default="a2舆情", help="输出文件名前缀")

    parser.add_argument("--content-file", help="原始内容文件；与 --comment-file 一起用于清洗")
    parser.add_argument("--comment-file", help="原始评论文件；与 --content-file 一起用于清洗")
    parser.add_argument("--cleaned-file", help="已清洗Excel；提供后跳过清洗")
    parser.add_argument("--cleaned-output", help="清洗输出路径")
    parser.add_argument("--tagged-output", help="标记数据输出路径")
    parser.add_argument("--report-output", help="Word报告输出路径")
    parser.add_argument("--output-dir", default="reports/final", help="最终数据和报告输出目录")
    parser.add_argument("--work-dir", default="data/processed", help="中间清洗文件输出目录")

    parser.add_argument("--sheet", help="评论数据所在sheet，默认优先使用“评论数据”")
    parser.add_argument("--time-col", help="评论时间列名")
    parser.add_argument("--content-col", help="评论内容列名")
    parser.add_argument("--template", help="Word报告模板路径")
    parser.add_argument("--phase1-total", type=int, help="第一阶段分母；默认从数据计算")
    parser.add_argument("--phase2-total", type=int, help="第二阶段分母；默认从数据计算")

    parser.add_argument("--use-llm", action="store_true", help="启用LLM辅助；默认关闭以保持月度口径稳定")
    parser.add_argument("--no-emoji", action="store_true", help="禁用Emoji增强")
    parser.add_argument("--skip-report", action="store_true", help="只生成标记数据，不生成Word报告")
    return parser.parse_args()


if __name__ == "__main__":
    outputs = run_monthly_pipeline(parse_args())
    print("\n=== 月度流水线完成 ===")
    print(f"清洗数据: {outputs['cleaned']}")
    print(f"标记数据: {outputs['tagged']}")
    print(f"Word报告: {outputs['report']}")
