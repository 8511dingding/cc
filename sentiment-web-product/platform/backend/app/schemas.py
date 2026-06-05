from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str
    name: str
    role: str
    avatar: str
    status: Literal["active", "invited", "disabled"] = "active"


class ProjectSummary(BaseModel):
    id: str
    name: str
    client: str
    brand: str
    description: str = ""
    objective: str = ""
    platforms: list[str] = Field(default_factory=list)
    created_at: str
    date_range: str
    delivery_due: str = ""
    updated_at: str
    owner: UserProfile
    label_schema: str
    rule_version: str
    report_template: str
    export_pattern: str = "{project}_{date}_{version}_{format}"
    priority: Literal["高", "中", "低"] = "中"
    status: str
    progress: int = Field(ge=0, le=100)
    confirmed_count: int
    total_count: int


class ProjectUpsertRequest(BaseModel):
    name: str
    client: str
    brand: str
    description: str = ""
    objective: str = ""
    platforms: list[str] = Field(default_factory=list)
    date_range: str
    delivery_due: str = ""
    owner_id: str = "u-001"
    label_schema: str = "A2 三层标签体系"
    rule_version: str = "v1.0"
    report_template: str = "默认报告模板"
    export_pattern: str = "{project}_{date}_{version}_{format}"
    priority: Literal["高", "中", "低"] = "中"
    status: str = "项目配置中"


class LabelOption(BaseModel):
    value: str
    label: str
    color: str | None = None
    parent_value: str | None = None


class LabelField(BaseModel):
    key: str
    name: str
    type: Literal["single_select", "text", "boolean"]
    options: list[LabelOption] = Field(default_factory=list)
    parent_key: str | None = None
    visible_in_grid: bool = True


class LabelSchema(BaseModel):
    id: str
    name: str
    version: str
    fields: list[LabelField]


class LabelValue(BaseModel):
    auto: str | None = None
    manual: str | None = None
    final: str | None = None
    confirmed: bool = False
    confirmed_by: UserProfile | None = None
    confirmed_at: datetime | None = None
    previous_value: str | None = None


class CommentEngagement(BaseModel):
    likes: int = 0
    replies: int = 0


class SourceContentMeta(BaseModel):
    id: str | None = None
    url: str | None = None
    author: str | None = None
    publish_time: str | None = None
    title: str | None = None
    topics: list[str] = Field(default_factory=list)
    comments: int = 0
    likes: int = 0
    favorites: int = 0
    shares: int = 0


class DataRecord(BaseModel):
    id: str
    platform: str
    publish_time: str
    author: str
    content: str
    comment_type: Literal["长评论", "提及竞品", "普通内容", "@他人", "符号表情"] = "普通内容"
    engagement: CommentEngagement = Field(default_factory=CommentEngagement)
    brand_detected: str = ""
    brands: list[str] = Field(default_factory=list, max_length=5)
    matched_keywords: list[str] = Field(default_factory=list)
    source_content: SourceContentMeta = Field(default_factory=SourceContentMeta)
    labels: dict[str, LabelValue]
    report_candidate: bool = False


class RecordReportPatchRequest(BaseModel):
    report_candidate: bool
    edited_by: str = "u-001"


class RecordBrandsPatchRequest(BaseModel):
    brands: list[str] = Field(default_factory=list, max_length=5)
    edited_by: str = "u-001"


class LabelPatch(BaseModel):
    field_key: str
    value: str | None
    confirmed: bool = False


class RecordPatchRequest(BaseModel):
    updates: list[LabelPatch] = Field(min_length=1, max_length=20)
    edited_by: str = "u-001"


class RuleSuggestion(BaseModel):
    id: str
    title: str
    summary: str
    suggestion_type: str
    evidence_count: int
    keywords: list[str]
    status: Literal["pending", "accepted", "ignored"] = "pending"


class ImportJob(BaseModel):
    id: str
    filename: str
    status: Literal["mapped", "importing", "ready", "failed"]
    total_rows: int
    valid_rows: int
    invalid_rows: int
    created_at: str
    owner: UserProfile


class ImportFieldMapping(BaseModel):
    source: str
    target: str
    required: bool = False
    confidence: int = Field(ge=0, le=100)
    sample: str = ""


class ImportQualityIssue(BaseModel):
    rule: str
    count: int
    description: str
    action: str
    enabled: bool = True


class ImportPreviewResponse(BaseModel):
    filename: str
    sheet_name: str
    total_rows: int
    headers: list[str]
    mappings: list[ImportFieldMapping]
    quality_issues: list[ImportQualityIssue]
    samples: list[dict[str, str]]
    inferred_platform: str
    duplicate_comment_ids: int = 0
    long_comments: int = 0
    brand_mentions: dict[str, int] = Field(default_factory=dict)


class BrandRule(BaseModel):
    id: str
    brand: str
    category: str
    aliases: list[str]
    products: list[str]
    typo_variants: list[str]
    competitor: bool = False
    enabled: bool = True


class RuleSet(BaseModel):
    id: str
    name: str
    layer: str
    version: str
    rule_count: int
    last_updated: str
    editable: bool = True


class ReportTemplate(BaseModel):
    id: str
    name: str
    version: str
    sections: list[str]
    formats: list[Literal["docx", "pdf", "pptx"]]
    updated_at: str


class ExportPreset(BaseModel):
    id: str
    name: str
    pattern: str
    formats: list[Literal["xlsx", "docx", "pdf", "pptx"]]


class ExportRecord(BaseModel):
    id: str
    filename: str
    format: Literal["xlsx", "docx", "pdf", "pptx"]
    status: Literal["ready", "exporting", "failed"]
    report_version: str
    created_at: str
    size: str
    owner: UserProfile


class ReportBlock(BaseModel):
    id: str
    title: str
    block_type: Literal["text", "chart", "table", "samples"]
    content: str


class ReportVersion(BaseModel):
    id: str
    project_id: str
    title: str
    version: str
    status: str
    blocks: list[ReportBlock]


class DashboardResponse(BaseModel):
    user: UserProfile
    users: list[UserProfile]
    projects: list[ProjectSummary]
    active_project: ProjectSummary
    label_schema: LabelSchema
    records: list[DataRecord]
    imports: list[ImportJob]
    brand_rules: list[BrandRule]
    rule_sets: list[RuleSet]
    suggestions: list[RuleSuggestion]
    report_templates: list[ReportTemplate]
    export_presets: list[ExportPreset]
    export_records: list[ExportRecord]
    report: ReportVersion
