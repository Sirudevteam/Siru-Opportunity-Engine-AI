import React from "react";
import { cn, titleCase } from "@/lib/utils";

const colorMap: Record<string, string> = {
  running: "border-blue/20 bg-lavender text-teal",
  completed: "border-blue/20 bg-blue/10 text-blue",
  paused: "border-amber/20 bg-amber/10 text-amber",
  failed: "border-coral/20 bg-coral/10 text-coral",
  draft: "border-blue/25 bg-lavender text-teal",
  very_hot: "border-coral/20 bg-coral/10 text-coral",
  hot: "border-amber/20 bg-amber/10 text-amber",
  warm: "border-blue/20 bg-blue/10 text-blue",
  low_priority: "border-line bg-ink/5 text-ink/70",
  won: "border-mint bg-mint text-success",
  lost: "border-coral/20 bg-coral/10 text-coral"
};

export function StatusBadge({ value, className }: { value?: string | null; className?: string }) {
  if (!value) return <span className="text-sm text-ink/50">None</span>;
  return (
    <span
      className={cn(
        "inline-flex h-7 items-center rounded-md px-2 text-xs font-semibold",
        "border",
        colorMap[value] ?? "border-line bg-ink/5 text-ink/70",
        className
      )}
    >
      {titleCase(value)}
    </span>
  );
}
