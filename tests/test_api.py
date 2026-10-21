"""API tests run with an isolated temporary SQLite database."""
import importlib

from fastapi.testclient import TestClient


def make_client(monkeypatch, tmp_path):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    import api.main as main
    importlib.reload(main)
    main.init_db()
    return main, TestClient(main.app)


def test_health_and_seed_data(monkeypatch, tmp_path):
    main, client = make_client(monkeypatch, tmp_path)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    data = client.get("/api/indicators").json()
    assert data["count"] == 6
    assert all("source_url" in row for row in data["data"])


def test_indicator_search_and_category_filter(monkeypatch, tmp_path):
    _, client = make_client(monkeypatch, tmp_path)
    response = client.get("/api/indicators", params={"q": "unemployment", "category": "labour"})
    assert response.status_code == 200
    assert response.json()["count"] == 3
    assert all(row["indicator_key"] == "unemployment_rate" for row in response.json()["data"])


def test_limits_are_validated(monkeypatch, tmp_path):
    _, client = make_client(monkeypatch, tmp_path)
    assert client.get("/api/indicators?limit=0").status_code == 422
    assert client.get("/api/research?limit=1000").status_code == 422


def test_database_initialization_is_idempotent(monkeypatch, tmp_path):
    main, client = make_client(monkeypatch, tmp_path)
    main.init_db()
    assert client.get("/api/indicators").json()["count"] == 6


def test_ai_endpoint_requires_server_key(monkeypatch, tmp_path):
    _, client = make_client(monkeypatch, tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/api/research/ask", json={"question": "Explain the latest inflation data"})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_ai_endpoint_uses_server_key_and_saves_history(monkeypatch, tmp_path):
    import sys
    from types import SimpleNamespace

    _, client = make_client(monkeypatch, tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "test-server-key")
    calls = {}

    class FakeResponses:
        def create(self, **kwargs):
            calls.update(kwargs)
            return SimpleNamespace(output_text="Official sources indicate a change. https://www.cbsl.gov.lk/")

    class FakeClient:
        def __init__(self, api_key):
            calls["api_key"] = api_key
            self.responses = FakeResponses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeClient))
    response = client.post("/api/research/ask", json={"question": "Summarise Sri Lanka inflation"})
    assert response.status_code == 200
    assert response.json()["saved"] is True
    assert calls["api_key"] == "test-server-key"
    assert {"type": "web_search"} in calls["tools"]
    assert client.get("/api/research").json()["count"] == 1


def test_ai_endpoint_rejects_too_short_questions(monkeypatch, tmp_path):
    _, client = make_client(monkeypatch, tmp_path)
    assert client.post("/api/research/ask", json={"question": "bad"}).status_code == 422
