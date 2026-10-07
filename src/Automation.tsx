import {useEffect,useState} from "react";
import {automationActions,automationHistory,executeAutomation} from "./api";

const presets=[
  ["open_app","Open Notepad","app","notepad"],
  ["open_app","Open Calculator","app","calculator"],
  ["open_app","Open Explorer","app","explorer"],
];

export default function Automation(){
  const[history,setHistory]=useState<any[]>([]);
  const[action,setAction]=useState("open_app");
  const[params,setParams]=useState<Record<string,string>>({app:"notepad"});
  const[pending,setPending]=useState<any>(null);
  const[busy,setBusy]=useState(false);
  const[message,setMessage]=useState("");
  const[loadError,setLoadError]=useState("");

  async function load(){try{const d=await automationHistory();setHistory(d)}catch(e){setLoadError(e instanceof Error?e.message:"History unavailable")}}
  useEffect(()=>{load()},[]);

  function selectAction(v:string){
    setAction(v);
    if(v==="open_app")setParams({app:"notepad"});
    else if(v==="open_url")setParams({url:"https://www.google.com"});
    else if(v==="open_folder")setParams({path:"C:\\Users"});
    else if(v==="search_files")setParams({path:"C:\\Users",pattern:"*.pdf"});
    else if(v==="create_folder")setParams({path:"C:\\Users\\Public\\AETHER-Test"});
    else if(v==="create_file")setParams({path:"C:\\Users\\Public\\AETHER-Test.txt"});
    else if(v==="rename_file")setParams({path:"C:\\Users\\Public\\AETHER-Test.txt",new_name:"AETHER-Renamed.txt"});
    else if(v==="copy_file")setParams({source:"C:\\Users\\Public\\AETHER-Test.txt",destination:"C:\\Users\\Public\\AETHER-Copy.txt"});
    else if(v==="move_file")setParams({source:"C:\\Users\\Public\\AETHER-Test.txt",destination:"C:\\Users\\Public\\AETHER-Moved.txt"});
    else if(v==="delete_file")setParams({path:"C:\\Users\\Public\\AETHER-Test.txt"});
  }

  async function run(confirmed=false){
    setBusy(true);setMessage("");try{
      const d=await executeAutomation(action,params,confirmed);
      if(d.status==="confirmation_required"){setPending(d);return}
      setMessage("Action completed successfully.");
      setPending(null);await load();
    }catch(e){setMessage(e instanceof Error?e.message:"Automation failed")}finally{setBusy(false)}
  }

  const keys=Object.keys(params);
  return <section className="automation">
    <div className="head"><div><label>WINDOWS CONTROL / PHASE 3</label><h1>Automation Center</h1><p>محفوظ Windows actions — کوئی arbitrary shell command نہیں۔</p></div></div>
    <div className="automation-grid">
      <div className="panel">
        <h2>Run an action</h2>
        <select value={action} onChange={e=>selectAction(e.target.value)}>
          <option value="open_app">Open App</option><option value="open_url">Open URL</option><option value="open_folder">Open Folder</option>
          <option value="search_files">Search Files</option><option value="create_folder">Create Folder</option><option value="create_file">Create File</option>
          <option value="rename_file">Rename File</option><option value="copy_file">Copy File</option><option value="move_file">Move File</option><option value="delete_file">Delete File</option>
        </select>
        {presets.map(([a,label,key,value])=><button className="preset" key={label} onClick={()=>{setAction(a);setParams({[key]:value})}}>{label}</button>)}
        {keys.map(k=><label className="field" key={k}>{k}<input value={params[k]||""} onChange={e=>setParams({...params,[k]:e.target.value})}/></label>)}
        <button onClick={()=>run(false)} disabled={busy}>{busy?"Working…":"Run Action"}</button>
        {message&&<div className="automation-message">{message}</div>}
      </div>
      <div className="panel">
        <h2>Safety</h2>
        <p>Low-risk actions run directly. File creation, rename, copy and move require confirmation. Delete is high-risk and always requires explicit confirmation.</p>
        {pending&&<div className="confirm-box"><strong>Confirmation required</strong><p>{pending.action}</p><pre>{JSON.stringify(pending.params,null,2)}</pre><div><button onClick={()=>run(true)}>Allow</button><button className="ghost" onClick={()=>setPending(null)}>Cancel</button></div></div>}
      </div>
    </div>
    <div className="panel history"><div className="head"><h2>Action History</h2><button className="ghost" onClick={load}>Refresh</button></div>{loadError&&<div className="error">{loadError}</div>}{history.length===0?<p className="muted">ابھی کوئی automation action نہیں ہوئی۔</p>:history.map(x=><div className="history-row" key={x.id}><span>{new Date(x.created_at).toLocaleString()}</span><b>{x.action}</b><em className={x.status}>{x.status}</em><small>{x.risk}</small></div>)}</div>
  </section>
}
