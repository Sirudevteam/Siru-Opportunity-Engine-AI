# Backend

FastAPI backend for Siru Opportunity Engine AI.

## Local Development

```bash
pip install ".[dev]"
uvicorn app.main:app --reload
```

The default `DATABASE_URL` is SQLite for quick local starts. Local development can use automatic table creation; production should run Alembic migrations and set `AUTO_CREATE_TABLES=false`.

Health checks:

```text
http://localhost:8000/health
http://localhost:8000/ready
```

Run migrations:

```bash
alembic upgrade head
```

Run the Celery worker:

```bash
celery -A app.workers.celery_app worker --loglevel=INFO
```

The worker requires Redis at `REDIS_URL`. For local development without Redis, set `CELERY_TASK_ALWAYS_EAGER=true` so task dispatch executes in the backend process.

When `SIRU_AUTH_SIGNATURE_SECRET` is configured, `/api/v1/*` requests require signed Siru headers. Leave it unset for unsigned local development.

Optional local services:

- Qdrant at `QDRANT_URL` enables audit embedding indexing.
- S3-compatible storage via `OBJECT_STORAGE_*` stores screenshots and PDFs outside the local process.
- OpenAI powers AI report generation and embeddings.
- Google Places powers campaign discovery jobs.

## Useful Endpoints

- `GET /health`
- `GET /ready`
- `GET /api/v1/reports/overview`
- `POST /api/v1/campaigns`
- `POST /api/v1/leads/import`
- `POST /api/v1/audits/leads/{lead_id}/run`
- `GET /api/v1/leads/{lead_id}/detail`
- `GET /api/v1/campaigns/{campaign_id}/detail`

