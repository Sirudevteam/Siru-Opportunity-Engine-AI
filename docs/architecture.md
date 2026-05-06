# Architecture

Siru Opportunity Engine AI is an internal growth platform, not a SaaS product. It is built as a mountable module for Siru's existing dashboard and keeps the acquisition workflow in one place: campaign setup, lead discovery, website audit, AI rating, outreach, CRM movement, proposal generation, and reporting.

## Runtime Components

- Frontend: Next.js dashboard module with operational screens for Siru teams.
- Backend: FastAPI API gateway for campaigns, leads, audits, AI, outreach, CRM, exports, and reports.
- Worker: Celery tasks for long-running discovery, crawl, analysis, AI, outreach, and PDF jobs.
- Database: PostgreSQL for structured records.
- Cache and queue: Redis for Celery broker/result backend and lightweight cache.
- Object storage: S3-compatible bucket for screenshots and generated PDFs.
- Vector database: Qdrant for website content and audit embeddings.

## Request Flow

1. Existing Siru dashboard links or mounts the frontend module.
2. Frontend calls the FastAPI backend with optional `X-Siru-*` attribution headers.
3. Campaigns define country, city, industry, lead target, service focus, priority, and currency.
4. Lead discovery imports CSV files or calls Google Places.
5. Leads are normalized, deduplicated, and assigned CRM status.
6. Website crawl jobs capture desktop/mobile evidence and extract HTML signals.
7. The analyzer calculates category scores and total website quality.
8. The AI engine creates structured business risk, opportunity, package, deal, and outreach guidance.
9. CRM and proposal workflows turn the audit into manual sales action.

## Data Ownership

The platform owns acquisition data. It does not own Siru user identity. When the parent dashboard passes a user ID/name/role, that attribution is recorded on activities, generated messages, proposals, and audit logs.

## Operational Defaults

- Outreach is generated and tracked, not automatically sent.
- Google Places and CSV are the only v1 discovery sources.
- Missing API keys produce explicit failed jobs or deterministic fallback content.
- Development can use SQLite fallback, but Docker Compose runs PostgreSQL.

