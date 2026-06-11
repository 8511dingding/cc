import os
import httpx
from typing import Literal

ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic")
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "MiniMax-M2.7")


async def ai_complete(
    prompt: str,
    action: Literal["expand", "translate_en", "translate_th", "polish", "summarize"] = "expand",
    max_tokens: int = 2048,
) -> str:
    """
    AI 协作功能：续写、翻译、优化、总结

    Args:
        prompt: 用户输入的内容
        action: 操作类型
        max_tokens: 最大生成token数

    Returns:
        AI 生成的内容
    """
    if not ANTHROPIC_AUTH_TOKEN:
        return "错误: 未配置 AI API Key"

    system_prompts = {
        "expand": "你是一位专业的商业文档撰写助手。用户会提供一段文档内容或提纲，你需要续写或扩写内容，使其更加详细、专业。保持原有的语气和风格，补充完整的段落内容。只返回生成的内容，不要解释。",
        "translate_en": "你是一位专业的中英翻译专家。用户会提供中文文档内容，你需要翻译成英文。保持原文的专业术语和格式，只返回英文翻译结果。",
        "translate_th": "你是一位专业的中泰翻译专家。用户会提供中文文档内容，你需要翻译成泰文。保持原文的专业术语和格式，只返回泰文翻译结果。",
        "polish": "你是一位专业的商业文档编辑。用户会提供中文文档内容，你需要优化语言表达，使内容更加专业、简洁、流畅。只返回优化后的内容，不要解释。",
        "summarize": "你是一位专业的文档摘要专家。用户会提供文档内容，你需要生成简洁的摘要，突出关键信息。只返回摘要内容，不要解释。",
    }

    system_prompt = system_prompts.get(action, system_prompts["expand"])

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ANTHROPIC_BASE_URL}/v1/messages",
            headers={
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": ANTHROPIC_MODEL,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
        )

        if response.status_code != 200:
            return f"AI 服务错误: {response.status_code} - {response.text}"

        data = response.json()
        return data.get("content", [{}])[0].get("text", "未能生成内容")


async def ai_generate_from_template(
    template_name: str,
    variables: dict,
    language: Literal["cn", "en", "th"] = "cn",
) -> str:
    """
    根据模板和变量生成文档内容

    Args:
        template_name: 模板名称
        variables: 变量字典
        language: 输出语言
    """
    if not ANTHROPIC_AUTH_TOKEN:
        return "错误: 未配置 AI API Key"

    lang_map = {"cn": "中文", "en": "英文", "th": "泰文"}
    language_name = lang_map.get(language, "中文")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{ANTHROPIC_BASE_URL}/v1/messages",
            headers={
                "Authorization": f"Bearer {ANTHROPIC_AUTH_TOKEN}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": ANTHROPIC_MODEL,
                "max_tokens": 4096,
                "system": f"""你是一位专业的商业文档撰写助手。用户会提供模板名称和变量信息，你需要根据这些信息生成完整的{language_name}文档。

模板类型包括：
- 经销协议：包含甲方乙方信息、产品授权、价格付款、双方权利义务、产品责任、争议解决等条款
- 产品责任条款：包含缺陷定义、责任范围、免责条款、赔偿限额
- 争议解决条款：包含友好协商、仲裁、适用法律等
- 跨境电商补充协议：包含电商平台责任、海关税务、知识产权、合规检查

请根据提供的模板和变量生成专业、完整的{language_name}商业文档。只返回文档内容，不要解释。""",
                "messages": [
                    {
                        "role": "user",
                        "content": f"模板名称: {template_name}\n变量信息: {variables}",
                    }
                ],
            },
        )

        if response.status_code != 200:
            return f"AI 服务错误: {response.status_code}"

        data = response.json()
        return data.get("content", [{}])[0].get("text", "未能生成内容")