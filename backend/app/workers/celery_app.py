from celery import Celery

from app.core.config import get_settings
from app.services.jobs import (
    run_audit_job,
    run_ai_report_job,
    run_google_places_job,
    run_outreach_job,
    run_proposal_job,
)

settings = get_settings()

celery_app = Celery(
    "siru_opportunity_engine",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    task_always_eager=settings.celery_task_always_eager,
    task_time_limit=settings.celery_task_time_limit_seconds,
    task_soft_time_limit=max(settings.celery_task_time_limit_seconds - 30, 30),
)


@celery_app.task(name="discover_google_places", autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def discover_google_places_task(job_id: str, limit: int = 50) -> None:
    run_google_places_job(job_id, limit)


@celery_app.task(name="crawl_website", autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def crawl_website_task(job_id: str) -> None:
    run_audit_job(job_id)


@celery_app.task(name="analyze_website", autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def analyze_website_task(job_id: str) -> None:
    run_audit_job(job_id)


@celery_app.task(name="generate_ai_report", autoretry_for=(Exception,), retry_backoff=True, max_retries=1)
def generate_ai_report_task(job_id: str, audit_id: str | None = None) -> None:
    run_ai_report_job(job_id, audit_id)


@celery_app.task(name="generate_outreach", autoretry_for=(Exception,), retry_backoff=True, max_retries=1)
def generate_outreach_task(
    job_id: str, channels: list[str] | None = None, actor_payload: dict | None = None
) -> None:
    run_outreach_job(job_id, channels, actor_payload)


@celery_app.task(name="generate_pdf", autoretry_for=(Exception,), retry_backoff=True, max_retries=1)
def generate_pdf_task(job_id: str, actor_payload: dict | None = None) -> None:
    run_proposal_job(job_id, actor_payload)
