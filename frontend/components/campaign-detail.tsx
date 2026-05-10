"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { RotateCw } from "lucide-react";
import { api } from "@/lib/api";
import { titleCase } from "@/lib/utils";
import type { CampaignDetail } from "@/types";
import { JobProgress } from "./job-progress";
import { Button } from "./ui/button";
import { StatusBadge } from "./ui/status-badge";

export function CampaignDetailScreen({ campaignId }: { campaignId: string }) {
  const [detail, setDetail] = useState<CampaignDetail | null>(null);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      setDetail(await api.campaignDetail(campaignId));
      setError("");
    } catch {
      setDetail(null);
      setError("Unable to load campaign detail.");
    }
  }, [campaignId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  if (error && !detail) return <div className="rounded-md border border-line bg-panel p-4 text-sm">{error}</div>;
  if (!detail) return <div className="rounded-md border border-line bg-panel p-4 text-sm text-ink/55">Loading...</div>;

  const stageCounts = (detail.metrics.stage_counts ?? {}) as Record<string, number>;
  const sourceCounts = (detail.metrics.source_counts ?? {}) as Record<string, number>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">{detail.campaign.name}</h1>
          <p className="mt-1 text-sm text-ink/60">
            {detail.campaign.city}, {detail.campaign.country} · {detail.campaign.industry}
          </p>
        </div>
        <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh}>
          Refresh
        </Button>
      </div>

      <section className="grid gap-4 md:grid-cols-4">
        <Metric label="Leads" value={Number(detail.metrics.total_leads ?? 0)} />
        <Metric label="Audited" value={Number(detail.metrics.audited_leads ?? 0)} />
        <Metric label="Audit Rate" value={`${detail.metrics.audit_completion_rate ?? 0}%`} />
        <Metric label="Open Jobs" value={Number(detail.metrics.open_jobs ?? 0)} />
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Stage Funnel</h2>
          <div className="mt-3 space-y-2">
            {Object.entries(stageCounts)
              .filter(([, count]) => count > 0)
              .map(([stage, count]) => (
                <div key={stage} className="flex items-center justify-between text-sm">
                  <span>{titleCase(stage)}</span>
                  <span className="font-semibold">{count}</span>
                </div>
              ))}
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Sources</h2>
          <div className="mt-3 space-y-2">
            {Object.entries(sourceCounts).map(([source, count]) => (
              <div key={source} className="flex items-center justify-between text-sm">
                <span>{titleCase(source)}</span>
                <span className="font-semibold">{count}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="mb-3 text-base font-semibold">Jobs</h2>
          <JobProgress jobs={detail.jobs.slice(0, 5)} />
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-panel">
        <div className="border-b border-line px-4 py-3">
          <h2 className="text-base font-semibold">Campaign Leads</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-ink/[0.03] text-xs uppercase text-ink/55">
              <tr>
                <th className="px-4 py-3">Business</th>
                <th className="px-4 py-3">Score</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Stage</th>
              </tr>
            </thead>
            <tbody>
              {detail.leads.map((lead) => (
                <tr key={lead.id} className="border-t border-line">
                  <td className="px-4 py-3">
                    <Link href={`/leads/${lead.id}`} className="font-medium underline-offset-2 hover:underline">
                      {lead.business_name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 font-semibold">{lead.final_lead_score ?? "-"}</td>
                  <td className="px-4 py-3">
                    <StatusBadge value={lead.priority_category} />
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge value={lead.crm_stage} />
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

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
      <p className="text-xs font-semibold text-ink/55">{label}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}
