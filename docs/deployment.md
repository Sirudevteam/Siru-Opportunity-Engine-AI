# Deployment

The platform is cloud-agnostic and is intended to run from manually managed backend, worker, frontend, database, queue, object storage, and vector-store services.

## Services

- `frontend`: Next.js dashboard module.
- `backend`: FastAPI API service.
- `worker`: Celery worker for long-running jobs.
- PostgreSQL or SQLite: structured database.
- Redis: Celery queue/result backend.
- Qdrant: vector database.
- S3-compatible storage: screenshots and generated PDFs.

## Production Checklist

- Use managed PostgreSQL or a backed-up database service.
- Run Alembic migrations during deployment. Set `AUTO_CREATE_TABLES=false` in production.
- Use managed Redis or a persistent Redis deployment.
- Configure an S3-compatible bucket and private credentials for screenshots and generated PDFs.
- Configure object storage lifecycle retention for screenshots and generated PDFs.
- Set `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`, and `GOOGLE_PLACES_API_KEY`.
- Route the backend behind the existing Siru dashboard auth boundary.
- Configure `SIRU_AUTH_SIGNATURE_SECRET` and forward signed `X-Siru-*` headers from the parent dashboard.
- Run a dedicated Celery worker service. API routes dispatch long-running work to Celery and return tracked jobs.
- Add HTTPS, request logging, Sentry, metrics, and backups.

## Key Environment Variables

- `DATABASE_URL`: SQLAlchemy database URL.
- `REDIS_URL`: Celery broker/result backend.
- `CELERY_TASK_ALWAYS_EAGER`: set to `true` only for local development without Redis.
- `CELERY_TASK_TIME_LIMIT_SECONDS`: Celery task hard time limit.
- `AUTO_CREATE_TABLES`: set to `false` in production when using migrations.
- `SIRU_AUTH_SIGNATURE_SECRET`: shared HMAC secret for signed dashboard requests.
- `SIRU_AUTH_SIGNATURE_TOLERANCE_SECONDS`: timestamp tolerance for signatures.
- `OPENAI_API_KEY`: required for AI report generation and embeddings.
- `OPENAI_MODEL`: model used for structured AI reports.
- `OPENAI_EMBEDDING_MODEL`: model used for Qdrant audit embeddings.
- `GOOGLE_PLACES_API_KEY`: required for Google Places discovery.
- `OBJECT_STORAGE_*`: endpoint, bucket, credentials, and public base URL for screenshots and PDFs.
- `QDRANT_URL` and `QDRANT_COLLECTION`: vector store configuration.

## Migrations

The repository includes Alembic configuration under `backend/alembic.ini` and `backend/migrations`.

Recommended production flow:

```bash
cd backend
alembic upgrade head
```

Local development may keep `AUTO_CREATE_TABLES=true` for quick starts, but production should rely on Alembic migrations.

## Manual Runtime Commands

Backend:

```bash
cd backend
python -m pip install ".[dev]"
uvicorn app.main:app --reload
```

Worker:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=INFO
```

Local no-Redis mode:

```bash
CELERY_TASK_ALWAYS_EAGER=true
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Manual service expectations:

- Backend can start with SQLite only.
- Normal job dispatch needs Redis and the Celery worker.
- Audit screenshots/PDFs need S3-compatible storage for durable artifact URLs.
- Embedding indexing needs Qdrant plus OpenAI.
- AI report generation needs OpenAI.
- Google Places discovery needs Google Places.

