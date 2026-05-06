"use client";

import { useEffect, useState } from "react";
import { FileText, MessageSquareText, RotateCw, Send } from "lucide-react";
import { api } from "@/lib/api";
import type { Lead, OutreachMessage, Proposal } from "@/types";
import { Button } from "./ui/button";
import { StatusBadge } from "./ui/status-badge";

export function ProposalCenter() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState("");
  const [messages, setMessages] = useState<OutreachMessage[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void refresh();
  }, []);

  async function refresh() {
    const [leadData, proposalData] = await Promise.all([api.leads(), api.proposals()]);
    setLeads(leadData);
    setProposals(proposalData);
    setSelectedLeadId((current) => current || leadData[0]?.id || "");
  }

  async function generateOutreach() {
    if (!selectedLeadId) return;
    setBusy(true);
    try {
      setMessages(await api.generateOutreach(selectedLeadId));
    } catch {
      const lead = leads.find((item) => item.id === selectedLeadId);
      setMessages([
        {
          id: "demo-message",
          lead_id: selectedLeadId,
          channel: "whatsapp",
          subject: null,
          body: `Hi, we reviewed ${lead?.business_name ?? "your business"}'s website and found a few improvements that may help increase enquiries from mobile users. Can I share the quick audit summary?`,
          status: "draft",
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setBusy(false);
    }
  }

  async function generateProposal() {
    if (!selectedLeadId) return;
    setBusy(true);
    try {
      const proposal = await api.generateProposal(selectedLeadId);
      setProposals((current) => [proposal, ...current]);
    } catch {
      const lead = leads.find((item) => item.id === selectedLeadId);
      setProposals((current) => [
        {
          id: `proposal-${Date.now()}`,
          lead_id: selectedLeadId,
          title: `Website Redesign + Local SEO Proposal for ${lead?.business_name ?? "Lead"}`,
          summary: "Mobile UX, local SEO, conversion CTAs, trust signals, and lead capture improvements.",
          estimated_value: "INR 75,000 - INR 250,000",
          status: "draft",
          pdf_url: null,
          created_at: new Date().toISOString()
        },
        ...current
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-normal">Outreach & Proposals</h1>
        <p className="mt-1 text-sm text-ink/60">Manual-send drafts, call scripts, proposal summaries, and PDFs.</p>
      </div>

      <section className="rounded-lg border border-line bg-panel p-4 shadow-panel">
        <div className="grid gap-3 md:grid-cols-[1fr_auto_auto_auto] md:items-end">
          <label>
            <span className="text-xs font-semibold text-ink/60">Lead</span>
            <select
              className="focus-ring mt-1 h-10 w-full rounded-md border border-line px-3 text-sm"
              value={selectedLeadId}
              onChange={(event) => setSelectedLeadId(event.target.value)}
            >
              {leads.map((lead) => (
                <option key={lead.id} value={lead.id}>
                  {lead.business_name}
                </option>
              ))}
            </select>
          </label>
          <Button
            variant="secondary"
            icon={<MessageSquareText size={16} />}
            onClick={generateOutreach}
            disabled={busy || !selectedLeadId}
          >
            Outreach
          </Button>
          <Button icon={<FileText size={16} />} onClick={generateProposal} disabled={busy || !selectedLeadId}>
            Proposal
          </Button>
          <Button variant="secondary" icon={<RotateCw size={16} />} onClick={refresh} title="Refresh proposals">
            Refresh
          </Button>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-line bg-panel shadow-panel">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <h2 className="text-base font-semibold">Draft Messages</h2>
            <Send size={18} className="text-teal" />
          </div>
          <div className="space-y-3 p-4">
            {messages.length ? (
              messages.map((message) => (
                <article key={message.id} className="rounded-md border border-line p-3">
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <StatusBadge value={message.channel} />
                    <span className="text-xs text-ink/55">{message.status}</span>
                  </div>
                  {message.subject ? <h3 className="mb-2 text-sm font-semibold">{message.subject}</h3> : null}
                  <p className="whitespace-pre-line text-sm leading-6 text-ink/75">{message.body}</p>
                </article>
              ))
            ) : (
              <div className="rounded-md border border-dashed border-line p-6 text-sm text-ink/45">No drafts</div>
            )}
          </div>
        </div>

        <div className="rounded-lg border border-line bg-panel shadow-panel">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <h2 className="text-base font-semibold">Proposal Drafts</h2>
            <FileText size={18} className="text-blue" />
          </div>
          <div className="space-y-3 p-4">
            {proposals.map((proposal) => (
              <article key={proposal.id} className="rounded-md border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-semibold">{proposal.title}</h3>
                    <p className="mt-1 text-sm text-ink/65">{proposal.summary}</p>
                  </div>
                  <StatusBadge value={proposal.status} />
                </div>
                <div className="mt-3 flex items-center justify-between text-sm">
                  <span className="font-semibold">{proposal.estimated_value}</span>
                  {proposal.pdf_url ? (
                    <a className="text-teal underline" href={proposal.pdf_url}>
                      PDF
                    </a>
                  ) : (
                    <span className="text-ink/45">PDF pending</span>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

