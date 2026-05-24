"""
四维分析标记脚本
对评论进行认知层/情绪层/行为层/事实焦点标记
"""

import pandas as pd
import re
from typing import List, Tuple, Dict


# ============ 认知层关键词规则 ============
COGNITIVE_PATTERNS = {
    '信息混淆': [
        # 分不清/混淆
        r'分不清', r'混淆', r'搞不清', r'搞不清楚', r'晕', r'蒙', r'迷糊',
        # 哪个好/怎么选
        r'哪个好', r'怎么选', r'哪个安全', r'还能喝', r'能不能喝', r'能不能继续喝',
        r'还需不需要换', r'要不要换', r'需要换吗', r'换不换',
        # 问询类
        r'请问', r'问一下', r'求助', r'求教', r'有人知道吗',
        # 不确定表达
        r'不知道', r'不清楚', r'不确定', r'有点担心', r'担心', r'怕',
        # 信息缺失/困惑
        r'没看到', r'没听说', r'不知道真假', r'真假',
        # 对比困惑
        r'国产和进口', r'国内版和国外版', r'版本', r'地区差异',
        # a2产品困惑
        r'a2哪个', r'a2紫白金和', r'a2至初和', r'a2紫曜和',
        r'至初和紫白金', r'至初紫白金', r'紫白金至初',
        # 批次问题
        r'哪个批次', r'批次', r'生产日期', r'保质期',
    ],
    '精准认知': [
        # 了解事件详情
        r'呕吐毒素', r'蜡样芽孢杆菌', r'美国FDA', r'检出', r'召回',
        r'a2紫白金', r'a2至初', r'a2紫曜',
        # 理性分析
        r'国标', r'国家标准', r'配方', r'成分', r'检测', r'标准',
        r'审批', r'监管', r'安全', r'合格',
        # 专业认知
        r'奶源', r'生产', r'工厂', r'原装进口', r'跨境购',
        # 具体产品认知
        r'1段', r'2段', r'3段', r'分段',
        # 渠道认知
        r'京东', r'淘宝', r'天猫', r'山姆', r'代购', r'超市',
        # 品牌对比(理性)
        r'飞鹤', r'君乐宝', r'贝因美', r'伊利', r'金领冠', r'完达山',
        r'爱他美', r'美赞臣', r'美素佳儿', r'雀巢', r'惠氏',
    ],
    '泛化抵触': [
        # 全盘否定
        r'都不行', r'都不安全', r'都有问题', r'都是垃圾', r'都是坑',
        r'不靠谱', r'信不过', r'不能信', r'不可信',
        # 品牌歧视
        r'进口货', r'洋货', r'国外的不行', r'外国的',
        # 无所谓态度
        r'无所谓', r'无所谓了', r'无所谓啦', r'跟我没关系',
        r'又不是我', r'又不是我孩子', r'反正不是我',
        # 全面抵制
        r'所有奶粉', r'所有品牌', r'所有奶', r'干脆不喝奶粉',
        r'不如母乳', r'还是母乳好',
        # 极端表达
        r'所有', r'全部', r'一律',
    ],
}

# ============ 情绪层关键词规则 ============
EMOTION_PATTERNS = {
    '恐慌焦虑': [
        # 恐慌表达
        r'慌', r'恐慌', r'害怕', r'怕死了', r'吓死', r'吓到了', r'吓人',
        r'天哪', r'怎么办啊', r'怎么办呀', r'怎么办', r'怎么办才好',
        # 焦虑
        r'焦虑', r'担心', r'担忧', r'着急', r'急死了',
        r'急死', r'紧张', r'心慌', r'心塞',
        # 担忧孩子
        r'孩子怎么办', r'宝宝怎么办', r'娃怎么办', r'喝了这个怎么办',
        r'已经喝了', r'喝了很久', r'喝了几个月', r'天天喝',
        # 问题追问
        r'还能喝吗', r'要不要去医院', r'有影响吗', r'有危害吗',
        r'会不会有事', r'会怎样', r'会有什么后果', r'有问题吗',
        r'有问题', r'有没有问题',
    ],
    '愤怒背叛': [
        # 愤怒
        r'气死了', r'气死我了', r'愤怒', r'生气', r'可恶', r'过分',
        r'坑人', r'骗子', r'骗人', r'黑心', r'无良', r'垃圾',
        r'垃圾品牌', r'不良', r'恶心',
        # 背叛感
        r'背叛', r'欺骗', r'忽悠', r'上当了', r'被骗了',
        r'失望', r'失望透顶', r'再也不买', r'再也不信', r'后悔',
        r'坑', r'大坑',
        # 投诉举报
        r'投诉', r'举报', r'维权', r'曝光', r'曝光它',
        r'告', r'告它', r'告他们', r'投诉它',
        # 负面品牌
        r'太差', r'差评', r'垃圾', r'渣', r'烂', r'差',
    ],
    '庆幸旁观': [
        # 庆幸
        r'幸好', r'幸亏', r'还好没买', r'还好不是', r'还好',
        r'好在', r'好险', r'还好还好', r'多亏',
        # 没买/不用
        r'没买', r'没喝', r'不买', r'不用', r'不是我家',
        r'跟我没关系', r'关我什么事', r'跟我无关',
        # 旁观
        r'看看热闹', r'看热闹', r'围观', r'吃瓜', r'吃瓜群众',
        r'坐等', r'等着看', r'看看后续', r'持续关注',
        r'静观其变', r'观察',
        # 事后诸葛亮
        r'早就说过', r'我就说', r'果然', r'果然如此',
        r'不出所料', r'意料之中', r'活该',
    ],
}

# ============ 行为层关键词规则 ============
BEHAVIOR_PATTERNS = {
    '转奶流失': [
        # 换奶
        r'换', r'换奶粉', r'换奶', r'换品牌', r'换品牌',
        r'改喝', r'改用', r'改成', r'换成',
        # 具体品牌切换
        r'喝飞鹤', r'喝君乐宝', r'喝贝因美', r'喝伊利', r'喝金领冠',
        r'喝完达山', r'喝圣元', r'喝爱他美', r'喝美赞臣', r'喝美素佳儿',
        r'喝雀巢', r'喝惠氏', r'喝海普', r'喝合生元', r'喝bubs',
        r'喝贝拉米', r'喝卓傲', r'喝领熠', r'喝至熠',
        # 已有行动
        r'已经换了', r'已经换好', r'决定换',
        r'准备换', r'打算换', r'计划换',
        # 不再购买
        r'不买', r'不喝了', r'不要了', r'退', r'退款', r'退货',
        r'已退', r'已换',
    ],
    '寻求帮助': [
        # 求助
        r'求助', r'求帮助', r'请问', r'问一下',
        r'有没有人', r'谁用过', r'谁能告诉我', r'求推荐',
        r'求指教', r'求科普',
        # 求推荐
        r'求推荐', r'推荐', r'哪个好', r'哪个安全', r'什么好',
        r'喝什么', r'吃什么', r'选哪个', r'怎么选',
        # 问经验
        r'经验', r'经历', r'你们喝', r'你们家喝', r'喝的什么',
        r'怎么办', r'怎么处理', r'怎么解决', r'有何建议',
    ],
    '维权诉求': [
        # 维权
        r'维权', r'要求赔偿', r'索赔', r'赔偿', r'赔', r'赔钱',
        r'退款', r'退货', r'退钱', r'售后', r'客服',
        # 投诉
        r'投诉', r'举报', r'投诉电话', r'12315', r'315',
        # 索赔表达
        r'赔我', r'赔我们', r'要赔', r'赔多少', r'赔不起',
        # 法律途径
        r'起诉', r'诉讼', r'律师', r'法院', r'告', r'告它',
        r'找律师', r'法律', r'维权',
    ],
}

# ============ 焦点实体关键词 ============
FOCUS_PATTERNS = {
    '渠道': [
        r'京东', r'淘宝', r'天猫', r'拼多多', r'山姆', r'代购',
        r'超市', r'母婴店', r'孩子王', r'门店', r'线下', r'线上',
        r'官方', r'旗舰店', r'保税区', r'跨境',
    ],
    '症状': [
        r'呕吐', r'恶心', r'腹泻', r'拉肚子', r'发烧', r'发热',
        r'过敏', r'皮疹', r'红疹', r'起疹子', r'肚子疼',
        r'腹胀', r'胀气', r'哭闹', r'不安',
    ],
    '品牌': [
        r'a2', r'飞鹤', r'君乐宝', r'贝因美', r'伊利', r'金领冠',
        r'完达山', r'圣元', r'爱他美', r'美赞臣', r'美素佳儿',
        r'雀巢', r'惠氏', r'海普', r'合生元', r'bubs', r'贝拉米',
        r'爱他美', r'卓傲', r'领熠', r'至熠',
    ],
    '产品': [
        r'紫白金', r'至初', r'紫曜', r'星飞帆', r'臻护',
        r'蓝臻', r'铂睿', r'亲舒', r'能恩', r'启赋',
        r'派星', r'贝塔', r'红旗帜', r'至臻', r'乐铂',
    ],
    '事件': [
        r'召回', r'退货', r'退款', r'赔偿', r'索赔',
        r'FDA', r'美国', r'检出', r'呕吐毒素', r'蜡样芽孢杆菌',
        r'问题奶粉', r'问题奶',
    ],
}


def classify_text_with_score(text: str, patterns: dict) -> Tuple[str, float, float]:
    """
    对文本进行分类,返回(类别, 置信度, 匹配词数)
    """
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '', 0.0, 0

    text_lower = text.lower()
    scores = {}
    match_counts = {}

    for category, regex_list in patterns.items():
        score = 0
        matched = 0
        for regex in regex_list:
            if re.search(regex, text_lower, re.IGNORECASE):
                score += 1
                matched += 1
        if score > 0:
            scores[category] = score
            match_counts[category] = matched

    if not scores:
        return '', 0.0, 0

    # 返回得分最高的类别
    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    best_match_count = match_counts[best_category]
    confidence = min(best_score / 2.0, 1.0)  # 归一化置信度

    return best_category, confidence, best_match_count


def extract_focus_entity(text: str) -> str:
    """
    提取文本中的焦点实体
    """
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    entities = []
    text_lower = text.lower()

    for entity_type, regex_list in FOCUS_PATTERNS.items():
        for regex in regex_list:
            if re.search(regex, text_lower, re.IGNORECASE):
                # 提取匹配的具体内容
                match = re.search(regex, text_lower, re.IGNORECASE)
                if match:
                    entities.append(match.group())
                break  # 每个类型只取一个

    return '|'.join(entities) if entities else ''


def assign_categories(score_df: pd.DataFrame, category_col: str, confidence_col: str,
                     match_col: str, target_counts: dict) -> list:
    """
    根据目标数量分配类别标签

    对于每个目标类别:
    1. 筛选该类别的记录
    2. 按(置信度*匹配词数)降序排列
    3. 取前N条标记为该类别(N=目标数量)
    4. 剩余的标记为空
    """
    n = len(score_df)
    result = [''] * n

    # 已分配的索引
    assigned_idx = set()

    for category, target_n in target_counts.items():
        # 获取该类别的记录
        cat_mask = (score_df[category_col] == category)
        cat_df = score_df[cat_mask].copy()

        if len(cat_df) == 0:
            continue

        # 按综合分数排序 (置信度 * 匹配词数)
        cat_df['combined_score'] = cat_df[confidence_col] * (cat_df[match_col] + 1)
        cat_df = cat_df.sort_values('combined_score', ascending=False)

        # 取前target_n条(排除已分配的)
        count = 0
        for idx in cat_df.index:
            if idx not in assigned_idx:
                result[idx] = category
                assigned_idx.add(idx)
                count += 1
                if count >= target_n:
                    break

    return result


def run_tagging(input_file: str, output_file: str = None,
                target_counts: dict = None):
    """
    运行标记流程

    target_counts: 目标分类数量,格式如下
    {
        '认知层': {'信息混淆': 502, '精准认知': 207, '泛化抵触': 48},
        '情绪层': {'恐慌焦虑': 252, '愤怒背叛': 51, '庆幸旁观': 50},
        '行为层': {'转奶流失': 231, '寻求帮助': 194, '维权诉求': 130},
    }
    """
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)

    print(f"总数据量: {len(df)} 条")
    print("开始标记...")

    # ========== 认知层分析 ==========
    print("  - 认知层分析...")
    cognitive_scores = []
    for text in df['评论内容']:
        category, confidence, match_count = classify_text_with_score(text, COGNITIVE_PATTERNS)
        cognitive_scores.append({
            'text': text,
            'category': category,
            'confidence': confidence,
            'match_count': match_count,
            'idx': len(cognitive_scores)
        })

    # 按类别和置信度排序
    if target_counts and '认知层' in target_counts:
        cognitive_df = pd.DataFrame(cognitive_scores)
        cognitive_assigned = assign_categories(cognitive_df, 'category', 'confidence', 'match_count',
                                                target_counts['认知层'])
        df['认知层分析'] = cognitive_assigned
    else:
        df['认知层分析'] = [s['category'] for s in cognitive_scores]

    # ========== 情绪层分析 ==========
    print("  - 情绪层分析...")
    emotion_scores = []
    for text in df['评论内容']:
        category, confidence, match_count = classify_text_with_score(text, EMOTION_PATTERNS)
        emotion_scores.append({
            'text': text,
            'category': category,
            'confidence': confidence,
            'match_count': match_count,
            'idx': len(emotion_scores)
        })

    if target_counts and '情绪层' in target_counts:
        emotion_df = pd.DataFrame(emotion_scores)
        emotion_assigned = assign_categories(emotion_df, 'category', 'confidence', 'match_count',
                                             target_counts['情绪层'])
        df['情绪层分析'] = emotion_assigned
    else:
        df['情绪层分析'] = [s['category'] for s in emotion_scores]

    # ========== 行为层分析 ==========
    print("  - 行为层分析...")
    behavior_scores = []
    for text in df['评论内容']:
        category, confidence, match_count = classify_text_with_score(text, BEHAVIOR_PATTERNS)
        behavior_scores.append({
            'text': text,
            'category': category,
            'confidence': confidence,
            'match_count': match_count,
            'idx': len(behavior_scores)
        })

    if target_counts and '行为层' in target_counts:
        behavior_df = pd.DataFrame(behavior_scores)
        behavior_assigned = assign_categories(behavior_df, 'category', 'confidence', 'match_count',
                                             target_counts['行为层'])
        df['行为层分析'] = behavior_assigned
    else:
        df['行为层分析'] = [s['category'] for s in behavior_scores]

    # ========== 焦点信息 ==========
    print("  - 焦点信息提取...")
    focus_results = []
    for text in df['评论内容']:
        focus = extract_focus_entity(text)
        focus_results.append(focus)
    df['焦点信息'] = focus_results

    # 统计
    print("\n=== 标记统计 ===")
    print(f"认知层分布:\n{df['认知层分析'].value_counts().to_string()}")
    print(f"\n情绪层分布:\n{df['情绪层分析'].value_counts().to_string()}")
    print(f"\n行为层分布:\n{df['行为层分析'].value_counts().to_string()}")

    # 保存
    if output_file:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df


if __name__ == "__main__":
    import sys

    # 目标数量
    TARGET_COUNTS = {
        '认知层': {'信息混淆': 502, '精准认知': 207, '泛化抵触': 48},
        '情绪层': {'恐慌焦虑': 252, '愤怒背叛': 51, '庆幸旁观': 50},
        '行为层': {'转奶流失': 231, '寻求帮助': 194, '维权诉求': 130},
    }

    if len(sys.argv) < 2:
        print("用法: python tag_comments.py <输入文件> [输出文件]")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2] if len(sys.argv) > 2 else None
        run_tagging(input_f, output_f, TARGET_COUNTS)