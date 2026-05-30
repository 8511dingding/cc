"""
Emoji增强模块
从YAML配置加载emoji元数据，支持emoji权重计算
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter


class EmojiEngine:
    """Emoji引擎：从YAML配置加载emoji规则并执行匹配"""

    def __init__(self, rules_dir: Optional[str] = None):
        if rules_dir is None:
            rules_dir = Path(__file__).parent.parent / "rules"
        self.rules_dir = Path(rules_dir)

        # 加载配置
        self._emoji_rules = self._load_yaml("a2_emoji_rules.yaml")

        # 构建emoji到分类的映射
        self._emoji_map: Dict[str, str] = {}
        self._emoji_weights: Dict[str, float] = {}

        self._build_emoji_index()

    def _load_yaml(self, filename: str) -> dict:
        """加载YAML配置文件"""
        filepath = self.rules_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _build_emoji_index(self):
        """构建emoji索引"""
        emojis_config = self._emoji_rules.get('emojis', {})

        for category, config in emojis_config.items():
            label = config.get('label', category)
            weight = config.get('weight', 0.5)
            items = config.get('items', [])

            for emoji in items:
                self._emoji_map[emoji] = label
                self._emoji_weights[emoji] = weight

    def extract_emojis(self, text: str) -> List[str]:
        """提取文本中所有emoji"""
        emojis = []
        for emoji in self._emoji_map.keys():
            if emoji in text:
                emojis.append(emoji)
        return emojis

    def count_emojis(self, text: str) -> Counter:
        """统计各类emoji数量"""
        found = []
        for emoji, category in self._emoji_map.items():
            count = text.count(emoji)
            if count > 0:
                found.append((emoji, count, category))
        return Counter({cat: cnt for emoji, cnt, cat in found})

    def get_dominant_emotion(self, text: str) -> Tuple[str, float]:
        """
        获取文本主导情绪（基于emoji）
        返回 (情绪标签, 置信度)
        """
        emoji_counter = self.count_emojis(text)

        if not emoji_counter:
            return '中性', 0.3  # 无emoji，低置信度

        # 按权重计算总分
        scores: Dict[str, float] = {}
        for emoji, category in self._emoji_map.items():
            count = text.count(emoji)
            if count > 0:
                weight = self._emoji_weights.get(emoji, 0.5)
                scores[category] = scores.get(category, 0) + weight * count

        if not scores:
            return '中性', 0.3

        # 取最高分
        dominant = max(scores.items(), key=lambda x: x[1])
        return dominant[0], min(dominant[1] / (dominant[1] + 1), 0.95)  # 归一化

    def check_combo_boost(self, text: str) -> Tuple[Optional[str], float]:
        """检查组合增强"""
        combos = self._emoji_rules.get('combo_boosts', {})

        for combo_name, combo_config in combos.items():
            items = combo_config.get('items', [])
            emotion = combo_config.get('emotion', '')
            boost = combo_config.get('boost', 0.1)

            # 统计匹配数量
            count = sum(text.count(item) for item in items)

            if count >= 2:
                return emotion, boost

        return None, 0

    def check_emoji_keyword_combo(self, text: str) -> Tuple[Optional[str], float]:
        """检查emoji+关键词组合"""
        combos = self._emoji_rules.get('emoji_keyword_combos', {})
        text_lower = text.lower()

        for combo_name, combo_list in combos.items():
            for combo in combo_list:
                emoji = combo.get('emoji', '')
                keywords = combo.get('keywords', [])
                emotion = combo.get('emotion', '')
                confidence = combo.get('confidence', 0.8)

                if emoji in text:
                    # 检查关键词
                    for kw in keywords:
                        if kw in text_lower:
                            return emotion, confidence

        return None, 0

    def enhance_emotion_classification(
        self,
        text: str,
        rule_based_emotion: str,
        rule_confidence: float
    ) -> Tuple[str, float]:
        """
        增强情绪分类
        结合规则引擎结果和emoji分析

        Args:
            text: 原始文本
            rule_based_emotion: 规则引擎分类的情绪
            rule_confidence: 规则引擎置信度

        Returns:
            (最终情绪, 最终置信度)
        """
        # 1. 检查emoji+关键词组合（高优先级）
        combo_emotion, combo_confidence = self.check_emoji_keyword_combo(text)
        if combo_emotion:
            # 组合匹配优先级最高
            if combo_confidence > rule_confidence:
                return combo_emotion, combo_confidence

        # 2. 检查emoji主导情绪
        emoji_emotion, emoji_conf = self.get_dominant_emotion(text)

        # 如果emoji情绪与规则引擎结果一致，增强置信度
        if emoji_emotion == rule_based_emotion:
            return rule_based_emotion, min(rule_confidence + 0.1, 0.95)

        # 如果emoji情绪与规则引擎结果不一致，且emoji置信度高
        if emoji_conf > 0.7 and emoji_emotion != rule_based_emotion:
            # 但只有当规则置信度较低时才考虑emoji判断
            if rule_confidence < 0.6:
                return emoji_emotion, emoji_conf

        # 3. 检查组合增强
        boost_emotion, boost_value = self.check_combo_boost(text)
        if boost_emotion and boost_emotion == rule_based_emotion:
            return rule_based_emotion, min(rule_confidence + boost_value, 0.95)

        return rule_based_emotion, rule_confidence


# 全局单例
_emoji_engine_instance = None


def get_emoji_engine(rules_dir: Optional[str] = None) -> EmojiEngine:
    """获取Emoji引擎单例"""
    global _emoji_engine_instance
    if _emoji_engine_instance is None:
        _emoji_engine_instance = EmojiEngine(rules_dir)
    return _emoji_engine_instance