# Deployment

The platform is cloud-agnostic. The included Docker Compose stack is suitable for local development and can be adapted to any container runtime.

## Services

- `frontend`: Next.js dashboard module.
- `backend`: FastAPI API service.
- `worker`: Celery worker for long-running jobs.
- `postgres`: PostgreSQL database.
- `redis`: Redis queue/cache.
- `qdrant`: Vector database.
- `minio`: S3-compatible object storage.

## Production Checklist

- Use managed PostgreSQL or a backed-up database service.
- Use managed Redis or a persistent Redis deployment.
- Replace local MinIO with an S3-compatible bucket and private credentials.
- Configure object storage lifecycle retention for screenshots and generated PDFs.
- Set `OPENAI_API_KEY` and `GOOGLE_PLACES_API_KEY`.
- Route the backend behind the existing Siru dashboard auth boundary.
- Forward `X-Siru-*` attribution headers from the parent dashboard.
- Add HTTPS, request logging, Sentry, metrics, and backups.

