"""
A2奶粉舆情分析 - 完整分类标记脚本 v4
基于最新的分类标准手册，对每条评论进行标记
增强转奶流失识别
"""

import pandas as pd
import re
from typing import Tuple, List

# ============ 分类函数 ============

def classify_comment(text: str, current_cognitive: str, current_emotion: str, current_behavior: str) -> Tuple[str, str, str]:
    """
    根据最新规则对评论进行三维分类
    规则优先级：
    1. 愤怒背叛 > 其他情绪
    2. 恐慌焦虑 > 中性
    3. 正面 > 中性
    4. 庆幸旁观判定
    5. 负面判定
    6. 转奶流失检测
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
        '偷偷召回', '根本没有', '站不住脚', '缺乏说服力',
        '人为分类', '夸大宣传', '什么鬼东西', '为什么这么害人'
    ]

    has_anger = any(kw in text_lower for kw in anger_keywords)

    # 小作文类（长篇质疑分析）
    is_long_essay = len(text) > 100 and any(kw in text_lower for kw in [
        '请问', '为什么', '问题', '疑问', '几个问题', '是不是',
        '怎么突然', '到底', '根本站不住脚', '缺乏说服力', '分析'
    ])

    if has_anger or is_long_essay:
        new_cog = '泛化抵触'
        new_emo = '愤怒背叛'
        new_beh = '暂无行动'
        return new_cog, new_emo, new_beh

    # ========== 恐慌焦虑检测（优先级第二）==========

    panic_keywords = [
        '会不会有事', '有影响吗', '有危害吗', '怎么办', '瑟瑟发抖',
        '慌', '害怕', '担心', '担忧', '焦虑', '着急', '害怕',
        '天哪', '急死人', '揪心', '好担心', '还能喝不', '要不要换',
        '有没有问题', '能不能喝', '还能不能喝', '咋办', '咋搞',
        '要不要换', '选什么奶粉', '选麻了', '天塌了',
        '不知道买什么奶粉', '不知道换啥', '不知道换哪个',
        '求推荐', '马上要生产了', '6月份预产期',
        '买不到货', '到处都买不到', '断货', '魂都吓飞',
        '紧张', '扎心', '不敢', '不懂给娃喝什么', '要命',
        '新生儿', '刚喝上', '暂时没症状', '该不该转', '贝拉米吗'
    ]

    is_doubao = '@豆包' in text

    has_panic = any(kw in text_lower for kw in panic_keywords)

    if has_panic or is_doubao:
        new_cog = current_cognitive if current_cognitive != '无明确认知' else '无明确认知'
        new_emo = '恐慌焦虑'
        new_beh = '寻求帮助' if current_behavior == '暂无行动' else current_behavior
        return new_cog, new_emo, new_beh

    # ========== 正面检测（优先级第三）==========

    approval_keywords = [
        '放心', '没有问题', '可以继续喝', '官方确认安全', '没影响',
        '未受影响', '没事', '娃从出生就喝', '一直喝', '这款奶粉',
        '没有问题', '肯定没事', '爱喝', '嘎嘎爱喝', '不会换',
        '各方面都挺好', '长势稳稳当当', '身高', '长高', '长肉',
        '体重', '涨了', '健康', '壮', '好得很', '囤奶', '正常喝',
        '货源稳定', '有货', '补货', 'PDD', '刚在', '没有问题呀',
        '没有不良反应', '没有异常', '金黄色', '黏糊糊', '非常好',
        '自己很机智', '转奶成功', '一直很好', '没什么问题',
        '可以继续吃', '相信a2', '万幸'
    ]

    has_approval = any(kw in text_lower for kw in approval_keywords)

    if has_approval:
        new_cog = '精准认知' if current_cognitive == '无明确认知' else current_cognitive
        new_emo = '正面'
        new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 庆幸旁观检测（优先级第四）==========

    lucky_keywords = [
        '还好没买', '幸好没买', '多亏没买', '还好不是', '还好',
        '好在', '好险', '国产更好', '喝母乳', '不喝外国奶',
        '幸好没选', '两个娃都喝', '不喝外国货', '感谢自己拖拉',
        '幸亏没换', '幸亏没', '暗自观察', '又出事啦',
        '希望守住', '洋货', '崇洋', '只适合薅礼品',
        '跟风', '虚荣心', '有钱人', '自己国家产的', '从来不坑穷人',
        '一百多快', '才一百多', '便宜又好', '有机美素佳儿',
        '母乳坚持', '奶粉喝不起', '自愿召回', '抠字眼', '嘲讽'
    ]

    competitor_bad = any(re.search(kw, text_lower) for kw in [
        r'德爱.*拉肚子', r'德爱.*塌', r'飞鹤.*又吐又拉', r'爱他美.*召回',
        r'贝巴.*不长肉', r'贝拉米.*问题', r'君乐宝.*没事', r'飞鹤.*没事',
        r'雀巢.*塌', r'蓝河.*断货', r'蓝河.*经常断货'
    ])

    has_lucky = any(kw in text_lower for kw in lucky_keywords) or competitor_bad

    if has_lucky:
        new_cog = current_cognitive
        new_emo = '庆幸旁观'
        new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 负面检测（优先级第五）==========

    a2_problem = any(kw in text_lower for kw in [
        '拉肚子', '腹泻', '吐奶', '呕吐', '绿便', '奶瓣',
        '不舒服', '腹胀', '哭闹', '发烧', '过敏', '崩溃',
        '不咋地', '不长肉', '踩雷', '惊心', '背刺', '贝壳',
        '干呕', '爱吐', '喷射', '化不开', '大便结块',
        '性价比不高', '又贵', '市场占有率', '塌房', '塌了',
        '不行', '不合适', '丧心病狂', '网红产品', '分次数转'
    ])

    has_a2 = any(kw in text_lower for kw in ['a2', '至初', '紫白金', '紫曜'])

    if a2_problem and has_a2:
        # 只有提到"所有"、"所有奶粉"等泛化概念才是泛化抵触
        # 具体产品问题（吐、拉肚子、不合适等）不算泛化抵触
        has_generalize = any(kw in text_lower for kw in [
            '所有奶粉', '所有品牌', '都不行', '都有问题', '都不安全',
            '不如母乳', '干脆不喝', '还是母乳好', '所有', '全部', '一律'
        ])
        new_cog = '泛化抵触' if has_generalize else '精准认知'
        new_emo = '负面'
        # 检查转奶动作
        switch_action = any(kw in text_lower for kw in [
            '换了', '转奶', '退了', '换回', '准备换', '已经换',
            '买了国产', '算了买国产', '转皇家', '转爱他美', '转德爱',
            '转雀巢', '换飞鹤', '换蓝臻', '换海普', '换1897',
            '换皇家', '换爱他美', '换澳爱', '换回国产', '换国产',
            '吃完就换', '只喝了一箱', '马上换', '退了2罐'
        ])

        if switch_action:
            new_beh = '转奶流失'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 泛化抵触检测 ==========

    resist_keywords = [
        '所有奶粉', '所有品牌', '都不行', '都有问题', '都不安全',
        '不如母乳', '干脆不喝', '还是母乳好', '所有', '全部', '一律'
    ]

    has_resist = any(kw in text_lower for kw in resist_keywords)

    if has_resist:
        new_cog = '泛化抵触'
        new_emo = '负面'
        switch_action = any(kw in text_lower for kw in [
            '换了', '转奶', '退了', '换回', '准备换'
        ])
        new_beh = '转奶流失' if switch_action else current_behavior
        return new_cog, new_emo, new_beh

    # ========== 转奶流失检测（优先级第六）==========

    switch_keywords = [
        '换了', '换了x', '换奶粉', '转x了', '准备换', '吃完就换',
        '推荐哪个', '不知道换哪个', '选麻了', '又要换奶粉',
        '换什么奶粉好', '换哪个呀', '转奶', '换回', '换国产',
        '转皇家', '转爱他美', '转德爱', '转雀巢', '换飞鹤', '换蓝臻',
        '换海普', '换1897', '换澳爱', '换皇家', '换爱他美卓傲',
        '退2罐', '退不了', '只喝了一箱', '马上换', '要换奶粉了',
        '不知道换啥', '求推荐', '又要找奶粉', '不知道买什么奶粉',
        '纠结选', '想换成', '准备换', '不知道买什么', '马上要生产',
        '6月份预产期', '要断货了', '没货了', '山姆没货',
        '转贝拉米', '要转贝拉米吗', '一夜转奶', '转奶成功',
        '踩坑', '每次都踩坑', '算了买国产', '信不过了',
        '一样吗', '是一样吗', '是不是', '国产的.*有问题吗'
    ]

    has_switch = any(kw in text_lower for kw in switch_keywords)

    if has_switch:
        new_cog = current_cognitive if current_cognitive != '无明确认知' else '无明确认知'
        new_emo = '负面' if a2_problem else ('中性' if current_emotion == '中性' else current_emotion)
        new_beh = '转奶流失'
        return new_cog, new_emo, new_beh

    # ========== 精准认知检测 ==========

    precise_keywords = [
        'fda.*检出', '仅限美国', '特定批次', '国标', '配方.*安全',
        '海关总署', '检测.*合格', '召回范围', '官方声明', '美版问题',
        '区域配方', '单点质控', '美国标准差异',
        '美版.*不是', '完全两码事', '客服.*告诉', '特意问了客服',
        '批次号.*2210', '批次号.*2211', '半毛钱关系没有',
        '美国市场销售', '0-12个月', '婴儿配方奶粉', '自愿召回',
        '白紧张', '没关系'
    ]

    has_precise = any(re.search(kw, text_lower, re.IGNORECASE) for kw in precise_keywords)

    if has_precise:
        new_cog = '精准认知'
        new_emo = '正面' if current_emotion == '中性' else current_emotion
        new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # 如果已经是目标状态之外，不修改
    return current_cognitive, current_emotion, current_behavior


def get_comment_type(text: str) -> str:
    """判断评论类型"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '普通内容'

    if re.search(r'@[一-龥a-zA-Z0-9_-]+', text):
        return '@某人互动'

    if len(text) > 100:
        return '长内容(>100字)'

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
    """提取品牌提及（修正版：小写a2）"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    text_lower = text.lower()
    brands = []

    # a2品牌
    if re.search(r'a2至初|a2紫白金|a2紫曜|至初.*a2|紫白金.*a2|紫曜.*a2|a2.*至初|a2.*紫白金|a2.*紫曜', text_lower):
        brands.append('a2')
    elif re.search(r'\ba2\b', text_lower) and 'a2蛋白质' not in text_lower and 'a2成分' not in text_lower:
        brands.append('a2')

    # 爱他美
    if re.search(r'爱他美|德爱|领熠|至熠|卓傲|澳爱', text_lower):
        brands.append('爱他美')

    # 飞鹤
    if re.search(r'飞鹤|卓睿|臻爱倍护', text_lower):
        brands.append('飞鹤')

    # 君乐宝
    if re.search(r'君乐宝|至臻|乐铂|红旗帜', text_lower):
        brands.append('君乐宝')

    # 金领冠
    if re.search(r'金领冠|塞纳牧|珍护|育护', text_lower):
        brands.append('金领冠')

    # 美素佳儿
    if re.search(r'美素佳儿|皇家美素佳儿|源悦', text_lower):
        brands.append('美素佳儿')

    # 美赞臣
    if re.search(r'美赞臣|蓝臻|铂睿|亲舒', text_lower):
        brands.append('美赞臣')

    # 合生元
    if re.search(r'合生元|派星|贝塔星耀', text_lower):
        brands.append('合生元')

    # 雀巢
    if re.search(r'雀巢|能恩|贝巴|beba|贝芭', text_lower):
        brands.append('雀巢')

    # 惠氏
    if re.search(r'惠氏|启赋', text_lower):
        brands.append('惠氏')

    # 圣元
    if re.search(r'圣元|剖蓓舒|金爱嘉', text_lower):
        brands.append('圣元')

    # 完达山
    if re.search(r'完达山|菁稚非凡', text_lower):
        brands.append('完达山')

    # 贝拉米
    if re.search(r'贝拉米', text_lower):
        brands.append('贝拉米')

    # 海普诺凯1897
    if re.search(r'海普|海普诺凯|荷致|1897', text_lower):
        brands.append('海普诺凯1897')

    # 佳贝艾特
    if re.search(r'佳贝艾特', text_lower):
        brands.append('佳贝艾特')

    # 优博瑞霖
    if re.search(r'优博瑞霖|优博', text_lower):
        brands.append('优博瑞霖')

    # 其他品牌
    if re.search(r'伊利|贝因美|雅士利|澳优|蒙牛|旗帜|bubs', text_lower):
        if 'a2' not in brands and '爱他美' not in brands:
            brands.append('其他品牌')

    return '|'.join(brands) if brands else ''


def run_tagging_v4(input_file: str, output_file: str = None):
    """运行v4标记流程"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)

    print(f"总数据量: {len(df)} 条")
    print("开始逐条分类...")

    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    p1_count = phase1_mask.sum()
    p2_count = phase2_mask.sum()
    print(f"第一阶段(4月): {p1_count}条")
    print(f"第二阶段(5月): {p2_count}条")

    stats = {
        'modified': 0,
        'cognitive': {'阶段一': {}, '阶段二': {}},
        'emotion': {'阶段一': {}, '阶段二': {}},
        'action': {'阶段一': {}, '阶段二': {}},
    }

    for idx, row in df.iterrows():
        text = str(row['评论内容']) if pd.notna(row['评论内容']) else ''
        is_p1 = phase1_mask[idx]
        is_p2 = phase2_mask[idx]

        comment_type = get_comment_type(text)
        df.at[idx, '评论内容类型'] = comment_type

        new_brands = extract_brand_mentions(text)
        df.at[idx, '品牌提及'] = new_brands

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

        new_cog, new_emo, new_beh = classify_comment(text, current_cog, current_emo, current_beh)

        if new_cog != current_cog or new_emo != current_emo or new_beh != current_beh:
            stats['modified'] += 1

        if is_p1:
            df.at[idx, '认知层阶段一'] = new_cog
            df.at[idx, '情绪层阶段一'] = new_emo
            df.at[idx, '行动层阶段一'] = new_beh
            stats['cognitive']['阶段一'][new_cog] = stats['cognitive']['阶段一'].get(new_cog, 0) + 1
            stats['emotion']['阶段一'][new_emo] = stats['emotion']['阶段一'].get(new_emo, 0) + 1
            stats['action']['阶段一'][new_beh] = stats['action']['阶段一'].get(new_beh, 0) + 1

        elif is_p2:
            df.at[idx, '认知层阶段二'] = new_cog
            df.at[idx, '情绪层阶段二'] = new_emo
            df.at[idx, '行动层阶段二'] = new_beh
            stats['cognitive']['阶段二'][new_cog] = stats['cognitive']['阶段二'].get(new_cog, 0) + 1
            stats['emotion']['阶段二'][new_emo] = stats['emotion']['阶段二'].get(new_emo, 0) + 1
            stats['action']['阶段二'][new_beh] = stats['action']['阶段二'].get(new_beh, 0) + 1

        if idx % 1000 == 0:
            print(f"  已处理 {idx}/{len(df)} 条...")

    df = df.drop(columns=['评论时间_str'])

    # 后处理：将所有"认可"替换为"正面"（情绪层合并）
    for col in ['情绪层阶段一', '情绪层阶段二']:
        if col in df.columns:
            df[col] = df[col].replace('认可', '正面')

    print("\n" + "="*50)
    print("=== v4分类统计结果 ===")
    print("="*50)
    print(f"修改记录: {stats['modified']}条")

    print("\n【第一阶段分类】")
    print(f"  认知层: {stats['cognitive']['阶段一']}")
    print(f"  情绪层: {stats['emotion']['阶段一']}")
    print(f"  行动层: {stats['action']['阶段一']}")

    print("\n【第二阶段分类】")
    print(f"  认知层: {stats['cognitive']['阶段二']}")
    print(f"  情绪层: {stats['emotion']['阶段二']}")
    print(f"  行动层: {stats['action']['阶段二']}")

    print("\n【品牌提及TOP10】")
    all_brands = []
    for brands_str in df['品牌提及']:
        if pd.notna(brands_str) and isinstance(brands_str, str) and brands_str.strip():
            all_brands.extend(brands_str.split('|'))
    brand_counts = pd.Series(all_brands).value_counts()
    print(brand_counts.head(10).to_string())

    if output_file:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df, stats


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python tag_comments_v4.py <输入文件> <输出文件>")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2]
        run_tagging_v4(input_f, output_f)