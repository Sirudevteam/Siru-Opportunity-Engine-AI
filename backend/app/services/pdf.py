from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.models import AIReport, Lead, Proposal, WebsiteAudit


def build_audit_pdf(lead: Lead, audit: WebsiteAudit, ai_report: AIReport | None = None) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 56
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, y, "Siru Website Audit Summary")
    y -= 34
    pdf.setFont("Helvetica", 11)
    for line in [
        f"Business: {lead.business_name}",
        f"Website: {lead.website_url or 'Not available'}",
        f"Score: {audit.total_score}/100",
        f"Priority: {audit.lead_priority.replace('_', ' ').title()}",
        "",
        "Problem Summary:",
        audit.problem_summary,
    ]:
        y = draw_wrapped(pdf, line, 48, y, width - 96)
    if ai_report:
        for line in [
            "",
            "Recommended Service:",
            ai_report.recommended_service,
            "",
            "Estimated Project Value:",
            ai_report.estimated_project_value,
            "",
            "Outreach Angle:",
            ai_report.outreach_angle,
        ]:
            y = draw_wrapped(pdf, line, 48, y, width - 96)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def build_proposal_pdf(proposal: Proposal, lead: Lead) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 56
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, y, proposal.title)
    y -= 34
    pdf.setFont("Helvetica", 11)
    for line in [
        f"Prepared for: {lead.business_name}",
        f"Estimated value: {proposal.estimated_value}",
        "",
        "Summary:",
        proposal.summary,
        "",
        "Recommended Work:",
        ", ".join(proposal.content.get("recommended_work", [])),
    ]:
        y = draw_wrapped(pdf, line, 48, y, width - 96)
    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def draw_wrapped(pdf: canvas.Canvas, text: str, x: int, y: float, max_width: float) -> float:
    if not text:
        return y - 14
    words = text.split()
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if pdf.stringWidth(candidate, "Helvetica", 11) > max_width:
            pdf.drawString(x, y, line)
            y -= 14
            line = word
        else:
            line = candidate
    if line:
        pdf.drawString(x, y, line)
        y -= 14
    return y

