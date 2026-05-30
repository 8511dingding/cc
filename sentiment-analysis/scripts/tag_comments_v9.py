"""
A2舆情分析 - 完整分类标记脚本 v9
基于v3模板和客户纠正规则，剔除纯@无互动后重新分析
"""

import pandas as pd
import re
from typing import Tuple, List

# ============ 分类函数（基于客户纠正规则更新）===========

def classify_comment(text: str, current_cognitive: str, current_emotion: str, current_behavior: str, phase: int) -> Tuple[str, str, str]:
    """
    根据最新规则对评论进行三维分类
    规则优先级（基于客户纠正规则）：
    1. 愤怒背叛 > 其他情绪（企业不负责任、双标、欺骗、"背刺"、"资本家"）
    2. 恐慌焦虑 > 中性（宝宝症状+担忧、询问是否中招、表情[流泪]）
    3. 正面 > 中性
    4. 庆幸旁观判定
    5. 负面判定
    """
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return current_cognitive, current_emotion, current_behavior

    text_lower = text.lower()

    # ========== 愤怒背叛检测（优先级最高）==========
    anger_keywords = [
        '该死', '欺骗', '忽悠', '被骗', '上当', '造假', '破产',
        '恶意', '黑心', '无良', '骗子', '垃圾品牌', '气愤',
        '失望透顶', '谁还敢喝', '骗人是狗', '转黑', '极其厌恶',
        '三鹿', '代加工', '代工', '贴牌', '塌房', '步步惊心',
        '进口信不过', '膈应', '不要心存幻想', '品牌失望',
        # 客户纠正规则新增
        '背刺', '资本家', '没人性', '双标', '不负责任',
        '建议严查', '企业无良', '败絮其中'
    ]

    has_anger = any(kw in text_lower for kw in anger_keywords)

    # 小作文类（长篇质疑分析）
    is_long_essay = len(text) > 100 and any(kw in text_lower for kw in [
        '请问', '为什么', '问题', '疑问', '几个问题', '是不是',
        '怎么突然', '到底', '根本站不住脚', '缺乏说服力'
    ])

    if has_anger or is_long_essay:
        return '泛化抵触', '愤怒背叛', current_behavior if current_behavior != '暂无行动' else '暂无行动'

    # ========== 恐慌焦虑检测（优先级第二）==========
    # 客户纠正规则：宝宝出现症状+担忧 = 恐慌焦虑（不是负面）

    # 恐慌焦虑关键词
    panic_keywords = [
        '会不会有事', '有影响吗', '有危害吗', '怎么办', '瑟瑟发抖',
        '慌', '害怕', '担心', '担忧', '焦虑', '着急', '害怕',
        '天哪', '急死人', '揪心', '好担心', '还能喝不', '要不要换',
        '有没有问题', '能不能喝', '还能不能喝', '咋办', '咋整',
        '要不要换', '选什么奶粉', '选麻了', '天塌了',
        '不知道买什么奶粉', '不知道换啥', '不知道换哪个',
        '求推荐', '马上要生产了', '6月份预产期',
        # 客户纠正规则新增
        '是不是我娃', '我娃吃了', '宝宝吃了', '娃吃了',
        '这要换啥', '这下咋整', '怎么办啊', '怎么办'
    ]

    # @豆包 模式
    is_doubao = '@豆包' in text

    # 宝宝症状关键词（客户纠正规则）
    symptom_keywords = [
        '吐奶', '拉肚子', '腹泻', '便血', '呕吐', '绿便', '奶瓣',
        '不舒服', '腹胀', '哭闹', '发烧', '过敏', '厌奶',
        '不肯喝', '抗拒', '难受', '喷射', '化不开'
    ]

    has_symptom = any(kw in text_lower for kw in symptom_keywords)
    has_panic = any(kw in text_lower for kw in panic_keywords)

    # 客户纠正规则：如果提到宝宝症状但有担忧情绪 → 恐慌焦虑
    # 即使之前被归类为负面，也应该是恐慌焦虑
    if (has_symptom and has_panic) or (has_symptom and '[流泪]' in text) or is_doubao:
        return current_cognitive if current_cognitive != '无明确认知' else '无明确认知', '恐慌焦虑', '寻求帮助' if current_behavior == '暂无行动' else current_behavior

    if has_panic or is_doubao:
        return current_cognitive if current_cognitive != '无明确认知' else '无明确认知', '恐慌焦虑', '寻求帮助' if current_behavior == '暂无行动' else current_behavior

    # ========== 正面检测（优先级第三）==========
    approval_keywords = [
        '放心', '没有问题', '可以继续喝', '官方确认安全', '没影响',
        '未受影响', '没事', '娃从出生就喝', '一直喝', '这款奶粉',
        '没有问题', '肯定没事', '爱喝', '嘎嘎爱喝', '不会换',
        '各方面都挺好', '长势稳稳当当', '身高', '长高', '长肉',
        '体重', '涨了', '健康', '壮', '好得很', '囤奶', '正常喝',
        '货源稳定', '有货', '补货', 'PDD', '刚在'
    ]

    has_approval = any(kw in text_lower for kw in approval_keywords)

    if has_approval:
        return '精准认知' if current_cognitive == '无明确认知' else current_cognitive, '正面', current_behavior

    # ========== 庆幸旁观检测（优先级第四）==========
    # 客户纠正规则：庆幸自己没买/已换 → 庆幸旁观
    lucky_keywords = [
        '还好没买', '幸好没买', '多亏没买', '还好不是', '还好',
        '好在', '好险', '国产更好', '喝母乳', '不喝外国奶',
        '幸好没选', '两个娃都喝', '不喝外国货', '感谢自己拖拉',
        '幸亏没换', '幸亏没', '暗自观察', '又出事啦',
        '希望守住', '洋货', '崇洋', '只适合薅礼品',
        # 客户纠正规则新增
        '早就换了', '暗自庆幸', '我机智', '我选对了', '还好换了'
    ]

    competitor_bad = any(re.search(kw, text_lower) for kw in [
        r'德爱.*拉肚子', r'德爱.*塌', r'飞鹤.*又吐又拉', r'爱他美.*召回',
        r'贝巴.*不长肉', r'贝拉米.*问题', r'君乐宝.*没事', r'飞鹤.*没事',
        r'雀巢.*塌', r'蓝河.*断货', r'蓝河.*经常断货'
    ])

    has_lucky = any(kw in text_lower for kw in lucky_keywords) or competitor_bad

    if has_lucky:
        return current_cognitive, '庆幸旁观', current_behavior

    # ========== 负面检测（优先级第五）==========
    # 客户纠正规则：宝宝症状但无担忧 → 负面（但如果有担忧应该是恐慌焦虑）

    a2_problem = any(kw in text_lower for kw in [
        '拉肚子', '腹泻', '吐奶', '呕吐', '绿便', '奶瓣',
        '不舒服', '腹胀', '哭闹', '发烧', '过敏', '崩溃',
        '不咋地', '不长肉', '踩雷', '惊心', '背刺', '贝壳',
        '干呕', '爱吐', '喷射', '化不开', '大便结块',
        '性价比不高', '又贵', '市场占有率', '塌房', '塌了'
    ])

    has_a2 = any(kw in text_lower for kw in ['a2', '至初', '紫白金', '紫曜'])

    switch_action = any(kw in text_lower for kw in [
        '换了', '转奶', '退了', '换回', '准备换', '已经换',
        '买了国产', '算了买国产', '转皇家', '转爱他美', '转德爱',
        '转雀巢', '换飞鹤', '换蓝臻', '换海普', '换1897',
        '换皇家', '换澳爱', '换回国产', '换国产',
        '吃完就换', '只喝了一箱', '马上换', '退了2罐'
    ])

    if a2_problem and has_a2:
        new_emo = '负面'
        new_beh = '转奶流失' if switch_action else current_behavior
        return '泛化抵触', new_emo, new_beh

    # ========== 泛化抵触检测 ==========
    resist_keywords = [
        '所有奶粉', '所有品牌', '都不行', '都有问题', '都不安全',
        '不如母乳', '干脆不喝', '还是母乳好', '所有', '全部', '一律'
    ]

    has_resist = any(kw in text_lower for kw in resist_keywords)

    if has_resist:
        new_emo = '负面' if a2_problem else '中性'
        new_beh = '转奶流失' if switch_action else current_behavior
        return '泛化抵触', new_emo, new_beh

    # ========== 转奶流失检测（客户纠正规则更新）==========
    # 客户纠正规则：表达换奶意向、彻底失望 → 转奶流失

    switch_keywords = [
        '换了', '换了x', '换奶粉', '转x了', '准备换', '吃完就换',
        '推荐哪个', '不知道换哪个', '选麻了', '又要换奶粉',
        '换什么奶粉好', '换哪个呀', '转奶', '换回', '换国产',
        '转皇家', '转爱他美', '转德爱', '转雀巢', '换飞鹤', '换蓝臻',
        '换海普', '换1897', '换澳爱', '换皇家', '换爱他美卓傲',
        '退2罐', '退不了', '只喝了一箱', '马上换', '要换奶粉了',
        '不知道换啥', '求推荐', '又要找奶粉', '不知道买什么奶粉',
        '纠结选', '想换成', '不知道买什么', '马上要生产',
        '6月份预产期', '要断货了', '没货了', '山姆没货',
        # 客户纠正规则新增
        '彻底下决心', '彻底失望', '再也不会', '绝对不买'
    ]

    has_switch = any(kw in text_lower for kw in switch_keywords)

    if has_switch:
        new_emo = '负面' if a2_problem else ('中性' if current_emotion == '中性' else current_emotion)
        return current_cognitive if current_cognitive != '无明确认知' else '无明确认知', new_emo, '转奶流失'

    # ========== 精准认知检测 ==========
    precise_keywords = [
        'fda.*检出', '仅限美国', '特定批次', '国标', '配方.*安全',
        '海关总署', '检测.*合格', '召回范围', '官方声明', '美版问题',
        '区域配方', '单点质控', '美国标准差异'
    ]

    has_precise = any(re.search(kw, text_lower, re.IGNORECASE) for kw in precise_keywords)

    if has_precise:
        return '精准认知', '正面' if current_emotion == '中性' else current_emotion, current_behavior

    # 如果已经是目标状态之外，不修改
    return current_cognitive, current_emotion, current_behavior


def get_comment_type(text: str) -> str:
    """判断评论类型"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '普通内容'

    # 纯@无互动 - 不算@某人互动
    at_matches = re.findall(r'@[a-zA-Z0-9_-]+', text)
    if at_matches:
        # 检查是否是纯@无互动
        at = at_matches[0]
        idx = text.find(at)
        before_at = text[:idx].strip()
        after_at = text[idx + len(at):].strip()
        if len(before_at) == 0:
            after_clean = re.sub(r'[\U0001F000-\U0001F9FF👏👍❤️🥰😊🙏🎉💪🤔😅😢😭😱😨🫣🤷😂🤣\[\]（）()【】、，。：:,,.\\s]+', '', after_at)
            if len(after_clean) == 0:
                return '纯@无互动'

    # @某人互动
    if re.search(r'@[一-龥a-zA-Z0-9_-]+', text):
        return '@某人互动'

    # 长内容(>100字)
    if len(text) > 100:
        return '长内容(>100字)'

    # 提及竞品
    competitor_keywords = [
        '爱他美', '美赞臣', '美素佳儿', '雀巢', '惠氏', '海普', '合生元',
        '飞鹤', '君乐宝', '金领冠', '贝因美', '伊利', '完达山', '圣元',
        '贝拉米', 'bubs', '澳优', '蒙牛', '雅士利', '佳贝艾特', '优博',
    ]
    for kw in competitor_keywords:
        if kw in text:
            return '提及竞品'

    return '普通内容'


def extract_brand_mentions(text: str) -> str:
    """提取品牌提及"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    text_lower = text.lower()
    brands = []

    if re.search(r'a2至初|a2紫白金|a2紫曜|至初.*a2|紫白金.*a2|紫曜.*a2|a2.*至初|a2.*紫白金|a2.*紫曜', text_lower):
        brands.append('a2')
    elif re.search(r'\ba2\b', text_lower) and 'a2蛋白质' not in text_lower and 'a2成分' not in text_lower:
        brands.append('a2')

    if re.search(r'爱他美|德爱|领熠|至熠|卓傲|澳爱', text_lower):
        brands.append('爱他美')

    if re.search(r'飞鹤|卓睿|臻爱倍护', text_lower):
        brands.append('飞鹤')

    if re.search(r'君乐宝|至臻|乐铂|红旗帜', text_lower):
        brands.append('君乐宝')

    if re.search(r'金领冠|塞纳牧|珍护|育护', text_lower):
        brands.append('金领冠')

    if re.search(r'美素佳儿|皇家美素佳儿|源悦', text_lower):
        brands.append('美素佳儿')

    if re.search(r'美赞臣|蓝臻|铂睿|亲舒', text_lower):
        brands.append('美赞臣')

    if re.search(r'合生元|派星|贝塔星耀', text_lower):
        brands.append('合生元')

    if re.search(r'雀巢|能恩|贝巴|beba|贝芭', text_lower):
        brands.append('雀巢')

    if re.search(r'惠氏|启赋', text_lower):
        brands.append('惠氏')

    if re.search(r'圣元|剖蓓舒|金爱嘉', text_lower):
        brands.append('圣元')

    if re.search(r'完达山|菁稚非凡', text_lower):
        brands.append('完达山')

    if re.search(r'贝拉米', text_lower):
        brands.append('贝拉米')

    if re.search(r'海普|海普诺凯|荷致|1897', text_lower):
        brands.append('海普诺凯1897')

    if re.search(r'佳贝艾特', text_lower):
        brands.append('佳贝艾特')

    if re.search(r'优博瑞霖|优博', text_lower):
        brands.append('优博瑞霖')

    if re.search(r'伊利|贝因美|雅士利|澳优|蒙牛|旗帜|bubs', text_lower):
        if 'a2' not in brands and '爱他美' not in brands:
            brands.append('其他品牌')

    return '|'.join(brands) if brands else ''


def run_tagging_v9(input_file: str, output_file: str = None):
    """运行v9标记流程"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)

    print(f"总数据量: {len(df)} 条")

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    # 过滤纯@无互动评论
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

    print(f"第一阶段(4月): {p1_count}条 (去除 {(phase1_mask & df['is_pure_at']).sum()} 条纯@无互动)")
    print(f"第二阶段(5月): {p2_count}条 (去除 {(phase2_mask & df['is_pure_at']).sum()} 条纯@无互动)")

    # 初始化统计
    stats = {
        'modified': 0,
        'cognitive': {'阶段一': {}, '阶段二': {}},
        'emotion': {'阶段一': {}, '阶段二': {}},
        'action': {'阶段一': {}, '阶段二': {}},
    }

    # 逐行处理
    for idx, row in df_to_analyze.iterrows():
        text = str(row['评论内容']) if pd.notna(row['评论内容']) else ''
        is_p1 = phase1_mask[idx]
        is_p2 = phase2_mask[idx]

        # 更新评论类型
        comment_type = get_comment_type(text)
        df_to_analyze.at[idx, '评论内容类型'] = comment_type

        # 更新品牌提及
        new_brands = extract_brand_mentions(text)
        df_to_analyze.at[idx, '品牌提及'] = new_brands

        # 获取当前分类
        if is_p1:
            current_cog = str(row['认知层阶段一']) if pd.notna(row['认知层阶段一']) else ''
            current_emo = str(row['情绪层阶段一']) if pd.notna(row['情绪层阶段一']) else ''
            current_beh = str(row['行动层阶段一']) if pd.notna(row['行动层阶段一']) else ''
        elif is_p2:
            current_cog = str(row['认知层阶段二']) if pd.notna(row['认知层阶段二']) else ''
            current_emo = str(row['情绪层阶段二']) if pd.notna(row['情绪层阶段二']) else ''
            current_beh = str(row['行动层阶段二']) if pd.notna(row['行动层阶段二']) else ''
        else:
            continue

        # 重新分类
        new_cog, new_emo, new_beh = classify_comment(text, current_cog, current_emo, current_beh, 2 if is_p2 else 1)

        # 更新分类
        if new_cog != current_cog or new_emo != current_emo or new_beh != current_beh:
            stats['modified'] += 1

        if is_p1:
            df_to_analyze.at[idx, '认知层阶段一'] = new_cog
            df_to_analyze.at[idx, '情绪层阶段一'] = new_emo
            df_to_analyze.at[idx, '行动层阶段一'] = new_beh
            stats['cognitive']['阶段一'][new_cog] = stats['cognitive']['阶段一'].get(new_cog, 0) + 1
            stats['emotion']['阶段一'][new_emo] = stats['emotion']['阶段一'].get(new_emo, 0) + 1
            stats['action']['阶段一'][new_beh] = stats['action']['阶段一'].get(new_beh, 0) + 1

        elif is_p2:
            df_to_analyze.at[idx, '认知层阶段二'] = new_cog
            df_to_analyze.at[idx, '情绪层阶段二'] = new_emo
            df_to_analyze.at[idx, '行动层阶段二'] = new_beh
            stats['cognitive']['阶段二'][new_cog] = stats['cognitive']['阶段二'].get(new_cog, 0) + 1
            stats['emotion']['阶段二'][new_emo] = stats['emotion']['阶段二'].get(new_emo, 0) + 1
            stats['action']['阶段二'][new_beh] = stats['action']['阶段二'].get(new_beh, 0) + 1

        if idx % 1000 == 0:
            print(f"  已处理 {idx}/{len(df_to_analyze)} 条...")

    # 后处理：将所有"认可"替换为"正面"
    for col in ['情绪层阶段一', '情绪层阶段二']:
        if col in df_to_analyze.columns:
            df_to_analyze[col] = df_to_analyze[col].replace('认可', '正面')

    # 删除临时列
    if '评论时间_str' in df_to_analyze.columns:
        df_to_analyze = df_to_analyze.drop(columns=['评论时间_str'])
    if 'is_pure_at' in df_to_analyze.columns:
        df_to_analyze = df_to_analyze.drop(columns=['is_pure_at'])

    # 打印统计
    print("\n" + "="*50)
    print("=== v9分类统计结果 ===")
    print("="*50)
    print(f"修改记录: {stats['modified']}条")

    print("\n【第一阶段分类】(共{}条)".format(p1_count))
    print(f"  认知层: {stats['cognitive']['阶段一']}")
    print(f"  情绪层: {stats['emotion']['阶段一']}")
    print(f"  行动层: {stats['action']['阶段一']}")

    print("\n【第二阶段分类】(共{}条)".format(p2_count))
    print(f"  认知层: {stats['cognitive']['阶段二']}")
    print(f"  情绪层: {stats['emotion']['阶段二']}")
    print(f"  行动层: {stats['action']['阶段二']}")

    # 保存
    if output_file:
        df_to_analyze.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df_to_analyze, stats


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python tag_comments_v9.py <输入文件> <输出文件>")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2]
        run_tagging_v9(input_f, output_f)