"use client";

import type { AuditJob } from "@/types";
import { StatusBadge } from "./ui/status-badge";

export function JobProgress({ jobs }: { jobs: AuditJob[] }) {
  if (!jobs.length) {
    return <div className="rounded-md border border-dashed border-line p-6 text-sm text-ink/45">No jobs yet.</div>;
  }
  return (
    <div className="space-y-3">
      {jobs.map((job) => (
        <article key={job.id} className="rounded-md border border-line p-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold">{job.job_type}</p>
              <p className="mt-1 text-xs text-ink/55">{job.current_step ?? job.id}</p>
            </div>
            <StatusBadge value={job.status} />
          </div>
          <div className="mt-3 h-2 rounded-sm bg-ink/10">
            <div className="h-2 rounded-sm bg-teal" style={{ width: `${job.progress_percent}%` }} />
          </div>
          {job.error ? <p className="mt-2 text-xs text-red-600">{job.error}</p> : null}
        </article>
      ))}
    </div>
  );
}
