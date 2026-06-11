from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas import (
    CommentEngagement,
    DataRecord,
    DashboardResponse,
    ExportRecord,
    ExportPreset,
    ImportJob,
    ImportPreviewResponse,
    LabelField,
    LabelOption,
    LabelSchema,
    LabelValue,
    ProjectRuleStatus,
    ProjectRulesPatchRequest,
    ProjectUpsertRequest,
    ProjectSummary,
    RecordBrandsPatchRequest,
    ReportBlock,
    RecordReportPatchRequest,
    ReportTemplate,
    ReportVersion,
    RuleImpactPreview,
    RuleImpactSample,
    RuleSuggestion,
    SourceContentMeta,
    UserProfile,
)
from app.rule_seed import RULE_SETS, build_brand_rules, build_rule_definitions


USERS = {
    "u-001": UserProfile(id="u-001", name="Ning", role="项目管理员", avatar="N"),
    "u-002": UserProfile(id="u-002", name="Jane", role="分析师", avatar="J"),
    "u-003": UserProfile(id="u-003", name="Mia", role="标注员", avatar="M", status="invited"),
}

PROJECTS = [
    ProjectSummary(
        id="p-a2",
        name="A2 舆情分析项目",
        client="A2",
        brand="a2",
        description="围绕 A2 奶粉舆情事件建立数据导入、规则学习、人工确认和在线报告闭环。",
        objective="识别消费者正负向态度、核心认知偏差、情绪风险和转奶/维权行动倾向。",
        platforms=["小红书", "抖音", "微博"],
        created_at="2026-06-05",
        date_range="2026-05-19 至 2026-06-05",
        delivery_due="2026-06-08",
        updated_at="2026-06-05 16:40",
        owner=USERS["u-001"],
        label_schema="A2 三层标签体系",
        rule_version="v9.3",
        report_template="0604 报告结构",
        export_pattern="{client}_舆情分析_{report_version}_{YYYYMMDD}",
        selected_rule_set_ids=[
            "rules-sentiment-a2-v9",
            "rules-cognition-a2-v9",
            "rules-action-a2-v9",
            "rules-brand-milk-powder-top40",
            "rules-cleaning-default",
        ],
        applied_rule_set_ids=[
            "rules-sentiment-a2-v9",
            "rules-cognition-a2-v9",
            "rules-action-a2-v9",
            "rules-brand-milk-powder-top40",
            "rules-cleaning-default",
        ],
        priority="高",
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
        description="用于持续监测母婴奶粉品牌风险讨论，识别高互动负面样本和品牌竞品变化。",
        objective="形成周度风险看板，支持品牌侧及时发现异常议题和需要人工复核的样本。",
        platforms=["小红书", "抖音"],
        created_at="2026-06-04",
        date_range="2026-06-01 至 2026-06-05",
        delivery_due="2026-06-07",
        updated_at="2026-06-05 15:18",
        owner=USERS["u-002"],
        label_schema="风险等级 + 议题类型",
        rule_version="v2.1",
        report_template="风险周报",
        export_pattern="{project}_{date}_{version}_{format}",
        selected_rule_set_ids=["rules-brand-milk-powder-top40", "rules-cleaning-default"],
        applied_rule_set_ids=["rules-brand-milk-powder-top40"],
        priority="中",
        status="标注中",
        progress=39,
        confirmed_count=3900,
        total_count=10000,
    ),
]

IMPORTS = [
    ImportJob(
        id="imp-001",
        filename="0527_a2舆情_数据_v1.xlsx",
        status="ready",
        total_rows=91230,
        valid_rows=88410,
        invalid_rows=2820,
        created_at="2026-06-05 10:18",
        owner=USERS["u-001"],
    ),
    ImportJob(
        id="imp-002",
        filename="fb_0522_内容和评论合并_清洗后.xlsx",
        status="mapped",
        total_rows=18642,
        valid_rows=0,
        invalid_rows=0,
        created_at="2026-06-05 14:07",
        owner=USERS["u-002"],
    ),
]

PROJECT_IMPORTS: dict[str, list[ImportJob]] = {
    "p-a2": IMPORTS,
    "p-risk": [
        ImportJob(
            id="imp-risk-001",
            filename="risk_week_0601_0605.xlsx",
            status="ready",
            total_rows=10000,
            valid_rows=9450,
            invalid_rows=550,
            created_at="2026-06-05 13:12",
            owner=USERS["u-002"],
            file_size_label="历史记录",
            note="历史导入记录",
        )
    ],
}
IMPORT_FILE_PATHS: dict[str, Path] = {}

BRAND_RULES = build_brand_rules()
RULE_DEFINITIONS = build_rule_definitions()

REPORT_TEMPLATES = [
    ReportTemplate(
        id="tpl-a2-crisis",
        name="A2 舆情分析报告",
        version="0604 v2",
        sections=["项目概览", "传播声量", "情绪结构", "认知与行动", "重点样本", "策略建议"],
        formats=["docx", "pdf", "pptx"],
        updated_at="2026-06-04 18:30",
    ),
    ReportTemplate(
        id="tpl-risk-weekly",
        name="母婴品牌风险周报",
        version="v1",
        sections=["本周摘要", "风险品牌", "高频议题", "异常样本", "处理建议"],
        formats=["docx", "pdf"],
        updated_at="2026-06-05 09:20",
    ),
]

EXPORT_PRESETS = [
    ExportPreset(
        id="export-default",
        name="项目标准命名",
        pattern="{project}_{date}_{version}_{format}",
        formats=["xlsx", "docx", "pdf", "pptx"],
    ),
    ExportPreset(
        id="export-client",
        name="客户交付命名",
        pattern="{client}_舆情分析_{report_version}_{YYYYMMDD}",
        formats=["xlsx", "docx", "pdf"],
    ),
]

EXPORT_RECORDS = [
    ExportRecord(
        id="exp-001",
        filename="A2_舆情分析_0605_v03.docx",
        format="docx",
        status="ready",
        report_version="v03",
        created_at="2026-06-05 16:22",
        size="4.8 MB",
        owner=USERS["u-001"],
    ),
    ExportRecord(
        id="exp-002",
        filename="A2_舆情分析_0605_v03.xlsx",
        format="xlsx",
        status="ready",
        report_version="v03",
        created_at="2026-06-05 16:21",
        size="18.4 MB",
        owner=USERS["u-002"],
    ),
    ExportRecord(
        id="exp-003",
        filename="A2_舆情分析_0605_v02.pdf",
        format="pdf",
        status="ready",
        report_version="v02",
        created_at="2026-06-05 11:10",
        size="3.2 MB",
        owner=USERS["u-001"],
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
        comment_type="普通内容",
        engagement=CommentEngagement(likes=128, replies=18),
        brand_detected="a2",
        brands=["a2"],
        matched_keywords=["不敢喝", "有没有事", "真的假的"],
        source_content=SourceContentMeta(
            id="note-001",
            url="https://www.xiaohongshu.com/explore/note-001",
            author="母婴观察号",
            publish_time="2026-05-22 09:18",
            title="热门奶粉品牌讨论",
            topics=["奶粉", "母婴", "品牌反馈"],
            comments=240,
            likes=1840,
            favorites=316,
            shares=72,
        ),
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
        content="真的假的，先观望一下，等官方说法。@姐妹们 有没有看到更完整的解释？",
        comment_type="@他人",
        engagement=CommentEngagement(likes=46, replies=6),
        brand_detected="a2",
        brands=["a2", "爱他美"],
        matched_keywords=["真的假的", "@姐妹们", "官方说法"],
        source_content=SourceContentMeta(
            id="dy-8891",
            url="https://www.douyin.com/video/dy-8891",
            author="育儿记录本",
            publish_time="2026-05-23 11:02",
            title="抖音视频：奶粉选择记录",
            topics=["育儿", "奶粉选择", "抖音热评"],
            comments=518,
            likes=8620,
            favorites=910,
            shares=184,
        ),
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
        content="太离谱了，必须维权，不能让消费者自己承担。之前还考虑过爱他美和飞鹤，现在整个品类都要重新看看，客服如果不回应，后面肯定会继续投诉。而且很多妈妈不是专业人士，只能看平台和品牌怎么解释，所以信息越模糊越容易引发恐慌。",
        comment_type="长评论",
        engagement=CommentEngagement(likes=392, replies=64),
        brand_detected="a2",
        brands=["a2", "爱他美", "飞鹤"],
        matched_keywords=["太离谱", "必须维权", "爱他美", "飞鹤", "投诉"],
        source_content=SourceContentMeta(
            id="note-039",
            url="https://www.xiaohongshu.com/explore/note-039",
            author="消费者反馈墙",
            publish_time="2026-05-24 16:40",
            title="小红书笔记：近期奶粉反馈汇总",
            topics=["消费者反馈", "维权", "奶粉"],
            comments=132,
            likes=2490,
            favorites=488,
            shares=96,
        ),
        labels={
            "sentiment_polarity": _label("neutral", "negative", True, "u-001"),
            "sentiment_type": _label("fact", "anger", True, "u-001"),
            "cognition": _label("confused", "resistant", True, "u-001"),
            "action": _label("none", "rights", True, "u-001"),
        },
        report_candidate=True,
    ),
]

RISK_RECORDS = [
    DataRecord(
        id="risk-001",
        platform="抖音",
        publish_time="2026-06-02",
        author="敏感观察",
        content="这个品牌最近好多讨论，先观望一下，别急着下单。",
        comment_type="普通内容",
        engagement=CommentEngagement(likes=86, replies=14),
        brand_detected="多品牌",
        brands=["飞鹤", "爱他美"],
        matched_keywords=["观望", "别急着下单"],
        source_content=SourceContentMeta(
            id="dy-risk-001",
            url="https://www.douyin.com/video/dy-risk-001",
            author="母婴热点",
            publish_time="2026-06-02 13:20",
            title="母婴品牌近期讨论",
            topics=["母婴", "品牌风险", "奶粉"],
            comments=332,
            likes=5200,
            favorites=430,
            shares=116,
        ),
        labels={
            "sentiment_polarity": _label("neutral"),
            "sentiment_type": _label("question"),
            "cognition": _label("none"),
            "action": _label("none"),
        },
        report_candidate=False,
    ),
    DataRecord(
        id="risk-002",
        platform="小红书",
        publish_time="2026-06-03",
        author="认真选奶粉",
        content="如果一直说不清楚，我可能会直接换品牌，安全感太重要了。",
        comment_type="普通内容",
        engagement=CommentEngagement(likes=214, replies=39),
        brand_detected="多品牌",
        brands=["a2", "美素佳儿"],
        matched_keywords=["说不清楚", "换品牌", "安全感"],
        source_content=SourceContentMeta(
            id="note-risk-002",
            url="https://www.xiaohongshu.com/explore/note-risk-002",
            author="奶粉避坑记录",
            publish_time="2026-06-03 18:04",
            title="近期品牌信任讨论",
            topics=["奶粉", "品牌信任", "风险监测"],
            comments=96,
            likes=1880,
            favorites=260,
            shares=48,
        ),
        labels={
            "sentiment_polarity": _label("negative", "negative", True, "u-002"),
            "sentiment_type": _label("panic", "anger", True, "u-002"),
            "cognition": _label("confused", "resistant", True, "u-002"),
            "action": _label("none", "switch", True, "u-002"),
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

RISK_REPORT = ReportVersion(
    id="report-risk-v01",
    project_id="p-risk",
    title="母婴品牌风险监测周报",
    version="v01",
    status="标注中",
    blocks=[
        ReportBlock(
            id="risk-b-001",
            title="本周摘要",
            block_type="text",
            content="本周重点监测多品牌信任风险、转奶倾向与高互动讨论样本。",
        ),
        ReportBlock(
            id="risk-b-002",
            title="风险品牌与议题",
            block_type="table",
            content="展示品牌提及、风险情绪、行动倾向与重点样本。",
        ),
    ],
)


def _active_project(project_id: str | None) -> ProjectSummary:
    for project in PROJECTS:
        if project.id == project_id:
            return project
    return PROJECTS[0]


def _project_records(project_id: str) -> list[DataRecord]:
    if project_id == "p-risk":
        return RISK_RECORDS
    if project_id == "p-a2":
        return RECORDS
    return []


def _project_imports(project_id: str) -> list[ImportJob]:
    return PROJECT_IMPORTS.setdefault(project_id, [])


def _project_report(project_id: str) -> ReportVersion:
    if project_id == "p-risk":
        return RISK_REPORT
    if project_id == "p-a2":
        return REPORT
    return ReportVersion(
        id=f"report-{project_id}",
        project_id=project_id,
        title="在线舆情分析报告",
        version="v00",
        status="待生成",
        blocks=[
            ReportBlock(
                id=f"{project_id}-empty-summary",
                title="项目摘要",
                block_type="text",
                content="项目创建后，请先完成数据导入、规则学习与自动打标，再生成在线报告。",
            )
        ],
    )


def _project_exports(project_id: str) -> list[ExportRecord]:
    if project_id == "p-risk":
        return [
            ExportRecord(
                id="exp-risk-001",
                filename="母婴品牌风险监测_0605_v01.docx",
                format="docx",
                status="exporting",
                report_version="v01",
                created_at="2026-06-05 15:40",
                size="生成中",
                owner=USERS["u-002"],
            )
        ]
    if project_id == "p-a2":
        return EXPORT_RECORDS
    return []


def _project_rule_status(project: ProjectSummary) -> list[ProjectRuleStatus]:
    selected = set(project.selected_rule_set_ids)
    applied = set(project.applied_rule_set_ids)
    return [
        ProjectRuleStatus(
            rule_set_id=rule_set.id,
            selected=rule_set.id in selected,
            applied=rule_set.id in applied,
            pending_apply=rule_set.id in selected and rule_set.id not in applied,
        )
        for rule_set in RULE_SETS
    ]


def _count_record_sentiment(records: list[DataRecord], use_after_rules: bool = False, selected_rule_set_ids: list[str] | None = None) -> dict[str, int]:
    counts: dict[str, int] = {"positive": 0, "neutral": 0, "negative": 0}
    for record in records:
        value = record.labels.get("sentiment_polarity", LabelValue()).final or "neutral"
        if use_after_rules:
            predicted = _predict_record_sentiment(record, selected_rule_set_ids or [])
            value = predicted or value
        counts[value] = counts.get(value, 0) + 1
    return counts


def _predict_record_sentiment(record: DataRecord, selected_rule_set_ids: list[str]) -> str | None:
    if "rules-sentiment-a2-v9" not in selected_rule_set_ids:
        return None
    if record.labels.get("sentiment_polarity", LabelValue()).confirmed:
        return record.labels.get("sentiment_polarity", LabelValue()).final
    content = record.content.lower()
    negative_keywords = ["不敢", "有事", "维权", "投诉", "离谱", "担心", "焦虑", "害怕", "换品牌", "不安全", "被骗", "塌房"]
    positive_keywords = ["放心", "没事", "没有问题", "继续喝", "健康", "安全"]
    if any(keyword.lower() in content for keyword in negative_keywords):
        return "negative"
    if any(keyword.lower() in content for keyword in positive_keywords):
        return "positive"
    return "neutral"


def preview_project_rules(project_id: str, payload: ProjectRulesPatchRequest) -> RuleImpactPreview | None:
    project = _active_project(project_id)
    if project.id != project_id:
        return None
    selected_ids = _normalize_rule_set_ids(payload.selected_rule_set_ids)
    records = _project_records(project_id)
    protected_records = sum(1 for record in records if any(label.confirmed for label in record.labels.values()))
    sample_changes: list[RuleImpactSample] = []
    changed_records = 0
    for record in records:
        before = record.labels.get("sentiment_polarity", LabelValue()).final or "neutral"
        after = _predict_record_sentiment(record, selected_ids) or before
        if after == before:
            continue
        changed_records += 1
        if len(sample_changes) < 5:
            sample_changes.append(
                RuleImpactSample(
                    record_id=record.id,
                    content=record.content,
                    before=before,
                    after=after,
                    matched_rule="A2 情绪两级规则",
                )
            )
    return RuleImpactPreview(
        project_id=project_id,
        selected_rule_set_ids=selected_ids,
        newly_selected_rule_set_ids=[rule_id for rule_id in selected_ids if rule_id not in project.applied_rule_set_ids],
        already_applied_rule_set_ids=[rule_id for rule_id in selected_ids if rule_id in project.applied_rule_set_ids],
        protected_records=protected_records,
        before_counts=_count_record_sentiment(records),
        after_counts=_count_record_sentiment(records, True, selected_ids),
        changed_records=changed_records,
        sample_changes=sample_changes,
    )


def apply_project_rules(project_id: str, payload: ProjectRulesPatchRequest) -> RuleImpactPreview | None:
    preview = preview_project_rules(project_id, payload)
    if preview is None:
        return None
    if payload.edited_by not in USERS:
        raise ValueError(f"Unknown editor: {payload.edited_by}")
    selected_ids = _normalize_rule_set_ids(payload.selected_rule_set_ids)
    for index, project in enumerate(PROJECTS):
        if project.id != project_id:
            continue
        PROJECTS[index] = project.model_copy(
            update={
                "selected_rule_set_ids": selected_ids,
                "applied_rule_set_ids": selected_ids,
                "rule_version": _merged_rule_version(selected_ids),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )
        return preview
    return None


def _merged_rule_version(rule_set_ids: list[str]) -> str:
    versions = [rule_set.version for rule_set in RULE_SETS if rule_set.id in rule_set_ids]
    return " + ".join(dict.fromkeys(versions)) or "未应用规则"


def _project_id() -> str:
    existing = {project.id for project in PROJECTS}
    index = len(PROJECTS) + 1
    while f"p-custom-{index:03d}" in existing:
        index += 1
    return f"p-custom-{index:03d}"


def _rule_set_ids() -> set[str]:
    return {rule_set.id for rule_set in RULE_SETS}


def _normalize_rule_set_ids(rule_set_ids: list[str]) -> list[str]:
    known_ids = _rule_set_ids()
    cleaned = []
    for rule_set_id in rule_set_ids:
        normalized = rule_set_id.strip()
        if not normalized:
            continue
        if normalized not in known_ids:
            raise ValueError(f"规则不存在：{normalized}")
        if normalized not in cleaned:
            cleaned.append(normalized)
    return cleaned


def _validated_project_payload(payload: ProjectUpsertRequest) -> None:
    required = {
        "项目名称": payload.name,
        "客户": payload.client,
        "品牌": payload.brand,
        "项目周期": payload.date_range,
    }
    missing = [label for label, value in required.items() if not value.strip()]
    if missing:
        raise ValueError(f"请补充：{'、'.join(missing)}")
    if payload.owner_id not in USERS:
        raise ValueError("负责人不存在")
    _normalize_rule_set_ids(payload.selected_rule_set_ids)


def create_project(payload: ProjectUpsertRequest) -> ProjectSummary:
    _validated_project_payload(payload)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    project = ProjectSummary(
        id=_project_id(),
        name=payload.name.strip(),
        client=payload.client.strip(),
        brand=payload.brand.strip(),
        description=payload.description.strip(),
        objective=payload.objective.strip(),
        platforms=payload.platforms,
        created_at=now[:10],
        date_range=payload.date_range.strip(),
        delivery_due=payload.delivery_due.strip(),
        updated_at=now,
        owner=USERS[payload.owner_id],
        label_schema=payload.label_schema.strip() or "A2 三层标签体系",
        rule_version=payload.rule_version.strip() or "v1.0",
        report_template=payload.report_template.strip() or "默认报告模板",
        export_pattern=payload.export_pattern.strip() or "{project}_{date}_{version}_{format}",
        selected_rule_set_ids=_normalize_rule_set_ids(payload.selected_rule_set_ids),
        applied_rule_set_ids=[],
        priority=payload.priority,
        status=payload.status.strip() or "项目配置中",
        progress=0,
        confirmed_count=0,
        total_count=0,
    )
    PROJECTS.insert(0, project)
    return deepcopy(project)


def update_project(project_id: str, payload: ProjectUpsertRequest) -> ProjectSummary | None:
    _validated_project_payload(payload)
    for index, project in enumerate(PROJECTS):
        if project.id != project_id:
            continue
        updated = project.model_copy(
            update={
                "name": payload.name.strip(),
                "client": payload.client.strip(),
                "brand": payload.brand.strip(),
                "description": payload.description.strip(),
                "objective": payload.objective.strip(),
                "platforms": payload.platforms,
                "date_range": payload.date_range.strip(),
                "delivery_due": payload.delivery_due.strip(),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "owner": USERS[payload.owner_id],
                "label_schema": payload.label_schema.strip() or project.label_schema,
                "rule_version": payload.rule_version.strip() or project.rule_version,
                "report_template": payload.report_template.strip() or project.report_template,
                "export_pattern": payload.export_pattern.strip() or project.export_pattern,
                "selected_rule_set_ids": _normalize_rule_set_ids(payload.selected_rule_set_ids),
                "priority": payload.priority,
                "status": payload.status.strip() or project.status,
            }
        )
        PROJECTS[index] = updated
        return deepcopy(updated)
    return None


def delete_project(project_id: str) -> bool:
    if len(PROJECTS) <= 1:
        raise ValueError("至少需要保留一个项目")
    for index, project in enumerate(PROJECTS):
        if project.id == project_id:
            PROJECTS.pop(index)
            return True
    return False


def register_import_job(
    project_id: str,
    preview: ImportPreviewResponse,
    *,
    owner_id: str,
    file_size_label: str,
    storage_path: Path,
) -> ImportJob | None:
    project = _active_project(project_id)
    if project.id != project_id:
        return None
    if owner_id not in USERS:
        raise ValueError("上传人不存在")
    import_id = f"imp-{uuid4().hex[:12]}"
    note = (
        f"已扫描 {preview.sheet_count} 个 sheet，预计有效数据按内容列非空且非乱码统计。"
        if preview.duplicate_comment_ids == 0
        else f"检测到 {preview.duplicate_comment_ids} 条疑似重复数据；预计有效数据仍只按内容列是否可用统计。"
    )
    job = ImportJob(
        id=import_id,
        filename=preview.filename,
        status="ready",
        total_rows=preview.total_rows,
        valid_rows=preview.effective_rows,
        invalid_rows=preview.invalid_content_rows,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        owner=USERS[owner_id],
        duplicate_rows=preview.duplicate_comment_ids,
        file_size_label=file_size_label,
        download_url=f"/api/platform/projects/{project_id}/imports/{import_id}/download",
        note=note,
    )
    _project_imports(project_id).insert(0, job)
    IMPORT_FILE_PATHS[import_id] = storage_path
    for index, item in enumerate(PROJECTS):
        if item.id != project_id:
            continue
        PROJECTS[index] = item.model_copy(
            update={
                "total_count": sum(import_job.valid_rows for import_job in _project_imports(project_id)),
                "status": "待自动打标" if item.status in {"待导入数据", "项目配置中", "待字段映射"} else item.status,
                "progress": max(item.progress, 18),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )
        break
    return deepcopy(job)


def import_file_path(import_id: str) -> Path | None:
    path = IMPORT_FILE_PATHS.get(import_id)
    if path and path.exists():
        return path
    return None


def import_job(project_id: str, import_id: str) -> ImportJob | None:
    for job in _project_imports(project_id):
        if job.id == import_id:
            return deepcopy(job)
    return None


def dashboard(project_id: str | None = None) -> DashboardResponse:
    active_project = _active_project(project_id)
    return DashboardResponse(
        user=USERS["u-001"],
        users=deepcopy(list(USERS.values())),
        projects=deepcopy(PROJECTS),
        active_project=deepcopy(active_project),
        label_schema=deepcopy(LABEL_SCHEMA),
        records=deepcopy(_project_records(active_project.id)),
        imports=deepcopy(_project_imports(active_project.id)),
        brand_rules=deepcopy(BRAND_RULES),
        rule_sets=deepcopy(RULE_SETS),
        rule_definitions=deepcopy(RULE_DEFINITIONS),
        project_rule_status=deepcopy(_project_rule_status(active_project)),
        suggestions=deepcopy(SUGGESTIONS),
        report_templates=deepcopy(REPORT_TEMPLATES),
        export_presets=deepcopy(EXPORT_PRESETS),
        export_records=deepcopy(_project_exports(active_project.id)),
        report=deepcopy(_project_report(active_project.id)),
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
    for record in [*RECORDS, *RISK_RECORDS]:
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


def patch_report_candidate(record_id: str, payload: RecordReportPatchRequest) -> DataRecord | None:
    if payload.edited_by not in USERS:
        raise ValueError(f"Unknown editor: {payload.edited_by}")
    for record in [*RECORDS, *RISK_RECORDS]:
        if record.id == record_id:
            record.report_candidate = payload.report_candidate
            return deepcopy(record)
    return None


def patch_brands(record_id: str, payload: RecordBrandsPatchRequest) -> DataRecord | None:
    if payload.edited_by not in USERS:
        raise ValueError(f"Unknown editor: {payload.edited_by}")
    cleaned = []
    for brand in payload.brands:
        normalized = brand.strip()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    for record in [*RECORDS, *RISK_RECORDS]:
        if record.id == record_id:
            record.brands = cleaned[:5]
            record.brand_detected = "、".join(record.brands)
            return deepcopy(record)
    return None
