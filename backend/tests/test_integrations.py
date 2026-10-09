from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_integration_status_never_exposes_api_keys():
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    data = response.json()
    assert "groq" in data["ai"]
    assert "tavily_configured" in data["search"]
    assert "DEEPGRAM_API_KEY" not in response.text


def test_search_requires_tavily_key(monkeypatch):
    from backend.app.config import get_settings
    monkeypatch.setattr(get_settings(), "tavily_api_key", "")
    response = client.post("/api/integrations/search", json={"query": "weather in Lahore"})
    assert response.status_code == 503


def test_calendar_creation_requires_confirmation(monkeypatch):
    response = client.post("/api/integrations/google/calendar", json={
        "summary": "AETHER test",
        "start": "2026-11-01T10:00:00+05:00",
        "end": "2026-11-01T10:30:00+05:00",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "confirmation_required"


def test_gmail_send_requires_confirmation():
    response = client.post("/api/integrations/google/gmail/send", json={
        "to": "test@example.com",
        "subject": "AETHER confirmation test",
        "body": "This must not send until confirmed.",
    })
    assert response.status_code == 200
    assert response.json()["status"] == "confirmation_required"


def test_calendar_rejects_invalid_time_range():
    response = client.post("/api/integrations/google/calendar", json={
        "summary": "AETHER test",
        "start": "2026-11-01T10:30:00+05:00",
        "end": "2026-11-01T10:00:00+05:00",
    })
    assert response.status_code == 400
