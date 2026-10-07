import {useEffect,useState} from "react";
type Coin="BTCUSDT"|"ETHUSDT"|"BNBUSDT"|"SOLUSDT";
type Status={mode:string;balances:Record<string,number>;prices:Record<Coin,number>;orders:any[]};
const API="http://127.0.0.1:8765/api";
async function call(path:string,init?:RequestInit){const r=await fetch(API+path,init);const d=await r.json();if(!r.ok)throw Error(d.detail||"Trading request failed");return d}
export default function TradingLab(){
 const[s,setS]=useState<Status|null>(null),[symbol,setSymbol]=useState<Coin>("BTCUSDT"),[side,setSide]=useState<"BUY"|"SELL">("BUY"),[type,setType]=useState<"MARKET"|"LIMIT">("MARKET"),[qty,setQty]=useState("0.001"),[price,setPrice]=useState(""),[msg,setMsg]=useState("");
 async function load(){try{setS(await call("/trading/status"))}catch(e){setMsg(e instanceof Error?e.message:"Offline")}} useEffect(()=>{load()},[]);
 async function order(){try{const d=await call("/trading/order",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({symbol,side,type,quantity:Number(qty),price:type==="LIMIT"?Number(price):undefined})});setS(d);setMsg("Demo order filled — real funds نہیں لگے۔")}catch(e){setMsg(e instanceof Error?e.message:"Order failed")}}
 async function reset(){setS(await call("/trading/reset",{method:"POST"}));setMsg("Demo account reset ہو گیا۔")}
 const p=s?.prices?.[symbol]||0;
 return <section className="trading">
  <div className="head"><div><label>TRADING LAB / PHASE 4</label><h1>Binance Test Lab</h1><p>Local paper-trading simulator — real Binance account یا real money استعمال نہیں ہوتا۔</p></div><span className="demo-badge">● LOCAL DEMO</span></div>
  <div className="cards"><div className="card"><span>Mode</span><strong>LOCAL PAPER</strong><small>100% simulated</small></div><div className="card"><span>{symbol}</span><strong>{"$"+p.toLocaleString()}</strong><small>Demo market price</small></div><div className="card"><span>Demo USDT</span><strong>{(s?.balances.USDT||0).toLocaleString(undefined,{maximumFractionDigits:2})}</strong><small>Starting balance: 100,000 USDT</small></div></div>
  <div className="trading-grid">
   <div className="panel"><h2>Place Demo Order</h2><label className="field">Symbol<select value={symbol} onChange={e=>setSymbol(e.target.value as Coin)}>{Object.keys(s?.prices||{BTCUSDT:1,ETHUSDT:1,BNBUSDT:1,SOLUSDT:1}).map(x=><option key={x}>{x}</option>)}</select></label><div className="side-toggle"><button className={side==="BUY"?"buy active":"buy"} onClick={()=>setSide("BUY")}>BUY</button><button className={side==="SELL"?"sell active":"sell"} onClick={()=>setSide("SELL")}>SELL</button></div><label className="field">Order Type<select value={type} onChange={e=>setType(e.target.value as "MARKET"|"LIMIT")}><option>MARKET</option><option>LIMIT</option></select></label><label className="field">Quantity<input value={qty} onChange={e=>setQty(e.target.value)} type="number" min="0.000001" step="0.001"/></label>{type==="LIMIT"&&<label className="field">Limit Price<input value={price} onChange={e=>setPrice(e.target.value)} type="number" min="0.01"/></label>}<button className="trade-button" onClick={order}>Place Demo Order</button>{msg&&<div className="trading-message">{msg}</div>}</div>
   <div className="panel"><div className="head"><h2>Balances</h2><button className="ghost" onClick={reset}>Reset Demo</button></div>{Object.entries(s?.balances||{}).map(([coin,b])=><div className="balance-row" key={coin}><b>{coin}</b><span>{Number(b).toLocaleString(undefined,{maximumFractionDigits:8})}</span></div>)}</div>
  </div>
  <div className="panel"><div className="head"><h2>Order History</h2><button className="ghost" onClick={load}>Refresh</button></div>{s?.orders.length?s.orders.slice().reverse().map(o=><div className="order-row" key={o.id}><b>{o.side} {o.symbol}</b><span>{o.quantity}</span><span>{"$"+o.price.toLocaleString()}</span><em>{o.status}</em></div>):<p className="muted">ابھی کوئی demo order نہیں ہے۔</p>}</div>
  <div className="panel"><h2>Safety</h2><p>یہ screen صرف local simulation کے لیے ہے۔ Live Binance trading اس build میں فعال نہیں کی گئی۔</p></div>
 </section>
}