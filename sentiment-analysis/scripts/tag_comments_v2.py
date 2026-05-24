"""
A2奶粉舆情分析 - 重新分类标记脚本 v2
严格按照分类标准对每条评论进行标记
基于人工标注样本学习规律
"""

import pandas as pd
import re
from typing import List, Tuple

# ============ 核心分类规则（基于标注样本学习）============

def classify_comment(text: str) -> Tuple[str, str, str]:
    """
    对评论进行三维分类
    返回: (认知层, 情绪层, 行为层)
    """
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '', '', ''

    text_lower = text.lower()

    # ========== 情绪层判断（最先判断，影响最大）==========

    # 1. 愤怒背叛检测 - 品牌阴谋论、被骗感、全盘否定
    # "该死"、"欺骗"、"造假"、"破产被收购"、"怀疑是因为A2"、等
    if re.search(r'该死|欺骗|忽悠|被骗|上当|造假|破产|恶意|黑心|无良|骗子|垃圾品牌|气愤|愤怒|失望透顶', text_lower):
        # 如果还有"所有奶粉"、"所有品牌" = 泛化抵触
        if re.search(r'所有|全部|都|一律|不如母乳', text_lower):
            return '泛化抵触', '愤怒背叛', '暂无行动'
        return '泛化抵触', '愤怒背叛', '暂无行动'

    # 2. 恐慌焦虑检测 - 担心宝宝健康、问有没有问题
    # "会不会有事"、"有影响吗"、"怎么办"、"瑟瑟发抖"、等
    if re.search(r'会不会有事|有影响吗|有危害吗|怎么办|瑟瑟发抖|慌|害怕|担心|担忧|焦虑|着急|害怕|天哪', text_lower):
        # 如果提到A2产品问题（拉肚子、呕吐等）= 负面
        if re.search(r'拉肚子|腹泻|吐奶|呕吐|绿便|不舒服|有问题', text_lower):
            return '无明确认知', '负面', '暂无行动'
        return '无明确认知', '恐慌焦虑', '寻求帮助'

    # 3. 庆幸旁观检测 - 竞品负面、庆幸没买/已换、品牌对比
    # "还好没买"、"德爱拉肚子"、"飞鹤又吐又拉"、"我家没事"
    competitor_negative = re.search(r'德爱.*拉肚子|德爱.*吐|飞鹤.*又吐又拉|爱他美.*召回|贝巴.*不长肉|贝拉米.*问题|君乐宝.*没事|飞鹤.*没事|金领冠.*没事', text_lower)
    lucky_escape = re.search(r'还好没买|幸好没买|多亏没买|还好不是|还好|好在|好险', text_lower)
    own_brand_ok = re.search(r'我家.*没事|我们.*没问题|孩子.*没事|一直喝.*没事', text_lower)

    if competitor_negative or lucky_escape or own_brand_ok:
        # 检查是否是A2产品问题导致的
        if re.search(r'a2.*拉肚子|a2.*腹泻|a2.*吐|a2.*绿便|至初.*问题|紫白金.*问题', text_lower):
            return '泛化抵触', '负面', '转奶流失'
        return '无明确认知', '庆幸旁观', '暂无行动'

    # 4. A2产品问题 = 负面情绪
    # "拉肚子三个月"、"绿便"、"腹泻" - 宝宝喝A2出现问题
    a2_problem = re.search(r'拉肚子|腹泻|吐奶|呕吐|绿便|奶瓣|不舒服|腹胀|哭闹|发烧|过敏', text_lower)
    if a2_problem and re.search(r'a2|至初|紫白金', text_lower):
        # 判断是A2问题导致的转奶还是只是询问
        if re.search(r'转奶|换奶粉|换奶|准备换|打算换|已经换|不想喝|不要了', text_lower):
            return '泛化抵触', '负面', '转奶流失'
        return '泛化抵触', '负面', '暂无行动'

    # 5. 官方声明/理性分析 - 精准认知 + 正面
    # "FDA检出"、"仅限美国"、"国标"、"配方"
    if re.search(r'海关总署|fda.*检出|国行版.*安全|未受影响|仅限美国|特定批次|配方.*安全|检测.*合格', text_lower):
        return '精准认知', '正面', '暂无行动'

    # 6. 为A2辩护/一直喝A2没事 - 正面
    if re.search(r'一直喝.*没事|从出生.*就喝|我家一直喝|孩子一直喝.*没问题', text_lower):
        if not a2_problem:
            return '无明确认知', '正面', '暂无行动'

    # 7. 中性询问 - 无明确认知 + 中性
    # "请问"、"求助"、"怎么样"、"哪个好"、"能喝吗"
    if re.search(r'请问|求助|问一下|求推荐|哪个好|怎么样|能不能喝|能喝吗|有问题吗', text_lower):
        # 如果提到竞品，在做选择
        if re.search(r'爱他美|飞鹤|君乐宝|金领冠|贝拉米|美素|海普', text_lower):
            return '信息混淆', '中性', '寻求帮助'
        return '无明确认知', '中性', '寻求帮助'

    # 8. 泛化抵触 - 全盘否定所有奶粉
    if re.search(r'所有奶粉|所有品牌|都不行|都有问题|都不安全|不如母乳|干脆不喝|还是母乳好', text_lower):
        return '泛化抵触', '负面', '转奶流失'

    # 默认：无明确认知 + 中性 + 暂无行动
    return '无明确认知', '中性', '暂无行动'


def get_comment_type(text: str, is_phase1: bool) -> str:
    """判断评论类型"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return '普通内容'

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


def extract_brand_mentions(text: str) -> List[str]:
    """提取品牌提及（仅品牌层面）"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return []

    brands = []

    # A2品牌
    if re.search(r'a2至初|a2紫白金|a2紫曜|A2至初|A2紫白金|A2紫曜', text):
        brands.append('A2')

    # 爱他美
    if re.search(r'爱他美|德爱|领熠|至熠|卓傲|澳爱', text):
        brands.append('爱他美')

    # 飞鹤
    if re.search(r'飞鹤|卓睿|臻爱倍护', text):
        brands.append('飞鹤')

    # 君乐宝
    if re.search(r'君乐宝|至臻|乐铂|红旗帜', text):
        brands.append('君乐宝')

    # 金领冠
    if re.search(r'金领冠|塞纳牧|珍护|育护', text):
        brands.append('金领冠')

    # 美素佳儿
    if re.search(r'美素佳儿|皇家美素佳儿|源悦', text):
        brands.append('美素佳儿')

    # 美赞臣
    if re.search(r'美赞臣|蓝臻|铂睿|亲舒', text):
        brands.append('美赞臣')

    # 合生元
    if re.search(r'合生元|派星|贝塔星耀', text):
        brands.append('合生元')

    # 雀巢
    if re.search(r'雀巢|能恩|贝巴|beba|BEBA', text):
        brands.append('雀巢')

    # 惠氏
    if re.search(r'惠氏|启赋', text):
        brands.append('惠氏')

    # 圣元
    if re.search(r'圣元|剖蓓舒|金爱嘉', text):
        brands.append('圣元')

    # 完达山
    if re.search(r'完达山|菁稚非凡', text):
        brands.append('完达山')

    # 贝拉米
    if re.search(r'贝拉米', text):
        brands.append('贝拉米')

    # 海普诺凯1897
    if re.search(r'海普|海普诺凯|荷致|1897', text):
        brands.append('海普诺凯1897')

    # 其他
    if re.search(r'伊利|贝因美|雅士利|澳优|蒙牛|旗帜|bubs|佳贝艾特|优博', text):
        brands.append('其他品牌')

    return brands


def run_tagging(input_file: str, output_file: str = None):
    """运行完整标记流程"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)

    print(f"总数据量: {len(df)} 条")
    print("开始逐条分类...")

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    p1_count = phase1_mask.sum()
    p2_count = phase2_mask.sum()
    print(f"第一阶段(4月): {p1_count}条")
    print(f"第二阶段(5月): {p2_count}条")

    # 初始化新列
    df['评论内容类型'] = ''
    df['认知层阶段一'] = ''
    df['认知层阶段二'] = ''
    df['情绪层阶段一'] = ''
    df['情绪层阶段二'] = ''
    df['行动层阶段一'] = ''
    df['行动层阶段二'] = ''
    df['品牌提及'] = ''

    # 统计计数
    stats = {
        '评论内容类型': {},
        '认知层': {'阶段一': {}, '阶段二': {}},
        '情绪层': {'阶段一': {}, '阶段二': {}},
        '行动层': {'阶段一': {}, '阶段二': {}},
    }

    # 逐条分类
    for idx, row in df.iterrows():
        text = str(row['评论内容']) if pd.notna(row['评论内容']) else ''
        is_p1 = phase1_mask[idx]
        is_p2 = phase2_mask[idx]

        # 评论内容类型
        comment_type = get_comment_type(text, is_p1)
        df.at[idx, '评论内容类型'] = comment_type
        stats['评论内容类型'][comment_type] = stats['评论内容类型'].get(comment_type, 0) + 1

        # 品牌提及
        brands = extract_brand_mentions(text)
        df.at[idx, '品牌提及'] = '|'.join(brands) if brands else ''

        # 三维分类
        cognitive, emotion, behavior = classify_comment(text)

        if is_p1:
            df.at[idx, '认知层阶段一'] = cognitive
            df.at[idx, '情绪层阶段一'] = emotion
            df.at[idx, '行动层阶段一'] = behavior

            stats['认知层']['阶段一'][cognitive] = stats['认知层']['阶段一'].get(cognitive, 0) + 1
            stats['情绪层']['阶段一'][emotion] = stats['情绪层']['阶段一'].get(emotion, 0) + 1
            stats['行动层']['阶段一'][behavior] = stats['行动层']['阶段一'].get(behavior, 0) + 1

        elif is_p2:
            df.at[idx, '认知层阶段二'] = cognitive
            df.at[idx, '情绪层阶段二'] = emotion
            df.at[idx, '行动层阶段二'] = behavior

            stats['认知层']['阶段二'][cognitive] = stats['认知层']['阶段二'].get(cognitive, 0) + 1
            stats['情绪层']['阶段二'][emotion] = stats['情绪层']['阶段二'].get(emotion, 0) + 1
            stats['行动层']['阶段二'][behavior] = stats['行动层']['阶段二'].get(behavior, 0) + 1

        if idx % 1000 == 0:
            print(f"  已处理 {idx}/{len(df)} 条...")

    # 删除临时列
    df = df.drop(columns=['评论时间_str'])

    # 打印统计
    print("\n" + "="*50)
    print("=== 分类统计结果 ===")
    print("="*50)

    print("\n【评论内容类型分布】(全部)")
    for k, v in sorted(stats['评论内容类型'].items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}条")

    print(f"\n【第一阶段({p1_count}条)】")
    print(f"  认知层: {stats['认知层']['阶段一']}")
    print(f"  情绪层: {stats['情绪层']['阶段一']}")
    print(f"  行动层: {stats['行动层']['阶段一']}")

    print(f"\n【第二阶段({p2_count}条)】")
    print(f"  认知层: {stats['认知层']['阶段二']}")
    print(f"  情绪层: {stats['情绪层']['阶段二']}")
    print(f"  行动层: {stats['行动层']['阶段二']}")

    # 品牌提及统计
    print("\n【品牌提及TOP10】")
    all_brands = []
    for brands_str in df['品牌提及']:
        if brands_str and isinstance(brands_str, str):
            all_brands.extend(brands_str.split('|'))
    brand_counts = pd.Series(all_brands).value_counts()
    print(brand_counts.head(10).to_string())

    # 保存
    if output_file:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df, stats


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python tag_comments_v2.py <输入文件> <输出文件>")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2]
        run_tagging(input_f, output_f)