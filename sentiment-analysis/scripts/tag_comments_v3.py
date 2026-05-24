"""
A2奶粉舆情分析 - 修正标记脚本 v3
基于已有标注进行修正：
1. 修复品牌识别(A2产品:至初/紫白金/紫曜)
2. 对指定行进行重新分类
3. 降低负面内容门槛
"""

import pandas as pd
import re
from typing import Tuple

# ============ 品牌识别函数 ============
def extract_brand_mentions(text: str) -> str:
    """提取品牌提及（修正版：A2包括至初/紫白金/紫曜）"""
    if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
        return ''

    text_lower = text.lower()
    brands = []

    # A2品牌 - 包括至初/紫白金/紫曜/a2/A2
    if re.search(r'a2至初|a2紫白金|a2紫曜|A2至初|A2紫白金|A2紫曜|至初.*a2|紫白金.*a2|紫曜.*a2|a2.*至初|a2.*紫白金|a2.*紫曜', text_lower):
        brands.append('A2')
    elif re.search(r'\ba2\b|a2奶粉|a2牛奶', text_lower):
        brands.append('A2')

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
    if re.search(r'雀巢|能恩|贝巴|beba|BEBA', text_lower):
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

    # 其他品牌
    if re.search(r'伊利|贝因美|雅士利|澳优|蒙牛|旗帜|bubs|佳贝艾特|优博', text_lower):
        if 'A2' not in brands and '爱他美' not in brands:
            brands.append('其他品牌')

    return '|'.join(brands) if brands else ''


# ============ 分类函数 ============
def classify_comment(text: str, current_cognitive: str, current_emotion: str, current_behavior: str) -> Tuple[str, str, str]:
    """
    根据用户要求，只修改以下情况的标签：
    - 认知层 = 无明确认知 → 可以改为精准认知/信息混淆/泛化抵触
    - 情绪层 = 中性 → 可以改为正面/负面/庆幸旁观/恐慌焦虑/愤怒背叛
    - 行动层 = 暂无行动 → 可以改为寻求帮助/转奶流失/维权诉求

    已在目标状态的保持不变
    """
    text_lower = text.lower()

    # ========== 愤怒背叛检测 ==========
    # "该死"、"欺骗"、"造假"、"破产被收购"、等
    if re.search(r'该死|欺骗|忽悠|被骗|上当|造假|破产|恶意|黑心|无良|骗子|垃圾品牌|气愤|失望透顶', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '泛化抵触'
        else:
            new_cog = current_cognitive

        if current_emotion == '中性':
            new_emo = '愤怒背叛'
        else:
            new_emo = current_emotion

        if current_behavior == '暂无行动':
            new_beh = '暂无行动'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 恐慌焦虑检测 ==========
    # "会不会有事"、"有影响吗"、"怎么办"、"瑟瑟发抖"、"急死人了"、等
    # 特别是提到A2问有没有问题的
    if re.search(r'会不会有事|有影响吗|有危害吗|怎么办|瑟瑟发抖|慌|害怕|担心|担忧|焦虑|着急|害怕|天哪|急死人', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '无明确认知'
        else:
            new_cog = current_cognitive

        if current_emotion == '中性':
            new_emo = '恐慌焦虑'
        else:
            new_emo = current_emotion

        if current_behavior == '暂无行动':
            new_beh = '寻求帮助'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 正面情绪检测 ==========
    # "放心"、"没有召回"、"放心喝"、"没问题"、"可以继续喝"、等
    if re.search(r'放心|没有召回|放心喝|没问题|可以继续喝|没事|没影响|未受影响', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '精准认知'
        else:
            new_cog = current_cognitive

        if current_emotion == '中性':
            new_emo = '正面'
        else:
            new_emo = current_emotion

        if current_behavior == '暂无行动':
            new_beh = '暂无行动'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 庆幸旁观检测 ==========
    # "还好没买"、"德爱拉肚子"、"飞鹤又吐又拉"、等
    competitor_negative = re.search(r'德爱.*拉肚子|德爱.*吐|飞鹤.*又吐又拉|爱他美.*召回|贝巴.*不长肉|贝拉米.*问题|君乐宝.*没事|飞鹤.*没事|金领冠.*没事', text_lower)
    lucky_escape = re.search(r'还好没买|幸好没买|多亏没买|还好不是|还好|好在|好险', text_lower)
    own_brand_ok = re.search(r'我家.*没事|我们.*没问题|孩子.*没事|一直喝.*没事', text_lower)

    if competitor_negative or lucky_escape or own_brand_ok:
        if current_emotion == '中性':
            new_emo = '庆幸旁观'
        else:
            new_emo = current_emotion

        if current_cognitive == '无明确认知':
            new_cog = '无明确认知'
        else:
            new_cog = current_cognitive

        if current_behavior == '暂无行动':
            new_beh = '暂无行动'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 负面情绪检测（降低门槛） ==========
    # "拉肚子"、"呕吐"、"绿便"、"崩溃"、"吐槽"、等
    a2_problem = re.search(r'拉肚子|腹泻|吐奶|呕吐|绿便|奶瓣|不舒服|腹胀|哭闹|发烧|过敏|崩溃|吐槽|好担心', text_lower)
    if a2_problem and re.search(r'a2|至初|紫白金|紫曜', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '泛化抵触'
        else:
            new_cog = current_cognitive

        if current_emotion == '中性':
            new_emo = '负面'
        else:
            new_emo = current_emotion

        if current_behavior == '暂无行动':
            if re.search(r'转奶|换奶粉|换奶|准备换|打算换|已经换|不想喝|不要了', text_lower):
                new_beh = '转奶流失'
            else:
                new_beh = '暂无行动'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 信息混淆检测 ==========
    # "分不清"、"哪个好"、"怎么选"、等
    if re.search(r'分不清|混淆|搞不清|哪个好|怎么选|哪个安全|能不能喝|要不要换', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '信息混淆'
        else:
            new_cog = current_cognitive
        return current_cognitive, current_emotion, current_behavior

    # ========== 泛化抵触检测 ==========
    # "所有奶粉"、"所有品牌"、"都不行"、等
    if re.search(r'所有奶粉|所有品牌|都不行|都有问题|都不安全|不如母乳|干脆不喝|还是母乳好', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '泛化抵触'
        else:
            new_cog = current_cognitive

        if current_emotion == '中性':
            new_emo = '负面'
        else:
            new_emo = current_emotion

        if current_behavior == '暂无行动':
            new_beh = '转奶流失'
        else:
            new_beh = current_behavior
        return new_cog, new_emo, new_beh

    # ========== 精准认知检测 ==========
    # 提到官方声明、FDA、具体批次等
    if re.search(r'fda.*检出|仅限美国|特定批次|国标|配方.*安全|海关总署|检测.*合格|召回范围', text_lower):
        if current_cognitive == '无明确认知':
            new_cog = '精准认知'
        else:
            new_cog = current_cognitive
        return new_cog, current_emotion, current_behavior

    # 如果已经在目标状态之外，不修改
    return current_cognitive, current_emotion, current_behavior


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


def run_correction(input_file: str, output_file: str = None):
    """运行修正流程"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)

    print(f"总数据量: {len(df)} 条")

    # 解析时间阶段
    df['评论时间_str'] = df['评论时间'].astype(str)
    phase1_mask = df['评论时间_str'].str.startswith('2026-04')
    phase2_mask = df['评论时间_str'].str.startswith('2026-05')

    # 初始化统计
    stats = {
        'modified': 0,
        'brand_fixed': 0,
        'cognitive': {'阶段一': {}, '阶段二': {}},
        'emotion': {'阶段一': {}, '阶段二': {}},
        'action': {'阶段一': {}, '阶段二': {}},
    }

    # 逐行处理
    for idx, row in df.iterrows():
        text = str(row['评论内容']) if pd.notna(row['评论内容']) else ''
        is_p1 = phase1_mask[idx]
        is_p2 = phase2_mask[idx]

        # 1. 修复品牌提及列(Z列)
        old_brands = row['品牌提及']
        new_brands = extract_brand_mentions(text)
        if old_brands != new_brands:
            df.at[idx, '品牌提及'] = new_brands
            stats['brand_fixed'] += 1

        # 2. 根据阶段获取当前分类
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

        # 3. 重新分类（只修改指定状态）
        new_cog, new_emo, new_beh = classify_comment(text, current_cog, current_emo, current_beh)

        # 4. 更新分类
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

        # Progress
        if idx % 1000 == 0:
            print(f"  已处理 {idx}/{len(df)} 条...")

    # 删除临时列
    df = df.drop(columns=['评论时间_str'])

    # 打印统计
    print("\n" + "="*50)
    print("=== 修正统计 ===")
    print("="*50)
    print(f"品牌提及修复: {stats['brand_fixed']}条")
    print(f"分类修改: {stats['modified']}条")

    print("\n【第一阶段分类】")
    print(f"  认知层: {stats['cognitive']['阶段一']}")
    print(f"  情绪层: {stats['emotion']['阶段一']}")
    print(f"  行动层: {stats['action']['阶段一']}")

    print("\n【第二阶段分类】")
    print(f"  认知层: {stats['cognitive']['阶段二']}")
    print(f"  情绪层: {stats['emotion']['阶段二']}")
    print(f"  行动层: {stats['action']['阶段二']}")

    # 品牌统计
    print("\n【品牌提及TOP10】")
    all_brands = []
    for brands_str in df['品牌提及']:
        if pd.notna(brands_str) and isinstance(brands_str, str) and brands_str.strip():
            all_brands.extend(brands_str.split('|'))
    brand_counts = pd.Series(all_brands).value_counts()
    print(brand_counts.head(10).to_string())

    # 保存
    if output_file:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"\n已保存到: {output_file}")

    return df


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python tag_comments_v3.py <输入文件> <输出文件>")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2]
        run_correction(input_f, output_f)