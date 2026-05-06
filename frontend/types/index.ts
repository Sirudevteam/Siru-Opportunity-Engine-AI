export type CampaignStatus = "draft" | "running" | "completed" | "paused" | "failed";
export type CRMStage =
  | "new_lead"
  | "qualified"
  | "audit_ready"
  | "contacted"
  | "follow_up_1"
  | "follow_up_2"
  | "interested"
  | "meeting_booked"
  | "proposal_sent"
  | "negotiation"
  | "won"
  | "lost";

export type LeadPriority = "very_hot" | "hot" | "warm" | "low_priority";

export type Campaign = {
  id: string;
  name: string;
  country: string;
  city: string;
  industry: string;
  target_leads: number;
  service_focus: string;
  priority: string;
  status: CampaignStatus;
  currency: string;
  created_at: string;
  updated_at: string;
};

export type Lead = {
  id: string;
  campaign_id: string;
  business_name: string;
  website_url?: string | null;
  phone?: string | null;
  email?: string | null;
  city?: string | null;
  country?: string | null;
  industry?: string | null;
  google_rating?: number | null;
  review_count?: number | null;
  website_score?: number | null;
  final_lead_score?: number | null;
  priority_category?: LeadPriority | null;
  crm_stage: CRMStage;
  owner_name?: string | null;
  created_at: string;
  updated_at: string;
};

export type DashboardOverview = {
  campaigns: { total: number; running: number };
  leads: {
    total: number;
    audited: number;
    average_final_score: number;
    priority_counts: Record<string, number>;
  };
  audits: { completed: number };
  crm: { stage_counts: Record<string, number>; won: number; lost: number };
  proposals: { total: number };
  sales: { conversion_rate: number; open_pipeline: number };
};

export type PipelineColumn = {
  stage: CRMStage;
  leads: Lead[];
  count: number;
  total_score: number;
};

export type OutreachMessage = {
  id: string;
  lead_id: string;
  channel: string;
  subject?: string | null;
  body: string;
  status: string;
  created_at: string;
};

export type Proposal = {
  id: string;
  lead_id: string;
  title: string;
  summary: string;
  estimated_value: string;
  status: string;
  pdf_url?: string | null;
  created_at: string;
};

export type AuditJob = {
  id: string;
  campaign_id?: string | null;
  lead_id?: string | null;
  job_type: string;
  status: "pending" | "running" | "completed" | "failed";
  error?: string | null;
  result: Record<string, unknown>;
};

