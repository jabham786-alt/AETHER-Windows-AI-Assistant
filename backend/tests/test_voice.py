from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_voice_providers_are_free():
    response = client.get("/api/voice/providers")
    assert response.status_code == 200
    data = response.json()
    assert data["stt"][0]["paid"] is False
    assert data["tts"][0]["paid"] is False
    assert data["wake_word"][0]["paid"] is False


def test_transcribe_rejects_empty_audio():
    response = client.post(
        "/api/voice/transcribe",
        files={"audio": ("empty.webm", b"", "audio/webm")},
    )
    assert response.status_code == 400
