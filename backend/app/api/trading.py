from datetime import datetime,timezone
from uuid import uuid4
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field

router=APIRouter()

PRICES={"BTCUSDT":65000.0,"ETHUSDT":3200.0,"BNBUSDT":600.0,"SOLUSDT":150.0}
state={"balances":{"USDT":100000.0,"BTC":0.0,"ETH":0.0,"BNB":0.0,"SOL":0.0},"orders":[]}

class OrderRequest(BaseModel):
 symbol:str=Field(pattern="^(BTCUSDT|ETHUSDT|BNBUSDT|SOLUSDT)$")
 side:str=Field(pattern="^(BUY|SELL)$")
 type:str=Field(pattern="^(MARKET|LIMIT)$")
 quantity:float=Field(gt=0,le=100000)
 price:float|None=Field(default=None,gt=0)

def snapshot():
 return {"mode":"LOCAL_PAPER","balances":state["balances"],"prices":PRICES,"orders":state["orders"][-50:]}

@router.get("/trading/status")
def status(): return snapshot()

@router.post("/trading/reset")
def reset():
 state["balances"]={"USDT":100000.0,"BTC":0.0,"ETH":0.0,"BNB":0.0,"SOL":0.0};state["orders"]=[];return snapshot()

@router.post("/trading/order")
def order(req:OrderRequest):
 symbol=req.symbol; base=symbol[:-4]; price=req.price if req.type=="LIMIT" else PRICES[symbol]; cost=price*req.quantity
 if req.side=="BUY":
  if state["balances"]["USDT"]<cost: raise HTTPException(400,detail="Insufficient demo USDT")
  state["balances"]["USDT"]-=cost;state["balances"][base]+=req.quantity
 else:
  if state["balances"].get(base,0)<req.quantity: raise HTTPException(400,detail=f"Insufficient demo {base}")
  state["balances"][base]-=req.quantity;state["balances"]["USDT"]+=cost
 item={"id":str(uuid4()),"symbol":symbol,"side":req.side,"type":req.type,"quantity":req.quantity,"price":price,"status":"FILLED","created_at":datetime.now(timezone.utc).isoformat()}
 state["orders"].append(item);return {"order":item,**snapshot()}
