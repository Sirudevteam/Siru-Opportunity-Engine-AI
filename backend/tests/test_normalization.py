from app.services.normalization import (
    build_dedupe_key,
    contactability_score,
    extract_domain,
    normalize_phone,
    normalize_url,
)


def test_normalize_url_adds_scheme_and_removes_trailing_slash():
    assert normalize_url("Example.com/") == "https://example.com"


def test_extract_domain_removes_www():
    assert extract_domain("https://www.example.com/about") == "example.com"


def test_dedupe_prefers_domain():
    key = build_dedupe_key("Example Dental", "https://example.com", "hello@example.com", "+91 99999")
    assert key == "domain:example.com"


def test_phone_and_contactability_score():
    assert normalize_phone("+91 98765-43210") == "+919876543210"
    assert contactability_score("hello@example.com", "+919876543210", "https://example.com") == 100

