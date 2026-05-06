from __future__ import annotations

from app.models import AIReport, Lead, MessageChannel


def generate_outreach_messages(
    lead: Lead,
    ai_report: AIReport | None,
    channels: list[MessageChannel],
) -> list[dict]:
    business = lead.business_name
    service = ai_report.recommended_service if ai_report else "website and SEO improvements"
    angle = (
        ai_report.outreach_angle
        if ai_report
        else "Offer a quick free website audit focused on mobile enquiries and local visibility."
    )
    messages: list[dict] = []
    for channel in channels:
        if channel == MessageChannel.email:
            messages.append(
                {
                    "channel": channel,
                    "subject": f"Quick website audit idea for {business}",
                    "body": (
                        f"Hi {business} team,\n\n"
                        "We reviewed your website and noticed a few practical improvements that could "
                        "help convert more mobile visitors into enquiries.\n\n"
                        f"The biggest opportunity appears to be around {service}. "
                        "We prepared a short audit summary your team can review without any obligation.\n\n"
                        "Would it be okay if I shared the audit with you?"
                    ),
                }
            )
        elif channel == MessageChannel.whatsapp:
            messages.append(
                {
                    "channel": channel,
                    "subject": None,
                    "body": (
                        f"Hi, we reviewed {business}'s website and found a few improvements that may "
                        "help increase enquiries from mobile users. We prepared a quick free audit "
                        "summary. Can I share it with you?"
                    ),
                }
            )
        elif channel == MessageChannel.linkedin:
            messages.append(
                {
                    "channel": channel,
                    "subject": None,
                    "body": (
                        f"Hi, I came across {business} while reviewing local websites. "
                        "We found a few practical website and SEO improvements that could help with "
                        "enquiry conversion. Happy to share the short audit summary."
                    ),
                }
            )
        elif channel == MessageChannel.follow_up:
            messages.append(
                {
                    "channel": channel,
                    "subject": f"Following up on the {business} website audit",
                    "body": (
                        "Just following up on the website audit note. The quick win is to make the "
                        "site easier for mobile visitors to trust the business and enquire quickly. "
                        "I can send the summary if useful."
                    ),
                }
            )
        elif channel == MessageChannel.call_script:
            messages.append(
                {
                    "channel": channel,
                    "subject": "Call script",
                    "body": (
                        f"Open with: We prepared a short website audit for {business}. "
                        "Ask: Are you currently trying to increase website enquiries? "
                        f"Positioning: {angle} "
                        "Close: Offer to send the audit summary and schedule a 15-minute review."
                    ),
                }
            )
        elif channel == MessageChannel.proposal_summary:
            messages.append(
                {
                    "channel": channel,
                    "subject": "Proposal summary",
                    "body": (
                        f"Recommended package: {service}. Focus areas: mobile experience, local SEO, "
                        "trust signals, clearer CTAs, and lead capture improvements."
                    ),
                }
            )
    return messages

