from fastapi.testclient import TestClient
from backend.main import app
c=TestClient(app)
def test_health():r=c.get("/api/health");assert r.status_code==200;assert r.json()["status"]=="ok"
def test_system():r=c.get("/api/system/status");assert r.status_code==200;assert "cpu_percent" in r.json()