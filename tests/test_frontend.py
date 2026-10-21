from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_homepage_has_live_api_and_ai_controls():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "api-client.js").read_text(encoding="utf-8")
    for element_id in ("api-base-url", "api-connect-button", "api-connection-status", "api-search-form", "ai-research-form"):
        assert element_id in html
    assert '"/health"' in js
    assert '"/api/indicators?q="' in js
    assert '"/api/research/ask"' in js


def test_frontend_does_not_embed_secret_names_or_example_credentials():
    js = (ROOT / "api-client.js").read_text(encoding="utf-8")
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    combined = js + html
    assert "OPENAI_API_KEY=" not in combined
    assert "DATABASE_URL=" not in combined
    assert "service_role" not in combined.lower()
