"use client";

import type {
  AuditJob,
  Campaign,
  CampaignDetail,
  DashboardOverview,
  Lead,
  LeadDetail,
  OutreachMessage,
  PipelineColumn,
  Proposal
} from "@/types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export const api = {
  overview: () => request<DashboardOverview>("/reports/overview"),
  campaigns: () => request<Campaign[]>("/campaigns"),
  campaignDetail: (campaignId: string) => request<CampaignDetail>(`/campaigns/${campaignId}/detail`),
  createCampaign: (payload: Partial<Campaign>) =>
    request<Campaign>("/campaigns", { method: "POST", body: JSON.stringify(payload) }),
  leads: () => request<Lead[]>("/leads"),
  leadDetail: (leadId: string) => request<LeadDetail>(`/leads/${leadId}/detail`),
  createLead: (payload: Partial<Lead>) =>
    request<Lead>("/leads", { method: "POST", body: JSON.stringify(payload) }),
  importLeads: async (campaignId: string, file: File) => {
    const form = new FormData();
    form.append("campaign_id", campaignId);
    form.append("file", file);
    const response = await fetch(`${API_BASE}/leads/import`, { method: "POST", body: form });
    if (!response.ok) throw new Error(await response.text());
    return response.json() as Promise<{
      campaign_id: string;
      imported: number;
      duplicates: number;
      skipped: number;
      lead_ids: string[];
    }>;
  },
  discoverGooglePlaces: (campaignId: string, limit: number) =>
    request<AuditJob>("/leads/discover/google-places", {
      method: "POST",
      body: JSON.stringify({ campaign_id: campaignId, limit })
    }),
  runAudit: (leadId: string) =>
    request<{ job: AuditJob; message: string }>(`/audits/leads/${leadId}/run`, {
      method: "POST"
    }),
  pipeline: () => request<PipelineColumn[]>("/crm/pipeline"),
  moveStage: (leadId: string, stage: string) =>
    request(`/crm/leads/${leadId}/stage`, {
      method: "POST",
      body: JSON.stringify({ stage })
    }),
  generateOutreach: (leadId: string) =>
    request<AuditJob>(`/outreach/leads/${leadId}/generate`, {
      method: "POST",
      body: JSON.stringify({})
    }),
  outreach: (leadId: string) => request<OutreachMessage[]>(`/outreach/leads/${leadId}`),
  generateProposal: (leadId: string) =>
    request<AuditJob>(`/proposals/leads/${leadId}/generate`, { method: "POST" }),
  proposals: () => request<Proposal[]>("/proposals"),
  updateProposal: (proposalId: string, payload: Partial<Proposal>) =>
    request<Proposal>(`/proposals/${proposalId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  approveProposal: (proposalId: string) => request<Proposal>(`/proposals/${proposalId}/approve`, { method: "POST" }),
  archiveProposal: (proposalId: string) => request<Proposal>(`/proposals/${proposalId}/archive`, { method: "POST" }),
  regenerateProposalPdf: (proposalId: string) =>
    request<Proposal>(`/proposals/${proposalId}/regenerate-pdf`, { method: "POST" }),
  job: (jobId: string) => request<AuditJob>(`/audits/jobs/${jobId}`)
};
