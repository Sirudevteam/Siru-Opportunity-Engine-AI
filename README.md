# Siru Opportunity Engine AI

Siru Opportunity Engine AI is Siru's private AI-powered global client acquisition engine. It discovers businesses, audits their websites, scores opportunity quality, generates outreach and proposals, and tracks conversion through an internal CRM pipeline.

This repository is a self-contained internal module designed to be mounted or linked from an existing Siru dashboard. It intentionally does not include standalone login screens or public signup.

## What Is Included

- Next.js internal dashboard module for campaigns, leads, audits, CRM, proposals, and reports.
- FastAPI backend with campaign, lead, audit, AI, outreach, CRM, export, and reporting APIs.
- Celery worker task entrypoints for Google Places discovery, crawling, analysis, AI reports, outreach, proposals, and PDFs.
- Manual runtime configuration for the backend, worker, frontend, Redis, Qdrant, and S3-compatible storage.
- Alembic migration scaffold for production schema management.
- Playwright-based website crawling with HTTP fallback for local development.
- Deterministic scoring heuristics plus OpenAI-powered structured AI summaries and embeddings.
- Signed Siru dashboard request verification when `SIRU_AUTH_SIGNATURE_SECRET` is configured.

## Quick Start

Copy the environment template:

```bash
cp .env.example .env
```

Install and run the backend manually:

```bash
cd backend
python -m pip install ".[dev]"
uvicorn app.main:app --reload
```

The backend starts at `http://localhost:8000`. Check it with:

```text
http://localhost:8000/health
http://localhost:8000/ready
```

For quick local reads and manual record creation, SQLite works out of the box through `DATABASE_URL=sqlite:///./siru.db`. Long-running jobs need Redis and a worker. If Redis is running locally, open another terminal and start the worker:

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=INFO
```

If you do not want to run Redis during local development, set `CELERY_TASK_ALWAYS_EAGER=true` in `.env` so Celery tasks execute in-process.

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:3000` and expects the backend at `http://localhost:8000/api/v1`. If the backend is unavailable, dashboard screens show empty states or connection errors instead of synthetic data. The production build uses system fonts and does not fetch Google Fonts at build time.

## Manual Service Notes

- Redis is required for normal asynchronous job dispatch.
- Qdrant is optional for local development; embedding indexing fails silently when unavailable.
- S3-compatible storage is optional for local development; without object storage credentials, generated files are stored through the local fallback behavior in the storage service.
- OpenAI is required for AI reports and embeddings. Missing OpenAI configuration creates failed AI jobs instead of fallback sales content.
- Google Places discovery requires `GOOGLE_PLACES_API_KEY`.

## Repository Layout

```text
backend/   FastAPI app, database models, services, worker tasks, tests
frontend/  Next.js dashboard module
docs/      Architecture, API, scoring, and deployment notes
workers/   Worker ownership notes and runtime entrypoint docs
```

## Authentication Boundary

This module assumes the existing Siru dashboard owns user identity. When `SIRU_AUTH_SIGNATURE_SECRET` is configured, every `/api/v1/*` request must include signed Siru headers. Local development may omit the secret to run without signature enforcement.

- `X-Siru-User-Id`
- `X-Siru-User-Name`
- `X-Siru-Role`
- `X-Siru-Timestamp`
- `X-Siru-Signature`

The signature payload is:

```text
METHOD
/api/v1/path
X-Siru-Timestamp
X-Siru-User-Id
X-Siru-Role
```

`X-Siru-Signature` is the hex HMAC-SHA256 of that payload using `SIRU_AUTH_SIGNATURE_SECRET`. The backend enforces read, operate, and manage role groups for sensitive endpoints.

