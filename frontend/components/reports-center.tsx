"use client";

import { useEffect, useMemo, useState } from "react";
import { Download, PieChart, RotateCw } from "lucide-react";
import { Cell, Pie, PieChart as RePieChart, ResponsiveContainer, Tooltip } from "recharts";
import { API_BASE, api } from "@/lib/api";
import { titleCase } from "@/lib/utils";
import type { DashboardOverview } from "@/types";
import { Button } from "./ui/button";
import { KpiCard } from "./ui/kpi-card";

const colors = ["#062bff", "#8b90ff", "#d97706", "#10885f", "#dc2626", "#070b16"];

export function ReportsCenter() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    try {
      setOverview(await api.overview());
      setError("");
    } catch {
      setOverview(null);
      setError("Unable to load reports. Check the backend connection and refresh.");
    }
  }

  const stageData = useMemo(() => {
    const counts = overview?.crm.stage_counts ?? {};
    return Object.entries(counts)
      .filter(([, count]) => count > 0)
      .map(([name, value]) => ({ name: titleCase(name), value }));
  }, [overview]);

  const exports = [
    ["Leads", "/exports/leads.csv"],
    ["Audits", "/exports/audits.csv"],
    ["CRM", "/exports/crm.csv"],
    ["Campaigns", "/exports/campaigns.csv"],
    ["Proposals", "/exports/proposals.csv"]
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">Reports</h1>
          <p className="mt-1 text-sm text-ink/60">Campaign performance, lead quality, pipeline, and exports.</p>
        </div>
        <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh} title="Refresh reports">
          Refresh
        </Button>
      </div>
      {error ? <div className="rounded-md border border-line bg-panel p-3 text-sm text-ink/60">{error}</div> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Open Pipeline"
          value={overview?.sales.open_pipeline ?? 0}
          detail="active opportunities"
          icon={<PieChart size={18} />}
        />
        <KpiCard
          label="Won"
          value={overview?.crm.won ?? 0}
          detail={`${overview?.sales.conversion_rate ?? 0}% conversion`}
          icon={<PieChart size={18} />}
          accent="blue"
        />
        <KpiCard
          label="Very Hot"
          value={overview?.leads.priority_counts.very_hot ?? 0}
          detail="website score 0-40"
          icon={<PieChart size={18} />}
          accent="coral"
        />
        <KpiCard
          label="Audited"
          value={overview?.leads.audited ?? 0}
          detail="completed audits"
          icon={<PieChart size={18} />}
          accent="amber"
        />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_0.8fr]">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Pipeline Distribution</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RePieChart>
                <Pie data={stageData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={120} paddingAngle={2}>
                  {stageData.map((entry, index) => (
                    <Cell key={entry.name} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </RePieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Exports</h2>
          <div className="mt-4 grid gap-3">
            {exports.map(([label, path]) => (
              <a
                key={path}
                className="focus-ring flex h-12 items-center justify-between rounded-md border border-line px-3 text-sm font-medium hover:border-teal/50"
                href={`${API_BASE}${path}`}
              >
                {label}
                <Download size={16} />
              </a>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
