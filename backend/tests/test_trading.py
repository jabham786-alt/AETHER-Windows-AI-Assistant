from fastapi.testclient import TestClient
from backend.main import app
client=TestClient(app)

def test_local_trading_buy_and_reset():
    client.post("/api/trading/reset")
    before=client.get("/api/trading/status").json()
    assert before["mode"]=="LOCAL_PAPER"
    assert before["balances"]["USDT"]==100000.0

    r=client.post("/api/trading/order",json={"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":0.001})
    assert r.status_code==200
    assert r.json()["orders"][-1]["status"]=="FILLED"
    assert r.json()["balances"]["BTC"]>0

    reset=client.post("/api/trading/reset")
    assert reset.status_code==200
    assert reset.json()["balances"]["BTC"]==0.0
    assert reset.json()["balances"]["USDT"]==100000.0
