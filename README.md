# Siru Opportunity Engine AI

Siru Opportunity Engine AI is Siru's private AI-powered global client acquisition engine. It discovers businesses, audits their websites, scores opportunity quality, generates outreach and proposals, and tracks conversion through an internal CRM pipeline.

This repository is a self-contained internal module designed to be mounted or linked from an existing Siru dashboard. It intentionally does not include standalone login screens or public signup.

## What Is Included

- Next.js internal dashboard module for campaigns, leads, audits, CRM, proposals, and reports.
- FastAPI backend with campaign, lead, audit, AI, outreach, CRM, export, and reporting APIs.
- Celery worker task entrypoints for Google Places discovery, crawling, analysis, AI reports, outreach, and PDFs.
- PostgreSQL, Redis, Qdrant, and S3-compatible storage wiring through Docker Compose.
- Playwright-based website crawling with HTTP fallback for local development.
- Deterministic scoring heuristics plus OpenAI-powered structured AI summaries when an API key is configured.

## Quick Start

Copy the environment template:

```bash
cp .env.example .env
```

Start the full local stack with Docker:

```bash
docker compose -f infra/docker-compose.yml up --build
```

Or run the frontend only:

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:3000` and expects the backend at `http://localhost:8000/api/v1`. If the backend is unavailable, the UI falls back to demo data so dashboard screens remain usable during design and integration.

## Repository Layout

```text
backend/   FastAPI app, database models, services, worker tasks, tests
frontend/  Next.js dashboard module
infra/     Docker Compose and container build files
docs/      Architecture, API, scoring, and deployment notes
workers/   Worker ownership notes and runtime entrypoint docs
```

## Authentication Boundary

This module assumes the existing Siru dashboard handles authentication and access control. Backend endpoints accept optional attribution headers:

- `X-Siru-User-Id`
- `X-Siru-User-Name`
- `X-Siru-Role`

If absent, audit/activity records use `system`.

