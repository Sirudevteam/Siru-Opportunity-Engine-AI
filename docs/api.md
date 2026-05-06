# API Overview

Base path: `/api/v1`

Optional attribution headers:

- `X-Siru-User-Id`
- `X-Siru-User-Name`
- `X-Siru-Role`

## Campaigns

- `GET /campaigns` - list campaigns with filters.
- `POST /campaigns` - create campaign.
- `GET /campaigns/{campaign_id}` - campaign detail.
- `PATCH /campaigns/{campaign_id}` - update campaign.
- `POST /campaigns/{campaign_id}/status` - set status to draft, running, paused, completed, or failed.

## Leads

- `GET /leads` - list leads with campaign, status, priority, and search filters.
- `GET /leads/{lead_id}` - lead detail.
- `POST /leads/import` - import CSV leads for a campaign.
- `POST /leads/discover/google-places` - start Google Places discovery for a campaign.
- `PATCH /leads/{lead_id}` - update owner, contact fields, notes, and CRM stage.

## Audits

- `POST /audits/leads/{lead_id}/run` - start a crawl and audit job.
- `GET /audits/jobs/{job_id}` - inspect job status.
- `GET /audits/leads/{lead_id}` - fetch latest audit, scores, screenshots, and AI report.
- `POST /audits/{audit_id}/ai-report` - generate or regenerate AI report.

## Outreach And Proposals

- `POST /outreach/leads/{lead_id}/generate` - create draft email, WhatsApp, LinkedIn, follow-up, call script, and proposal summary.
- `GET /outreach/leads/{lead_id}` - list generated messages.
- `POST /proposals/leads/{lead_id}/generate` - create proposal draft and PDF artifact.
- `GET /proposals/{proposal_id}` - proposal detail.

## CRM

- `GET /crm/pipeline` - pipeline grouped by CRM stage.
- `POST /crm/leads/{lead_id}/stage` - move lead to another stage.
- `POST /crm/leads/{lead_id}/activities` - add call, note, email, WhatsApp, meeting, proposal, won, or lost activity.

## Reports And Exports

- `GET /reports/overview` - KPI summary for dashboard home.
- `GET /reports/campaigns/{campaign_id}` - campaign performance.
- `GET /exports/leads.csv` - lead CSV export.
- `GET /exports/audits.csv` - audit CSV export.
- `GET /exports/crm.csv` - CRM CSV export.

