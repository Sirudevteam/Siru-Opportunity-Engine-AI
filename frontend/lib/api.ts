"use client";

import type {
  AuditJob,
  Campaign,
  DashboardOverview,
  Lead,
  OutreachMessage,
  PipelineColumn,
  Proposal
} from "@/types";
import { mockCampaigns, mockLeads, mockOverview, mockPipeline, mockProposals } from "./mock-data";

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

export async function safeRequest<T>(path: string, fallback: T, init?: RequestInit): Promise<T> {
  try {
    return await request<T>(path, init);
  } catch {
    return fallback;
  }
}

export const api = {
  overview: () => safeRequest<DashboardOverview>("/reports/overview", mockOverview),
  campaigns: () => safeRequest<Campaign[]>("/campaigns", mockCampaigns),
  createCampaign: (payload: Partial<Campaign>) =>
    request<Campaign>("/campaigns", { method: "POST", body: JSON.stringify(payload) }),
  leads: () => safeRequest<Lead[]>("/leads", mockLeads),
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
  pipeline: () => safeRequest<PipelineColumn[]>("/crm/pipeline", mockPipeline),
  moveStage: (leadId: string, stage: string) =>
    request(`/crm/leads/${leadId}/stage`, {
      method: "POST",
      body: JSON.stringify({ stage })
    }),
  generateOutreach: (leadId: string) =>
    request<OutreachMessage[]>(`/outreach/leads/${leadId}/generate`, {
      method: "POST",
      body: JSON.stringify({})
    }),
  generateProposal: (leadId: string) =>
    request<Proposal>(`/proposals/leads/${leadId}/generate`, { method: "POST" }),
  proposals: () => safeRequest<Proposal[]>("/proposals", mockProposals)
};
