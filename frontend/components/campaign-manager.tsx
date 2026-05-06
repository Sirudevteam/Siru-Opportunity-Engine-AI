"use client";

import { FormEvent, useEffect, useState } from "react";
import { Pause, Play, Plus, RotateCw } from "lucide-react";
import { api } from "@/lib/api";
import type { Campaign } from "@/types";
import { Button } from "./ui/button";
import { StatusBadge } from "./ui/status-badge";

const emptyCampaign = {
  name: "",
  country: "UAE",
  city: "Dubai",
  industry: "Dental Clinics",
  target_leads: 500,
  service_focus: "Website Redesign + Local SEO",
  priority: "high",
  currency: "INR"
};

export function CampaignManager() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [form, setForm] = useState(emptyCampaign);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    setCampaigns(await api.campaigns());
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await api.createCampaign(form);
      setForm(emptyCampaign);
      await refresh();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-normal">Campaigns</h1>
        <p className="mt-1 text-sm text-ink/60">Country, city, industry, target, and service focus.</p>
      </div>

      <section className="rounded-lg border border-line bg-panel p-4 shadow-panel">
        <form className="grid gap-3 lg:grid-cols-12" onSubmit={submit}>
          <label className="lg:col-span-3">
            <span className="text-xs font-semibold text-ink/60">Name</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              placeholder="Dubai Dental Website Audit"
              required
            />
          </label>
          <label className="lg:col-span-2">
            <span className="text-xs font-semibold text-ink/60">Country</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.country}
              onChange={(event) => setForm({ ...form, country: event.target.value })}
              required
            />
          </label>
          <label className="lg:col-span-2">
            <span className="text-xs font-semibold text-ink/60">City</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.city}
              onChange={(event) => setForm({ ...form, city: event.target.value })}
              required
            />
          </label>
          <label className="lg:col-span-2">
            <span className="text-xs font-semibold text-ink/60">Industry</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.industry}
              onChange={(event) => setForm({ ...form, industry: event.target.value })}
              required
            />
          </label>
          <label className="lg:col-span-1">
            <span className="text-xs font-semibold text-ink/60">Target</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              type="number"
              min={1}
              value={form.target_leads}
              onChange={(event) => setForm({ ...form, target_leads: Number(event.target.value) })}
              required
            />
          </label>
          <label className="lg:col-span-2">
            <span className="text-xs font-semibold text-ink/60">Currency</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.currency}
              onChange={(event) => setForm({ ...form, currency: event.target.value })}
              required
            />
          </label>
          <label className="lg:col-span-5">
            <span className="text-xs font-semibold text-ink/60">Service Focus</span>
            <input
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.service_focus}
              onChange={(event) => setForm({ ...form, service_focus: event.target.value })}
              required
            />
          </label>
          <label className="lg:col-span-2">
            <span className="text-xs font-semibold text-ink/60">Priority</span>
            <select
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={form.priority}
              onChange={(event) => setForm({ ...form, priority: event.target.value })}
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </label>
          <div className="flex items-end lg:col-span-5">
            <Button type="submit" disabled={saving} icon={<Plus size={16} />}>
              {saving ? "Creating" : "Create Campaign"}
            </Button>
          </div>
        </form>
      </section>

      <section className="rounded-lg border border-line bg-panel shadow-panel">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-base font-semibold">Campaign List</h2>
          <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh} title="Refresh campaigns">
            Refresh
          </Button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] text-left text-sm">
            <thead className="bg-ink/[0.03] text-xs uppercase text-ink/55">
              <tr>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Market</th>
                <th className="px-4 py-3">Industry</th>
                <th className="px-4 py-3">Target</th>
                <th className="px-4 py-3">Service</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Priority</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((campaign) => (
                <tr key={campaign.id} className="border-t border-line">
                  <td className="px-4 py-3 font-medium">{campaign.name}</td>
                  <td className="px-4 py-3 text-ink/65">
                    {campaign.city}, {campaign.country}
                  </td>
                  <td className="px-4 py-3">{campaign.industry}</td>
                  <td className="px-4 py-3">{campaign.target_leads}</td>
                  <td className="px-4 py-3 text-ink/65">{campaign.service_focus}</td>
                  <td className="px-4 py-3">
                    <StatusBadge value={campaign.status} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="inline-flex items-center gap-2">
                      {campaign.priority === "high" ? <Play size={15} /> : <Pause size={15} />}
                      {campaign.priority}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

