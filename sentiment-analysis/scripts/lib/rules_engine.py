"""
A2舆情分析规则引擎
从YAML配置加载规则，执行分类和品牌识别
"""

import re
import yaml
from pathlib import Path
from typing import Tuple, List, Optional


class RulesEngine:
    """规则引擎：从YAML加载规则并执行匹配"""

    def __init__(self, rules_dir: Optional[str] = None):
        if rules_dir is None:
            rules_dir = Path(__file__).parent.parent / "rules"
        self.rules_dir = Path(rules_dir)

        # 加载配置
        self._sentiment_rules = self._load_yaml("a2_sentiment_rules.yaml")
        self._brand_rules = self._load_yaml("a2_brand_rules.yaml")

        # 预编译正则表达式
        self._compile_patterns()

    def _load_yaml(self, filename: str) -> dict:
        """加载YAML配置文件"""
        filepath = self.rules_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _compile_patterns(self):
        """预编译所有正则表达式"""
        # 情绪层关键词编译
        self._emotion_patterns = {}
        for category, config in self._sentiment_rules['emotion'].items():
            if category == 'priority_order':
                continue
            keywords = config.get('keywords', [])
            self._emotion_patterns[category] = {
                'label': config['label'],
                'patterns': [re.compile(kw, re.IGNORECASE) for kw in keywords]
            }

        # 恐慌焦虑特殊配置
        panic_config = self._sentiment_rules['emotion'].get('panic', {})
        self._panic_special_mentions = panic_config.get('special_mentions', [])
        self._panic_emojis = panic_config.get('emojis', [])
        self._panic_symptom_keywords = panic_config.get('symptom_keywords', [])

        # 认知层关键词编译
        self._cognitive_patterns = {}
        for category, config in self._sentiment_rules['cognitive'].items():
            if category == 'priority_order':
                continue
            keywords = config.get('keywords', [])
            self._cognitive_patterns[category] = {
                'label': config['label'],
                'patterns': [re.compile(kw, re.IGNORECASE) for kw in keywords]
            }

        # 行动层关键词编译
        self._action_patterns = {}
        for category, config in self._sentiment_rules['action'].items():
            if category == 'priority_order':
                continue
            keywords = config.get('keywords', [])
            self._action_patterns[category] = {
                'label': config['label'],
                'patterns': [re.compile(kw, re.IGNORECASE) for kw in keywords]
            }

        # 纯@配置
        self._pure_at_config = self._sentiment_rules.get('pure_at', {})
        self._emoji_pattern = re.compile(
            self._pure_at_config.get('emoji_pattern', ''),
            re.IGNORECASE
        )

        # 评论类型配置
        comment_type_cfg = self._sentiment_rules.get('comment_type', {})
        self._long_threshold = comment_type_cfg.get('long_content_threshold', 100)
        self._competitor_keywords = comment_type_cfg.get('competitor_keywords', [])

        # 品牌配置编译
        self._a2_patterns = []
        for p in self._brand_rules['a2_brand']['patterns']:
            self._a2_patterns.append(re.compile(p, re.IGNORECASE))

        a2_exclude = self._brand_rules['a2_brand'].get('exclude', [])
        self._a2_exclude_patterns = [re.compile(f".*{exc}.*", re.IGNORECASE) for exc in a2_exclude]

        self._a2_standalone = re.compile(
            self._brand_rules['a2_brand'].get('standalone_pattern', '\\ba2\\b'),
            re.IGNORECASE
        )

        self._brand_patterns = {}
        self._brand_misspellings = {}
        for brand, config in self._brand_rules['brands'].items():
            patterns = [re.compile(p, re.IGNORECASE) for p in config['patterns']]
            self._brand_patterns[brand] = patterns

            # 加载错别字容错
            misspellings = config.get('misspellings', [])
            self._brand_misspellings[brand] = [re.compile(m, re.IGNORECASE) for m in misspellings]

    def match_any(self, text: str, patterns: List) -> bool:
        """检查文本是否匹配任意一个模式"""
        for pattern in patterns:
            if pattern.search(text):
                return True
        return False

    def is_pure_at_no_interaction(self, text: str) -> bool:
        """判断是否为纯@无互动评论"""
        if not text or not isinstance(text, str):
            return False

        at_matches = re.findall(r'@[a-zA-Z0-9_-]+', text)
        if not at_matches:
            return False

        # 多个@直接判定为纯@
        if len(at_matches) > 1:
            return True

        # 单个@：检查前面是否为空
        at = at_matches[0]
        idx = text.find(at)
        before_at = text[:idx].strip()
        if len(before_at) > 0:
            return False

        # 检查@后面内容是否为空
        after_at = text[idx + len(at):].strip()
        after_clean = self._emoji_pattern.sub('', after_at)
        return len(after_clean) == 0

    def classify_emotion(self, text: str) -> str:
        """情绪层分类"""
        text_lower = text.lower()
        priority = self._sentiment_rules['emotion']['priority_order']

        for category in priority:
            if category == 'neutral':
                continue  # 中性是默认的，最后处理

            config = self._emotion_patterns.get(category)
            if config and self.match_any(text_lower, config['patterns']):
                return config['label']

            # 恐慌焦虑特殊处理
            if category == 'panic':
                # 检查@豆包
                if any(mention in text for mention in self._panic_special_mentions):
                    return config['label']

                # 检查emoji + 症状
                panic_emojis = self._sentiment_rules['emotion']['panic'].get('emojis', [])
                symptom_kw = self._panic_symptom_keywords

                if any(emoji in text for emoji in panic_emojis):
                    if any(kw in text_lower for kw in symptom_kw):
                        return config['label']

        return self._emotion_patterns['neutral']['label']

    def classify_cognitive(self, text: str) -> str:
        """认知层分类"""
        text_lower = text.lower()
        priority = self._sentiment_rules['cognitive']['priority_order']

        for category in priority:
            if category == 'unclear':
                continue  # 无明确认知是默认的

            config = self._cognitive_patterns.get(category)
            if config and self.match_any(text_lower, config['patterns']):
                return config['label']

        return self._cognitive_patterns['unclear']['label']

    def classify_action(self, text: str) -> str:
        """行动层分类"""
        text_lower = text.lower()
        priority = self._sentiment_rules['action']['priority_order']

        for category in priority:
            if category == 'none':
                continue  # 暂无行动是默认的

            config = self._action_patterns.get(category)
            if config and self.match_any(text_lower, config['patterns']):
                return config['label']

        return self._action_patterns['none']['label']

    def classify(self, text: str) -> Tuple[str, str, str]:
        """三维分类"""
        if not text or not isinstance(text, str) or text.strip() == '':
            return '', '', ''

        cognitive = self.classify_cognitive(text)
        emotion = self.classify_emotion(text)
        action = self.classify_action(text)

        return cognitive, emotion, action

    def get_comment_type(self, text: str) -> str:
        """判断评论类型"""
        if not text or not isinstance(text, str) or text.strip() == '':
            return '普通内容'

        # 检查纯@无互动
        if self.is_pure_at_no_interaction(text):
            return '纯@无互动'

        # @某人互动
        if re.search(r'@[a-zA-Z0-9_-]+', text):
            return '@某人互动'

        # 长内容
        if len(text) > self._long_threshold:
            return f'长内容(>{self._long_threshold}字)'

        # 提及竞品
        if any(kw in text for kw in self._competitor_keywords):
            return '提及竞品'

        return '普通内容'

    def extract_brands(self, text: str) -> str:
        """提取品牌提及"""
        if not text or not isinstance(text, str) or text.strip() == '':
            return ''

        text_lower = text.lower()
        brands = []

        # 检查A2变体
        for pattern in self._a2_patterns:
            if pattern.search(text_lower):
                brands.append('a2')
                break

        # 检查独立a2（排除 a2蛋白质）
        if 'a2' not in brands:
            exclude_match = any(p.search(text_lower) for p in self._a2_exclude_patterns)
            if not exclude_match and self._a2_standalone.search(text_lower):
                brands.append('a2')

        # 检查其他品牌（包括错别字容错）
        for brand, patterns in self._brand_patterns.items():
            if brand in brands:
                continue
            if self.match_any(text_lower, patterns):
                brands.append(brand)

        # 检查错别字容错（如果没有匹配到正式名称）
        for brand, miss_patterns in self._brand_misspellings.items():
            if brand in brands:
                continue
            if self.match_any(text_lower, miss_patterns):
                brands.append(brand)

        return '|'.join(brands) if brands else ''


# 全局单例（延迟加载）
_engine_instance = None


def get_engine(rules_dir: Optional[str] = None) -> RulesEngine:
    """获取规则引擎单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RulesEngine(rules_dir)
    return _engine_instance