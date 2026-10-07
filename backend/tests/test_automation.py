from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_automation_action_catalog():
    r = client.get("/api/automation/actions")
    assert r.status_code == 200
    actions = {x["id"]: x for x in r.json()["actions"]}
    assert actions["open_app"]["requires_confirmation"] is False
    assert actions["delete_file"]["risk"] == "high"
    assert actions["delete_file"]["requires_confirmation"] is True

def test_delete_requires_confirmation():
    r = client.post("/api/automation/execute", json={
        "action": "delete_file",
        "params": {"path": "C:\\temp\\example.txt"},
        "confirmed": False,
    })
    assert r.status_code == 200
    assert r.json()["status"] == "confirmation_required"

def test_unsupported_action():
    r = client.post("/api/automation/execute", json={"action": "run_shell", "params": {}})
    assert r.status_code == 400

def test_invalid_action_parameters_return_400():
    r = client.post("/api/automation/execute", json={
        "action": "open_app",
        "params": {},
    })
    assert r.status_code == 400
    assert "required" in r.json()["detail"].lower()
