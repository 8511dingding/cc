"""
LLM辅助分类模块
当规则引擎置信度低时，调用LLM进行二次判断
"""

import os
import re
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

# 可用的LLM提供商
LLM_PROVIDERS = {
    'anthropic': 'anthropic',
    'openai': 'openai',
    'siliconflow': 'siliconflow',  # 硅基流动
}


@dataclass
class ClassificationResult:
    """分类结果"""
    cognitive: str
    emotion: str
    action: str
    confidence: float  # 0-1
    reasoning: Optional[str] = None


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = 'anthropic'
    model: str = 'claude-sonnet-4-7'
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 200
    temperature: float = 0.3


class LLMEvaluator:
    """LLM评估器"""

    # 情绪层分类提示
    EMOTION_PROMPT = """你是一个舆情分析专家。请根据评论内容判断消费者的情绪倾向。

评论内容：{text}

可选的情绪类别：
- 正面：对品牌持信任态度，相信产品安全
- 中性：普通讨论，无明显情绪倾向
- 恐慌焦虑：担忧宝宝健康，害怕中招
- 庆幸旁观：庆幸自己没买/已换奶粉
- 愤怒背叛：对企业不负责任行为愤怒，感觉被背叛

请只输出一个类别名称，不要其他内容。"""

    # 认知层分类提示
    COGNITIVE_PROMPT = """你是一个舆情分析专家。请根据评论内容判断消费者的认知程度。

评论内容：{text}

可选的认知类别：
- 无明确认知：消费者未表现出明确的认知标签
- 信息混淆：分不清国行版、澳洲版、美版的区别
- 精准认知：明白召回范围和特定批次，理解美版/国版区别
- 泛化抵触：出现泛化抵触或阴谋论倾向，认为所有奶粉都有问题

请只输出一个类别名称，不要其他内容。"""

    # 行动层分类提示
    ACTION_PROMPT = """你是一个舆情分析专家。请根据评论内容判断消费者的行动倾向。

评论内容：{text}

可选的行动类别：
- 暂无行动：无明显行动倾向
- 寻求帮助：主动寻求信息或帮助（如问怎么办、求推荐）
- 转奶流失：明确表示要换奶粉或已经换奶粉
- 维权诉求：提到12315投诉、退款、赔偿等

请只输出一个类别名称，不要其他内容。"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._load_config()
        self._client = None

    def _load_config(self) -> LLMConfig:
        """从环境变量加载配置"""
        provider = os.environ.get('LLM_PROVIDER', 'anthropic')
        api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('OPENAI_API_KEY') or os.environ.get('SILICONFLOW_API_KEY')
        model = os.environ.get('LLM_MODEL', 'claude-sonnet-4-7')
        base_url = os.environ.get('LLM_BASE_URL')

        return LLMConfig(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url
        )

    def _get_client(self):
        """获取LLM客户端"""
        if self._client is None:
            if self.config.provider == 'anthropic':
                try:
                    from anthropic import Anthropic
                    self._client = Anthropic(api_key=self.config.api_key)
                except ImportError:
                    return None
            elif self.config.provider == 'openai':
                try:
                    from openai import OpenAI
                    self._client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
                except ImportError:
                    return None
            elif self.config.provider == 'siliconflow':
                try:
                    from openai import OpenAI
                    self._client = OpenAI(
                        api_key=self.config.api_key,
                        base_url=self.config.base_url or 'https://api.siliconflow.cn/v1'
                    )
                except ImportError:
                    return None
        return self._client

    def _call_llm(self, prompt: str) -> Optional[str]:
        """调用LLM"""
        client = self._get_client()
        if client is None:
            return None

        try:
            if self.config.provider == 'anthropic':
                response = client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()

            elif self.config.provider in ('openai', 'siliconflow'):
                response = client.chat.completions.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[LLMEvaluator] 调用失败: {e}")
            return None

    def evaluate_emotion(self, text: str) -> Tuple[str, float]:
        """评估情绪层"""
        prompt = self.EMOTION_PROMPT.format(text=text)
        result = self._call_llm(prompt)

        valid_labels = ['正面', '中性', '恐慌焦虑', '庆幸旁观', '愤怒背叛']
        if result in valid_labels:
            return result, 0.9
        return '中性', 0.3  # 默认中性，低置信度

    def evaluate_cognitive(self, text: str) -> Tuple[str, float]:
        """评估认知层"""
        prompt = self.COGNITIVE_PROMPT.format(text=text)
        result = self._call_llm(prompt)

        valid_labels = ['无明确认知', '信息混淆', '精准认知', '泛化抵触']
        if result in valid_labels:
            return result, 0.9
        return '无明确认知', 0.3

    def evaluate_action(self, text: str) -> Tuple[str, float]:
        """评估行动层"""
        prompt = self.ACTION_PROMPT.format(text=text)
        result = self._call_llm(prompt)

        valid_labels = ['暂无行动', '寻求帮助', '转奶流失', '维权诉求']
        if result in valid_labels:
            return result, 0.9
        return '暂无行动', 0.3

    def classify(self, text: str) -> ClassificationResult:
        """完整三维分类"""
        cog, cog_conf = self.evaluate_cognitive(text)
        emo, emo_conf = self.evaluate_emotion(text)
        act, act_conf = self.evaluate_action(text)

        avg_conf = (cog_conf + emo_conf + act_conf) / 3

        return ClassificationResult(
            cognitive=cog,
            emotion=emo,
            action=act,
            confidence=avg_conf,
            reasoning=None
        )


# 置信度判断规则
CONFIDENCE_RULES = {
    'emotion': {
        'high_confidence_keywords': [
            '该死', '欺骗', '背刺', '资本家',  # 愤怒背叛
            '慌', '害怕', '担心', '怎么办',   # 恐慌焦虑
            '还好没买', '幸好没买', '多亏',   # 庆幸旁观
            '放心', '没问题', '官方确认',     # 正面
        ],
        'low_confidence_indicators': [
            '？？？', '？？', '[微笑]', '[发怒]',  # 复杂表情
        ]
    }
}


def calculate_confidence(text: str, layer: str) -> float:
    """
    计算规则引擎分类的置信度
    返回 0-1 的值，1表示高置信度
    """
    text_lower = text.lower()

    if layer == 'emotion':
        # 高置信度关键词匹配
        high_kw = CONFIDENCE_RULES['emotion']['high_confidence_keywords']
        matches = sum(1 for kw in high_kw if kw in text_lower)
        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.7

        # 低置信度指标
        low_ind = CONFIDENCE_RULES['emotion']['low_confidence_indicators']
        for ind in low_ind:
            if ind in text:
                return 0.5

        return 0.6  # 默认中等置信度

    elif layer == 'cognitive':
        # 精准认知和泛化抵触通常置信度较高
        high_kw = ['fda', '所有奶粉', '所有品牌', '不如母乳', '召回范围']
        for kw in high_kw:
            if kw in text_lower:
                return 0.85
        return 0.6

    elif layer == 'action':
        # 明确行动关键词置信度高
        high_kw = ['12315', '转奶', '退了', '换回', '投诉', '赔偿']
        for kw in high_kw:
            if kw in text_lower:
                return 0.85
        return 0.6

    return 0.5


# 全局单例
_evaluator_instance = None


def get_evaluator(config: Optional[LLMConfig] = None) -> LLMEvaluator:
    """获取LLM评估器单例"""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = LLMEvaluator(config)
    return _evaluator_instance