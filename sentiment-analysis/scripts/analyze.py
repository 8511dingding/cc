"""
舆情分析 - 分析脚本
根据分析逻辑对清洗后的数据进行定性定量分析
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set


class SentimentAnalyzer:
    """舆情分析器"""

    # 品牌映射表
    BRAND_PRODUCTS = {
        'a2': ['a2至初', 'a2紫白金', 'a2紫曜'],
        '合生元': ['派星', '天呵', '贝塔星耀'],
        '爱他美': ['奇迹绿', '德爱', '领熠', '澳爱', '至熠', '卓傲'],
        '美素佳儿': ['皇家美素佳儿', '源悦', '莼悦', '签名版'],
        '圣元优博': ['剖蓓舒', '瑞霂', '金爱嘉', '瑞可嘉'],
        '美赞臣': ['蓝臻', '铂睿', '亲舒'],
        '金领冠': ['塞纳牧', '珍护', '育护', '铂粹', '护'],
        '惠氏': ['启赋蕴淳', '未来', '蓝钻', '铂金'],
        '完达山': ['菁稚非凡', '元乳臻益', '菁采稚护', '菁美稚纯'],
        '贝拉米': ['卓越', '白金', '蓝盾', '贝拉米经典'],
        '雀巢': ['能恩全护', '超级能恩', '贝巴'],
        '飞鹤': ['卓睿', '臻爱倍护', '臻稚卓蓓', '星飞帆'],
        '君乐宝': ['至臻', '乐铂博越', '红旗帜', '淳护'],
        '海普1897': ['未来', '荷'],
        'bubs': ['贝臻'],
    }

    # 品牌归属纠正表
    CORRECTION_MAP = {
        'a2智初': ('a2', 'a2至初'),
        'a2紫耀': ('a2', 'a2紫曜'),
        '紫药': None,
        'a2倍臻': ('君乐宝', '至臻A2'),
        '倍臻a2': ('君乐宝', '至臻A2'),
        '爱他美致意': ('爱他美', '至熠'),
        '爱他美领意': ('爱他美', '领熠'),
    }

    # a2品牌产品
    A2_PRODUCTS = {'a2至初', 'a2紫白金', 'a2紫曜'}

    # 痛点关键词（按阶段分类）
    PAIN_POINTS = {
        '孕期': ['催产', '顺产', '胎教', '糖筛', '孕辰纹', '孕期瑜伽', '预期护肤', '妊娠纹', '腿抽筋',
                '静脉曲张', '口腔不适', '孕吐', '胎动', '孕期糖尿病', '孕期高血压', '流鼻血', '产检',
                '囤货', '腰疼', '营养', '新生儿', '待产包', '奶粉店', '月嫂', '坐月子', '接近母乳',
                '胎位', '奶粉一段', '第一口奶', '痔疮', '宫缩', '便秘', '抽筋', '水肿', '肚肚健康',
                '肠道', '肠胃', '消化不好', '积食', '吸收'],
        '1段（0-7个月）': ['适应', '基础', '消化', '刚出生', '新生儿', '0-12个月', '早产', '哺乳期', '月子',
                         '1段', '母乳', '奶源', '奶量不足', '胀气', '便秘', '吸收', '哭闹', '夜醒', '熬夜',
                         '咕咕叫', '每天拉几次', '玻璃胃', '绿便', '奶瓣', '吐奶', '起小疹子', '红点点', '过敏'],
        '2段（7-12个月）': ['成长', '体重变化', '添加辅食', '2段', '0-12个月', '长肉', '长胖', '身高', '体检',
                          '断奶', '转奶', '混喂', '厌奶', '哺乳期', '产假', '拉稀', '发烧', '儿保'],
        '3段（1岁以上）': ['3段', '拉肚子', '消化', '腹痛', '长高', '体重不达标'],
        '喂养痛点': ['拉肚子', '宝宝胀气', '奶粉过敏', '新生儿吐奶', '便秘', '消化不良', '肚子咕咕叫',
                   '宝宝拉奶瓣', '不长肉', '体重不够', '瘦', '不长个', '绿便', '拉稀', '便便干',
                   '便便硬', '红疹', '上火', '不吸收', '消耗不好', '肚肚不舒服哭闹'],
    }

    def __init__(self, analysis_logic_dir: str = None):
        self.all_products = set()
        for products in self.BRAND_PRODUCTS.values():
            self.all_products.update(products)
        self.all_products.update(self.A2_PRODUCTS)

    def correct_text(self, text: str) -> str:
        """文本纠错"""
        for error, correction in self.CORRECTION_MAP.items():
            if correction is None:
                if error in text:
                    return ""
            else:
                actual_brand, actual_product = correction
                if error in text:
                    text = text.replace(error, actual_product)
        return text

    def extract_brand_mentions(self, text: str) -> List[Tuple[str, str]]:
        """提取品牌和产品提及"""
        mentions = []
        for product in self.A2_PRODUCTS:
            if product in text:
                mentions.append(('a2', product))
        for brand, products in self.BRAND_PRODUCTS.items():
            if brand == 'a2':
                continue
            for product in products:
                if product in text:
                    mentions.append((brand, product))
        return mentions

    def extract_pain_points(self, text: str) -> Dict[str, List[str]]:
        """提取痛点关键词"""
        found = {stage: [] for stage in self.PAIN_POINTS.keys()}
        for stage, keywords in self.PAIN_POINTS.items():
            for kw in keywords:
                if kw in text:
                    found[stage].append(kw)
        return {k: v for k, v in found.items() if v}

    def analyze_sentiment(self, text: str) -> str:
        """分析情感倾向"""
        positive_words = ['好', '棒', '喜欢', '推荐', '赞', '值得', '不错', '满意', '健康', '长肉', '长高', '长胖', '厉害', '感谢', '完美']
        negative_words = ['差', '烂', '不好', '失望', '后悔', '讨厌', '吐槽', '问题', '过敏', '便秘', '拉肚子', '吐奶', '绿便', '糟', '坑', '黑', '骗子']
        neutral_words = ['吗', '是不是', '怎么样', '哪个好', '如何', '求助', '求教']

        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)

        if pos_count > neg_count:
            return '正面'
        elif neg_count > pos_count:
            return '负面'
        else:
            return '中性'

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'cleaned_text') -> Dict:
        """分析整个DataFrame"""
        results = {
            'total_count': len(df),
            'sentiment_distribution': {},
            'brand_mentions': {},
            'product_mentions': {},
            'pain_points': {},
            'a2_mentions': 0,
        }

        sentiments = df[text_column].apply(self.analyze_sentiment)
        results['sentiment_distribution'] = sentiments.value_counts().to_dict()

        all_brands = []
        all_products = []
        pain_points_all = []

        for text in df[text_column]:
            mentions = self.extract_brand_mentions(text)
            all_brands.extend([m[0] for m in mentions])
            all_products.extend([m[1] for m in mentions])

            pain_points = self.extract_pain_points(text)
            for stage, kws in pain_points.items():
                pain_points_all.extend([f"{stage}:{kw}" for kw in kws])

            if any(p in text for p in self.A2_PRODUCTS):
                results['a2_mentions'] += 1

        results['brand_mentions'] = pd.Series(all_brands).value_counts().to_dict() if all_brands else {}
        results['product_mentions'] = pd.Series(all_products).value_counts().to_dict() if all_products else {}
        results['pain_points'] = pd.Series(pain_points_all).value_counts().to_dict() if pain_points_all else {}

        return results


def run_analysis(input_file: str, output_file: str = None, text_column: str = 'cleaned_text'):
    """运行分析"""
    print(f"读取数据: {input_file}")
    df = pd.read_excel(input_file)
    analyzer = SentimentAnalyzer()
    print("开始分析...")
    results = analyzer.analyze_dataframe(df, text_column)

    print("\n=== 分析结果 ===")
    print(f"总条数: {results['total_count']}")
    print(f"a2品牌提及: {results['a2_mentions']}条")
    print(f"\n情感分布: {results['sentiment_distribution']}")
    print(f"\n品牌提及: {results['brand_mentions']}")
    print(f"\n产品提及: {results['product_mentions']}")
    print(f"\n痛点词分布: {results['pain_points']}")

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python analyze.py <清洗后数据文件> [输出文件]")
    else:
        input_f = sys.argv[1]
        output_f = sys.argv[2] if len(sys.argv) > 2 else None
        run_analysis(input_f, output_f)