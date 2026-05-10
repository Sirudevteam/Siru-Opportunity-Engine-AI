from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def uuid_str() -> str:
    return str(uuid.uuid4())


class CampaignStatus(str, Enum):
    draft = "draft"
    running = "running"
    completed = "completed"
    paused = "paused"
    failed = "failed"


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class CRMStage(str, Enum):
    new_lead = "new_lead"
    qualified = "qualified"
    audit_ready = "audit_ready"
    contacted = "contacted"
    follow_up_1 = "follow_up_1"
    follow_up_2 = "follow_up_2"
    interested = "interested"
    meeting_booked = "meeting_booked"
    proposal_sent = "proposal_sent"
    negotiation = "negotiation"
    won = "won"
    lost = "lost"


class LeadPriority(str, Enum):
    very_hot = "very_hot"
    hot = "hot"
    warm = "warm"
    low_priority = "low_priority"


class MessageChannel(str, Enum):
    email = "email"
    whatsapp = "whatsapp"
    linkedin = "linkedin"
    follow_up = "follow_up"
    call_script = "call_script"
    proposal_summary = "proposal_summary"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    industry: Mapped[str] = mapped_column(String(160), nullable=False)
    target_leads: Mapped[int] = mapped_column(Integer, default=100)
    service_focus: Mapped[str] = mapped_column(String(240), default="Website Redesign + SEO")
    priority: Mapped[str] = mapped_column(String(40), default="medium")
    status: Mapped[CampaignStatus] = mapped_column(String(40), default=CampaignStatus.draft.value)
    currency: Mapped[str] = mapped_column(String(12), default="INR")
    source_config: Mapped[dict] = mapped_column(JSON, default=dict)

    leads: Mapped[list[Lead]] = relationship(
        back_populates="campaign", cascade="all, delete-orphan"
    )


class Lead(TimestampMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (UniqueConstraint("campaign_id", "dedupe_key", name="uq_lead_campaign_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    business_name: Mapped[str] = mapped_column(String(240), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(500))
    normalized_domain: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(80))
    email: Mapped[str | None] = mapped_column(String(180))
    city: Mapped[str | None] = mapped_column(String(120))
    country: Mapped[str | None] = mapped_column(String(120))
    industry: Mapped[str | None] = mapped_column(String(160))
    google_rating: Mapped[float | None] = mapped_column(Float)
    review_count: Mapped[int | None] = mapped_column(Integer)
    address: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(80), default="csv")
    social_links: Mapped[dict] = mapped_column(JSON, default=dict)
    dedupe_key: Mapped[str] = mapped_column(String(320), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    contactability_score: Mapped[int] = mapped_column(Integer, default=50)
    business_value_score: Mapped[int] = mapped_column(Integer, default=50)
    industry_priority_score: Mapped[int] = mapped_column(Integer, default=70)
    location_priority_score: Mapped[int] = mapped_column(Integer, default=70)
    ai_closing_probability: Mapped[int | None] = mapped_column(Integer)
    website_score: Mapped[int | None] = mapped_column(Integer)
    final_lead_score: Mapped[int | None] = mapped_column(Integer)
    priority_category: Mapped[str | None] = mapped_column(String(40))

    crm_stage: Mapped[CRMStage] = mapped_column(String(60), default=CRMStage.new_lead.value)
    owner_id: Mapped[str | None] = mapped_column(String(120))
    owner_name: Mapped[str | None] = mapped_column(String(180))
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)

    campaign: Mapped[Campaign] = relationship(back_populates="leads")
    websites: Mapped[list[Website]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    audits: Mapped[list[WebsiteAudit]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    ai_reports: Mapped[list[AIReport]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    outreach_messages: Mapped[list[OutreachMessage]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    crm_activities: Mapped[list[CRMActivity]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )
    proposals: Mapped[list[Proposal]] = relationship(
        back_populates="lead", cascade="all, delete-orphan"
    )


class Website(TimestampMixin, Base):
    __tablename__ = "websites"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    final_url: Mapped[str | None] = mapped_column(String(500))
    title: Mapped[str | None] = mapped_column(String(500))
    meta_description: Mapped[str | None] = mapped_column(Text)
    html_excerpt: Mapped[str | None] = mapped_column(Text)
    headings: Mapped[dict] = mapped_column(JSON, default=dict)
    links: Mapped[dict] = mapped_column(JSON, default=dict)
    images: Mapped[dict] = mapped_column(JSON, default=dict)
    forms: Mapped[dict] = mapped_column(JSON, default=dict)
    cta_buttons: Mapped[dict] = mapped_column(JSON, default=dict)
    tech_stack: Mapped[dict] = mapped_column(JSON, default=dict)
    raw_metrics: Mapped[dict] = mapped_column(JSON, default=dict)

    lead: Mapped[Lead] = relationship(back_populates="websites")
    screenshots: Mapped[list[Screenshot]] = relationship(
        back_populates="website", cascade="all, delete-orphan"
    )
    audits: Mapped[list[WebsiteAudit]] = relationship(back_populates="website")


class Screenshot(TimestampMixin, Base):
    __tablename__ = "screenshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    website_id: Mapped[str] = mapped_column(ForeignKey("websites.id"), nullable=False)
    viewport: Mapped[str] = mapped_column(String(40), nullable=False)
    storage_url: Mapped[str] = mapped_column(String(800), nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)

    website: Mapped[Website] = relationship(back_populates="screenshots")


class CrawlJob(TimestampMixin, Base):
    __tablename__ = "crawl_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    campaign_id: Mapped[str | None] = mapped_column(ForeignKey("campaigns.id"))
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id"))
    job_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[JobStatus] = mapped_column(String(40), default=JobStatus.pending.value)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[str | None] = mapped_column(String(180))
    error: Mapped[str | None] = mapped_column(Text)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WebsiteAudit(TimestampMixin, Base):
    __tablename__ = "website_audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    website_id: Mapped[str | None] = mapped_column(ForeignKey("websites.id"))
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    lead_priority: Mapped[str] = mapped_column(String(40), nullable=False)
    problem_summary: Mapped[str] = mapped_column(Text, nullable=False)
    raw_checks: Mapped[dict] = mapped_column(JSON, default=dict)

    lead: Mapped[Lead] = relationship(back_populates="audits")
    website: Mapped[Website | None] = relationship(back_populates="audits")
    scores: Mapped[list[AuditScore]] = relationship(
        back_populates="audit", cascade="all, delete-orphan"
    )
    ai_reports: Mapped[list[AIReport]] = relationship(back_populates="audit")


class AuditScore(TimestampMixin, Base):
    __tablename__ = "audit_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    audit_id: Mapped[str] = mapped_column(ForeignKey("website_audits.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    audit: Mapped[WebsiteAudit] = relationship(back_populates="scores")


class AIReport(TimestampMixin, Base):
    __tablename__ = "ai_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    audit_id: Mapped[str | None] = mapped_column(ForeignKey("website_audits.id"))
    website_score: Mapped[int] = mapped_column(Integer, nullable=False)
    problem_summary: Mapped[str] = mapped_column(Text, nullable=False)
    business_risk: Mapped[str] = mapped_column(Text, nullable=False)
    improvement_opportunities: Mapped[list] = mapped_column(JSON, default=list)
    recommended_service: Mapped[str] = mapped_column(String(240), nullable=False)
    estimated_project_value: Mapped[str] = mapped_column(String(120), nullable=False)
    outreach_angle: Mapped[str] = mapped_column(Text, nullable=False)
    closing_probability: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_response: Mapped[dict] = mapped_column(JSON, default=dict)
    prompt_version: Mapped[str] = mapped_column(String(40), default="audit-strategy-v1")
    model_name: Mapped[str | None] = mapped_column(String(120))
    input_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    output_schema_version: Mapped[str] = mapped_column(String(40), default="ai-report-v1")
    token_usage: Mapped[dict] = mapped_column(JSON, default=dict)
    cost_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    failure_details: Mapped[dict] = mapped_column(JSON, default=dict)

    lead: Mapped[Lead] = relationship(back_populates="ai_reports")
    audit: Mapped[WebsiteAudit | None] = relationship(back_populates="ai_reports")


class OutreachMessage(TimestampMixin, Base):
    __tablename__ = "outreach_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    ai_report_id: Mapped[str | None] = mapped_column(ForeignKey("ai_reports.id"))
    channel: Mapped[MessageChannel] = mapped_column(String(60), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(240))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    created_by_id: Mapped[str | None] = mapped_column(String(120))
    created_by_name: Mapped[str | None] = mapped_column(String(180))

    lead: Mapped[Lead] = relationship(back_populates="outreach_messages")


class CRMActivity(TimestampMixin, Base):
    __tablename__ = "crm_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    activity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    from_stage: Mapped[str | None] = mapped_column(String(60))
    to_stage: Mapped[str | None] = mapped_column(String(60))
    actor_id: Mapped[str | None] = mapped_column(String(120))
    actor_name: Mapped[str | None] = mapped_column(String(180))
    actor_role: Mapped[str | None] = mapped_column(String(120))
    next_follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    lead: Mapped[Lead] = relationship(back_populates="crm_activities")


class Proposal(TimestampMixin, Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    ai_report_id: Mapped[str | None] = mapped_column(ForeignKey("ai_reports.id"))
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_value: Mapped[str] = mapped_column(String(120), nullable=False)
    currency: Mapped[str] = mapped_column(String(12), default="INR")
    status: Mapped[str] = mapped_column(String(60), default="draft")
    pdf_url: Mapped[str | None] = mapped_column(String(800))
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by_id: Mapped[str | None] = mapped_column(String(120))
    created_by_name: Mapped[str | None] = mapped_column(String(180))

    lead: Mapped[Lead] = relationship(back_populates="proposals")


class EnrichmentRecord(TimestampMixin, Base):
    __tablename__ = "enrichment_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    lead_id: Mapped[str] = mapped_column(ForeignKey("leads.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    signals: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float | None] = mapped_column(Float)


class EmbeddingRecord(TimestampMixin, Base):
    __tablename__ = "embedding_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    provider: Mapped[str] = mapped_column(String(80), default="openai")
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    source_object_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_object_id: Mapped[str] = mapped_column(String(80), nullable=False)
    version: Mapped[str] = mapped_column(String(40), default="v1")
    vector_id: Mapped[str | None] = mapped_column(String(120))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

