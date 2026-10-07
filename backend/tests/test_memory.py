from fastapi.testclient import TestClient
from backend.main import app
from backend.app.database import Base,engine
from backend.app.models import Memory

client=TestClient(app)

def test_memory_create_search_update_delete():
    created=client.post("/api/memories",json={"category":"preference","content":"Urdu responses are preferred","source":"user"})
    assert created.status_code==201
    memory_id=created.json()["id"]

    found=client.get("/api/memories/search",params={"q":"Urdu responses"})
    assert found.status_code==200
    assert any(x["id"]==memory_id for x in found.json())

    updated=client.patch(f"/api/memories/{memory_id}",json={"content":"Urdu replies are preferred"})
    assert updated.status_code==200
    assert updated.json()["content"]=="Urdu replies are preferred"

    deleted=client.delete(f"/api/memories/{memory_id}")
    assert deleted.status_code==204
