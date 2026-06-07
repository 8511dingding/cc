#!/usr/bin/env python3
"""
泰文商品名批量翻译脚本
使用 Claude API 翻译泰语商品名为中文
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic

# 加载产品名
PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "orbstack-www" / "ning_mac" / "FastMOSS-Report"
names_file = DATA_DIR / "product_names.txt"
with open(names_file, 'r', encoding='utf-8') as f:
    lines = f.read().strip().split('\n')

products = []
for line in lines:
    if '|' in line:
        idx, name = line.split('|', 1)
        products.append({'idx': int(idx), 'name': name.strip()})

print(f"加载了 {len(products)} 个商品名")

# 翻译结果存储
translations = {}

# 分批翻译（每批20个，减少单次token消耗）
batch_size = 20
for batch_start in range(0, len(products), batch_size):
    batch_end = min(batch_start + batch_size, len(products))
    batch = products[batch_start:batch_end]

    print(f"\n翻译批次 {batch_start//batch_size + 1}: 产品 {batch_start+1}-{batch_end}")

    # 构建翻译prompt
    name_list = '\n'.join([f"{p['idx']}. {p['name']}" for p in batch])

    prompt = f"""你是一个泰语到中文的翻译助手。请将以下泰国TikTok商品名称从泰语翻译成简体中文。

翻译要求：
- 保留原意，简洁易懂
- 包含产品主名、规格、数量单位
- 常见品牌名可保留英文

商品名称列表：
{name_list}

请直接输出JSON格式的翻译结果，格式为：
{{"序号": "中文翻译", ...}}

只输出JSON，不要其他内容。"""

    print(f"  正在翻译 {len(batch)} 个商品名...")

    # 调用 Claude API
    client = Anthropic(
        base_url=os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com'),
        api_key=os.environ.get('ANTHROPIC_AUTH_TOKEN', '')
    )

    response = client.messages.create(
        model=os.environ.get('ANTHROPIC_MODEL', 'claude-opus-4-7'),
        thinking={"type": "disabled"},
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result_text = ''
    for block in response.content:
        if block.type == 'text':
            result_text = block.text.strip()
            break
    if not result_text:
        result_text = str(response.content)
    print(f"  API响应: {result_text[:200]}...")

    # 解析JSON结果
    try:
        # 尝试直接解析
        result = json.loads(result_text)
        for idx, translation in result.items():
            translations[idx] = translation
        print(f"  成功解析 {len(result)} 个翻译")
    except json.JSONDecodeError:
        # 尝试清理并重新解析
        # 提取JSON部分
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = result_text[start:end]
            try:
                result = json.loads(json_str)
                for idx, translation in result.items():
                    translations[idx] = translation
                print(f"  清理后成功解析 {len(result)} 个翻译")
            except:
                print(f"  解析失败: {result_text[:300]}")
                # 手动解析换行分隔的 "序号: 翻译" 格式
                for line in result_text.split('\n'):
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            idx = parts[0].strip().strip('"')
                            translation = parts[1].strip().strip('",')
                            if idx.isdigit():
                                translations[idx] = translation

    print(f"  当前进度: {len(translations)}/{len(products)} 个已翻译")

# 保存翻译结果
output_file = DATA_DIR / "translations.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)
print(f"\n翻译结果已保存到: {output_file}")
print(f"总计 {len(translations)} 个翻译")
