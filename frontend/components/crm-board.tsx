"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowRight, RotateCw } from "lucide-react";
import { api } from "@/lib/api";
import { titleCase } from "@/lib/utils";
import type { CRMStage, Lead, PipelineColumn } from "@/types";
import { Button } from "./ui/button";
import { StatusBadge } from "./ui/status-badge";

const stages: CRMStage[] = [
  "new_lead",
  "qualified",
  "audit_ready",
  "contacted",
  "follow_up_1",
  "follow_up_2",
  "interested",
  "meeting_booked",
  "proposal_sent",
  "negotiation",
  "won",
  "lost"
];

export function CRMBoard() {
  const [pipeline, setPipeline] = useState<PipelineColumn[]>([]);
  const [moving, setMoving] = useState<string | null>(null);

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    setPipeline(await api.pipeline());
  }

  const total = useMemo(() => pipeline.reduce((sum, column) => sum + column.count, 0), [pipeline]);

  async function moveLead(lead: Lead) {
    const currentIndex = stages.indexOf(lead.crm_stage);
    const nextStage = stages[Math.min(currentIndex + 1, stages.length - 1)];
    setMoving(lead.id);
    try {
      await api.moveStage(lead.id, nextStage);
      await refresh();
    } catch {
      setPipeline((columns) =>
        columns.map((column) => ({
          ...column,
          leads:
            column.stage === lead.crm_stage
              ? column.leads.filter((item) => item.id !== lead.id)
              : column.stage === nextStage
                ? [{ ...lead, crm_stage: nextStage }, ...column.leads]
                : column.leads
        }))
      );
    } finally {
      setMoving(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-normal">CRM Pipeline</h1>
          <p className="mt-1 text-sm text-ink/60">{total} active lead records across sales stages.</p>
        </div>
        <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh} title="Refresh CRM">
          Refresh
        </Button>
      </div>

      <section className="grid auto-cols-[300px] grid-flow-col gap-4 overflow-x-auto pb-4">
        {pipeline.map((column) => (
          <div key={column.stage} className="rounded-lg border border-line bg-panel shadow-panel">
            <div className="flex h-14 items-center justify-between border-b border-line px-4">
              <div>
                <h2 className="text-sm font-semibold">{titleCase(column.stage)}</h2>
                <p className="text-xs text-ink/55">Score {column.total_score}</p>
              </div>
              <span className="grid h-8 min-w-8 place-items-center rounded-md bg-ink/10 px-2 text-sm font-semibold">
                {column.count}
              </span>
            </div>
            <div className="space-y-3 p-3">
              {column.leads.length ? (
                column.leads.map((lead) => (
                  <article key={lead.id} className="rounded-md border border-line p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-sm font-semibold">{lead.business_name}</h3>
                        <p className="mt-1 text-xs text-ink/55">
                          {lead.city}, {lead.country}
                        </p>
                      </div>
                      <span className="text-sm font-semibold">{lead.final_lead_score ?? "-"}</span>
                    </div>
                    <div className="mt-3 flex items-center justify-between gap-2">
                      <StatusBadge value={lead.priority_category} />
                      {lead.crm_stage !== "won" && lead.crm_stage !== "lost" ? (
                        <Button
                          variant="ghost"
                          icon={<ArrowRight size={15} />}
                          onClick={() => moveLead(lead)}
                          disabled={moving === lead.id}
                          title="Move to next stage"
                        >
                          Move
                        </Button>
                      ) : null}
                    </div>
                  </article>
                ))
              ) : (
                <div className="rounded-md border border-dashed border-line p-6 text-sm text-ink/45">Empty</div>
              )}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

