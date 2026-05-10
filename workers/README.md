# Workers

The worker runtime lives in `backend/app/workers`. It exposes Celery tasks for:

- `discover_google_places`
- `crawl_website`
- `analyze_website`
- `generate_ai_report`
- `generate_outreach`
- `generate_pdf`

API routes create tracked `crawl_jobs` records and dispatch long-running work to Celery. Job records expose status, progress percent, current step, retry count, result, and error details.

`POST /api/v1/audits/leads/{lead_id}/run` still supports `?inline=true` for local audit debugging. Production deployments should run the dedicated Celery worker service and use normal asynchronous dispatch.

## Manual Local Run

Start Redis first, then run:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=INFO
```

For local development without Redis, set `CELERY_TASK_ALWAYS_EAGER=true` before starting the backend. This runs dispatched tasks in the backend process and is not recommended for production.

