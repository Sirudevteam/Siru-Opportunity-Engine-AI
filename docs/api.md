# API Overview

Base path: `/api/v1`

When `SIRU_AUTH_SIGNATURE_SECRET` is configured, all `/api/v1/*` endpoints require signed Siru dashboard headers:

- `X-Siru-User-Id`
- `X-Siru-User-Name`
- `X-Siru-Role`
- `X-Siru-Timestamp`
- `X-Siru-Signature`

Signature payload:

```text
METHOD
/api/v1/path
X-Siru-Timestamp
X-Siru-User-Id
X-Siru-Role
```

`X-Siru-Signature` is a hex HMAC-SHA256 using `SIRU_AUTH_SIGNATURE_SECRET`.

## Campaigns

- `GET /campaigns` - list campaigns with filters.
- `POST /campaigns` - create campaign.
- `GET /campaigns/{campaign_id}` - campaign record.
- `GET /campaigns/{campaign_id}/detail` - campaign metrics, leads, and jobs.
- `PATCH /campaigns/{campaign_id}` - update campaign.
- `POST /campaigns/{campaign_id}/status` - set status to draft, running, paused, completed, or failed.

## Leads

- `GET /leads` - list leads with campaign, status, priority, and search filters.
- `GET /leads/{lead_id}` - lead record.
- `GET /leads/{lead_id}/detail` - lead, campaign, latest website evidence, audit scores, AI report, outreach, proposals, CRM timeline, jobs, and enrichments.
- `POST /leads/import` - import CSV leads for a campaign.
- `POST /leads/discover/google-places` - start Google Places discovery for a campaign.
- `PATCH /leads/{lead_id}` - update owner, contact fields, notes, and CRM stage.

## Audits

- `POST /audits/leads/{lead_id}/run` - create a tracked crawl and audit job. Returns a job.
- `GET /audits/jobs/{job_id}` - inspect job status, progress, current step, result, and error.
- `GET /audits/leads/{lead_id}` - fetch latest audit, scores, screenshots, and AI report.
- `POST /audits/{audit_id}/ai-report` - create a tracked AI report job. Returns a job.

## Outreach And Proposals

- `POST /outreach/leads/{lead_id}/generate` - create a tracked job for draft email, WhatsApp, LinkedIn, follow-up, call script, and proposal summary.
- `GET /outreach/leads/{lead_id}` - list generated messages.
- `POST /proposals/leads/{lead_id}/generate` - create a tracked proposal/PDF job.
- `GET /proposals` - list proposals.
- `GET /proposals/{proposal_id}` - proposal detail.
- `PATCH /proposals/{proposal_id}` - edit structured proposal fields and content.
- `POST /proposals/{proposal_id}/approve` - approve a proposal.
- `POST /proposals/{proposal_id}/archive` - archive a proposal.
- `POST /proposals/{proposal_id}/regenerate-pdf` - rebuild and store the PDF artifact.

## CRM

- `GET /crm/pipeline` - pipeline grouped by CRM stage.
- `POST /crm/leads/{lead_id}/stage` - move lead to another stage.
- `POST /crm/leads/{lead_id}/activities` - add call, note, email, WhatsApp, meeting, proposal, won, or lost activity.
- `GET /crm/leads/{lead_id}/activities` - list CRM timeline entries for a lead.

## Reports And Exports

- `GET /reports/overview` - KPI summary for dashboard home.
- `GET /exports/leads.csv` - lead CSV export.
- `GET /exports/audits.csv` - audit CSV export.
- `GET /exports/crm.csv` - CRM CSV export.
- `GET /exports/campaigns.csv` - campaign CSV export.
- `GET /exports/proposals.csv` - proposal CSV export.

## Job Response Shape

Tracked job endpoints return:

- `id`
- `campaign_id`
- `lead_id`
- `job_type`
- `status`: `pending`, `running`, `completed`, or `failed`
- `progress_percent`
- `current_step`
- `error`
- `result`
- `retry_count`
- `created_at`, `updated_at`, `started_at`, `completed_at`

