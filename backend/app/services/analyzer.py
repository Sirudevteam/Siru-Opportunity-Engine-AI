from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.services.scoring import score_website_checks


CTA_TERMS = {
    "book",
    "call",
    "contact",
    "enquire",
    "inquire",
    "quote",
    "schedule",
    "appointment",
    "consultation",
    "buy",
    "order",
    "start",
}

SOCIAL_DOMAINS = ("facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com", "youtube.com")


@dataclass
class AnalysisResult:
    website_data: dict
    checks: dict
    scoring: dict


def analyze_html(
    url: str,
    html: str,
    response_ms: int = 0,
    status_code: int = 200,
    final_url: str | None = None,
    mobile_screenshot: bool = False,
) -> AnalysisResult:
    soup = BeautifulSoup(html or "", "html.parser")
    title = text_or_none(soup.title.string if soup.title else None)
    meta_description = meta_content(soup, "description")
    canonical_url = canonical_link(soup, url)
    headings = {
        "h1": [tag.get_text(" ", strip=True) for tag in soup.find_all("h1")][:8],
        "h2": [tag.get_text(" ", strip=True) for tag in soup.find_all("h2")][:16],
    }
    links = extract_links(soup, url)
    images = extract_images(soup)
    forms = [{"action": form.get("action"), "method": form.get("method", "get")} for form in soup.find_all("form")]
    ctas = extract_ctas(soup)
    text = soup.get_text(" ", strip=True)
    lower_html = html.lower()
    lower_text = text.lower()
    tech_stack = detect_tech_stack(lower_html, soup)

    checks = {
        "status_code": status_code,
        "has_title": bool(title and 8 <= len(title) <= 80),
        "has_meta_description": bool(meta_description and 50 <= len(meta_description) <= 180),
        "has_h1": len(headings["h1"]) == 1,
        "canonical_url": canonical_url,
        "image_alt_ratio": images["alt_ratio"],
        "cta_count": len(ctas),
        "form_count": len(forms),
        "has_phone_or_email": has_phone_or_email(text, html),
        "has_https": urlparse(final_url or url).scheme == "https",
        "has_address": bool(re.search(r"\b(street|road|avenue|suite|floor|dubai|uae|india)\b", lower_text)),
        "social_link_count": len([link for link in links["external"] if any(domain in link for domain in SOCIAL_DOMAINS)]),
        "has_schema_org": "schema.org" in lower_html or "application/ld+json" in lower_html,
        "has_testimonial_terms": any(term in lower_text for term in ["review", "testimonial", "clients", "patients"]),
        "has_viewport_meta": bool(soup.find("meta", attrs={"name": "viewport"})),
        "has_responsive_css": any(token in lower_html for token in ["@media", "max-width", "min-width", "viewport"]),
        "mobile_screenshot": mobile_screenshot,
        "page_size_kb": round(len(html.encode("utf-8")) / 1024),
        "response_ms": response_ms,
        "has_navigation": bool(soup.find("nav") or soup.find(attrs={"role": "navigation"})),
        "has_service_or_product_links": has_link_terms(links["internal"], ["service", "product", "treatment", "solution"]),
        "text_length": len(text),
        "image_count": images["count"],
        "has_contact_page": has_link_terms(links["internal"], ["contact"]),
        "has_about_page": has_link_terms(links["internal"], ["about"]),
        "uses_modern_framework": tech_stack["modern_framework"] is not None,
        "has_structured_assets": bool(soup.find_all("script") or soup.find_all("link", rel="stylesheet")),
        "old_tech_signals": tech_stack["old_tech_signals"],
    }
    scoring = score_website_checks(checks)
    website_data = {
        "url": url,
        "final_url": final_url or url,
        "title": title,
        "meta_description": meta_description,
        "html_excerpt": text[:4000],
        "headings": headings,
        "links": links,
        "images": images,
        "forms": {"count": len(forms), "items": forms[:10]},
        "cta_buttons": {"count": len(ctas), "items": ctas[:20]},
        "tech_stack": tech_stack,
        "raw_metrics": checks,
    }
    return AnalysisResult(website_data=website_data, checks=checks, scoring=scoring)


def text_or_none(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def meta_content(soup: BeautifulSoup, name: str) -> str | None:
    tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": f"og:{name}"})
    if not tag:
        return None
    return text_or_none(tag.get("content"))


def canonical_link(soup: BeautifulSoup, base_url: str) -> str | None:
    tag = soup.find("link", rel=lambda rel: rel and "canonical" in rel)
    href = tag.get("href") if tag else None
    return urljoin(base_url, href) if href else None


def extract_links(soup: BeautifulSoup, base_url: str) -> dict:
    base_host = urlparse(base_url).netloc
    internal: list[str] = []
    external: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = urljoin(base_url, tag["href"])
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        host = urlparse(href).netloc
        if host == base_host or not host:
            internal.append(href)
        else:
            external.append(href)
    return {
        "internal": sorted(set(internal))[:100],
        "external": sorted(set(external))[:100],
        "count": len(set(internal + external)),
    }


def extract_images(soup: BeautifulSoup) -> dict:
    tags = soup.find_all("img")
    count = len(tags)
    alt_count = len([tag for tag in tags if tag.get("alt")])
    return {
        "count": count,
        "with_alt": alt_count,
        "alt_ratio": round(alt_count / count, 2) if count else 1,
    }


def extract_ctas(soup: BeautifulSoup) -> list[str]:
    found: list[str] = []
    for tag in soup.find_all(["a", "button"]):
        text = tag.get_text(" ", strip=True)
        if not text:
            continue
        words = set(re.findall(r"[a-z]+", text.lower()))
        if words & CTA_TERMS:
            found.append(text[:120])
    return found


def has_phone_or_email(text: str, html: str) -> bool:
    if "mailto:" in html.lower() or "tel:" in html.lower():
        return True
    if re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", text):
        return True
    return bool(re.search(r"\+?\d[\d\s().-]{7,}\d", text))


def has_link_terms(links: list[str], terms: list[str]) -> bool:
    return any(any(term in link.lower() for term in terms) for link in links)


def detect_tech_stack(lower_html: str, soup: BeautifulSoup) -> dict:
    modern = None
    if "__next" in lower_html or "next/static" in lower_html:
        modern = "Next.js"
    elif "react" in lower_html:
        modern = "React"
    elif "vue" in lower_html:
        modern = "Vue"
    elif "angular" in lower_html:
        modern = "Angular"

    cms = None
    if "wp-content" in lower_html:
        cms = "WordPress"
    elif "wixstatic" in lower_html:
        cms = "Wix"
    elif "squarespace" in lower_html:
        cms = "Squarespace"
    elif "cdn.shopify" in lower_html or "shopify" in lower_html:
        cms = "Shopify"

    scripts = [tag.get("src") for tag in soup.find_all("script") if tag.get("src")]
    old_signals = any(token in lower_html for token in ["<font", "flash", "frontpage", "jquery/1."])
    return {
        "modern_framework": modern,
        "cms": cms,
        "scripts": scripts[:20],
        "old_tech_signals": old_signals,
    }

