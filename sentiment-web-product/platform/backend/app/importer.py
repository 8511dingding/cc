from __future__ import annotations

from collections import Counter
import csv
from html import unescape
from io import BytesIO, StringIO
import re
from zipfile import ZipFile
from xml.etree import ElementTree

from app.schemas import ImportFieldMapping, ImportPreviewResponse, ImportQualityIssue


MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MAX_PREVIEW_ROWS = 100_000
DEFAULT_PLATFORM = "抖音"
CONTENT_HEADER_CANDIDATES = (
    "评论内容",
    "内容",
    "content",
    "comment_content",
    "comment",
    "text",
    "正文",
)
NON_CONTENT_HEADER_PARTS = (
    "id",
    "链接",
    "url",
    "话题",
    "发布时间",
    "发布者",
    "作者",
    "互动",
    "点赞",
    "评论数",
    "收藏",
    "分享",
)

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
    if filename.lower().endswith(".csv"):
        return _preview_csv(filename, content)
    raise ValueError("当前导入预览支持 .xlsx 和 .csv 文件")


def _preview_csv(filename: str, content: bytes) -> ImportPreviewResponse:
    text = _decode_csv(content)
    reader = csv.reader(StringIO(text))
    try:
        headers = [header.strip() for header in next(reader)]
    except StopIteration as exc:
        raise ValueError("CSV 文件没有可读取的数据") from exc

    total_rows = 0
    effective_rows = 0
    duplicate_comment_ids = 0
    long_comments = 0
    empty_content = 0
    garbled = 0
    missing_platform = 0
    missing_source_content = 0
    missing_content_column = 0
    seen_comment_ids: set[str] = set()
    samples: list[dict[str, str]] = []
    brand_mentions: Counter[str] = Counter()
    header_index = {header: index for index, header in enumerate(headers)}
    content_header = _content_header(headers)
    has_platform_field = "platform" in header_index or "平台" in header_index

    for row in reader:
        if total_rows >= MAX_PREVIEW_ROWS:
            break
        if not any(str(cell).strip() for cell in row):
            continue
        total_rows += 1
        item = {header: _value_at(row, header_index.get(header)) for header in headers}
        item["_sheet_name"] = "CSV"
        comment_id = item.get("comment_id", "") or item.get("评论ID", "") or item.get("评论id", "")
        content_value = _value_at(row, header_index.get(content_header)) if content_header else ""
        source_id = item.get("aweme_id", "") or item.get("内容ID", "") or item.get("内容id", "")
        if comment_id in seen_comment_ids:
            duplicate_comment_ids += 1
        elif comment_id:
            seen_comment_ids.add(comment_id)
        if not content_header or not content_value.strip():
            empty_content += 1
        elif _is_garbled(content_value):
            garbled += 1
        else:
            effective_rows += 1
        if content_value.strip() and not _is_garbled(content_value) and len(content_value) > 100:
            long_comments += 1
        if not source_id.strip():
            missing_source_content += 1
        if not has_platform_field:
            missing_platform += 1
        for brand in BRAND_TERMS:
            if brand.lower() in content_value.lower():
                brand_mentions[brand] += 1
        if len(samples) < 20:
            sample = _normalize_sample(item)
            sample["content"] = content_value
            samples.append(sample)

    if not content_header:
        missing_content_column = total_rows
    if total_rows == 0:
        raise ValueError("CSV 文件没有可读取的数据")

    invalid_content_rows = empty_content + garbled
    quality_issues = [
        ImportQualityIssue(rule="空内容", count=empty_content, description="内容列为空、只有空格，或未识别到内容列", action="排除", enabled=True),
        ImportQualityIssue(rule="乱码内容", count=garbled, description="内容列包含异常编码或不可读字符", action="排除", enabled=True),
        ImportQualityIssue(rule="重复评论ID", count=duplicate_comment_ids, description="仅提示疑似重复，不影响预计有效数据", action="提示", enabled=True),
        ImportQualityIssue(rule="未识别内容列", count=missing_content_column, description="文件中未找到“内容”或“评论内容”列", action="待确认", enabled=True),
        ImportQualityIssue(rule="缺失内容ID", count=missing_source_content, description="aweme_id 为空时无法生成内容链接", action="保留并待补", enabled=False),
        ImportQualityIssue(rule="缺失平台", count=missing_platform, description="本文件无平台列，按项目默认推断为抖音", action="自动补平台", enabled=True),
    ]

    return ImportPreviewResponse(
        filename=filename,
        sheet_name="CSV",
        total_rows=total_rows,
        effective_rows=effective_rows,
        invalid_content_rows=invalid_content_rows,
        sheet_count=1,
        headers=headers,
        mappings=[_mapping_for_header(header, samples) for header in headers],
        quality_issues=quality_issues,
        samples=samples[:10],
        inferred_platform=DEFAULT_PLATFORM,
        duplicate_comment_ids=duplicate_comment_ids,
        long_comments=long_comments,
        brand_mentions=dict(brand_mentions.most_common(20)),
    )


def _decode_csv(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV 文件编码无法识别，请使用 UTF-8 或 GB18030 编码")


def _preview_xlsx(filename: str, content: bytes) -> ImportPreviewResponse:
    with ZipFile(BytesIO(content)) as archive:
        sheets = _workbook_sheets(archive)
        shared_strings = _shared_strings(archive)

        total_rows = 0
        effective_rows = 0
        invalid_content_rows = 0
        duplicate_comment_ids = 0
        long_comments = 0
        empty_content = 0
        garbled = 0
        missing_platform = 0
        missing_source_content = 0
        missing_content_column = 0
        seen_comment_ids: set[str] = set()
        all_headers: list[str] = []
        samples: list[dict[str, str]] = []
        brand_mentions: Counter[str] = Counter()

        for sheet_name, sheet_path in sheets:
            rows = _iter_sheet_rows(archive, sheet_path, shared_strings)
            try:
                headers = [header.strip() for header in next(rows)]
            except StopIteration:
                continue
            all_headers.extend(header for header in headers if header and header not in all_headers)
            header_index = {header: index for index, header in enumerate(headers)}
            content_header = _content_header(headers)
            has_platform_field = "platform" in header_index or "平台" in header_index
            sheet_data_rows = 0

            for row in rows:
                if total_rows >= MAX_PREVIEW_ROWS:
                    break
                if not any(str(cell).strip() for cell in row):
                    continue
                sheet_data_rows += 1
                total_rows += 1
                item = {header: _value_at(row, header_index.get(header)) for header in headers}
                item["_sheet_name"] = sheet_name
                comment_id = item.get("comment_id", "") or item.get("评论ID", "") or item.get("评论id", "")
                content_value = _value_at(row, header_index.get(content_header)) if content_header else ""
                source_id = item.get("aweme_id", "") or item.get("内容ID", "") or item.get("内容id", "")
                if comment_id in seen_comment_ids:
                    duplicate_comment_ids += 1
                elif comment_id:
                    seen_comment_ids.add(comment_id)
                if not content_header or not content_value.strip():
                    empty_content += 1
                elif _is_garbled(content_value):
                    garbled += 1
                else:
                    effective_rows += 1
                if content_value.strip() and not _is_garbled(content_value) and len(content_value) > 100:
                    long_comments += 1
                if not source_id.strip():
                    missing_source_content += 1
                if not has_platform_field:
                    missing_platform += 1
                for brand in BRAND_TERMS:
                    if brand.lower() in content_value.lower():
                        brand_mentions[brand] += 1
                if len(samples) < 20:
                    sample = _normalize_sample(item)
                    sample["content"] = content_value
                    samples.append(sample)
            if not content_header:
                missing_content_column += sheet_data_rows
            if total_rows >= MAX_PREVIEW_ROWS:
                break

        if total_rows == 0:
            raise ValueError("Excel 文件没有可读取的数据")
        invalid_content_rows = empty_content + garbled

    quality_issues = [
        ImportQualityIssue(rule="空内容", count=empty_content, description="内容列为空、只有空格，或未识别到内容列", action="排除", enabled=True),
        ImportQualityIssue(rule="乱码内容", count=garbled, description="内容列包含异常编码或不可读字符", action="排除", enabled=True),
        ImportQualityIssue(rule="重复评论ID", count=duplicate_comment_ids, description="仅提示疑似重复，不影响预计有效数据", action="提示", enabled=True),
        ImportQualityIssue(rule="未识别内容列", count=missing_content_column, description="sheet 中未找到“内容”或“评论内容”列", action="待确认", enabled=True),
        ImportQualityIssue(rule="缺失内容ID", count=missing_source_content, description="aweme_id 为空时无法生成内容链接", action="保留并待补", enabled=False),
        ImportQualityIssue(rule="缺失平台", count=missing_platform, description="本文件无平台列，按项目默认推断为抖音", action="自动补平台", enabled=True),
    ]

    return ImportPreviewResponse(
        filename=filename,
        sheet_name="、".join(sheet[0] for sheet in sheets[:5]),
        total_rows=total_rows,
        effective_rows=effective_rows,
        invalid_content_rows=invalid_content_rows,
        sheet_count=len(sheets),
        headers=all_headers,
        mappings=[_mapping_for_header(header, samples) for header in all_headers],
        quality_issues=quality_issues,
        samples=samples[:10],
        inferred_platform=DEFAULT_PLATFORM,
        duplicate_comment_ids=duplicate_comment_ids,
        long_comments=long_comments,
        brand_mentions=dict(brand_mentions.most_common(20)),
    )


def _workbook_sheets(archive: ZipFile) -> list[tuple[str, str]]:
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    sheet_elements = workbook.findall(f"{MAIN_NS}sheets/{MAIN_NS}sheet")
    if not sheet_elements:
        raise ValueError("Excel 文件没有工作表")
    rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {}
    for rel in rels:
        rel_id = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rel_id and target:
            rel_targets[rel_id] = _sheet_target_path(target)
    sheets: list[tuple[str, str]] = []
    for index, sheet in enumerate(sheet_elements, start=1):
        sheet_name = sheet.attrib.get("name", f"Sheet{index}")
        rel_id = sheet.attrib.get(f"{REL_NS}id")
        target = rel_targets.get(rel_id or "")
        if target:
            sheets.append((sheet_name, target))
    if not sheets:
        raise ValueError("无法定位 Excel 工作表")
    return sheets


def _sheet_target_path(target: str) -> str:
    normalized = target.lstrip("/")
    if normalized.startswith("../"):
        normalized = normalized[3:]
    if not normalized.startswith("xl/"):
        normalized = f"xl/{normalized}"
    return normalized


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


def _content_header(headers: list[str]) -> str | None:
    normalized_headers = [(header, header.strip().lower()) for header in headers if header.strip()]
    for candidate in CONTENT_HEADER_CANDIDATES:
        candidate_lower = candidate.lower()
        for original, normalized in normalized_headers:
            if normalized == candidate_lower:
                return original
    for original, normalized in normalized_headers:
        if any(part in normalized for part in NON_CONTENT_HEADER_PARTS):
            continue
        if "评论内容" in original or original == "内容" or normalized == "content":
            return original
    for original, normalized in normalized_headers:
        if any(part in normalized for part in NON_CONTENT_HEADER_PARTS):
            continue
        if "内容" in original or "comment" in normalized or "text" in normalized:
            return original
    return None


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
