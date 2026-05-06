import type { Campaign, DashboardOverview, Lead, PipelineColumn, Proposal } from "@/types";

export const mockCampaigns: Campaign[] = [
  {
    id: "campaign-dubai-dental",
    name: "Dubai Dental Website Audit",
    country: "UAE",
    city: "Dubai",
    industry: "Dental Clinics",
    target_leads: 500,
    service_focus: "Website Redesign + Local SEO",
    priority: "high",
    status: "running",
    currency: "INR",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "campaign-singapore-spa",
    name: "Singapore Wellness Clinics",
    country: "Singapore",
    city: "Singapore",
    industry: "Wellness Clinics",
    target_leads: 220,
    service_focus: "Conversion Website Refresh",
    priority: "medium",
    status: "draft",
    currency: "INR",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

export const mockLeads: Lead[] = [
  {
    id: "lead-1",
    campaign_id: "campaign-dubai-dental",
    business_name: "Pearl Smile Dental",
    website_url: "https://pearlsmile.example",
    phone: "+971555123456",
    email: "hello@pearlsmile.example",
    city: "Dubai",
    country: "UAE",
    industry: "Dental Clinics",
    google_rating: 4.4,
    review_count: 96,
    website_score: 38,
    final_lead_score: 79,
    priority_category: "very_hot",
    crm_stage: "audit_ready",
    owner_name: "Siru Sales",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "lead-2",
    campaign_id: "campaign-dubai-dental",
    business_name: "Marina Dental Care",
    website_url: "https://marinadental.example",
    phone: "+971555987654",
    city: "Dubai",
    country: "UAE",
    industry: "Dental Clinics",
    google_rating: 4.1,
    review_count: 42,
    website_score: 57,
    final_lead_score: 69,
    priority_category: "hot",
    crm_stage: "contacted",
    owner_name: "Siru Sales",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: "lead-3",
    campaign_id: "campaign-singapore-spa",
    business_name: "Orchard Skin Studio",
    website_url: "https://orchardskin.example",
    city: "Singapore",
    country: "Singapore",
    industry: "Wellness Clinics",
    google_rating: 4.7,
    review_count: 133,
    website_score: 72,
    final_lead_score: 64,
    priority_category: "warm",
    crm_stage: "proposal_sent",
    owner_name: "Siru Sales",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

export const mockOverview: DashboardOverview = {
  campaigns: { total: 2, running: 1 },
  leads: {
    total: 3,
    audited: 3,
    average_final_score: 70.7,
    priority_counts: { very_hot: 1, hot: 1, warm: 1, low_priority: 0 }
  },
  audits: { completed: 3 },
  crm: {
    stage_counts: {
      new_lead: 0,
      qualified: 0,
      audit_ready: 1,
      contacted: 1,
      follow_up_1: 0,
      follow_up_2: 0,
      interested: 0,
      meeting_booked: 0,
      proposal_sent: 1,
      negotiation: 0,
      won: 0,
      lost: 0
    },
    won: 0,
    lost: 0
  },
  proposals: { total: 1 },
  sales: { conversion_rate: 0, open_pipeline: 3 }
};

export const mockPipeline: PipelineColumn[] = Object.entries(mockOverview.crm.stage_counts).map(
  ([stage]) => {
    const leads = mockLeads.filter((lead) => lead.crm_stage === stage);
    return {
      stage: stage as PipelineColumn["stage"],
      leads,
      count: leads.length,
      total_score: leads.reduce((sum, lead) => sum + (lead.final_lead_score ?? 0), 0)
    };
  }
);

export const mockProposals: Proposal[] = [
  {
    id: "proposal-1",
    lead_id: "lead-3",
    title: "Conversion Website Refresh Proposal for Orchard Skin Studio",
    summary: "Mobile UX, trust signals, enquiry flow, and local SEO foundation.",
    estimated_value: "INR 50,000 - INR 150,000",
    status: "draft",
    pdf_url: null,
    created_at: new Date().toISOString()
  }
];

