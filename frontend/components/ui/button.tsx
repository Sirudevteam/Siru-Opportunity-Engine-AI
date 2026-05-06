import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  icon?: ReactNode;
};

export function Button({ className, variant = "primary", icon, children, ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border px-3 text-sm font-bold transition",
        "disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "border-teal bg-teal text-white shadow-[0_8px_18px_rgba(6,43,255,0.14)] hover:bg-teal/90",
        variant === "secondary" && "border-line bg-panel text-ink hover:border-teal/40 hover:text-teal",
        variant === "ghost" && "border-transparent bg-transparent text-ink hover:bg-lavender hover:text-teal",
        variant === "danger" && "border-coral bg-coral text-white hover:bg-coral/90",
        className
      )}
      {...props}
    >
      {icon}
      {children}
    </button>
  );
}
