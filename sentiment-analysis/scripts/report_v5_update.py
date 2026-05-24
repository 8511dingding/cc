"""
A2舆情报告生成脚本 - v5版（保持v3格式）
只更新数据，不改变任何格式和结构
"""

import pandas as pd
import zipfile
import shutil
import os
import re
from io import BytesIO

def update_report_v3_to_v5(data_file: str, output_file: str):
    """基于v3模板更新数据生成v5报告"""

    print(f"读取数据: {data_file}")
    df = pd.read_excel(data_file)

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    df_p1 = df[phase1_mask]
    df_p2 = df[phase2_mask]
    p1_count = len(df_p1)
    p2_count = len(df_p2)
    total_count = len(df)

    # 计算各维度数据
    # 评论类型
    type_p1 = df_p1['评论内容类型'].value_counts().to_dict()
    type_p2 = df_p2['评论内容类型'].value_counts().to_dict()

    # 认知层
    cog_p1 = df_p1['认知层阶段一'].value_counts().to_dict()
    cog_p2 = df_p2['认知层阶段二'].value_counts().to_dict()

    # 情绪层
    emo_p1 = df_p1['情绪层阶段一'].value_counts().to_dict()
    emo_p2 = df_p2['情绪层阶段二'].value_counts().to_dict()

    # 行动层
    beh_p1 = df_p1['行动层阶段一'].value_counts().to_dict()
    beh_p2 = df_p2['行动层阶段二'].value_counts().to_dict()

    # 品牌提及
    all_brands = []
    for brands_str in df['品牌提及']:
        if pd.notna(brands_str) and isinstance(brands_str, str) and brands_str.strip():
            all_brands.extend(brands_str.split('|'))
    brand_counts = pd.Series(all_brands).value_counts().to_dict()

    # 读取v3模板
    template_file = "/Users/jianing/Ning's Git/sentiment-analysis/reports/final/old/0524_a2舆情_报告_v3.docx"

    # 复制模板到输出文件
    shutil.copy(template_file, output_file)

    # 读取并修改XML
    with zipfile.ZipFile(output_file, 'r') as zin:
        xml_content = zin.read('word/document.xml').decode('utf-8')
        all_files = {name: zin.read(name) for name in zin.namelist()}

    # ========== 替换数据 ==========

    # 1. 替换总评论数 6136 -> total_count
    xml_content = xml_content.replace('6136', str(total_count))

    # 2. 替换第一阶段 599 -> p1_count
    xml_content = xml_content.replace('599条', f'{p1_count}条')
    xml_content = xml_content.replace('599</w:t>', f'{p1_count}</w:t>')

    # 3. 替换第二阶段 5536 -> p2_count
    xml_content = xml_content.replace('5536条', f'{p2_count}条')
    xml_content = xml_content.replace('5536</w:t>', f'{p2_count}</w:t>')

    # 4. 替换认知层第一阶段数据
    # 无明确认知: 475 -> 实际值, 79.3% -> 实际百分比
    old_cog_p1 = {
        '475': ('475', f'{475/p1_count*100:.1f}%'),
        '5': ('5', f'{5/p1_count*100:.1f}%'),
        '96': ('96', f'{96/p1_count*100:.1f}%'),
        '23': ('23', f'{23/p1_count*100:.1f}%'),
    }
    for old_val, (new_val, new_pct) in old_cog_p1.items():
        cog_val = cog_p1.get('无明确认知' if old_val == '475' else ('信息混淆' if old_val == '5' else ('精准认知' if old_val == '96' else '泛化抵触')), int(old_val))
        cog_pct = f'{cog_val/p1_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_val}%', f'{cog_pct}%', 1)  # 替换百分比
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{cog_val}</w:t>', 1)  # 替换数值

    # 5. 替换认知层第二阶段数据
    old_cog_p2 = {
        '4702': '4702',
        '26': '26',
        '469': '469',
        '339': '339',
    }
    for old_val in old_cog_p2:
        cog_type = '无明确认知' if old_val == '4702' else ('信息混淆' if old_val == '26' else ('精准认知' if old_val == '469' else '泛化抵触'))
        cog_val = cog_p2.get(cog_type, int(old_val))
        cog_pct = f'{cog_val/p2_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_val}%', f'{cog_pct}%', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{cog_val}</w:t>', 1)

    # 6. 替换评论类型数据
    # 第一阶段: 507, 20, 16, 56
    type_p1_mapping = {'普通内容': 507, '@某人互动': 20, '长内容(>100字)': 16, '提及竞品': 56}
    for t, old_v in type_p1_mapping.items():
        new_v = type_p1.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 第二阶段: 3096, 1658, 174, 608
    type_p2_mapping = {'普通内容': 3096, '@某人互动': 1658, '长内容(>100字)': 174, '提及竞品': 608}
    for t, old_v in type_p2_mapping.items():
        new_v = type_p2.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 7. 替换情绪层数据
    # 第一阶段情绪层
    old_emo_p1 = {
        '愤怒背叛': 5,
        '恐慌焦虑': 26,
        '中性': 442,
        '负面': 17,
        '庆幸旁观': 9,
        '认可': 98  # 会变成正面
    }
    for emo, old_v in old_emo_p1.items():
        new_v = emo_p1.get(emo, old_v)
        if new_v != old_v:
            xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 第二阶段情绪层
    old_emo_p2 = {
        '愤怒背叛': 175,
        '恐慌焦虑': 397,
        '中性': 4202,
        '负面': 133,
        '庆幸旁观': 168,
        '认可': 31  # 会变成正面
    }
    for emo, old_v in old_emo_p2.items():
        new_v = emo_p2.get(emo, old_v)
        if new_v != old_v:
            xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 8. 替换行动层数据
    # 第一阶段
    old_beh_p1 = {'暂无行动': 545, '寻求帮助': 51, '转奶流失': 3}
    for beh, old_v in old_beh_p1.items():
        new_v = beh_p1.get(beh, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 第二阶段
    old_beh_p2 = {'暂无行动': 4890, '寻求帮助': 576, '转奶流失': 70}
    for beh, old_v in old_beh_p2.items():
        new_v = beh_p2.get(beh, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 写回docx
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, content in all_files.items():
            if name == 'word/document.xml':
                zout.writestr(name, xml_content.encode('utf-8'))
            else:
                zout.writestr(name, content)

    print(f"报告已生成: {output_file}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python report_v5_update.py <数据文件> <输出报告文件>")
    else:
        data_f = sys.argv[1]
        output_f = sys.argv[2]
        update_report_v3_to_v5(data_f, output_f)