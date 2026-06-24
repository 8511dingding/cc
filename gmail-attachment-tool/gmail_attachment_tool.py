#!/usr/bin/env python3
"""
Gmail Attachment Extractor & Organizer
从 Gmail 中提取与指定联系人的所有附件，按类型分类并基于邮件内容重命名

Usage:
    python gmail_attachment_tool.py                    # 交互模式
    python gmail_attachment_tool.py --sender zhangfang66@hotmail.com --days 365
"""

import os
import sys
import json
import base64
import email
import mimetypes
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs

# Gmail API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# 如果需要 AI 重命名功能，启用以下
ENABLE_AI_RENAME = True

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ============ 配置 ============
SENDER_EMAIL = 'zhangfang66@hotmail.com'
OUTPUT_DIR = Path.home() / 'Gmail_Attachments' / 'zhangfang66hotmailcom'
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'
TOKEN_FILE = Path(__file__).parent / 'token.json'


def get_gmail_service():
    """获取 Gmail API 服务"""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_FILE.read_text()), SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                print("❌ 缺少 credentials.json 文件！")
                print("请先从 Google Cloud Console 下载 OAuth 凭证:")
                print("1. 访问 https://console.cloud.google.com/")
                print("2. 创建项目 → 启用 Gmail API")
                print("3. 创建 OAuth 2.0 客户端 ID (桌面应用)")
                print("4. 下载 JSON 文件，重命名为 credentials.json 放入此目录")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    import googleapiclient.discovery
    return googleapiclient.discovery.build('gmail', 'v1', credentials=creds)


def search_emails(service, sender: str, days: Optional[int] = None,
                  max_results: int = 500) -> list:
    """
    搜索与指定发件人的所有邮件

    Args:
        service: Gmail API 服务
        sender: 发件人邮箱
        days: 搜索最近 N 天的邮件 (None = 全部)
        max_results: 最大返回数量

    Returns:
        邮件 ID 列表
    """
    query = f'from:{sender}'
    if days:
        after_date = datetime.now() - timedelta(days=days)
        query += f' after:{after_date.strftime("%Y/%m/%d")}'

    print(f"🔍 搜索邮件: {query}")

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    print(f"📬 找到 {len(messages)} 封邮件")

    return messages


def get_email_metadata(service, msg_id: str) -> dict:
    """获取邮件的元数据（主题、日期、正文摘要）"""
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    headers = msg['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(无主题)')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

    # 提取正文用于 AI 重命名参考
    body_snippet = msg.get('snippet', '')

    return {
        'id': msg_id,
        'subject': subject,
        'date': date,
        'snippet': body_snippet
    }


def extract_attachments(service, msg_id: str, output_dir: Path) -> list:
    """
    从邮件中提取所有附件

    Returns:
        [(original_filename, saved_path, mime_type), ...]
    """
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    attachments = []
    payload = msg['payload']

    # 处理简单的单部分邮件
    if 'parts' not in payload:
        if 'filename' in payload and payload['filename']:
            att_id = payload.get('body', {}).get('attachmentId')
            if att_id:
                attachments.append({
                    'part_id': payload['partId'],
                    'filename': payload['filename'],
                    'mime_type': payload.get('mimeType', 'application/octet-stream'),
                    'attachment_id': att_id
                })
    else:
        # 处理多部分邮件
        for part in payload['parts']:
            if part.get('filename'):
                att_id = part.get('body', {}).get('attachmentId')
                if att_id:
                    attachments.append({
                        'part_id': part['partId'],
                        'filename': part['filename'],
                        'mime_type': part.get('mimeType', 'application/octet-stream'),
                        'attachment_id': att_id
                    })

    saved = []
    for att in attachments:
        try:
            # 下载附件
            att_data = service.users().messages().attachments().get(
                userId='me',
                messageId=msg_id,
                id=att['attachment_id']
            ).execute()

            file_data = base64.urlsafe_b64decode(att_data['data'])

            # 确定保存路径
            ext = Path(att['filename']).suffix.lower()
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', att['filename'])

            # 按类型分类
            category = get_file_category(att['mime_type'], ext)
            category_dir = output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)

            # AI 重命名
            if ENABLE_AI_RENAME:
                metadata = get_email_metadata(service, msg_id)
                new_name = generate_ai_filename(
                    original_name=safe_name,
                    email_subject=metadata['subject'],
                    email_snippet=metadata['snippet'],
                    email_date=metadata['date']
                )
            else:
                new_name = safe_name

            # 处理重名
            save_path = category_dir / new_name
            counter = 1
            while save_path.exists():
                stem = Path(new_name).stem
                suffix = Path(new_name).suffix
                save_path = category_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            save_path.write_bytes(file_data)
            saved.append((att['filename'], str(save_path), att['mime_type']))
            print(f"  ✅ {att['filename']} → {save_path.relative_to(output_dir)}")

        except Exception as e:
            print(f"  ⚠️  下载失败 {att['filename']}: {e}")

    return saved


def get_file_category(mime_type: str, ext: str) -> str:
    """根据 MIME 类型和扩展名确定文件类别"""
    ext = ext.lower()

    categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.heic', '.heif', '.tiff', '.tif'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
        'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
        'presentations': ['.ppt', '.pptx', '.key', '.odp'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'videos': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm'],
        'audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
    }

    if mime_type.startswith('image/') or ext in categories['images']:
        return 'images'
    elif mime_type.startswith('application/pdf') or ext in categories['documents']:
        return 'documents'
    elif mime_type.startswith('text/') or ext in ['.txt', '.rtf']:
        return 'documents'
    elif 'spreadsheet' in mime_type or ext in categories['spreadsheets']:
        return 'spreadsheets'
    elif 'presentation' in mime_type or ext in categories['presentations']:
        return 'presentations'
    elif mime_type.startswith('application/zip') or ext in categories['archives']:
        return 'archives'
    elif mime_type.startswith('video/') or ext in categories['videos']:
        return 'videos'
    elif mime_type.startswith('audio/') or ext in categories['audio']:
        return 'audio'
    else:
        return 'others'


def generate_ai_filename(original_name: str, email_subject: str,
                          email_snippet: str, email_date: str) -> str:
    """
    基于邮件内容生成描述性文件名
    使用简单关键词提取 + 规则，而非调用 AI API（避免额外成本）
    """
    # 提取日期信息
    date_match = re.search(r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})', email_date)
    if date_match:
        date_str = f"{date_match.group(1)}{date_match.group(2).zfill(2)}{date_match.group(3).zfill(2)}"
    else:
        date_str = datetime.now().strftime('%Y%m%d')

    # 从主题提取关键词
    # 移除常见前缀
    clean_subject = re.sub(r'^(Re:|Fwd?:|回复:|转发:)\s*', '', email_subject)
    # 移除特殊字符，保留中文、英文、数字
    keywords = re.sub(r'[^\w\s一-鿿]', '', clean_subject)
    keywords = keywords.strip()[:30]  # 限制长度

    # 原始文件扩展名
    ext = Path(original_name).suffix.lower()

    # 如果主题太短或无意义，直接用原名
    if len(keywords) < 2:
        return original_name

    # 组合新名称: 日期_关键词_原名
    new_name = f"{date_str}_{keywords}{ext}"

    # 确保文件名不会过长
    if len(new_name) > 200:
        new_name = new_name[:196] + ext

    return new_name


def run_extraction(sender: str = SENDER_EMAIL, days: Optional[int] = None):
    """执行提取流程"""
    print("=" * 60)
    print("📥 Gmail 附件提取工具")
    print("=" * 60)
    print(f"发件人: {sender}")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"时间范围: {'全部' if not days else f'最近 {days} 天'}")
    print("=" * 60)

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 获取 Gmail 服务
    print("\n🔐 连接 Gmail...")
    service = get_gmail_service()

    # 搜索邮件
    messages = search_emails(service, sender, days)

    if not messages:
        print("❌ 没有找到邮件")
        return

    # 统计
    stats = {
        'images': 0,
        'documents': 0,
        'spreadsheets': 0,
        'presentations': 0,
        'archives': 0,
        'videos': 0,
        'audio': 0,
        'others': 0
    }
    total_attachments = 0

    # 处理每封邮件
    for i, msg_ref in enumerate(messages, 1):
        msg_id = msg_ref['id']
        print(f"\n📧 [{i}/{len(messages)}] 处理邮件 {msg_id[:12]}...")

        try:
            attachments = extract_attachments(service, msg_id, OUTPUT_DIR)
            total_attachments += len(attachments)

            for _, _, mime_type in attachments:
                category = get_file_category(mime_type, '')
                stats[category] += 1

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

    # 打印统计
    print("\n" + "=" * 60)
    print("📊 提取完成!")
    print("=" * 60)
    print(f"处理邮件: {len(messages)} 封")
    print(f"提取附件: {total_attachments} 个")
    print("\n分类统计:")
    for category, count in stats.items():
        if count > 0:
            print(f"  📁 {category}: {count}")
    print(f"\n💾 保存位置: {OUTPUT_DIR}")
    print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Gmail 附件提取工具')
    parser.add_argument('--sender', '-s', default=SENDER_EMAIL,
                        help=f'发件人邮箱 (默认: {SENDER_EMAIL})')
    parser.add_argument('--days', '-d', type=int, default=None,
                        help='只提取最近 N 天的邮件 (默认: 全部)')
    parser.add_argument('--all', action='store_true',
                        help='提取所有邮件 (等同于 --days 不限制)')

    args = parser.parse_args()

    run_extraction(
        sender=args.sender,
        days=None if args.all else args.days
    )


if __name__ == '__main__':
    main()
