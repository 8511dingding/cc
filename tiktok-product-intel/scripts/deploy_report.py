#!/usr/bin/env python3
"""
FastMOSS报告部署脚本
创建 日期文件夹 并复制最新的报告数据
"""

import os
import shutil
import json
from datetime import datetime

BASE_DIR = Path("/Applications/ServBay/www/ning_mac/FastMOSS-Report")
DATA_DIR = Path("/Applications/ServBay/www/ning_mac")

def deploy_report(date_str=None):
    """部署报告到指定日期文件夹"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    target_dir = BASE_DIR / date_str
    target_dir.mkdir(parents=True, exist_ok=True)

    files_to_copy = [
        "web_report.html",
        "report_data.json",
        "name_translations.json",
        "full_market_data.json"
    ]

    print(f"部署报告到: {target_dir}")
    for fname in files_to_copy:
        src = DATA_DIR / fname
        dst = target_dir / fname
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✓ {fname}")
        else:
            print(f"  ✗ {fname} (不存在)")

    # 更新index.html
    update_index(date_str)
    print(f"\n部署完成!")
    print(f"访问: http://192.168.31.18/FastMOSS-Report/{date_str}/web_report.html")

def update_index(date_str):
    """更新index.html的日期链接"""
    index_path = BASE_DIR / "index.html"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 检查是否已有该日期的链接
        if f'data-date="{date_str}"' not in content:
            # 简单的更新 - 实际应该解析HTML更复杂
            pass

if __name__ == "__main__":
    from pathlib import Path
    import sys

    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    deploy_report(date_arg)