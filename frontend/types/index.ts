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
  content: Record<string, unknown>;
  approved_at?: string | null;
  archived_at?: string | null;
  created_at: string;
};

export type AuditJob = {
  id: string;
  campaign_id?: string | null;
  lead_id?: string | null;
  job_type: string;
  status: "pending" | "running" | "completed" | "failed";
  progress_percent: number;
  current_step?: string | null;
  error?: string | null;
  result: Record<string, unknown>;
  retry_count: number;
};

export type WebsiteAudit = {
  id: string;
  lead_id: string;
  website_id?: string | null;
  total_score: number;
  lead_priority: LeadPriority;
  problem_summary: string;
  raw_checks: Record<string, unknown>;
  scores: { id: string; category: string; score: number; max_score: number; notes?: string | null }[];
  created_at: string;
};

export type WebsiteEvidence = {
  id: string;
  url: string;
  final_url?: string | null;
  title?: string | null;
  meta_description?: string | null;
  headings: Record<string, unknown>;
  links: Record<string, unknown>;
  images: Record<string, unknown>;
  forms: Record<string, unknown>;
  cta_buttons: Record<string, unknown>;
  tech_stack: Record<string, unknown>;
  raw_metrics: Record<string, unknown>;
  screenshots: { id: string; viewport: string; storage_url: string; width?: number | null; height?: number | null }[];
};

export type AIReport = {
  id: string;
  lead_id: string;
  audit_id?: string | null;
  website_score: number;
  problem_summary: string;
  business_risk: string;
  improvement_opportunities: unknown[];
  recommended_service: string;
  estimated_project_value: string;
  outreach_angle: string;
  closing_probability: number;
  raw_response: Record<string, unknown>;
  prompt_version: string;
  model_name?: string | null;
  input_snapshot: Record<string, unknown>;
  output_schema_version: string;
  token_usage: Record<string, unknown>;
  cost_metadata: Record<string, unknown>;
  failure_details: Record<string, unknown>;
  created_at: string;
};

export type CRMActivity = {
  id: string;
  lead_id: string;
  activity_type: string;
  note: string;
  from_stage?: string | null;
  to_stage?: string | null;
  actor_id?: string | null;
  actor_name?: string | null;
  actor_role?: string | null;
  next_follow_up_at?: string | null;
  created_at: string;
};

export type LeadDetail = {
  lead: Lead;
  campaign?: Campaign | null;
  website?: WebsiteEvidence | null;
  audit?: WebsiteAudit | null;
  ai_report?: AIReport | null;
  outreach_messages: OutreachMessage[];
  proposals: Proposal[];
  crm_activities: CRMActivity[];
  jobs: AuditJob[];
  enrichments: unknown[];
};

export type CampaignDetail = {
  campaign: Campaign;
  metrics: Record<string, unknown>;
  leads: Lead[];
  jobs: AuditJob[];
};

