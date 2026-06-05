from __future__ import annotations

from collections import Counter
from html import unescape
from io import BytesIO
import re
from zipfile import ZipFile
from xml.etree import ElementTree

from app.schemas import ImportFieldMapping, ImportPreviewResponse, ImportQualityIssue


MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MAX_PREVIEW_ROWS = 100_000
DEFAULT_PLATFORM = "抖音"

FIELD_TARGETS = {
    "comment_id": ("id", True, 98),
    "create_time": ("publish_time", False, 94),
    "ip_location": ("ip_location", False, 82),
    "aweme_id": ("source_content.id", False, 95),
    "content": ("content", True, 99),
    "nickname": ("author", False, 92),
    "sub_comment_count": ("engagement.replies", False, 90),
    "like_count": ("engagement.likes", False, 92),
    "last_modify_ts": ("last_modify_ts", False, 78),
    "parent_comment_id": ("parent_comment_id", False, 84),
    "pictures": ("pictures", False, 72),
    "user_id": ("user_id", False, 70),
    "sec_uid": ("sec_uid", False, 70),
    "short_user_id": ("short_user_id", False, 66),
    "user_unique_id": ("user_unique_id", False, 66),
    "user_signature": ("user_signature", False, 60),
    "avatar": ("avatar", False, 72),
}

BRAND_TERMS = [
    "a2",
    "爱他美",
    "飞鹤",
    "金领冠",
    "合生元",
    "美素佳儿",
    "完达山",
    "君乐宝",
    "贝因美",
    "伊利",
    "圣元",
    "蒙牛",
    "澳优",
    "雅士利",
]


def build_import_preview(filename: str, content: bytes) -> ImportPreviewResponse:
    if filename.lower().endswith(".xlsx"):
        return _preview_xlsx(filename, content)
    raise ValueError("当前导入预览只支持 .xlsx 文件")


def _preview_xlsx(filename: str, content: bytes) -> ImportPreviewResponse:
    with ZipFile(BytesIO(content)) as archive:
        sheet_name, sheet_path = _first_sheet(archive)
        shared_strings = _shared_strings(archive)
        rows = _iter_sheet_rows(archive, sheet_path, shared_strings)
        try:
            headers = next(rows)
        except StopIteration as exc:
            raise ValueError("Excel 文件没有可读取的数据") from exc
        headers = [header.strip() for header in headers]

        total_rows = 0
        duplicate_comment_ids = 0
        long_comments = 0
        empty_content = 0
        pure_at = 0
        pure_symbol = 0
        garbled = 0
        missing_platform = 0
        missing_source_content = 0
        seen_comment_ids: set[str] = set()
        samples: list[dict[str, str]] = []
        brand_mentions: Counter[str] = Counter()

        header_index = {header: index for index, header in enumerate(headers)}
        has_platform_field = "platform" in header_index or "平台" in header_index
        for row in rows:
            total_rows += 1
            if total_rows > MAX_PREVIEW_ROWS:
                break
            item = {header: _value_at(row, header_index.get(header)) for header in headers}
            comment_id = item.get("comment_id", "")
            content_value = item.get("content", "")
            source_id = item.get("aweme_id", "")
            if comment_id in seen_comment_ids:
                duplicate_comment_ids += 1
            elif comment_id:
                seen_comment_ids.add(comment_id)
            if not content_value.strip():
                empty_content += 1
            if _is_pure_at(content_value):
                pure_at += 1
            if _is_pure_symbol(content_value):
                pure_symbol += 1
            if _is_garbled(content_value):
                garbled += 1
            if len(content_value) > 100:
                long_comments += 1
            if not source_id.strip():
                missing_source_content += 1
            if not has_platform_field:
                missing_platform += 1
            for brand in BRAND_TERMS:
                if brand.lower() in content_value.lower():
                    brand_mentions[brand] += 1
            if len(samples) < 20:
                samples.append(_normalize_sample(item))

    quality_issues = [
        ImportQualityIssue(rule="空内容", count=empty_content, description="正文为空或只包含空白字符", action="排除", enabled=True),
        ImportQualityIssue(rule="纯@他人", count=pure_at, description="评论只是在 @ 用户，没有实际语义", action="排除", enabled=True),
        ImportQualityIssue(rule="纯符号表情", count=pure_symbol, description="仅包含符号、标点、emoji 或平台表情", action="排除", enabled=True),
        ImportQualityIssue(rule="乱码内容", count=garbled, description="异常编码或不可读字符比例较高", action="排除", enabled=True),
        ImportQualityIssue(rule="重复评论ID", count=duplicate_comment_ids, description="comment_id 重复，建议按评论ID去重", action="合并", enabled=True),
        ImportQualityIssue(rule="缺失内容ID", count=missing_source_content, description="aweme_id 为空时无法生成内容链接", action="保留并待补", enabled=False),
        ImportQualityIssue(rule="缺失平台", count=missing_platform, description="本文件无平台列，按项目默认推断为抖音", action="自动补平台", enabled=True),
    ]

    return ImportPreviewResponse(
        filename=filename,
        sheet_name=sheet_name,
        total_rows=total_rows,
        headers=headers,
        mappings=[_mapping_for_header(header, samples) for header in headers],
        quality_issues=quality_issues,
        samples=samples[:10],
        inferred_platform=DEFAULT_PLATFORM,
        duplicate_comment_ids=duplicate_comment_ids,
        long_comments=long_comments,
        brand_mentions=dict(brand_mentions.most_common(20)),
    )


def _first_sheet(archive: ZipFile) -> tuple[str, str]:
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    sheet = workbook.find(f"{MAIN_NS}sheets/{MAIN_NS}sheet")
    if sheet is None:
        raise ValueError("Excel 文件没有工作表")
    sheet_name = sheet.attrib.get("name", "Sheet1")
    rel_id = sheet.attrib.get(f"{REL_NS}id")
    rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    target = None
    for rel in rels:
        if rel.attrib.get("Id") == rel_id:
            target = rel.attrib.get("Target")
            break
    if not target:
        raise ValueError("无法定位 Excel 工作表")
    if not target.startswith("xl/"):
        target = f"xl/{target.lstrip('/')}"
    return sheet_name, target


def _shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall(f"{MAIN_NS}si"):
        texts = [node.text or "" for node in item.iter(f"{MAIN_NS}t")]
        values.append("".join(texts))
    return values


def _iter_sheet_rows(archive: ZipFile, sheet_path: str, shared_strings: list[str]):
    with archive.open(sheet_path) as sheet_file:
        for _, row_element in ElementTree.iterparse(sheet_file, events=("end",)):
            if row_element.tag != f"{MAIN_NS}row":
                continue
            row: list[str] = []
            for cell in row_element.findall(f"{MAIN_NS}c"):
                ref = cell.attrib.get("r", "A1")
                index = _column_index(ref)
                while len(row) <= index:
                    row.append("")
                row[index] = _cell_value(cell, shared_strings)
            row_element.clear()
            yield row


def _cell_value(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        text_nodes = [node.text or "" for node in cell.iter(f"{MAIN_NS}t")]
        return unescape("".join(text_nodes))
    value = cell.find(f"{MAIN_NS}v")
    if value is None or value.text is None:
        return ""
    if cell_type == "s":
        index = int(value.text)
        return shared_strings[index] if index < len(shared_strings) else ""
    return value.text


def _column_index(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref)
    if not letters:
        return 0
    index = 0
    for char in letters.group(0):
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def _mapping_for_header(header: str, samples: list[dict[str, str]]) -> ImportFieldMapping:
    target, required, confidence = FIELD_TARGETS.get(header, ("ignore", False, 35))
    sample = ""
    for row in samples:
        if row.get(header):
            sample = row[header]
            break
    return ImportFieldMapping(source=header, target=target, required=required, confidence=confidence, sample=sample[:80])


def _normalize_sample(item: dict[str, str]) -> dict[str, str]:
    source_id = item.get("aweme_id", "")
    normalized = dict(item)
    normalized["platform"] = DEFAULT_PLATFORM
    normalized["source_content.url"] = f"https://www.douyin.com/video/{source_id}" if source_id else ""
    normalized["publish_time"] = _format_unix_seconds(item.get("create_time", ""))
    normalized["last_modify_time"] = _format_unix_milliseconds(item.get("last_modify_ts", ""))
    normalized["engagement.likes"] = item.get("like_count", "0")
    normalized["engagement.replies"] = item.get("sub_comment_count", "0")
    return normalized


def _value_at(row: list[str], index: int | None) -> str:
    if index is None or index >= len(row):
        return ""
    return str(row[index] or "")


def _is_pure_at(value: str) -> bool:
    stripped = value.strip()
    return bool(stripped.startswith("@") and len(stripped.split()) <= 2)


def _is_pure_symbol(value: str) -> bool:
    stripped = value.strip()
    return bool(stripped and re.fullmatch(r"[\W_\s\[\]（）()【】]+", stripped))


def _is_garbled(value: str) -> bool:
    if not value:
        return False
    replacement_count = value.count("�")
    return replacement_count >= 2 or replacement_count / max(len(value), 1) > 0.1


def _format_unix_seconds(value: str) -> str:
    if not value.isdigit():
        return ""
    from datetime import datetime

    return datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")


def _format_unix_milliseconds(value: str) -> str:
    if not value.isdigit():
        return ""
    from datetime import datetime

    return datetime.fromtimestamp(int(value) / 1000).strftime("%Y-%m-%d %H:%M:%S")
