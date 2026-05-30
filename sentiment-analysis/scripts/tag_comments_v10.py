"""
A2舆情分析 - v10分类标记脚本
基于v9标准：情绪层5分类、剔除纯@无互动、分母586/4093
"""

import pandas as pd
import re
from typing import Tuple

def is_pure_at_no_interaction(text: str) -> bool:
    """判断是否为纯@无互动评论"""
    if pd.isna(text) or not isinstance(text, str):
        return False
    at_matches = re.findall(r'@[a-zA-Z0-9_-]+', text)
    if len(at_matches) == 0:
        return False
    if len(at_matches) > 1:
        return True  # 多个@算纯@

    at = at_matches[0]
    idx = text.find(at)
    before_at = text[:idx].strip()
    after_at = text[idx + len(at):].strip()

    if len(before_at) > 0:
        return False

    # 去除emoji、空格、标点后检查是否为空
    after_clean = re.sub(r'[\U0001F000-\U0001F9FF👏👍❤️🥰😊🙏🎉💪🤔😅😢😭😱😨🫣🤷😂🤣\[\]（）()【】、，。：:,,.\s]+', '', after_at)
    return len(after_clean) == 0


def classify_comment(text: str) -> Tuple[str, str, str]:
    """
    三维分类：认知层、情绪层、行动层
    情绪层5分类：正面、中性、恐慌焦虑、庆幸旁观、愤怒背叛
    """
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '', '', ''

    text_lower = text.lower()
    emotion = ''

    # ========== 情绪层分类（5分类）==========
    # 优先级：愤怒背叛 > 恐慌焦虑 > 正面 > 庆幸旁观 > 中性

    # 1. 愤怒背叛检测
    anger_keywords = [
        '该死', '欺骗', '忽悠', '被骗', '上当', '造假', '破产',
        '恶意', '黑心', '无良', '骗子', '垃圾品牌', '气愤',
        '失望透顶', '谁还敢喝', '骗人是狗', '转黑', '极其厌恶',
        '三鹿', '代加工', '代工', '贴牌', '塌房', '步步惊心',
        '进口信不过', '膈应', '不要心存幻想', '品牌失望',
        '背刺', '资本家', '没人性', '双标', '不负责任',
        '建议严查', '企业无良', '败絮其中'
    ]

    if any(kw in text_lower for kw in anger_keywords):
        emotion = '愤怒背叛'

    # 2. 恐慌焦虑检测
    elif emotion == '':
        panic_keywords = [
            '会不会有事', '有影响吗', '有危害吗', '怎么办', '瑟瑟发抖',
            '慌', '害怕', '担心', '担忧', '焦虑', '着急',
            '天哪', '急死人', '揪心', '好担心',
            '还能喝不', '要不要换', '有没有问题',
            '能不能喝', '咋办', '咋整',
            '选什么奶粉', '选麻了', '天塌了',
            '不知道买什么奶粉', '不知道换啥',
            '求推荐', '马上要生产了',
            '是不是我娃', '我娃吃了', '宝宝吃了',
            '这要换啥', '这下咋整'
        ]
        has_panic = any(kw in text_lower for kw in panic_keywords)
        is_doubao = '@豆包' in text

        if has_panic or is_doubao:
            emotion = '恐慌焦虑'
        # 宝宝症状+担忧 → 恐慌焦虑
        elif '[流泪]' in text or '[大哭]' in text:
            symptom_keywords = ['吐奶', '拉肚子', '腹泻', '便血', '呕吐', '绿便', '奶瓣',
                               '不舒服', '腹胀', '哭闹', '发烧', '过敏']
            if any(kw in text_lower for kw in symptom_keywords):
                emotion = '恐慌焦虑'

    # 3. 正面检测
    if emotion == '':
        approval_keywords = [
            '放心', '没有问题', '可以继续喝', '官方确认安全', '没影响',
            '未受影响', '没事', '娃从出生就喝', '一直喝', '这款奶粉',
            '爱喝', '嘎嘎爱喝', '不会换', '各方面都挺好',
            '长势稳稳当当', '身高', '长高', '长肉',
            '体重', '涨了', '健康', '壮', '好得很', '囤奶', '正常喝'
        ]
        if any(kw in text_lower for kw in approval_keywords):
            emotion = '正面'

    # 4. 庆幸旁观检测
    if emotion == '':
        lucky_keywords = [
            '还好没买', '幸好没买', '多亏没买', '还好不是', '还好', '好在', '好险',
            '国产更好', '喝母乳', '不喝外国奶',
            '幸好没选', '两个娃都喝', '不喝外国货',
            '感谢自己拖拉', '幸亏没换', '幸亏没',
            '暗自观察', '又出事啦', '希望守住',
            '早就换了', '暗自庆幸', '我机智', '我选对了'
        ]
        if any(kw in text_lower for kw in lucky_keywords):
            emotion = '庆幸旁观'

    # 5. 默认中性
    if emotion == '':
        emotion = '中性'

    # ========== 认知层分类（4分类）==========
    # 优先级：泛化抵触 > 精准认知 > 信息混淆 > 无明确认知

    # 1. 泛化抵触检测
    resist_keywords = [
        '所有奶粉', '所有品牌', '都不行', '都有问题', '都不安全',
        '不如母乳', '干脆不喝', '还是母乳好',
        '所有', '全部', '一律'
    ]
    if any(kw in text_lower for kw in resist_keywords):
        cognitive = '泛化抵触'
    # 2. 精准认知检测
    elif any(kw in text_lower for kw in [
        'fda', '检出', '仅限美国', '特定批次', '国标', '配方安全',
        '海关总署', '检测合格', '召回范围', '官方声明'
    ]):
        cognitive = '精准认知'
    # 3. 信息混淆检测
    elif any(kw in text_lower for kw in ['分不清', '搞混', '版本']):
        cognitive = '信息混淆'
    # 4. 默认无明确认知
    else:
        cognitive = '无明确认知'

    # ========== 行动层分类（4分类）==========
    # 优先级：维权诉求 > 转奶流失 > 寻求帮助 > 暂无行动

    # 1. 维权诉求检测
    if any(kw in text_lower for kw in ['12315', '投诉', '索赔', '退换', '退款', '赔偿', '退货', '维权']):
        action = '维权诉求'
    # 2. 转奶流失检测
    elif any(kw in text_lower for kw in [
        '换了', '转奶', '退了', '换回', '准备换', '已经换',
        '买了国产', '算买国产', '转皇家', '转爱他美', '转德爱',
        '换飞鹤', '换蓝臻', '换海普', '换1897',
        '吃完就换', '只喝了一箱', '马上换',
        '彻底下决心', '再也不会', '绝对不买'
    ]):
        action = '转奶流失'
    # 3. 寻求帮助检测
    elif any(kw in text_lower for kw in [
        '怎么办', '咋整', '怎么处理', '求推荐', '哪个好',
        '有没有问题', '是不是', '能不能', '能不能喝',
        '要不要换', '怎么选', '选哪个'
    ]):
        action = '寻求帮助'
    # 4. 默认暂无行动
    else:
        action = '暂无行动'

    return cognitive, emotion, action


def get_comment_type(text: str) -> str:
    """判断评论类型"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '普通内容'

    # 检查纯@无互动
    if is_pure_at_no_interaction(text):
        return '纯@无互动'

    # @某人互动
    if re.search(r'@[a-zA-Z0-9_-]+', text):
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

    if re.search(r'a2至初|a2紫白金|a2紫曜|至初.*a2|紫白金.*a2|紫曜.*a2', text_lower):
        brands.append('a2')
    elif re.search(r'\ba2\b', text_lower) and 'a2蛋白质' not in text_lower:
        brands.append('a2')

    brand_patterns = {
        '爱他美': [r'爱他美', r'德爱', r'澳爱', r'卓傲', r'领熠'],
        '飞鹤': [r'飞鹤', r'卓睿', r'臻爱倍护'],
        '君乐宝': [r'君乐宝', r'至臻', r'乐铂', r'红旗帜'],
        '金领冠': [r'金领冠', r'塞纳牧', r'珍护', r'育护'],
        '美赞臣': [r'美赞臣', r'蓝臻', r'铂睿', r'亲舒'],
        '美素佳儿': [r'美素佳儿', r'皇家美素佳儿'],
        '雀巢': [r'雀巢', r'能恩', r'贝巴'],
        '惠氏': [r'惠氏', r'启赋'],
    }

    for brand, patterns in brand_patterns.items():
        if any(re.search(p, text_lower) for p in patterns):
            brands.append(brand)

    return '|'.join(brands) if brands else ''


def run_tagging_v10(input_file: str, output_file: str = None):
    """运行v10标记流程"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)
    print(f"原始数据: {len(df)}条")

    # 时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    # 统计纯@无互动
    df['is_pure_at'] = df['评论内容'].apply(is_pure_at_no_interaction)
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

    # 逐行处理
    for idx, row in df_to_analyze.iterrows():
        text = str(row['评论内容']) if pd.notna(row['评论内容']) else ''
        is_p1 = phase1_mask[idx]
        is_p2 = phase2_mask[idx]

        # 更新评论类型
        df_to_analyze.at[idx, '评论内容类型'] = get_comment_type(text)

        # 更新品牌提及
        df_to_analyze.at[idx, '品牌提及'] = extract_brand_mentions(text)

        # 分类
        cog, emo, act = classify_comment(text)

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
    print("=== v10分类统计结果 ===")
    print("="*60)

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
    import sys
    if len(sys.argv) < 3:
        print("用法: python tag_comments_v10.py <输入文件> <输出文件>")
    else:
        run_tagging_v10(sys.argv[1], sys.argv[2])