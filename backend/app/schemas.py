from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import CampaignStatus, CRMStage, JobStatus, LeadPriority, MessageChannel
from app.services.normalization import normalize_url


class Actor(BaseModel):
    id: str = "system"
    name: str = "system"
    role: str = "system"


class CampaignBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    country: str = Field(min_length=2, max_length=120)
    city: str = Field(min_length=1, max_length=120)
    industry: str = Field(min_length=2, max_length=160)
    target_leads: int = Field(default=100, ge=1, le=100_000)
    service_focus: str = Field(default="Website Redesign + SEO", max_length=240)
    priority: str = Field(default="medium", max_length=40)
    currency: str = Field(default="INR", min_length=2, max_length=12)
    source_config: dict[str, Any] = Field(default_factory=dict)


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    country: str | None = Field(default=None, min_length=2, max_length=120)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    industry: str | None = Field(default=None, min_length=2, max_length=160)
    target_leads: int | None = Field(default=None, ge=1, le=100_000)
    service_focus: str | None = Field(default=None, max_length=240)
    priority: str | None = Field(default=None, max_length=40)
    status: CampaignStatus | None = None
    currency: str | None = Field(default=None, min_length=2, max_length=12)
    source_config: dict[str, Any] | None = None


class CampaignRead(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime


class CampaignStatusUpdate(BaseModel):
    status: CampaignStatus


class LeadBase(BaseModel):
    business_name: str = Field(min_length=1, max_length=240)
    website_url: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=80)
    email: str | None = Field(default=None, max_length=180)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    industry: str | None = Field(default=None, max_length=160)
    google_rating: float | None = None
    review_count: int | None = None
    address: str | None = None
    source_url: str | None = Field(default=None, max_length=500)
    source: str = Field(default="manual", max_length=80)
    social_links: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None

    @field_validator("website_url")
    @classmethod
    def normalize_website(cls, value: str | None) -> str | None:
        return normalize_url(value) if value else value


class LeadCreate(LeadBase):
    campaign_id: str


class LeadUpdate(BaseModel):
    business_name: str | None = Field(default=None, min_length=1, max_length=240)
    website_url: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=80)
    email: str | None = Field(default=None, max_length=180)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    industry: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    owner_id: str | None = Field(default=None, max_length=120)
    owner_name: str | None = Field(default=None, max_length=180)
    crm_stage: CRMStage | None = None

    @field_validator("website_url")
    @classmethod
    def normalize_website(cls, value: str | None) -> str | None:
        return normalize_url(value) if value else value


class LeadRead(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    normalized_domain: str | None
    dedupe_key: str
    contactability_score: int
    business_value_score: int
    industry_priority_score: int
    location_priority_score: int
    ai_closing_probability: int | None
    website_score: int | None
    final_lead_score: int | None
    priority_category: LeadPriority | None
    crm_stage: CRMStage
    owner_id: str | None
    owner_name: str | None
    is_duplicate: bool
    created_at: datetime
    updated_at: datetime


class CSVImportSummary(BaseModel):
    campaign_id: str
    imported: int
    duplicates: int
    skipped: int
    lead_ids: list[str]


class GooglePlacesDiscoveryRequest(BaseModel):
    campaign_id: str
    limit: int = Field(default=50, ge=1, le=500)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str | None
    lead_id: str | None
    job_type: str
    status: JobStatus
    progress_percent: int
    current_step: str | None
    error: str | None
    result: dict[str, Any]
    retry_count: int
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ScreenshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    viewport: str
    storage_url: str
    width: int | None
    height: int | None


class WebsiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    final_url: str | None
    title: str | None
    meta_description: str | None
    headings: dict[str, Any]
    links: dict[str, Any]
    images: dict[str, Any]
    forms: dict[str, Any]
    cta_buttons: dict[str, Any]
    tech_stack: dict[str, Any]
    raw_metrics: dict[str, Any]
    screenshots: list[ScreenshotRead] = []


class AuditScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    score: int
    max_score: int
    notes: str | None


class WebsiteAuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    website_id: str | None
    total_score: int
    lead_priority: LeadPriority
    problem_summary: str
    raw_checks: dict[str, Any]
    created_at: datetime
    scores: list[AuditScoreRead] = []


class AIReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    audit_id: str | None
    website_score: int
    problem_summary: str
    business_risk: str
    improvement_opportunities: list[Any]
    recommended_service: str
    estimated_project_value: str
    outreach_angle: str
    closing_probability: int
    raw_response: dict[str, Any]
    prompt_version: str
    model_name: str | None
    input_snapshot: dict[str, Any]
    output_schema_version: str
    token_usage: dict[str, Any]
    cost_metadata: dict[str, Any]
    failure_details: dict[str, Any]
    created_at: datetime


class LeadAuditDetail(BaseModel):
    lead: LeadRead
    campaign: CampaignRead | None = None
    website: WebsiteRead | None = None
    audit: WebsiteAuditRead | None = None
    ai_report: AIReportRead | None = None
    outreach_messages: list["OutreachMessageRead"] = []
    proposals: list["ProposalRead"] = []
    crm_activities: list["CRMActivityRead"] = []
    jobs: list[JobRead] = []
    enrichments: list["EnrichmentRecordRead"] = []


class AuditRunResponse(BaseModel):
    job: JobRead
    message: str


class OutreachGenerateRequest(BaseModel):
    channels: list[MessageChannel] = Field(
        default_factory=lambda: [
            MessageChannel.email,
            MessageChannel.whatsapp,
            MessageChannel.linkedin,
            MessageChannel.follow_up,
            MessageChannel.call_script,
            MessageChannel.proposal_summary,
        ]
    )


class OutreachMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    ai_report_id: str | None
    channel: MessageChannel
    subject: str | None
    body: str
    status: str
    created_by_id: str | None
    created_by_name: str | None
    created_at: datetime


class CRMStageUpdate(BaseModel):
    stage: CRMStage
    note: str | None = None


class CRMActivityCreate(BaseModel):
    activity_type: str = Field(min_length=2, max_length=80)
    note: str = Field(min_length=1)
    next_follow_up_at: datetime | None = None


class CRMActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    activity_type: str
    note: str
    from_stage: str | None
    to_stage: str | None
    actor_id: str | None
    actor_name: str | None
    actor_role: str | None
    next_follow_up_at: datetime | None
    created_at: datetime


class PipelineColumn(BaseModel):
    stage: CRMStage
    leads: list[LeadRead]
    count: int
    total_score: int


class ProposalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    ai_report_id: str | None
    title: str
    summary: str
    estimated_value: str
    currency: str
    status: str
    pdf_url: str | None
    content: dict[str, Any]
    approved_at: datetime | None
    archived_at: datetime | None
    created_by_id: str | None
    created_by_name: str | None
    created_at: datetime


class ProposalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=240)
    summary: str | None = None
    estimated_value: str | None = Field(default=None, max_length=120)
    status: str | None = Field(default=None, max_length=60)
    content: dict[str, Any] | None = None


class EnrichmentRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lead_id: str
    source: str
    signals: dict[str, Any]
    confidence: float | None
    created_at: datetime


class CampaignDetail(BaseModel):
    campaign: CampaignRead
    metrics: dict[str, Any]
    leads: list[LeadRead]
    jobs: list[JobRead]


class DashboardOverview(BaseModel):
    campaigns: dict[str, Any]
    leads: dict[str, Any]
    audits: dict[str, Any]
    crm: dict[str, Any]
    proposals: dict[str, Any]
    sales: dict[str, Any]


LeadAuditDetail.model_rebuild()

