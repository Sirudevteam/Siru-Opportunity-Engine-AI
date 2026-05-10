"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { FileUp, Globe2, Plus, RotateCw, Search } from "lucide-react";
import { api } from "@/lib/api";
import { scoreColor } from "@/lib/utils";
import type { Campaign, Lead } from "@/types";
import { Button } from "./ui/button";
import { StatusBadge } from "./ui/status-badge";

export function LeadWorkbench() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [campaignId, setCampaignId] = useState("");
  const [query, setQuery] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [jobMessage, setJobMessage] = useState("");
  const [error, setError] = useState("");
  const [leadForm, setLeadForm] = useState({
    business_name: "",
    website_url: "",
    phone: "",
    email: ""
  });

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    try {
      const [campaignData, leadData] = await Promise.all([api.campaigns(), api.leads()]);
      setCampaigns(campaignData);
      setLeads(leadData);
      setCampaignId((current) => current || campaignData[0]?.id || "");
      setError("");
    } catch {
      setCampaigns([]);
      setLeads([]);
      setCampaignId("");
      setError("Unable to load leads. Check the backend connection and refresh.");
    }
  }

  const filteredLeads = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return leads.filter((lead) => {
      const matchesQuery = normalized ? lead.business_name.toLowerCase().includes(normalized) : true;
      const matchesCampaign = campaignId ? lead.campaign_id === campaignId : true;
      return matchesQuery && matchesCampaign;
    });
  }, [campaignId, leads, query]);

  async function submitLead(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!campaignId) return;
    try {
      await api.createLead({
        campaign_id: campaignId,
        ...leadForm
      });
      setLeadForm({ business_name: "", website_url: "", phone: "", email: "" });
      await refresh();
      setError("");
    } catch {
      setError("Unable to add lead. Please try again after the backend completes the request.");
    }
  }

  async function importCsv() {
    if (!campaignId || !file) return;
    try {
      const result = await api.importLeads(campaignId, file);
      setJobMessage(`Imported ${result.imported}; duplicates ${result.duplicates}; skipped ${result.skipped}.`);
      setFile(null);
      await refresh();
      setError("");
    } catch {
      setError("Unable to import CSV. Please check the file and backend connection.");
    }
  }

  async function discover() {
    if (!campaignId) return;
    try {
      const job = await api.discoverGooglePlaces(campaignId, 50);
      setJobMessage(`Google Places job ${job.status}: ${job.id}`);
      setError("");
    } catch {
      setError("Unable to start Google Places discovery. Check the backend connection and API configuration.");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-normal">Leads</h1>
        <p className="mt-1 text-sm text-ink/60">Discovery, import, dedupe, and lead qualification.</p>
      </div>
      {error ? <div className="rounded-md border border-line bg-panel p-3 text-sm text-ink/60">{error}</div> : null}

      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Lead Intake</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="md:col-span-2">
              <span className="text-xs font-semibold text-ink/60">Campaign</span>
              <select
                className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
                value={campaignId}
                onChange={(event) => setCampaignId(event.target.value)}
              >
                {campaigns.map((campaign) => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="md:col-span-2">
              <span className="text-xs font-semibold text-ink/60">CSV</span>
              <input
                className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 py-2 text-sm"
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <Button variant="secondary" icon={<FileUp size={16} />} onClick={importCsv} disabled={!file}>
              Import CSV
            </Button>
            <Button variant="secondary" icon={<Globe2 size={16} />} onClick={discover} disabled={!campaignId}>
              Google Places
            </Button>
            {jobMessage ? <p className="md:col-span-2 text-sm text-ink/60">{jobMessage}</p> : null}
          </div>
        </div>

        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Manual Lead</h2>
          <form className="mt-4 grid gap-3 md:grid-cols-2" onSubmit={submitLead}>
            <label className="md:col-span-2">
              <span className="text-xs font-semibold text-ink/60">Business</span>
              <input
                className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
                value={leadForm.business_name}
                onChange={(event) => setLeadForm({ ...leadForm, business_name: event.target.value })}
                required
              />
            </label>
            <label>
              <span className="text-xs font-semibold text-ink/60">Website</span>
              <input
                className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
                value={leadForm.website_url}
                onChange={(event) => setLeadForm({ ...leadForm, website_url: event.target.value })}
              />
            </label>
            <label>
              <span className="text-xs font-semibold text-ink/60">Email</span>
              <input
                className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
                value={leadForm.email}
                onChange={(event) => setLeadForm({ ...leadForm, email: event.target.value })}
              />
            </label>
            <label>
              <span className="text-xs font-semibold text-ink/60">Phone</span>
              <input
                className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
                value={leadForm.phone}
                onChange={(event) => setLeadForm({ ...leadForm, phone: event.target.value })}
              />
            </label>
            <div className="flex items-end">
              <Button icon={<Plus size={16} />} type="submit" disabled={!campaignId}>
                Add Lead
              </Button>
            </div>
          </form>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-panel">
        <div className="flex flex-col gap-3 border-b border-line px-4 py-3 md:flex-row md:items-center md:justify-between">
          <h2 className="text-base font-semibold">Lead List</h2>
          <div className="flex gap-2">
            <label className="relative block">
              <Search className="pointer-events-none absolute left-3 top-2.5 text-ink/40" size={16} />
              <input
                className="focus-ring h-10 w-64 max-w-full rounded-md border border-line pl-9 pr-3 text-sm"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search"
              />
            </label>
            <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh} title="Refresh leads">
              Refresh
            </Button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[920px] text-left text-sm">
            <thead className="bg-ink/[0.03] text-xs uppercase text-ink/55">
              <tr>
                <th className="px-4 py-3">Business</th>
                <th className="px-4 py-3">Contact</th>
                <th className="px-4 py-3">Market</th>
                <th className="px-4 py-3">Reviews</th>
                <th className="px-4 py-3">Website</th>
                <th className="px-4 py-3">Lead</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Stage</th>
              </tr>
            </thead>
            <tbody>
              {filteredLeads.length ? (
                filteredLeads.map((lead) => (
                  <tr key={lead.id} className="border-t border-line">
                    <td className="px-4 py-3">
                      <Link className="font-medium underline-offset-2 hover:underline" href={`/leads/${lead.id}`}>
                        {lead.business_name}
                      </Link>
                      <p className="text-xs text-ink/55">{lead.website_url ?? "No website"}</p>
                    </td>
                    <td className="px-4 py-3 text-ink/65">
                      <p>{lead.email ?? "-"}</p>
                      <p>{lead.phone ?? "-"}</p>
                    </td>
                    <td className="px-4 py-3 text-ink/65">
                      {lead.city}, {lead.country}
                    </td>
                    <td className="px-4 py-3">{lead.review_count ?? 0}</td>
                    <td className={`px-4 py-3 font-semibold ${scoreColor(lead.website_score)}`}>
                      {lead.website_score ?? "-"}
                    </td>
                    <td className="px-4 py-3 font-semibold">{lead.final_lead_score ?? "-"}</td>
                    <td className="px-4 py-3">
                      <StatusBadge value={lead.priority_category} />
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge value={lead.crm_stage} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr className="border-t border-line">
                  <td className="px-4 py-6 text-sm text-ink/45" colSpan={8}>
                    No leads found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

