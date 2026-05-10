"use client";

import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, ClipboardCheck, FileText, Megaphone, Search, Trophy } from "lucide-react";
import { api } from "@/lib/api";
import { scoreColor, titleCase } from "@/lib/utils";
import type { DashboardOverview, Lead } from "@/types";
import { KpiCard } from "./ui/kpi-card";
import { StatusBadge } from "./ui/status-badge";

export function DashboardOverviewScreen() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    void Promise.all([api.overview(), api.leads()])
      .then(([overviewData, leadData]) => {
        setOverview(overviewData);
        setLeads(leadData);
        setError("");
      })
      .catch(() => {
        setOverview(null);
        setLeads([]);
        setError("Unable to load dashboard data. Check the backend connection and refresh.");
      });
  }, []);

  const priorityData = useMemo(() => {
    const counts = overview?.leads.priority_counts ?? {};
    return ["very_hot", "hot", "warm", "low_priority"].map((priority) => ({
      priority: titleCase(priority),
      count: counts[priority] ?? 0
    }));
  }, [overview]);

  const trendData = overview
    ? [{ period: "Current", leads: overview.leads.total, audits: overview.audits.completed }]
    : [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Command Center</h1>
          <p className="mt-1 text-sm text-ink/60">Campaigns, audits, pipeline, proposals, and sales movement.</p>
        </div>
      </div>
      {error ? <div className="rounded-md border border-line bg-panel p-3 text-sm text-ink/60">{error}</div> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <KpiCard
          label="Campaigns"
          value={overview?.campaigns.total ?? 0}
          detail={`${overview?.campaigns.running ?? 0} running`}
          icon={<Megaphone size={18} />}
        />
        <KpiCard
          label="Leads"
          value={overview?.leads.total ?? 0}
          detail={`${overview?.leads.audited ?? 0} audited`}
          icon={<Search size={18} />}
          accent="blue"
        />
        <KpiCard
          label="Avg Score"
          value={overview?.leads.average_final_score ?? 0}
          detail="final lead score"
          icon={<Activity size={18} />}
          accent="amber"
        />
        <KpiCard
          label="Audits"
          value={overview?.audits.completed ?? 0}
          detail="completed"
          icon={<ClipboardCheck size={18} />}
        />
        <KpiCard
          label="Proposals"
          value={overview?.proposals.total ?? 0}
          detail="drafted"
          icon={<FileText size={18} />}
          accent="blue"
        />
        <KpiCard
          label="Won"
          value={overview?.crm.won ?? 0}
          detail={`${overview?.sales.conversion_rate ?? 0}% conversion`}
          icon={<Trophy size={18} />}
          accent="coral"
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.35fr_0.65fr]">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Acquisition Movement</h2>
            <span className="text-xs text-ink/55">Current totals</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ left: -20, right: 10, top: 10, bottom: 0 }}>
                <CartesianGrid stroke="#e6e8ef" vertical={false} />
                <XAxis dataKey="period" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Area type="monotone" dataKey="leads" stroke="#062bff" fill="#062bff" fillOpacity={0.12} />
                <Area type="monotone" dataKey="audits" stroke="#8b90ff" fill="#8b90ff" fillOpacity={0.18} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold">Lead Heat</h2>
            <span className="text-xs text-ink/55">Website priority</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priorityData} margin={{ left: -20, right: 10, top: 10, bottom: 0 }}>
                <CartesianGrid stroke="#e6e8ef" vertical={false} />
                <XAxis dataKey="priority" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#062bff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-panel">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-base font-semibold">Top Opportunities</h2>
          <span className="text-xs text-ink/55">Sorted by final lead score</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="bg-ink/[0.03] text-xs uppercase text-ink/55">
              <tr>
                <th className="px-4 py-3">Business</th>
                <th className="px-4 py-3">Market</th>
                <th className="px-4 py-3">Website</th>
                <th className="px-4 py-3">Lead</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">CRM</th>
              </tr>
            </thead>
            <tbody>
              {leads.length ? (
                [...leads]
                  .sort((a, b) => (b.final_lead_score ?? 0) - (a.final_lead_score ?? 0))
                  .slice(0, 6)
                  .map((lead) => (
                    <tr key={lead.id} className="border-t border-line">
                      <td className="px-4 py-3 font-medium">{lead.business_name}</td>
                      <td className="px-4 py-3 text-ink/65">
                        {lead.city}, {lead.country}
                      </td>
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
                  <td className="px-4 py-6 text-sm text-ink/45" colSpan={6}>
                    No opportunities found.
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
