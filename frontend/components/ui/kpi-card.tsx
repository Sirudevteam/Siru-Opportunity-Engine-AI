import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function KpiCard({
  label,
  value,
  detail,
  icon,
  accent = "teal"
}: {
  label: string;
  value: string | number;
  detail: string;
  icon: ReactNode;
  accent?: "teal" | "amber" | "coral" | "blue";
}) {
  const colors = {
    teal: "bg-lavender text-teal",
    amber: "bg-amber/10 text-amber",
    coral: "bg-coral/10 text-coral",
    blue: "bg-blue/10 text-blue"
  };
  return (
    <section className="rounded-lg border border-line bg-panel p-4 shadow-panel">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-semibold text-ink/65">{label}</p>
        <span className={cn("grid h-9 w-9 place-items-center rounded-md", colors[accent])}>{icon}</span>
      </div>
      <p className="mt-4 text-3xl font-bold tracking-normal">{value}</p>
      <p className="mt-1 text-sm font-medium text-ink/60">{detail}</p>
    </section>
  );
}
