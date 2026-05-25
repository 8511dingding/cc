"""
A2舆情报告生成脚本 - v9版（修正版）
基于v3模板更新数据，使用精确的统计值替换，包括百分比
"""

import pandas as pd
import zipfile
import shutil
import os
import re
from io import BytesIO

def update_report_v9(data_file: str, output_file: str):
    """基于v3模板更新数据生成v9报告"""

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

    print(f"第一阶段: {p1_count}条")
    print(f"第二阶段: {p2_count}条")
    print(f"总计: {total_count}条")

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

    # 打印统计核对
    print("\n=== 数据核对 ===")
    print(f"阶段一情绪层: {emo_p1}")
    print(f"阶段二情绪层: {emo_p2}")

    # 读取v3模板
    template_file = "/Users/jianing/Ning's Git/sentiment-analysis/reports/final/old/0524_a2舆情_报告_v3.docx"

    # 复制模板到输出文件
    shutil.copy(template_file, output_file)

    # 读取并修改XML
    with zipfile.ZipFile(output_file, 'r') as zin:
        xml_content = zin.read('word/document.xml').decode('utf-8')
        all_files = {name: zin.read(name) for name in zin.namelist()}

    # 先替换"认可"标签为"正面"（用户要求合并）
    xml_content = xml_content.replace('>认可<', '>正面<')

    # ========== 替换数据 ==========

    # 1. 替换总评论数
    xml_content = xml_content.replace('6136', str(total_count))

    # 2. 替换第一阶段评论数 (599条 -> p1_count)
    xml_content = xml_content.replace('599条', f'{p1_count}条')
    xml_content = xml_content.replace('599</w:t>', f'{p1_count}</w:t>')

    # 3. 替换第二阶段评论数 (5536条 -> p2_count)
    xml_content = xml_content.replace('5536条', f'{p2_count}条')
    xml_content = xml_content.replace('5536</w:t>', f'{p2_count}</w:t>')

    # 4. 替换认知层第一阶段数据
    # v3模板数据: 无明确认知475(79.3%), 信息混淆5(0.8%), 精准认知96(16.0%), 泛化抵触23(3.8%)
    old_cog_p1 = {
        '475': ('无明确认知', cog_p1.get('无明确认知', 475), '79.3%'),
        '5': ('信息混淆', cog_p1.get('信息混淆', 5), '0.8%'),
        '96': ('精准认知', cog_p1.get('精准认知', 96), '16.0%'),
        '23': ('泛化抵触', cog_p1.get('泛化抵触', 23), '3.8%'),
    }
    for old_val, (cog_type, new_val, old_pct) in old_cog_p1.items():
        new_pct = f'{new_val/p1_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_pct}', f'{new_pct}', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 5. 替换认知层第二阶段数据
    # v3模板数据: 无明确认知4702(85.0%), 信息混淆26(0.5%), 精准认知469(8.5%), 泛化抵触339(6.1%)
    old_cog_p2 = {
        '4702': ('无明确认知', cog_p2.get('无明确认知', 4702), '85.0%'),
        '26': ('信息混淆', cog_p2.get('信息混淆', 26), '0.5%'),
        '469': ('精准认知', cog_p2.get('精准认知', 469), '8.5%'),
        '339': ('泛化抵触', cog_p2.get('泛化抵触', 339), '6.1%'),
    }
    for old_val, (cog_type, new_val, old_pct) in old_cog_p2.items():
        new_pct = f'{new_val/p2_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_pct}', f'{new_pct}', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

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

    # 7. 替换情绪层数据（第一阶段）
    # v3模板实际值: 愤怒背叛5(0.8%), 恐慌焦虑26(4.3%), 中性444(74.1%), 负面17(2.8%), 庆幸旁观9(1.5%), 认可63(10.5%)
    old_emo_p1 = {
        '5': ('愤怒背叛', emo_p1.get('愤怒背叛', 5), '0.8%'),
        '26': ('恐慌焦虑', emo_p1.get('恐慌焦虑', 26), '4.3%'),
        '444': ('中性', emo_p1.get('中性', 444), '74.1%'),
        '17': ('负面', emo_p1.get('负面', 17), '2.8%'),
        '9': ('庆幸旁观', emo_p1.get('庆幸旁观', 9), '1.5%'),
        '63': ('正面', emo_p1.get('正面', 63), '10.5%'),
    }
    for old_val, (emo_type, new_val, old_pct) in old_emo_p1.items():
        new_pct = f'{new_val/p1_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_pct}', f'{new_pct}', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 8. 替换情绪层数据（第二阶段）
    # v3模板实际值: 愤怒背叛175(3.2%), 恐慌焦虑397(7.2%), 中性4202(76.0%), 负面133(2.4%), 庆幸旁观168(3.0%), 认可31(0.6%)
    old_emo_p2 = {
        '175': ('愤怒背叛', emo_p2.get('愤怒背叛', 175), '3.2%'),
        '397': ('恐慌焦虑', emo_p2.get('恐慌焦虑', 397), '7.2%'),
        '4202': ('中性', emo_p2.get('中性', 4202), '76.0%'),
        '133': ('负面', emo_p2.get('负面', 133), '2.4%'),
        '168': ('庆幸旁观', emo_p2.get('庆幸旁观', 168), '3.0%'),
        '31': ('正面', emo_p2.get('正面', 31), '0.6%'),
    }
    for old_val, (emo_type, new_val, old_pct) in old_emo_p2.items():
        new_pct = f'{new_val/p2_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_pct}', f'{new_pct}', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 9. 替换行动层数据（第一阶段）
    # v3模板: 暂无行动545, 寻求帮助51, 转奶流失3
    old_beh_p1 = {
        '545': ('暂无行动', beh_p1.get('暂无行动', 545)),
        '51': ('寻求帮助', beh_p1.get('寻求帮助', 51)),
        '3': ('转奶流失', beh_p1.get('转奶流失', 3)),
    }
    for old_val, (beh_type, new_val) in old_beh_p1.items():
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 10. 替换行动层数据（第二阶段）
    # v3模板: 暂无行动4890, 寻求帮助576, 转奶流失70
    old_beh_p2 = {
        '4890': ('暂无行动', beh_p2.get('暂无行动', 4890)),
        '576': ('寻求帮助', beh_p2.get('寻求帮助', 576)),
        '70': ('转奶流失', beh_p2.get('转奶流失', 70)),
    }
    for old_val, (beh_type, new_val) in old_beh_p2.items():
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 写回docx
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, content in all_files.items():
            if name == 'word/document.xml':
                zout.writestr(name, xml_content.encode('utf-8'))
            else:
                zout.writestr(name, content)

    print(f"\n报告已生成: {output_file}")
    print("\n=== 最终统计确认 ===")
    print(f"阶段一情绪层: {emo_p1}")
    print(f"阶段二情绪层: {emo_p2}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python report_v9.py <数据文件> <输出报告文件>")
    else:
        data_f = sys.argv[1]
        output_f = sys.argv[2]
        update_report_v9(data_f, output_f)