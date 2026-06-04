from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str
    name: str
    role: str
    avatar: str


class ProjectSummary(BaseModel):
    id: str
    name: str
    client: str
    brand: str
    label_schema: str
    rule_version: str
    report_template: str
    status: str
    progress: int = Field(ge=0, le=100)
    confirmed_count: int
    total_count: int


class LabelOption(BaseModel):
    value: str
    label: str
    color: str | None = None
    parent_value: str | None = None


class LabelField(BaseModel):
    key: str
    name: str
    type: Literal["single_select", "text", "boolean"]
    options: list[LabelOption] = []
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


class DataRecord(BaseModel):
    id: str
    platform: str
    publish_time: str
    author: str
    content: str
    brand_detected: str
    labels: dict[str, LabelValue]
    report_candidate: bool = False


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
    projects: list[ProjectSummary]
    active_project: ProjectSummary
    label_schema: LabelSchema
    records: list[DataRecord]
    suggestions: list[RuleSuggestion]
    report: ReportVersion
