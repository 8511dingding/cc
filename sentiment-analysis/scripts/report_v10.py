"""
A2舆情报告生成脚本 - v10版（基于v9数据）
剔除纯@无互动后的数据，生成新的报告
"""

import pandas as pd
import zipfile
import shutil
import re

def generate_report_v10(data_file: str, output_file: str):
    """生成v10报告"""

    print(f"读取数据: {data_file}")
    df = pd.read_excel(data_file)

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    # 过滤纯@无互动
    def is_pure_at_no_interaction(text):
        if pd.isna(text) or not isinstance(text, str):
            return False
        at_matches = re.findall(r'@[a-zA-Z0-9_-]+', text)
        if len(at_matches) == 0:
            return False
        if len(at_matches) > 1:
            return False
        at = at_matches[0]
        idx = text.find(at)
        before_at = text[:idx].strip()
        after_at = text[idx + len(at):].strip()
        if len(before_at) > 0:
            return False
        after_clean = re.sub(r'[\U0001F000-\U0001F9FF👏👍❤️🥰😊🙏🎉💪🤔😅😢😭😱😨🫣🤷😂🤣\[\]（）()【】、，。：:,,.\\s]+', '', after_at)
        return len(after_clean) == 0

    df['is_pure_at'] = df['评论内容'].apply(is_pure_at_no_interaction)

    # 需要分析的评论
    df_to_analyze = df[~df['is_pure_at']].copy()

    p1_count = (phase1_mask & ~df['is_pure_at']).sum()
    p2_count = (phase2_mask & ~df['is_pure_at']).sum()
    total_count = p1_count + p2_count

    print(f"第一阶段: {p1_count}条")
    print(f"第二阶段: {p2_count}条")
    print(f"总计: {total_count}条")

    # 计算各维度数据
    df_p1 = df_to_analyze[phase1_mask]
    df_p2 = df_to_analyze[phase2_mask]

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
    xml_content = xml_content.replace('6136', str(total_count))

    # 2. 替换第一阶段评论数 (599条 -> p1_count)
    xml_content = xml_content.replace('599条', f'{p1_count}条')
    xml_content = xml_content.replace('599</w:t>', f'{p1_count}</w:t>')

    # 3. 替换第二阶段评论数 (5536条 -> p2_count)
    xml_content = xml_content.replace('5536条', f'{p2_count}条')
    xml_content = xml_content.replace('5536</w:t>', f'{p2_count}</w:t>')

    # 4. 替换认知层第一阶段数据
    old_cog_p1 = {
        '475': ('无明确认知', cog_p1.get('无明确认知', 475)),
        '5': ('信息混淆', cog_p1.get('信息混淆', 5)),
        '96': ('精准认知', cog_p1.get('精准认知', 96)),
        '23': ('泛化抵触', cog_p1.get('泛化抵触', 23)),
    }
    for old_val, (cog_type, new_val) in old_cog_p1.items():
        cog_pct = f'{new_val/p1_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_val}%', f'{cog_pct}%', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 5. 替换认知层第二阶段数据
    old_cog_p2 = {
        '4702': ('无明确认知', cog_p2.get('无明确认知', 4702)),
        '26': ('信息混淆', cog_p2.get('信息混淆', 26)),
        '469': ('精准认知', cog_p2.get('精准认知', 469)),
        '339': ('泛化抵触', cog_p2.get('泛化抵触', 339)),
    }
    for old_val, (cog_type, new_val) in old_cog_p2.items():
        cog_pct = f'{new_val/p2_count*100:.1f}%'
        xml_content = xml_content.replace(f'{old_val}%', f'{cog_pct}%', 1)
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 6. 替换评论类型数据
    type_p1_mapping = {'普通内容': 507, '@某人互动': 20, '长内容(>100字)': 16, '提及竞品': 56}
    for t, old_v in type_p1_mapping.items():
        new_v = type_p1.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    type_p2_mapping = {'普通内容': 3096, '@某人互动': 1658, '长内容(>100字)': 174, '提及竞品': 608}
    for t, old_v in type_p2_mapping.items():
        new_v = type_p2.get(t, old_v)
        xml_content = xml_content.replace(f'<w:t>{old_v}</w:t>', f'<w:t>{new_v}</w:t>', 1)

    # 7. 替换情绪层数据（第一阶段）
    old_emo_p1 = {
        '5': ('愤怒背叛', emo_p1.get('愤怒背叛', 5)),
        '26': ('恐慌焦虑', emo_p1.get('恐慌焦虑', 26)),
        '444': ('中性', emo_p1.get('中性', 444)),
        '17': ('负面', emo_p1.get('负面', 17)),
        '9': ('庆幸旁观', emo_p1.get('庆幸旁观', 9)),
        '63': ('正面', emo_p1.get('正面', 63)),
    }
    for old_val, (emo_type, new_val) in old_emo_p1.items():
        new_pct = f'{new_val/p1_count*100:.1f}%'
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)
        # 百分比替换需要找到正确的百分比

    # 8. 替换情绪层数据（第二阶段）
    old_emo_p2 = {
        '175': ('愤怒背叛', emo_p2.get('愤怒背叛', 175)),
        '397': ('恐慌焦虑', emo_p2.get('恐慌焦虑', 397)),
        '4202': ('中性', emo_p2.get('中性', 4202)),
        '133': ('负面', emo_p2.get('负面', 133)),
        '168': ('庆幸旁观', emo_p2.get('庆幸旁观', 168)),
        '31': ('正面', emo_p2.get('正面', 31)),
    }
    for old_val, (emo_type, new_val) in old_emo_p2.items():
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 9. 替换行动层数据（第一阶段）
    old_beh_p1 = {
        '545': ('暂无行动', beh_p1.get('暂无行动', 545)),
        '51': ('寻求帮助', beh_p1.get('寻求帮助', 51)),
        '3': ('转奶流失', beh_p1.get('转奶流失', 3)),
    }
    for old_val, (beh_type, new_val) in old_beh_p1.items():
        xml_content = xml_content.replace(f'<w:t>{old_val}</w:t>', f'<w:t>{new_val}</w:t>', 1)

    # 10. 替换行动层数据（第二阶段）
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

    # 打印最终统计
    print("\n=== 最终统计确认 ===")
    print(f"阶段一情绪层: {emo_p1}")
    print(f"阶段二情绪层: {emo_p2}")
    print(f"阶段一行动层: {beh_p1}")
    print(f"阶段二行动层: {beh_p2}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python report_v10.py <数据文件> <输出报告文件>")
    else:
        data_f = sys.argv[1]
        output_f = sys.argv[2]
        generate_report_v10(data_f, output_f)