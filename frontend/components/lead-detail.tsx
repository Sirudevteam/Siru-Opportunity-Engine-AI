"use client";

import { useCallback, useEffect, useState } from "react";
import { FileText, MessageSquareText, RotateCw, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { scoreColor, titleCase } from "@/lib/utils";
import type { LeadDetail } from "@/types";
import { Button } from "./ui/button";
import { JobProgress } from "./job-progress";
import { StatusBadge } from "./ui/status-badge";

export function LeadDetailScreen({ leadId }: { leadId: string }) {
  const [detail, setDetail] = useState<LeadDetail | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setDetail(await api.leadDetail(leadId));
      setError("");
    } catch {
      setDetail(null);
      setError("Unable to load lead detail.");
    }
  }, [leadId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function startJob(action: "audit" | "outreach" | "proposal") {
    setBusy(true);
    try {
      if (action === "audit") await api.runAudit(leadId);
      if (action === "outreach") await api.generateOutreach(leadId);
      if (action === "proposal") await api.generateProposal(leadId);
      await refresh();
    } catch {
      setError(`Unable to start ${action}.`);
    } finally {
      setBusy(false);
    }
  }

  if (error && !detail) return <div className="rounded-md border border-line bg-panel p-4 text-sm">{error}</div>;
  if (!detail) return <div className="rounded-md border border-line bg-panel p-4 text-sm text-ink/55">Loading lead...</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">{detail.lead.business_name}</h1>
          <p className="mt-1 text-sm text-ink/60">
            {detail.lead.city ?? "-"}, {detail.lead.country ?? "-"} · {detail.campaign?.name ?? "No campaign"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh}>
            Refresh
          </Button>
          <Button variant="secondary" icon={<Zap size={16} />} disabled={busy} onClick={() => startJob("audit")}>
            Audit
          </Button>
          <Button
            variant="secondary"
            icon={<MessageSquareText size={16} />}
            disabled={busy}
            onClick={() => startJob("outreach")}
          >
            Outreach
          </Button>
          <Button icon={<FileText size={16} />} disabled={busy} onClick={() => startJob("proposal")}>
            Proposal
          </Button>
        </div>
      </div>
      {error ? <div className="rounded-md border border-line bg-panel p-3 text-sm text-ink/60">{error}</div> : null}

      <section className="grid gap-4 md:grid-cols-4">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <p className="text-xs font-semibold text-ink/55">Website</p>
          <p className={`mt-2 text-2xl font-semibold ${scoreColor(detail.lead.website_score)}`}>
            {detail.lead.website_score ?? "-"}
          </p>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <p className="text-xs font-semibold text-ink/55">Lead Score</p>
          <p className="mt-2 text-2xl font-semibold">{detail.lead.final_lead_score ?? "-"}</p>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <p className="text-xs font-semibold text-ink/55">Priority</p>
          <div className="mt-3">
            <StatusBadge value={detail.lead.priority_category} />
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <p className="text-xs font-semibold text-ink/55">CRM</p>
          <div className="mt-3">
            <StatusBadge value={detail.lead.crm_stage} />
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Audit</h2>
          {detail.audit ? (
            <div className="mt-3 space-y-3 text-sm">
              <p className="text-ink/70">{detail.audit.problem_summary}</p>
              {detail.audit.scores.map((score) => (
                <div key={score.id} className="flex justify-between border-t border-line pt-2">
                  <span>{titleCase(score.category)}</span>
                  <span className="font-semibold">
                    {score.score}/{score.max_score}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-ink/45">No audit yet.</p>
          )}
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">AI Report</h2>
          {detail.ai_report ? (
            <div className="mt-3 space-y-2 text-sm text-ink/70">
              <p>{detail.ai_report.business_risk}</p>
              <p className="font-semibold">{detail.ai_report.recommended_service}</p>
              <p>{detail.ai_report.estimated_project_value}</p>
            </div>
          ) : (
            <p className="mt-3 text-sm text-ink/45">No AI report yet.</p>
          )}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">Outreach</h2>
          <div className="mt-3 space-y-3">
            {detail.outreach_messages.map((message) => (
              <article key={message.id} className="rounded-md border border-line p-3 text-sm">
                <StatusBadge value={message.channel} />
                <p className="mt-2 text-ink/70">{message.body}</p>
              </article>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="text-base font-semibold">CRM Timeline</h2>
          <div className="mt-3 space-y-3">
            {detail.crm_activities.map((activity) => (
              <article key={activity.id} className="rounded-md border border-line p-3 text-sm">
                <p className="font-semibold">{titleCase(activity.activity_type)}</p>
                <p className="mt-1 text-ink/65">{activity.note}</p>
              </article>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-line bg-panel p-4 shadow-panel">
          <h2 className="mb-3 text-base font-semibold">Jobs</h2>
          <JobProgress jobs={detail.jobs} />
        </div>
      </section>
    </div>
  );
}
