import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function titleCase(value: string) {
  return value
    .replaceAll("_", " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function scoreColor(score?: number | null) {
  if (score == null) return "text-ink/50";
  if (score >= 76) return "text-coral";
  if (score >= 61) return "text-amber";
  return "text-teal";
}

