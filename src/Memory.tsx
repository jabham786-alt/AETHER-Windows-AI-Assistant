import {useEffect,useState} from "react";
import {createMemory,deleteMemory,listMemories,searchMemories,updateMemory} from "./api";

type MemoryItem={id:string;category:string;content:string;source:string;created_at:string;updated_at:string};

export default function Memory(){
 const[memories,setMemories]=useState<MemoryItem[]>([]);
 const[query,setQuery]=useState("");
 const[category,setCategory]=useState("general");
 const[content,setContent]=useState("");
 const[busy,setBusy]=useState(false);
 const[error,setError]=useState("");

 async function load(){setBusy(true);setError("");try{setMemories(query.trim()?await searchMemories(query):await listMemories())}catch(e){setError(e instanceof Error?e.message:"Memory load failed")}finally{setBusy(false)}}
 useEffect(()=>{load()},[]);

 async function add(){if(!content.trim())return;setError("");try{await createMemory(category,content);setContent("");await load()}catch(e){setError(e instanceof Error?e.message:"Memory save failed")}}
 async function remove(id:string){try{await deleteMemory(id);setMemories(x=>x.filter(m=>m.id!==id))}catch(e){setError(e instanceof Error?e.message:"Memory delete failed")}}
 async function edit(m:MemoryItem){const next=window.prompt("Memory text",m.content);if(next===null||!next.trim())return;try{const updated=await updateMemory(m.id,{content:next});setMemories(x=>x.map(item=>item.id===m.id?updated:item))}catch(e){setError(e instanceof Error?e.message:"Memory update failed")}}

 return <section>
  <div className="head"><div><label>MEMORY / PHASE 4</label><h1>AETHER Memory</h1><p>مقامی SQLite memory اور lightweight RAG retrieval — آپ کا ڈیٹا local database میں رہتا ہے۔</p></div></div>
  <div className="memory-grid">
   <div className="panel"><h2>Save Memory</h2><label className="field">Category<input value={category} onChange={e=>setCategory(e.target.value)} maxLength={40}/></label><label className="field">Memory<textarea value={content} onChange={e=>setContent(e.target.value)} placeholder="مثلاً: مجھے اردو میں جواب چاہیے۔" maxLength={10000}/></label><button onClick={add} disabled={!content.trim()}>Save Memory</button></div>
   <div className="panel"><h2>Recall</h2><div className="memory-search"><input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")load()}} placeholder="Memory تلاش کریں…"/><button onClick={load}>Search</button></div><p className="muted">{busy?"Retrieving…":memories.length+" memories"}</p></div>
  </div>
  {error&&<div className="error">{error}</div>}
  <div className="memory-list">{memories.map(m=><article className="panel memory-card" key={m.id}><div><span className="memory-category">{m.category}</span><small>{m.source}</small></div><p>{m.content}</p><div className="memory-actions"><button className="ghost" onClick={()=>edit(m)}>Edit</button><button className="ghost" onClick={()=>remove(m.id)}>Delete</button></div></article>)}{!busy&&!memories.length&&<div className="empty"><h2>No memories yet</h2><p>Save a memory above، پھر AETHER اسے متعلقہ chat میں context کے طور پر استعمال کرے گا۔</p></div>}</div>
 </section>
}
