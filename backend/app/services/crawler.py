from __future__ import annotations

import time
from dataclasses import dataclass, field

import requests

from app.core.config import get_settings
from app.services.analyzer import analyze_html
from app.services.normalization import normalize_url


@dataclass
class ScreenshotArtifact:
    viewport: str
    content: bytes
    width: int
    height: int


@dataclass
class CrawlResult:
    url: str
    final_url: str
    html: str
    status_code: int
    response_ms: int
    screenshots: list[ScreenshotArtifact] = field(default_factory=list)
    analysis: dict = field(default_factory=dict)


def crawl_website(url: str) -> CrawlResult:
    normalized = normalize_url(url)
    if not normalized:
        raise ValueError("A valid website URL is required for crawling.")
    try:
        return _crawl_with_playwright(normalized)
    except Exception:
        return _crawl_with_requests(normalized)


def _crawl_with_playwright(url: str) -> CrawlResult:
    from playwright.sync_api import sync_playwright

    settings = get_settings()
    start = time.perf_counter()
    screenshots: list[ScreenshotArtifact] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        desktop = browser.new_page(viewport={"width": 1440, "height": 1200})
        desktop.goto(url, wait_until="networkidle", timeout=settings.crawl_timeout_ms)
        html = desktop.content()
        final_url = desktop.url
        screenshots.append(
            ScreenshotArtifact(
                viewport="desktop",
                content=desktop.screenshot(full_page=True, type="png"),
                width=1440,
                height=1200,
            )
        )
        mobile = browser.new_page(
            viewport={"width": 390, "height": 844},
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            ),
        )
        mobile.goto(url, wait_until="networkidle", timeout=settings.crawl_timeout_ms)
        screenshots.append(
            ScreenshotArtifact(
                viewport="mobile",
                content=mobile.screenshot(full_page=True, type="png"),
                width=390,
                height=844,
            )
        )
        status_code = 200
        browser.close()
    response_ms = int((time.perf_counter() - start) * 1000)
    analysis = analyze_html(
        url=url,
        html=html,
        response_ms=response_ms,
        status_code=status_code,
        final_url=final_url,
        mobile_screenshot=True,
    )
    return CrawlResult(
        url=url,
        final_url=final_url,
        html=html,
        status_code=status_code,
        response_ms=response_ms,
        screenshots=screenshots,
        analysis={
            "website_data": analysis.website_data,
            "checks": analysis.checks,
            "scoring": analysis.scoring,
        },
    )


def _crawl_with_requests(url: str) -> CrawlResult:
    start = time.perf_counter()
    response = requests.get(url, timeout=20, headers={"User-Agent": "SiruOpportunityBot/0.1"})
    response.raise_for_status()
    response_ms = int((time.perf_counter() - start) * 1000)
    html = response.text
    analysis = analyze_html(
        url=url,
        html=html,
        response_ms=response_ms,
        status_code=response.status_code,
        final_url=response.url,
        mobile_screenshot=False,
    )
    return CrawlResult(
        url=url,
        final_url=response.url,
        html=html,
        status_code=response.status_code,
        response_ms=response_ms,
        screenshots=[],
        analysis={
            "website_data": analysis.website_data,
            "checks": analysis.checks,
            "scoring": analysis.scoring,
        },
    )

