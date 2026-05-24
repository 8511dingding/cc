"""
A2奶粉舆情分析 - 完整分类标记脚本
严格按照分类标准对每条评论进行标记
"""

import pandas as pd
import re
from typing import Tuple, Dict, List

# ============ 分类标准常量 ============
COGNITIVE_LABELS = ['无明确认知', '信息混淆', '精准认知', '泛化抵触']
EMOTION_LABELS = ['正面', '中性', '负面', '庆幸旁观', '恐慌焦虑', '愤怒背叛']
BEHAVIOR_LABELS = ['暂无行动', '转奶流失', '寻求帮助', '维权诉求']

# ============ 认知层关键词规则 ============
COGNITIVE_PATTERNS = {
    '信息混淆': [
        r'分不清', r'混淆', r'搞不清', r'搞不清楚', r'晕', r'蒙', r'迷糊',
        r'哪个好', r'怎么选', r'哪个安全', r'还能喝', r'能不能喝', r'能不能继续喝',
        r'还需不需要换', r'要不要换', r'需要换吗', r'换不换',
        r'请问', r'问一下', r'求助', r'求教', r'有人知道吗',
        r'不知道', r'不清楚', r'不确定', r'有点担心', r'担心', r'怕',
        r'没看到', r'没听说', r'不知道真假', r'真假',
        r'国产和进口', r'国内版和国外版', r'版本', r'地区差异',
        r'a2哪个', r'a2紫白金和', r'a2至初和', r'a2紫曜和',
        r'至初和紫白金', r'至初紫白金', r'紫白金至初',
        r'哪个批次', r'批次', r'生产日期', r'保质期',
    ],
    '精准认知': [
        r'呕吐毒素', r'蜡样芽孢杆菌', r'美国FDA', r'检出', r'召回',
        r'a2紫白金', r'a2至初', r'a2紫曜',
        r'国标', r'国家标准', r'配方', r'成分', r'检测', r'标准',
        r'审批', r'监管', r'安全', r'合格',
        r'奶源', r'生产', r'工厂', r'原装进口', r'跨境购',
        r'1段', r'2段', r'3段', r'分段',
        r'京东', r'淘宝', r'天猫', r'山姆', r'代购', r'超市',
    ],
    '泛化抵触': [
        r'都不行', r'都不安全', r'都有问题', r'都是垃圾', r'都是坑',
        r'不靠谱', r'信不过', r'不能信', r'不可信',
        r'进口货', r'洋货', r'国外的不行', r'外国的',
        r'无所谓', r'无所谓了', r'无所谓啦', r'跟我没关系',
        r'又不是我', r'又不是我孩子', r'反正不是我',
        r'所有奶粉', r'所有品牌', r'所有奶', r'干脆不喝奶粉',
        r'不如母乳', r'还是母乳好',
        r'所有', r'全部', r'一律',
        r'破产', r'华人收购', r'造假',
    ],
}

# ============ 情绪层关键词规则 ============
EMOTION_PATTERNS = {
    '恐慌焦虑': [
        r'慌', r'恐慌', r'害怕', r'怕死了', r'吓死', r'吓到了', r'吓人',
        r'天哪', r'怎么办啊', r'怎么办呀', r'怎么办', r'怎么办才好',
        r'焦虑', r'担心', r'担忧', r'着急', r'急死了',
        r'急死', r'紧张', r'心慌', r'心塞',
        r'孩子怎么办', r'宝宝怎么办', r'娃怎么办', r'喝了这个怎么办',
        r'已经喝了', r'喝了很久', r'喝了几个月', r'天天喝',
        r'还能喝吗', r'要不要去医院', r'有影响吗', r'有危害吗',
        r'会不会有事', r'会怎样', r'会有什么后果', r'有问题吗',
        r'有问题', r'有没有问题', r'瑟瑟发抖',
    ],
    '愤怒背叛': [
        r'气死了', r'气死我了', r'愤怒', r'生气', r'可恶', r'过分',
        r'坑人', r'骗子', r'骗人', r'黑心', r'无良', r'垃圾',
        r'垃圾品牌', r'不良', r'恶心',
        r'背叛', r'欺骗', r'忽悠', r'上当了', r'被骗了',
        r'失望', r'失望透顶', r'再也不买', r'再也不信', r'后悔',
        r'坑', r'大坑', r'该死', r'要命',
    ],
    '庆幸旁观': [
        r'幸好', r'幸亏', r'还好没买', r'还好不是', r'还好',
        r'好在', r'好险', r'还好还好', r'多亏',
        r'没买', r'没喝', r'不买', r'不用', r'不是我家',
        r'跟我没关系', r'关我什么事', r'跟我无关',
        r'看看热闹', r'看热闹', r'围观', r'吃瓜', r'吃瓜群众',
        r'坐等', r'等着看', r'看看后续', r'持续关注',
        r'静观其变', r'观察',
        r'早就说过', r'我就说', r'果然', r'果然如此',
        r'不出所料', r'意料之中', r'活该',
    ],
}

# ============ 行为层关键词规则 ============
BEHAVIOR_PATTERNS = {
    '转奶流失': [
        r'换', r'换奶粉', r'换奶', r'换品牌', r'换品牌',
        r'改喝', r'改用', r'改成', r'换成',
        r'喝飞鹤', r'喝君乐宝', r'喝贝因美', r'喝伊利', r'喝金领冠',
        r'喝完达山', r'喝圣元', r'喝爱他美', r'喝美赞臣', r'喝美素佳儿',
        r'喝雀巢', r'喝惠氏', r'喝海普', r'喝合生元', r'喝bubs',
        r'喝贝拉米', r'喝卓傲', r'喝领熠', r'喝至熠',
        r'已经换了', r'已经换好', r'决定换',
        r'准备换', r'打算换', r'计划换',
        r'不买', r'不喝了', r'不要了', r'退', r'退款', r'退货',
        r'已退', r'已换', r'转奶', r'转奶粉',
    ],
    '寻求帮助': [
        r'求助', r'求帮助', r'请问', r'问一下',
        r'有没有人', r'谁用过', r'谁能告诉我', r'求推荐',
        r'求指教', r'求科普',
        r'求推荐', r'推荐', r'哪个好', r'哪个安全', r'什么好',
        r'喝什么', r'吃什么', r'选哪个', r'怎么选',
        r'经验', r'经历', r'你们喝', r'你们家喝', r'喝的什么',
        r'怎么办', r'怎么处理', r'怎么解决', r'有何建议',
    ],
    '维权诉求': [
        r'维权', r'要求赔偿', r'索赔', r'赔偿', r'赔', r'赔钱',
        r'退款', r'退货', r'退钱', r'售后', r'客服',
        r'投诉', r'举报', r'投诉电话', r'12315', r'315',
        r'赔我', r'赔我们', r'要赔', r'赔多少', r'赔不起',
        r'起诉', r'诉讼', r'律师', r'法院', r'告', r'告它',
        r'找律师', r'法律', r'维权',
    ],
}


def classify_cognitive(text: str) -> str:
    """认知层分类"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    text_lower = text.lower()
    scores = {}

    for category, regex_list in COGNITIVE_PATTERNS.items():
        score = 0
        for regex in regex_list:
            if re.search(regex, text_lower, re.IGNORECASE):
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return ''

    # 优先返回得分最高的类别
    best_category = max(scores, key=scores.get)
    return best_category


def classify_emotion(text: str) -> str:
    """情绪层分类"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    text_lower = text.lower()
    scores = {}

    for category, regex_list in EMOTION_PATTERNS.items():
        score = 0
        for regex in regex_list:
            if re.search(regex, text_lower, re.IGNORECASE):
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return ''

    # 优先返回得分最高的类别
    best_category = max(scores, key=scores.get)
    return best_category


def classify_behavior(text: str) -> str:
    """行为层分类"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    text_lower = text.lower()
    scores = {}

    for category, regex_list in BEHAVIOR_PATTERNS.items():
        score = 0
        for regex in regex_list:
            if re.search(regex, text_lower, re.IGNORECASE):
                score += 1
        if score > 0:
            scores[category] = score

    if not scores:
        return ''

    # 优先返回得分最高的类别
    best_category = max(scores, key=scores.get)
    return best_category


def extract_brand_mentions(text: str) -> List[str]:
    """提取品牌和产品提及"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return []

    brands_products = [
        # A2品牌
        'a2至初', 'a2紫白金', 'a2紫曜', 'A2至初', 'A2紫白金', 'A2紫曜',
        # 爱他美产品
        '爱他美', '德爱', '领熠', '至熠', '卓傲', '澳爱',
        # 飞鹤产品
        '飞鹤', '卓睿', '臻爱倍护', '臻稚卓蓓', '星飞帆',
        # 君乐宝产品
        '君乐宝', '至臻', '乐铂', '红旗帜', '淳护',
        # 金领冠产品
        '金领冠', '塞纳牧', '珍护', '育护', '铂粹', '护',
        # 美素佳儿产品
        '美素佳儿', '皇家美素佳儿', '源悦',
        # 美赞臣产品
        '美赞臣', '蓝臻', '铂睿', '亲舒',
        # 合生元产品
        '合生元', '派星', '天呵', '贝塔星耀',
        # 雀巢产品
        '雀巢', '能恩', '超级能恩', '贝巴', '贝芭',
        # 惠氏产品
        '惠氏', '启赋', '启赋蕴淳',
        # 圣元产品
        '圣元', '剖蓓舒', '瑞霂', '金爱嘉', '瑞可嘉',
        # 完达山产品
        '完达山', '菁稚非凡', '元乳臻益',
        # 贝拉米产品
        '贝拉米', '卓越', '白金',
        # 海普诺凯1897
        '海普', '海普诺凯1897', '荷致',
        # 其他品牌
        '伊利', '贝因美', '雅士利', '澳优', '蒙牛',
        '旗帜', '红帽子', '蓝钻', '铂金',
        'bubs', '贝臻', '佳贝艾特', '优博', '瑞利',
    ]

    mentions = []
    text_lower = text.lower()
    for bp in brands_products:
        if bp.lower() in text_lower:
            mentions.append(bp)

    return mentions


def get_comment_type(text: str) -> str:
    """判断评论类型"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '普通内容'

    # @某人互动
    if re.search(r'@[一-龥a-zA-Z0-9_-]+', text):
        return '@某人互动'

    # 长内容(>100字)
    if len(text) > 100:
        return '长内容(>100字)'

    # 提及竞品(检查常见竞品关键词)
    competitor_keywords = [
        '爱他美', '美赞臣', '美素佳儿', '雀巢', '惠氏', '海普', '合生元',
        '飞鹤', '君乐宝', '金领冠', '贝因美', '伊利', '完达山', '圣元',
        '贝拉米', 'bubs', '澳优', '蒙牛', '雅士利', '佳贝艾特', '优博',
    ]
    for kw in competitor_keywords:
        if kw in text:
            return '提及竞品'

    return '普通内容'


def run_tagging(input_file: str, output_file: str = None):
    """运行完整标记流程"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)

    print(f"总数据量: {len(df)} 条")
    print("开始逐条标记...")

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    print(f"第一阶段(4月): {phase1_mask.sum()}条")
    print(f"第二阶段(5月): {phase2_mask.sum()}条")

    # 初始化新列
    df['评论内容类型'] = ''
    df['认知层阶段一'] = ''
    df['认知层阶段二'] = ''
    df['情绪层阶段一'] = ''
    df['情绪层阶段二'] = ''
    df['行为层阶段一'] = ''
    df['行为层阶段二'] = ''
    df['品牌提及'] = ''

    # 逐条标记
    for idx, row in df.iterrows():
        text = str(row['评论内容']) if pd.notna(row['评论内容']) else ''

        # 评论类型
        comment_type = get_comment_type(text)
        df.at[idx, '评论内容类型'] = comment_type

        # 品牌提及
        brands = extract_brand_mentions(text)
        df.at[idx, '品牌提及'] = '|'.join(brands) if brands else ''

        # 根据阶段分配标签
        if phase1_mask[idx]:
            df.at[idx, '认知层阶段一'] = classify_cognitive(text)
            df.at[idx, '情绪层阶段一'] = classify_emotion(text)
            df.at[idx, '行为层阶段一'] = classify_behavior(text)
        elif phase2_mask[idx]:
            df.at[idx, '认知层阶段二'] = classify_cognitive(text)
            df.at[idx, '情绪层阶段二'] = classify_emotion(text)
            df.at[idx, '行为层阶段二'] = classify_behavior(text)

        if idx % 1000 == 0:
            print(f"  已处理 {idx}/{len(df)} 条...")

    print("\n=== 标记统计 ===")

    # 评论类型分布
    print("\n【评论类型分布】")
    print(df['评论内容类型'].value_counts().to_string())

    # 第一阶段统计
    p1_df = df[phase1_mask]
    print(f"\n【第一阶段({len(p1_df)}条)】")
    print(f"认知层: {p1_df['认知层阶段一'].value_counts().to_string()}")
    print(f"情绪层: {p1_df['情绪层阶段一'].value_counts().to_string()}")
    print(f"行为层: {p1_df['行为层阶段一'].value_counts().to_string()}")

    # 第二阶段统计
    p2_df = df[phase2_mask]
    print(f"\n【第二阶段({len(p2_df)}条)】")
    print(f"认知层: {p2_df['认知层阶段二'].value_counts().to_string()}")
    print(f"情绪层: {p2_df['情绪层阶段二'].value_counts().to_string()}")
    print(f"行为层: {p2_df['行为层阶段二'].value_counts().to_string()}")

    # 品牌提及统计
    print("\n【品牌提及TOP20】")
    all_brands = []
    for brands_str in df['品牌提及']:
        if brands_str:
            all_brands.extend(brands_str.split('|'))
    brand_counts = pd.Series(all_brands).value_counts()
    print(brand_counts.head(20).to_string())

    # 删除临时列
    df = df.drop(columns=['评论时间_str'])

    # 保存
    if output_file:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python tag_comments_full.py <输入文件> <输出文件>")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2]
        run_tagging(input_f, output_f)