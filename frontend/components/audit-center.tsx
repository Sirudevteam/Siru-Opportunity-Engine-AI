"use client";

import { useEffect, useState } from "react";
import { ClipboardCheck, MonitorSmartphone, RotateCw, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { scoreColor } from "@/lib/utils";
import type { AuditJob, Lead } from "@/types";
import { Button } from "./ui/button";
import { StatusBadge } from "./ui/status-badge";

const scoreRows = [
  ["UI/UX Design", 20],
  ["Mobile Responsiveness", 15],
  ["Page Speed", 15],
  ["SEO Basics", 15],
  ["Conversion / CTA", 15],
  ["Trust Signals", 10],
  ["Technology Modernity", 10]
] as const;

export function AuditCenter() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [jobs, setJobs] = useState<AuditJob[]>([]);
  const [busyLead, setBusyLead] = useState<string | null>(null);

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    setLeads(await api.leads());
  }

  async function runAudit(lead: Lead) {
    setBusyLead(lead.id);
    try {
      const response = await api.runAudit(lead.id);
      setJobs((current) => [response.job, ...current].slice(0, 8));
      await refresh();
    } finally {
      setBusyLead(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-normal">Audits</h1>
        <p className="mt-1 text-sm text-ink/60">Crawler jobs, website signals, scoring, and evidence capture.</p>
      </div>

      <section className="grid gap-4 lg:grid-cols-[0.7fr_1.3fr]">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Score Model</h2>
            <MonitorSmartphone size={18} className="text-teal" />
          </div>
          <div className="mt-4 space-y-3">
            {scoreRows.map(([label, value]) => (
              <div key={label}>
                <div className="mb-1 flex justify-between text-sm">
                  <span>{label}</span>
                  <span className="font-semibold">{value}</span>
                </div>
                <div className="h-2 rounded-sm bg-ink/10">
                  <div className="h-2 rounded-sm bg-teal" style={{ width: `${value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-base font-semibold">Recent Jobs</h2>
            <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh} title="Refresh audit leads">
              Refresh
            </Button>
          </div>
          <div className="grid gap-2">
            {jobs.length ? (
              jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between rounded-md border border-line p-3">
                  <div>
                    <p className="text-sm font-medium">{job.job_type}</p>
                    <p className="text-xs text-ink/55">{job.id}</p>
                  </div>
                  <StatusBadge value={job.status} />
                </div>
              ))
            ) : (
              <div className="rounded-md border border-line p-6 text-sm text-ink/55">No jobs in this session.</div>
            )}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-panel">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-base font-semibold">Audit Queue</h2>
          <span className="text-xs text-ink/55">Playwright with HTTP fallback</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-sm">
            <thead className="bg-ink/[0.03] text-xs uppercase text-ink/55">
              <tr>
                <th className="px-4 py-3">Business</th>
                <th className="px-4 py-3">Website</th>
                <th className="px-4 py-3">Score</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Stage</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {leads.map((lead) => (
                <tr key={lead.id} className="border-t border-line">
                  <td className="px-4 py-3 font-medium">{lead.business_name}</td>
                  <td className="px-4 py-3 text-ink/65">{lead.website_url ?? "-"}</td>
                  <td className={`px-4 py-3 font-semibold ${scoreColor(lead.website_score)}`}>
                    {lead.website_score ?? "-"}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge value={lead.priority_category} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge value={lead.crm_stage} />
                  </td>
                  <td className="px-4 py-3">
                    <Button
                      variant="secondary"
                      icon={lead.website_score == null ? <Zap size={16} /> : <ClipboardCheck size={16} />}
                      onClick={() => runAudit(lead)}
                      disabled={!lead.website_url || busyLead === lead.id}
                      title="Run audit"
                    >
                      {busyLead === lead.id ? "Running" : "Audit"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

