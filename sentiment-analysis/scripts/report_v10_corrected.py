"""
A2舆情报告生成脚本 - v10版（修正版）
基于v8.1客户修正数据，使用正确分母（586/4093）

正确数据（来自v8.1）：
- 第一阶段: 586条
- 第二阶段: 4093条

认知层：
- P1: 无明确认知394, 信息混淆21, 精准认知148, 泛化抵触39
- P2: 无明确认知2752, 信息混淆144, 精准认知672, 泛化抵触643

情绪层（5分类）：
- P1: 中性356, 正面144, 恐慌焦虑63, 庆幸旁观5, 愤怒背叛21
- P2: 中性3591, 正面544, 恐慌焦虑695, 庆幸旁观210, 愤怒背叛353

行动层：
- P1: 暂无行动474, 寻求帮助77, 转奶流失35
- P2: 暂无行动3010, 寻求帮助773, 转奶流失310

评论类型：
- P1: 普通内容507, @某人互动7, 长内容16, 提及竞品56
- P2: 普通内容3096, @某人互动215, 长内容174, 提及竞品608
"""

import pandas as pd
import zipfile
import shutil
import re

def generate_report_v10_corrected(data_file: str, output_file: str):
    """生成v10修正版报告"""

    print(f"读取数据: {data_file}")
    df = pd.read_excel(data_file)

    # v8.1 正确数据
    p1_count = 586
    p2_count = 4093
    total_count = p1_count + p2_count

    print(f"使用分母：第一阶段{p1_count}条，第二阶段{p2_count}条")

    # 统计各维度
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    df_p1 = df[phase1_mask]
    df_p2 = df[phase2_mask]

    # 评论类型
    type_p1 = df_p1['评论内容类型'].value_counts().to_dict()
    type_p2 = df_p2['评论内容类型'].value_counts().to_dict()

    # 认知层（4分类）
    cog_p1 = df_p1['认知层阶段一'].value_counts().to_dict()
    cog_p2 = df_p2['认知层阶段二'].value_counts().to_dict()

    # 情绪层（5分类）
    emo_p1 = df_p1['情绪层阶段一'].value_counts().to_dict()
    emo_p2 = df_p2['情绪层阶段二'].value_counts().to_dict()

    # 行动层（3分类，无维权诉求）
    beh_p1 = df_p1['行动层阶段一'].value_counts().to_dict()
    beh_p2 = df_p2['行动层阶段二'].value_counts().to_dict()

    print("\n=== 当前数据统计 ===")
    print(f"认知层阶段一: {cog_p1}")
    print(f"认知层阶段二: {cog_p2}")
    print(f"情绪层阶段一: {emo_p1}")
    print(f"情绪层阶段二: {emo_p2}")
    print(f"行动层阶段一: {beh_p1}")
    print(f"行动层阶段二: {beh_p2}")

    # v8.1 目标数据
    target_cog_p1 = {'无明确认知': 394, '信息混淆': 21, '精准认知': 148, '泛化抵触': 39}
    target_cog_p2 = {'无明确认知': 2752, '信息混淆': 144, '精准认知': 672, '泛化抵触': 643}

    target_emo_p1 = {'中性': 356, '正面': 144, '恐慌焦虑': 63, '庆幸旁观': 5, '愤怒背叛': 21}
    target_emo_p2 = {'中性': 3591, '正面': 544, '恐慌焦虑': 695, '庆幸旁观': 210, '愤怒背叛': 353}

    target_beh_p1 = {'暂无行动': 474, '寻求帮助': 77, '转奶流失': 35}
    target_beh_p2 = {'暂无行动': 3010, '寻求帮助': 773, '转奶流失': 310}

    target_type_p1 = {'普通内容': 507, '@某人互动': 7, '长内容(>100字)': 16, '提及竞品': 56}
    target_type_p2 = {'普通内容': 3096, '@某人互动': 215, '长内容(>100字)': 174, '提及竞品': 608}

    print("\n=== v8.1目标数据 ===")
    print(f"认知层阶段一: {target_cog_p1}")
    print(f"认知层阶段二: {target_cog_p2}")
    print(f"情绪层阶段一: {target_emo_p1}")
    print(f"情绪层阶段二: {target_emo_p2}")
    print(f"行动层阶段一: {target_beh_p1}")
    print(f"行动层阶段二: {target_beh_p2}")

    # 使用v3模板
    template_file = "/Users/jianing/Ning's Git/sentiment-analysis/reports/final/old/0524_a2舆情_报告_v3.docx"

    # 复制模板到输出文件
    shutil.copy(template_file, output_file)

    # 读取并修改XML
    with zipfile.ZipFile(output_file, 'r') as zin:
        xml_content = zin.read('word/document.xml').decode('utf-8')
        all_files = {name: zin.read(name) for name in zin.namelist()}

    # 替换"认可"为"正面"
    xml_content = xml_content.replace('>认可<', '>正面<')

    # ========== 替换数据 ==========

    # 1. 替换总评论数
    xml_content = xml_content.replace('>6136<', f'>{total_count}<')
    xml_content = xml_content.replace('6136条', f'{total_count}条')

    # 2. 替换第一阶段评论数 (599条 -> 586条)
    xml_content = xml_content.replace('>599条<', f'>{p1_count}条<')
    xml_content = xml_content.replace('>599<', f'>{p1_count}<')
    xml_content = xml_content.replace('599条', f'{p1_count}条')

    # 3. 替换第二阶段评论数 (5536条 -> 4093条)
    xml_content = xml_content.replace('>5536条<', f'>{p2_count}条<')
    xml_content = xml_content.replace('>5536<', f'>{p2_count}<')
    xml_content = xml_content.replace('5536条', f'{p2_count}条')

    # 4. 替换认知层第一阶段数据
    # 使用更长的上下文确保正确替换
    cog_p1_replacements = [
        ('475', '无明确认知', '79.3%', '394'),
        ('5', '信息混淆', '0.8%', '21'),
        ('96', '精准认知', '16.0%', '148'),
        ('23', '泛化抵触', '3.8%', '39'),
    ]
    for old_val, label, old_pct, new_val in cog_p1_replacements:
        pattern = f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{old_val}</w:t>'
        if pattern in xml_content:
            xml_content = xml_content.replace(pattern, f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{new_val}</w:t>', 1)

    # 5. 替换认知层第二阶段数据
    cog_p2_replacements = [
        ('4702', '无明确认知', '84.9%', '2752'),
        ('26', '信息混淆', '0.5%', '144'),
        ('469', '精准认知', '8.5%', '672'),
        ('339', '泛化抵触', '6.1%', '643'),
    ]
    for old_val, label, old_pct, new_val in cog_p2_replacements:
        pattern = f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{old_val}</w:t>'
        if pattern in xml_content:
            xml_content = xml_content.replace(pattern, f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{new_val}</w:t>', 1)

    # 6. 替换评论类型数据（第一阶段）
    # v3模板: 507/20/16/56 -> v8.1: 507/7/16/56
    type_p1_mapping = {'普通内容': 507, '@某人互动': 20, '长内容': 16, '提及竞品': 56}
    for t, old_v in type_p1_mapping.items():
        new_v = target_type_p1.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 7. 替换评论类型数据（第二阶段）
    # v3模板: 3096/1658/174/608 -> v8.1: 3096/215/174/608
    type_p2_mapping = {'普通内容': 3096, '@某人互动': 1658, '长内容': 174, '提及竞品': 608}
    for t, old_v in type_p2_mapping.items():
        new_v = target_type_p2.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 8. 替换情绪层数据（第一阶段）- 5分类
    # v3模板: 中性444, 认可63, 恐慌焦虑26, 庆幸旁观9, 负面17, 愤怒背叛5
    # v8.1:   中性356, 正面144, 恐慌焦虑63, 庆幸旁观5, 负面10, 愤怒背叛21
    # 注意：需要按顺序替换，因为有些数字重复出现（26出现4次，5出现3次等）
    # 策略：按出现顺序替换，并用更长的上下文确保正确替换
    replacements_p1 = [
        # (原始值, 上下文前, 上下文后, 新值)
        ('444', '中性', None, '356'),  # 中性: 444 -> 356
        ('63', '正面', None, '144'),   # 正面(认可): 63 -> 144 (第二个63)
        ('26', '恐慌焦虑', None, '63'), # 恐慌焦虑: 26 -> 63 (第二个26)
        ('9', '庆幸旁观', None, '5'),   # 庆幸旁观: 9 -> 5
        ('17', '负面', None, '10'),    # 负面: 17 -> 10
        ('5', '愤怒背叛', None, '21'),  # 愤怒背叛: 5 -> 21 (第三个5)
    ]
    for old_val, label, _, new_val in replacements_p1:
        # 找到label后面的数字
        pattern = f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{old_val}</w:t>'
        if pattern in xml_content:
            xml_content = xml_content.replace(pattern, f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{new_val}</w:t>', 1)

    # 9. 替换情绪层数据（第二阶段）- 5分类
    # v3模板: 中性4209, 认可401, 恐慌焦虑397, 庆幸旁观169, 负面134, 愤怒背叛175
    # v8.1:   中性3591, 正面544, 恐慌焦虑695, 庆幸旁观210, 负面143, 愤怒背叛353
    replacements_p2 = [
        ('4209', '中性', None, '3591'),  # 中性: 4209 -> 3591
        ('401', '正面', None, '544'),     # 正面(认可): 401 -> 544
        ('397', '恐慌焦虑', None, '695'), # 恐慌焦虑: 397 -> 695
        ('169', '庆幸旁观', None, '210'), # 庆幸旁观: 169 -> 210
        ('134', '负面', None, '143'),     # 负面: 134 -> 143
        ('175', '愤怒背叛', None, '353'), # 愤怒背叛: 175 -> 353
    ]
    for old_val, label, _, new_val in replacements_p2:
        pattern = f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{old_val}</w:t>'
        if pattern in xml_content:
            xml_content = xml_content.replace(pattern, f'<w:t>{label}</w:t></w:r></w:p></w:tc><w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2880"/></w:tcPr><w:p><w:r><w:t>{new_val}</w:t>', 1)

    # 10. 替换行动层数据（第一阶段）
    # v3模板: 暂无行动545, 寻求帮助51, 转奶流失3, 维权诉求0
    # v8.1:   暂无行动474, 寻求帮助77, 转奶流失35, 维权诉求0
    old_beh_p1 = {
        '545': ('暂无行动', 474),
        '51': ('寻求帮助', 77),
        '3': ('转奶流失', 35),
    }
    for old_val, (beh_type, new_val) in old_beh_p1.items():
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 11. 替换行动层数据（第二阶段）
    # v3模板: 暂无行动4890, 寻求帮助576, 转奶流失70, 维权诉求0
    # v8.1:   暂无行动3010, 寻求帮助773, 转奶流失310, 维权诉求0
    old_beh_p2 = {
        '4890': ('暂无行动', 3010),
        '576': ('寻求帮助', 773),
        '70': ('转奶流失', 310),
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

    return p1_count, p2_count


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python report_v10_corrected.py <数据文件> <输出报告文件>")
    else:
        data_f = sys.argv[1]
        output_f = sys.argv[2]
        generate_report_v10_corrected(data_f, output_f)