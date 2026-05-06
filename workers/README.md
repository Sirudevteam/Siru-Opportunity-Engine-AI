# Workers

The worker runtime lives in `backend/app/workers`. It exposes Celery tasks for:

- `discover_google_places`
- `crawl_website`
- `analyze_website`
- `generate_ai_report`
- `generate_outreach`
- `generate_pdf`

The backend can also run small jobs inline through FastAPI background tasks for local development. Production deployments should run the dedicated Celery worker service.

