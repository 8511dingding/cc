from copy import deepcopy
from datetime import datetime, timezone

from app.schemas import (
    DataRecord,
    DashboardResponse,
    LabelField,
    LabelOption,
    LabelSchema,
    LabelValue,
    ProjectSummary,
    ReportBlock,
    ReportVersion,
    RuleSuggestion,
    UserProfile,
)


USERS = {
    "u-001": UserProfile(id="u-001", name="Ning", role="项目管理员", avatar="N"),
    "u-002": UserProfile(id="u-002", name="Jane", role="分析师", avatar="J"),
}

PROJECTS = [
    ProjectSummary(
        id="p-a2",
        name="A2 舆情分析项目",
        client="A2",
        brand="a2",
        label_schema="A2 三层标签体系",
        rule_version="v9.3",
        report_template="0604 报告结构",
        status="报告待确认",
        progress=82,
        confirmed_count=12480,
        total_count=91230,
    ),
    ProjectSummary(
        id="p-risk",
        name="母婴品牌风险监测",
        client="内部项目",
        brand="多品牌",
        label_schema="风险等级 + 议题类型",
        rule_version="v2.1",
        report_template="风险周报",
        status="标注中",
        progress=39,
        confirmed_count=3900,
        total_count=10000,
    ),
]

LABEL_SCHEMA = LabelSchema(
    id="schema-a2-v1",
    name="A2 三层标签体系",
    version="v1",
    fields=[
        LabelField(
            key="sentiment_polarity",
            name="情绪一级",
            type="single_select",
            options=[
                LabelOption(value="positive", label="正面", color="green"),
                LabelOption(value="neutral", label="中性", color="gray"),
                LabelOption(value="negative", label="负面", color="red"),
            ],
        ),
        LabelField(
            key="sentiment_type",
            name="情绪二级",
            type="single_select",
            parent_key="sentiment_polarity",
            options=[
                LabelOption(value="trust", label="信任认可", parent_value="positive", color="green"),
                LabelOption(value="fact", label="事实陈述", parent_value="neutral", color="gray"),
                LabelOption(value="question", label="询问求证", parent_value="neutral", color="gray"),
                LabelOption(value="panic", label="恐慌焦虑", parent_value="negative", color="yellow"),
                LabelOption(value="bystander", label="庆幸旁观", parent_value="negative", color="yellow"),
                LabelOption(value="anger", label="愤怒背叛", parent_value="negative", color="red"),
            ],
        ),
        LabelField(
            key="cognition",
            name="认知标签",
            type="single_select",
            options=[
                LabelOption(value="none", label="无明确认知"),
                LabelOption(value="confused", label="信息混淆"),
                LabelOption(value="accurate", label="精准认知"),
                LabelOption(value="resistant", label="泛化抵触"),
            ],
        ),
        LabelField(
            key="action",
            name="行动标签",
            type="single_select",
            options=[
                LabelOption(value="none", label="暂无行动"),
                LabelOption(value="help", label="寻求帮助"),
                LabelOption(value="switch", label="转奶流失"),
                LabelOption(value="rights", label="维权诉求"),
            ],
        ),
    ],
)


def _label(auto: str, manual: str | None = None, confirmed: bool = False, user_id: str | None = None) -> LabelValue:
    confirmed_user = USERS[user_id] if user_id else None
    return LabelValue(
        auto=auto,
        manual=manual,
        final=manual or auto,
        confirmed=confirmed,
        confirmed_by=confirmed_user,
        confirmed_at=datetime(2026, 6, 5, 14, 22, tzinfo=timezone.utc) if confirmed else None,
        previous_value=auto if manual and manual != auto else None,
    )


RECORDS = [
    DataRecord(
        id="r-001",
        platform="小红书",
        publish_time="2026-05-22",
        author="小小妈妈",
        content="不敢喝了，有没有事啊？到底是真的假的？",
        brand_detected="a2",
        labels={
            "sentiment_polarity": _label("negative", "negative", True, "u-002"),
            "sentiment_type": _label("question", "panic", True, "u-002"),
            "cognition": _label("none", "confused", True, "u-002"),
            "action": _label("none"),
        },
        report_candidate=True,
    ),
    DataRecord(
        id="r-002",
        platform="抖音",
        publish_time="2026-05-23",
        author="奶粉观察",
        content="真的假的，先观望一下，等官方说法。",
        brand_detected="a2",
        labels={
            "sentiment_polarity": _label("neutral"),
            "sentiment_type": _label("question"),
            "cognition": _label("none"),
            "action": _label("none"),
        },
    ),
    DataRecord(
        id="r-003",
        platform="评论",
        publish_time="2026-05-24",
        author="认真生活",
        content="太离谱了，必须维权，不能让消费者自己承担。",
        brand_detected="a2",
        labels={
            "sentiment_polarity": _label("neutral", "negative", True, "u-001"),
            "sentiment_type": _label("fact", "anger", True, "u-001"),
            "cognition": _label("confused", "resistant", True, "u-001"),
            "action": _label("none", "rights", True, "u-001"),
        },
        report_candidate=True,
    ),
]

SUGGESTIONS = [
    RuleSuggestion(
        id="s-001",
        title="增强“恐慌焦虑”关键词",
        summary="18 条内容从“中性/询问求证”被人工改为“负面/恐慌焦虑”。建议提高相关表达命中权重。",
        suggestion_type="add_keyword",
        evidence_count=18,
        keywords=["不敢喝", "怕了", "吓人", "有没有事"],
    ),
    RuleSuggestion(
        id="s-002",
        title="提高“泛化抵触”优先级",
        summary="多条内容从事件讨论上升到品牌整体不信任，建议在认知层中提高泛化抵触优先级。",
        suggestion_type="adjust_priority",
        evidence_count=9,
        keywords=["以后不买", "整个牌子", "都不可信"],
    ),
]

REPORT = ReportVersion(
    id="report-v03",
    project_id="p-a2",
    title="A2 舆情分析报告",
    version="v03",
    status="待确认",
    blocks=[
        ReportBlock(
            id="b-001",
            title="项目概览",
            block_type="text",
            content="本报告基于导入数据、自动规则标注和人工确认标签生成，所有结论均可追溯到底层样本。",
        ),
        ReportBlock(
            id="b-002",
            title="情绪分析",
            block_type="chart",
            content="展示正面 / 中性 / 负面分布，以及恐慌焦虑、庆幸旁观、愤怒背叛等二级情绪类型。",
        ),
    ],
)


def dashboard() -> DashboardResponse:
    return DashboardResponse(
        user=USERS["u-001"],
        projects=deepcopy(PROJECTS),
        active_project=deepcopy(PROJECTS[0]),
        label_schema=deepcopy(LABEL_SCHEMA),
        records=deepcopy(RECORDS),
        suggestions=deepcopy(SUGGESTIONS),
        report=deepcopy(REPORT),
    )


def _schema_field(field_key: str) -> LabelField:
    for field in LABEL_SCHEMA.fields:
        if field.key == field_key:
            return field
    raise ValueError(f"Unknown label field: {field_key}")


def _validate_option(record: DataRecord, field: LabelField, value: str | None, pending: dict[str, str | None]) -> None:
    if value is None:
        return
    options = field.options
    if field.parent_key:
        parent_value = pending.get(field.parent_key, record.labels.get(field.parent_key, LabelValue()).final)
        options = [option for option in options if option.parent_value == parent_value]
    if value not in {option.value for option in options}:
        raise ValueError(f"Invalid value for {field.key}: {value}")


def _clear_invalid_children(record: DataRecord, parent_key: str) -> None:
    parent_value = record.labels[parent_key].final
    for field in LABEL_SCHEMA.fields:
        if field.parent_key != parent_key:
            continue
        child = record.labels.get(field.key)
        if child is None or child.final is None:
            continue
        allowed = {option.value for option in field.options if option.parent_value == parent_value}
        if child.final in allowed:
            continue
        child.previous_value = child.final
        child.manual = None
        child.final = child.auto if child.auto in allowed else None
        child.confirmed = False
        child.confirmed_by = None
        child.confirmed_at = None


def patch_record(record_id: str, updates: list[dict], edited_by: str) -> DataRecord | None:
    editor = USERS.get(edited_by)
    if editor is None:
        raise ValueError(f"Unknown editor: {edited_by}")
    for record in RECORDS:
        if record.id != record_id:
            continue
        now = datetime.now(timezone.utc)
        pending_values = {key: value.final for key, value in record.labels.items()}
        for update in updates:
            field = _schema_field(update["field_key"])
            value = update.get("value")
            _validate_option(record, field, value, pending_values)
            pending_values[field.key] = value

        for update in updates:
            field_key = update["field_key"]
            value = update.get("value")
            label = record.labels.get(field_key)
            if label is None:
                continue
            label.previous_value = label.final
            label.manual = value
            label.final = value or label.auto
            label.confirmed = bool(update.get("confirmed"))
            if label.confirmed:
                label.confirmed_by = editor
                label.confirmed_at = now
            else:
                label.confirmed_by = None
                label.confirmed_at = None
            _clear_invalid_children(record, field_key)
        return deepcopy(record)
    return None
