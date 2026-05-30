"""
A2舆情报告生成脚本 - v11版
基于v10数据，使用用户指定的分母（586/4093）
"""

import pandas as pd
import zipfile
import shutil
import re

def generate_report_v11(data_file: str, output_file: str, phase1_total: int = 586, phase2_total: int = 4093):
    """生成v11报告"""

    print(f"读取数据: {data_file}")
    df = pd.read_excel(data_file)

    print(f"使用分母：第一阶段{phase1_total}条，第二阶段{phase2_total}条")

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    # 统计
    df_p1 = df[phase1_mask]
    df_p2 = df[phase2_mask]

    p1_count = phase1_total  # 使用指定分母
    p2_count = phase2_total

    print(f"第一阶段: {p1_count}条")
    print(f"第二阶段: {p2_count}条")

    # 计算各维度数据
    # 评论类型
    type_p1 = df_p1['评论内容类型'].value_counts().to_dict()
    type_p2 = df_p2['评论内容类型'].value_counts().to_dict()

    # 认知层
    cog_p1 = df_p1['认知层阶段一'].value_counts().to_dict()
    cog_p2 = df_p2['认知层阶段二'].value_counts().to_dict()

    # 情绪层（5分类）
    emo_p1 = df_p1['情绪层阶段一'].value_counts().to_dict()
    emo_p2 = df_p2['情绪层阶段二'].value_counts().to_dict()

    # 行动层
    beh_p1 = df_p1['行动层阶段一'].value_counts().to_dict()
    beh_p2 = df_p2['行动层阶段二'].value_counts().to_dict()

    print("\n=== 原始统计数据 ===")
    print(f"认知层阶段一: {cog_p1}")
    print(f"认知层阶段二: {cog_p2}")
    print(f"情绪层阶段一: {emo_p1}")
    print(f"情绪层阶段二: {emo_p2}")
    print(f"行动层阶段一: {beh_p1}")
    print(f"行动层阶段二: {beh_p2}")

    # 读取v3模板
    template_file = "/Users/jianing/Ning's Git/sentiment-analysis/reports/final/old/0524_a2舆情_报告_v3.docx"

    # 复制模板到输出文件
    shutil.copy(template_file, output_file)

    # 读取并修改XML
    with zipfile.ZipFile(output_file, 'r') as zin:
        xml_content = zin.read('word/document.xml').decode('utf-8')
        all_files = {name: zin.read(name) for name in zin.namelist()}

    # 先替换"认可"标签为"正面"
    xml_content = xml_content.replace('>认可<', '>正面<')

    # ========== 替换数据 ==========

    # 1. 替换总评论数
    xml_content = xml_content.replace('6136', str(p1_count + p2_count))

    # 2. 替换第一阶段评论数
    xml_content = xml_content.replace('599条', f'{p1_count}条')
    xml_content = xml_content.replace('599</w:t>', f'{p1_count}</w:t>')

    # 3. 替换第二阶段评论数
    xml_content = xml_content.replace('5536条', f'{p2_count}条')
    xml_content = xml_content.replace('5536</w:t>', f'{p2_count}</w:t>')

    # 4. 替换认知层第一阶段数据
    old_cog_p1 = {
        '475': ('无明确认知', cog_p1.get('无明确认知', 0)),
        '5': ('信息混淆', cog_p1.get('信息混淆', 0)),
        '96': ('精准认知', cog_p1.get('精准认知', 0)),
        '23': ('泛化抵触', cog_p1.get('泛化抵触', 0)),
    }
    for old_val, (cog_type, new_val) in old_cog_p1.items():
        if new_val > 0:
            cog_pct = f'{new_val/p1_count*100:.1f}%'
            xml_content = xml_content.replace(f'{old_val}%', f'{cog_pct}%', 1)
            xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 5. 替换认知层第二阶段数据
    old_cog_p2 = {
        '4702': ('无明确认知', cog_p2.get('无明确认知', 0)),
        '26': ('信息混淆', cog_p2.get('信息混淆', 0)),
        '469': ('精准认知', cog_p2.get('精准认知', 0)),
        '339': ('泛化抵触', cog_p2.get('泛化抵触', 0)),
    }
    for old_val, (cog_type, new_val) in old_cog_p2.items():
        if new_val > 0:
            cog_pct = f'{new_val/p2_count*100:.1f}%'
            xml_content = xml_content.replace(f'{old_val}%', f'{cog_pct}%', 1)
            xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 6. 替换评论类型数据（第一阶段）
    type_p1_mapping = {'普通内容': 507, '@某人互动': 20, '长内容(>100字)': 16, '提及竞品': 56}
    for t, old_v in type_p1_mapping.items():
        new_v = type_p1.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 7. 替换评论类型数据（第二阶段）
    type_p2_mapping = {'普通内容': 3096, '@某人互动': 1658, '长内容(>100字)': 174, '提及竞品': 608}
    for t, old_v in type_p2_mapping.items():
        new_v = type_p2.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 8. 替换情绪层数据（第一阶段）- 5分类
    old_emo_p1 = {
        '5': ('愤怒背叛', emo_p1.get('愤怒背叛', 0)),
        '26': ('恐慌焦虑', emo_p1.get('恐慌焦虑', 0)),
        '444': ('中性', emo_p1.get('中性', 0)),
        '17': ('负面', emo_p1.get('负面', 0)),
        '9': ('庆幸旁观', emo_p1.get('庆幸旁观', 0)),
        '63': ('正面', emo_p1.get('正面', 0)),
    }
    for old_val, (emo_type, new_val) in old_emo_p1.items():
        if new_val > 0:
            xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 9. 替换情绪层数据（第二阶段）- 5分类
    old_emo_p2 = {
        '175': ('愤怒背叛', emo_p2.get('愤怒背叛', 0)),
        '397': ('恐慌焦虑', emo_p2.get('恐慌焦虑', 0)),
        '4202': ('中性', emo_p2.get('中性', 0)),
        '133': ('负面', emo_p2.get('负面', 0)),
        '168': ('庆幸旁观', emo_p2.get('庆幸旁观', 0)),
        '31': ('正面', emo_p2.get('正面', 0)),
    }
    for old_val, (emo_type, new_val) in old_emo_p2.items():
        if new_val > 0:
            xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 10. 替换行动层数据（第一阶段）
    old_beh_p1 = {
        '545': ('暂无行动', beh_p1.get('暂无行动', 0)),
        '51': ('寻求帮助', beh_p1.get('寻求帮助', 0)),
        '3': ('转奶流失', beh_p1.get('转奶流失', 0)),
    }
    for old_val, (beh_type, new_val) in old_beh_p1.items():
        if new_val > 0:
            xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 11. 替换行动层数据（第二阶段）
    old_beh_p2 = {
        '4890': ('暂无行动', beh_p2.get('暂无行动', 0)),
        '576': ('寻求帮助', beh_p2.get('寻求帮助', 0)),
        '70': ('转奶流失', beh_p2.get('转奶流失', 0)),
    }
    for old_val, (beh_type, new_val) in old_beh_p2.items():
        if new_val > 0:
            xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 写回docx
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, content in all_files.items():
            if name == 'word/document.xml':
                zout.writestr(name, xml_content.encode('utf-8'))
            else:
                zout.writestr(name, content)

    print(f"\n报告已生成: {output_file}")

    return p1_count, p2_count, cog_p1, cog_p2, emo_p1, emo_p2, beh_p1, beh_p2


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python report_v11.py <数据文件> <输出报告文件>")
    else:
        data_f = sys.argv[1]
        output_f = sys.argv[2]
        generate_report_v11(data_f, output_f)