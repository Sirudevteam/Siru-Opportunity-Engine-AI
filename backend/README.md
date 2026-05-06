# Backend

FastAPI backend for Siru Opportunity Engine AI.

## Local Development

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The default `DATABASE_URL` is SQLite for quick local starts. Docker Compose sets PostgreSQL.

## Useful Endpoints

- `GET /health`
- `GET /api/v1/reports/overview`
- `POST /api/v1/campaigns`
- `POST /api/v1/leads/import`
- `POST /api/v1/audits/leads/{lead_id}/run`

