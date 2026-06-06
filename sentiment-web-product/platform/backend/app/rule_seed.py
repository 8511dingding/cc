from app.schemas import BrandRule, RuleDefinition, RuleSet


HISTORICAL_LABEL_RULES = [
    {
        "set_id": "rules-sentiment-a2-v9",
        "category": "标签规则",
        "layer": "情绪层",
        "stage": "s1/s2",
        "label": "正面",
        "keywords": ["放心", "没有问题", "可以继续喝", "官方确认安全", "没影响", "未受影响", "没事", "一直喝", "健康", "囤奶", "正常喝", "货源稳定", "有货", "补货"],
        "priority": 4,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-sentiment-a2-v9",
        "category": "标签规则",
        "layer": "情绪层",
        "stage": "s1/s2",
        "label": "中性",
        "keywords": ["官方说法", "等通报", "看解释", "求证", "真假", "有没有依据"],
        "priority": 2,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-sentiment-a2-v9",
        "category": "标签规则",
        "layer": "情绪层",
        "stage": "s1/s2",
        "label": "恐慌焦虑",
        "keywords": ["会不会有事", "有影响吗", "有危害吗", "怎么办", "慌", "害怕", "担心", "担忧", "焦虑", "着急", "好担心", "还能喝不", "要不要换", "能不能喝", "选什么奶粉", "求推荐", "宝宝吃了", "安全吗", "没事吧", "吐奶", "拉肚子", "便血"],
        "priority": 3,
        "source": "A2 历史分类标准 v9 + 客户修正规则",
    },
    {
        "set_id": "rules-sentiment-a2-v9",
        "category": "标签规则",
        "layer": "情绪层",
        "stage": "s1/s2",
        "label": "庆幸旁观",
        "keywords": ["还好没买", "幸好没买", "多亏没买", "还好不是", "好险", "国产更好", "不喝外国奶", "幸好没选", "暗自观察", "希望守住", "崇洋", "早就换了", "暗自庆幸", "凑热闹", "得亏"],
        "priority": 3,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-sentiment-a2-v9",
        "category": "标签规则",
        "layer": "情绪层",
        "stage": "s1/s2",
        "label": "愤怒背叛",
        "keywords": ["该死", "欺骗", "忽悠", "被骗", "上当", "造假", "黑心", "无良", "骗子", "垃圾品牌", "气愤", "失望透顶", "谁还敢喝", "三鹿", "代工", "贴牌", "塌房", "膈应", "背刺", "资本家", "不负责任", "建议严查", "企业无良", "坑中国人"],
        "priority": 5,
        "source": "A2 历史分类标准 v9 + 客户修正规则",
    },
    {
        "set_id": "rules-cognition-a2-v9",
        "category": "标签规则",
        "layer": "认知层",
        "stage": "s1/s2",
        "label": "无明确认知",
        "keywords": ["看看", "观望", "不知道", "不清楚", "等解释"],
        "priority": 1,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-cognition-a2-v9",
        "category": "标签规则",
        "layer": "认知层",
        "stage": "s1/s2",
        "label": "信息混淆",
        "keywords": ["国行", "澳洲版", "美版", "版本", "分不清", "搞混", "区别", "到底哪个", "哪个是正版", "至初", "国版"],
        "priority": 2,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-cognition-a2-v9",
        "category": "标签规则",
        "layer": "认知层",
        "stage": "s1/s2",
        "label": "精准认知",
        "keywords": ["fda", "检出", "仅限美国", "特定批次", "国标", "配方安全", "海关总署", "检测合格", "召回范围", "官方声明", "美版问题", "区域配方", "美国标准差异"],
        "priority": 3,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-cognition-a2-v9",
        "category": "标签规则",
        "layer": "认知层",
        "stage": "s1/s2",
        "label": "泛化抵触",
        "keywords": ["所有奶粉", "所有品牌", "都不行", "都有问题", "都不安全", "不如母乳", "干脆不喝", "还是母乳好", "全部", "一律", "阴谋论"],
        "priority": 4,
        "source": "A2 历史分类标准 v9 + 客户修正规则",
    },
    {
        "set_id": "rules-action-a2-v9",
        "category": "标签规则",
        "layer": "行动层",
        "stage": "s1/s2",
        "label": "暂无行动",
        "keywords": ["观望", "看看", "等官方", "先不动"],
        "priority": 1,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-action-a2-v9",
        "category": "标签规则",
        "layer": "行动层",
        "stage": "s1/s2",
        "label": "寻求帮助",
        "keywords": ["怎么办", "咋整", "怎么处理", "求推荐", "哪个好", "有没有问题", "是不是", "能不能", "能不能喝", "要不要换", "怎么选", "选哪个", "没事吧", "安全吗", "潜伏期"],
        "priority": 2,
        "source": "A2 历史分类标准 v9",
    },
    {
        "set_id": "rules-action-a2-v9",
        "category": "标签规则",
        "layer": "行动层",
        "stage": "s1/s2",
        "label": "转奶流失",
        "keywords": ["换了", "转奶", "退了", "换回", "准备换", "已经换", "买了国产", "转皇家", "转爱他美", "换飞鹤", "换蓝臻", "吃完就换", "马上换", "再也不会", "绝对不买", "不喝外国奶"],
        "priority": 3,
        "source": "A2 历史分类标准 v9 + 客户修正规则",
    },
    {
        "set_id": "rules-action-a2-v9",
        "category": "标签规则",
        "layer": "行动层",
        "stage": "s1/s2",
        "label": "维权诉求",
        "keywords": ["12315", "投诉", "索赔", "退换", "退款", "赔偿", "退货", "维权", "投诉后退款", "贝壳碎片"],
        "priority": 4,
        "source": "A2 历史分类标准 v9 + 客户修正规则",
    },
]


MILK_POWDER_BRANDS = [
    ("飞鹤", 1, ["飞鹤", "飞鹤奶粉", "飞鹤星飞帆", "星飞帆", "飞鹤卓睿", "卓睿", "飞鹤茁萃", "茁萃", "飞鹤舒贝诺", "FEIHE", "feihe", "fhh"]),
    ("a2", 2, ["a2", "A2", "a2至初", "A2至初", "a2紫白金", "A2紫白金", "a2紫曜", "a2白金", "a2牛奶", "a2奶粉"]),
    ("爱他美", 3, ["爱他美", "Aptamil", "aptamil", "爱他美奶粉", "德爱", "德爱白金", "澳爱", "澳爱他美", "爱他美卓萃", "纽迪希亚"]),
    ("美赞臣", 4, ["美赞臣", "美赞成", "Enfamil", "enfamil", "美赞臣蓝臻", "蓝臻", "美赞臣铂睿", "铂睿", "安儿宝", "美赞臣奶粉"]),
    ("惠氏", 5, ["惠氏", "启赋", "Wyeth", "wyeth", "惠氏启赋", "启赋奶粉", "启赋有机", "启赋蕴淳", "惠氏铂臻", "惠氏S26"]),
    ("皇家美素力", 6, ["皇家美素力", "美素力", "美素佳儿", "皇家美素佳儿", "Friso", "friso", "菲仕兰", "皇家菲仕兰", "皇家美素力奶粉"]),
    ("君乐宝", 7, ["君乐宝", "君乐宝奶粉", "JUNLEBAO", "junlebao", "红旗", "优萃", "君乐宝红旗", "君乐宝优萃", "乐铂", "至臻"]),
    ("金领冠", 8, ["金领冠", "伊利金领冠", "金领冠奶粉", "塞纳牧", "珍护", "睿护", "金领冠塞纳牧", "金领冠珍护", "伊利", "YILI"]),
    ("贝拉米", 9, ["贝拉米", "Bellamy", "Bellamys", "bellamy", "贝拉米奶粉", "贝拉米有机", "贝拉米A2", "贝拉米白金"]),
    ("雀巢", 10, ["雀巢", "Nestle", "nestle", "BEBA", "beba", "雀巢BEBA", "卓傲", "雀巢卓傲", "贝巴", "超级能恩"]),
    ("圣元", 11, ["圣元", "圣元优博", "优博", "优博瑞安", "优博盖", "布瑞弗尼", "圣元奶粉", "SHENGYUAN", "shengyuan"]),
    ("合生元", 12, ["合生元", "Biostime", "biostime", "合生元派星", "派星", "派羊", "合生元有机", "阿尔法星", "合生元奶粉"]),
    ("雅培", 13, ["雅培", "Similac", "similac", "雅培奶粉", "雅培铂优", "铂优", "雅培亲护", "亲护", "雅培水奶"]),
    ("诺优能", 14, ["诺优能", "Nutrilon", "nutrilon", "诺优能奶粉", "荷兰牛栏", "牛栏", "诺优能白金", "诺优能3段"]),
    ("澳优", 15, ["澳优", "海普诺凯", "海普诺凯荷致", "荷致", "海普诺凯1897", "1897", "能力多", "澳优能力多", "佳贝艾特"]),
    ("蒙牛", 16, ["蒙牛", "MENGNIU", "mengniu", "蒙牛奶粉", "瑞哺恩", "蒙牛瑞哺恩", "朵拉", "蒙牛朵拉", "挚优"]),
    ("完达山", 17, ["完达山", "完达山奶粉", "安力聪", "完达山安力聪", "元乳", "亲贝", "优巧", "诸葛", "怡膳"]),
    ("三元", 18, ["三元", "三元奶粉", "三元爱力优", "爱力优", "福莱明", "三元福莱明", "三元蓝标", "三元喜晓"]),
    ("旗帜", 19, ["旗帜", "旗帜奶粉", "旗帜益佳", "益佳", "旗帜养道", "养道", "旗帜亲机", "亲机", "鲜活"]),
    ("麦蔻", 20, ["麦蔻", "MEEK", "meek", "麦蔻奶粉", "麦蔻乐冠", "乐冠", "麦蔻蜜儿", "蜜儿", "北欧麦蔻"]),
    ("蓝河", 21, ["蓝河", "BlueRiver", "blueriver", "蓝河奶粉", "蓝河绵羊奶", "蓝河山羊奶", "蓝河春天", "蓝河卡布", "睿知"]),
    ("佳贝艾特", 22, ["佳贝艾特", "Kabrita", "kabrita", "佳贝艾特奶粉", "佳贝艾特羊奶", "悠悦", "白佳", "佳贝艾特3段"]),
    ("圣元优博", 23, ["圣元优博", "优博瑞安", "优博盖", "优博布瑞弗尼", "优博58", "圣元58", "优博婴儿"]),
    ("宜品", 24, ["宜品", "蓓康僖", "蓓康僖羊奶", "宜品奶粉", "宜品益臻", "益臻", "宜品爱尼", "慧护"]),
    ("欧士达", 25, ["欧士达", "AUSTD", "austd", "欧士达奶粉", "欧士达绵羊奶", "欧士达山羊奶"]),
    ("倍恩母", 26, ["倍恩母", "BEIENMU", "beienmu", "倍恩母奶粉", "倍恩母羊奶", "倍恩母有机"]),
    ("燎原", 27, ["燎原", "LIAOYUAN", "liaoyuan", "燎原奶粉", "燎原牦牛", "藏巴", "燎原高原"]),
    ("雅泰", 28, ["雅泰", "YATAI", "yatai", "雅泰奶粉", "雅泰羊奶", "朵聪", "安护", "恩美"]),
    ("阳光呵护", 29, ["阳光呵护", "SUNSHINE", "sunshine", "阳光呵护奶粉", "阳光呵护有机", "阳光呵护A2"]),
    ("贝欧莱", 30, ["贝欧莱", "BABYL", "babyl", "贝欧莱奶粉", "贝欧莱有机", "贝欧莱A2"]),
    ("喜宝", 31, ["喜宝", "HIPP", "hipp", "喜宝奶粉", "德国喜宝", "喜宝有机", "喜宝益生菌"]),
    ("爱达力", 32, ["爱达力", "Adapta", "adapta", "爱达力奶粉", "法国爱达力", "爱达力A2"]),
    ("迈高", 33, ["迈高", "Murray", "murray", "迈高奶粉", "澳洲迈高", "迈高金装"]),
    ("亨氏", 34, ["亨氏", "Heinz", "heinz", "亨氏奶粉", "亨氏米粉", "heinz亨氏"]),
    ("美素", 35, ["美素", "美素奶粉", "美素佳儿", "美素力", "皇家美素", "friso美素"]),
    ("赐多利", 36, ["赐多利", "Stolle", "stolle", "赐多利奶粉", "赐多利羊奶"]),
    ("维爱佳", 37, ["维爱佳", "Viplus", "viplus", "维爱佳奶粉", "维爱佳A2"]),
    ("高培", 38, ["高培", "GoldMax", "goldmax", "高培奶粉", "高培臻爱", "高培1897"]),
    ("牧栏", 39, ["牧栏", "MULAN", "mulan", "牧栏奶粉", "牧栏有机", "牧栏A2"]),
    ("诺尔曼", 40, ["诺尔曼", "NORMAN", "norman", "诺尔曼奶粉", "诺尔曼配方"]),
]


CLEANING_RULES = [
    ("rules-cleaning-default", "清洗规则", "数据清洗", "空内容", ["空正文", "只包含空格", "无评论内容"], 100),
    ("rules-cleaning-default", "清洗规则", "数据清洗", "纯符号表情", ["纯emoji", "纯标点", "无语义符号"], 90),
    ("rules-cleaning-default", "清洗规则", "数据清洗", "纯@他人", ["只@账号", "@用户无正文"], 80),
    ("rules-cleaning-default", "清洗规则", "数据清洗", "乱码内容", ["异常编码", "不可读字符", "重复异常字符"], 70),
    ("rules-cleaning-default", "清洗规则", "数据清洗", "重复评论", ["评论ID重复", "内容ID与正文组合重复"], 60),
]


RULE_SETS = [
    RuleSet(id="rules-sentiment-a2-v9", name="A2 情绪两级规则", layer="情绪层", version="v9.3", rule_count=5, last_updated="2026-06-05 14:22", category="标签规则", description="正面 / 中性 / 负面一级判断，以及恐慌焦虑、庆幸旁观、愤怒背叛等二级情绪。"),
    RuleSet(id="rules-cognition-a2-v9", name="A2 认知判断规则", layer="认知层", version="v9.3", rule_count=4, last_updated="2026-06-05 14:22", category="标签规则", description="识别无明确认知、信息混淆、精准认知、泛化抵触。"),
    RuleSet(id="rules-action-a2-v9", name="A2 行动意图规则", layer="行动层", version="v9.3", rule_count=4, last_updated="2026-06-05 14:22", category="标签规则", description="识别暂无行动、寻求帮助、转奶流失、维权诉求。"),
    RuleSet(id="rules-brand-milk-powder-top40", name="母婴奶粉品牌产品识别", layer="品牌层", version="v1.5", rule_count=len(MILK_POWDER_BRANDS), last_updated="2026-06-06 11:30", category="品牌产品规则", description="覆盖母婴奶粉主流品牌、主力产品、消费者口语称呼和常见错字。"),
    RuleSet(id="rules-cleaning-default", name="通用无效数据清洗规则", layer="数据清洗", version="v1.0", rule_count=len(CLEANING_RULES), last_updated="2026-06-06 11:30", category="清洗规则", description="空内容、纯符号、纯@、乱码、重复评论等导入前清洗规则。"),
]


def build_brand_rules() -> list[BrandRule]:
    rules = []
    for brand, priority, keywords in MILK_POWDER_BRANDS:
        product_terms = [item for item in keywords if brand in item and item != brand]
        typo_terms = [item for item in keywords if item.lower() != item and item.isascii()]
        aliases = [item for item in keywords if item not in product_terms][:8]
        rules.append(
            BrandRule(
                id=f"brand-{priority:02d}",
                brand=brand,
                category="母婴奶粉",
                aliases=aliases,
                products=product_terms[:6] or [f"{brand}奶粉"],
                typo_variants=typo_terms[:5],
                competitor=brand.lower() != "a2",
                enabled=True,
            )
        )
    return rules


def build_rule_definitions() -> list[RuleDefinition]:
    definitions = [
        RuleDefinition(
            id=f"rule-label-{index:03d}",
            rule_set_id=item["set_id"],
            category=item["category"],
            layer=item["layer"],
            label=item["label"],
            stage=item["stage"],
            keywords=item["keywords"],
            priority=item["priority"],
            source=item["source"],
        )
        for index, item in enumerate(HISTORICAL_LABEL_RULES, start=1)
    ]
    for index, (brand, priority, keywords) in enumerate(MILK_POWDER_BRANDS, start=1):
        definitions.append(
            RuleDefinition(
                id=f"rule-brand-{index:03d}",
                rule_set_id="rules-brand-milk-powder-top40",
                category="品牌产品规则",
                layer="品牌层",
                label=brand,
                keywords=keywords,
                priority=priority,
                source="母婴奶粉品牌与竞品历史识别规则",
            )
        )
    for index, (set_id, category, layer, label, keywords, priority) in enumerate(CLEANING_RULES, start=1):
        definitions.append(
            RuleDefinition(
                id=f"rule-clean-{index:03d}",
                rule_set_id=set_id,
                category=category,
                layer=layer,
                label=label,
                keywords=keywords,
                priority=priority,
                source="历史导入清洗规则",
            )
        )
    return definitions
