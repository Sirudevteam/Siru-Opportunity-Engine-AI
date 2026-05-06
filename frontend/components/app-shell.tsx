"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  ClipboardCheck,
  FileText,
  KanbanSquare,
  LayoutDashboard,
  Megaphone,
  Search,
  Settings2
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/campaigns", label: "Campaigns", icon: Megaphone },
  { href: "/leads", label: "Leads", icon: Search },
  { href: "/audits", label: "Audits", icon: ClipboardCheck },
  { href: "/crm", label: "CRM", icon: KanbanSquare },
  { href: "/proposals", label: "Proposals", icon: FileText },
  { href: "/reports", label: "Reports", icon: BarChart3 }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-paper">
      <aside className="fixed inset-y-0 left-0 hidden w-60 border-r border-line bg-panel lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-line px-5">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-teal text-sm font-bold text-white shadow-[0_8px_18px_rgba(6,43,255,0.18)]">
            S
          </div>
          <div>
            <p className="text-sm font-bold">Siru</p>
            <p className="text-xs font-medium text-ink/55">Opportunity Engine AI</p>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "focus-ring flex h-11 items-center gap-3 rounded-md border border-transparent px-3 text-sm font-semibold text-ink/70 transition",
                  active
                    ? "border-blue/10 bg-lavender text-teal"
                    : "hover:border-line hover:bg-ink/[0.025] hover:text-ink"
                )}
              >
                <Icon size={18} aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-60">
        <header className="sticky top-0 z-20 border-b border-line bg-panel/95 px-4 shadow-[0_4px_18px_rgba(15,23,42,0.035)] backdrop-blur lg:px-8">
          <div className="flex h-16 items-center justify-between gap-3">
            <div>
              <p className="text-sm font-bold">Siru Opportunity Engine AI</p>
              <p className="text-xs font-medium text-ink/55">Private client acquisition module</p>
            </div>
            <div className="flex items-center gap-2 rounded-md border border-line bg-panel px-3 py-2 text-xs font-semibold text-ink/65">
              <Settings2 size={16} aria-hidden="true" />
              Internal
            </div>
          </div>
          <nav className="flex gap-2 overflow-x-auto pb-3 lg:hidden">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "focus-ring inline-flex h-10 shrink-0 items-center gap-2 rounded-md border px-3 text-sm font-semibold",
                    active ? "border-blue/10 bg-lavender text-teal" : "border-line bg-panel"
                  )}
                >
                  <Icon size={16} aria-hidden="true" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-7xl px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
