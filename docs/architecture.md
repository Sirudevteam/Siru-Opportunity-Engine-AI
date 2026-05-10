# Architecture

Siru Opportunity Engine AI is an internal growth platform, not a SaaS product. It is built as a mountable module for Siru's existing dashboard and keeps the acquisition workflow in one place: campaign setup, lead discovery, website audit, AI rating, outreach, CRM movement, structured proposal generation, and reporting.

## Runtime Components

- Frontend: Next.js dashboard module with operational screens for Siru teams.
- Backend: FastAPI API gateway for campaigns, leads, audits, AI, outreach, CRM, exports, and reports.
- Worker: Celery tasks for long-running discovery, crawl, analysis, AI, outreach, and PDF jobs.
- Database: SQLite for quick local development or PostgreSQL for production structured records.
- Cache and queue: Redis for Celery broker/result backend and lightweight cache.
- Object storage: S3-compatible bucket for screenshots and generated PDFs.
- Vector database: Qdrant for website content and audit embeddings.
- Migrations: Alembic migration scaffold for production schema changes.

## Request Flow

1. Existing Siru dashboard links or mounts the frontend module.
2. Frontend calls the FastAPI backend with Siru attribution headers. In secured environments the parent dashboard signs requests with `X-Siru-Signature`.
3. Campaigns define country, city, industry, lead target, service focus, priority, and currency.
4. Lead discovery imports CSV files or calls Google Places.
5. Leads are normalized, deduplicated, and assigned CRM status.
6. Website crawl jobs capture desktop/mobile evidence and extract HTML signals.
7. The analyzer calculates category scores and total website quality.
8. The AI engine creates structured business risk, opportunity, package, deal, and outreach guidance. Missing or failed OpenAI configuration produces a failed job rather than production fallback content.
9. CRM and proposal workflows turn the audit into manual sales action.
10. Detail screens expose campaign metrics, lead audit evidence, AI outputs, outreach drafts, proposal drafts, CRM timeline, and job progress.

## Data Ownership

The platform owns acquisition data. It does not own Siru user identity. The parent dashboard passes user ID/name/role headers, and the backend records that attribution on CRM activities, generated messages, proposals, and audit logs.

## Authentication And Roles

When `SIRU_AUTH_SIGNATURE_SECRET` is configured, `/api/v1/*` requests require:

- `X-Siru-User-Id`
- `X-Siru-User-Name`
- `X-Siru-Role`
- `X-Siru-Timestamp`
- `X-Siru-Signature`

The signature is an HMAC-SHA256 over method, path, timestamp, user ID, and role. The backend allows unsigned API requests only when the secret is not configured, which is intended for local development.

Role groups:

- Read: `admin`, `manager`, `sales`, `operator`, `readonly`, `read_only`, `system`
- Operate: `admin`, `manager`, `sales`, `operator`, `system`
- Manage: `admin`, `manager`, `system`

## Operational Defaults

- Outreach is generated and tracked, not automatically sent.
- Google Places and CSV are the only v1 discovery sources.
- Missing OpenAI configuration produces explicit failed AI jobs in production flows.
- Development can use SQLite and automatic table creation. Production should run Alembic migrations and set `AUTO_CREATE_TABLES=false`.
- The UI does not use mock or synthetic data when the backend is unavailable.
- Normal asynchronous jobs require Redis and the Celery worker. Local development can use `CELERY_TASK_ALWAYS_EAGER=true` to run tasks in the backend process.

