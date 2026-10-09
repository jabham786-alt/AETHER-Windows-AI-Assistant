import {useEffect,useState} from "react";
import {RefreshCw,Search,Mail,CalendarDays,Contact,Globe,Link2,ShieldCheck} from "lucide-react";

const API="http://127.0.0.1:8765/api";
async function request(path:string, options:RequestInit={}) {
  const response=await fetch(API+path,options);
  const data=await response.json().catch(()=>({}));
  if(!response.ok) throw new Error(data.detail||"Integration request failed");
  return data;
}
function post(path:string, body:unknown){return request(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})}

export default function Integrations(){
  const[status,setStatus]=useState<any>(null);
  const[error,setError]=useState("");
  const[message,setMessage]=useState("");
  const[busy,setBusy]=useState(false);
  const[searchQuery,setSearchQuery]=useState("");
  const[searchData,setSearchData]=useState<any>(null);
  const[authUrl,setAuthUrl]=useState("");
  const[calendar,setCalendar]=useState<any[]>([]);
  const[contacts,setContacts]=useState<any[]>([]);
  const[gmail,setGmail]=useState<any[]>([]);
  const[gmailQuery,setGmailQuery]=useState("");
  const[email,setEmail]=useState({to:"",subject:"",body:""});
  const[pendingEmail,setPendingEmail]=useState<any>(null);
  const[event,setEvent]=useState({summary:"",start:"",end:"",description:""});
  const[pendingEvent,setPendingEvent]=useState<any>(null);

  async function refresh(){try{setStatus(await request("/integrations/status"));setError("")}catch(e){setError(e instanceof Error?e.message:"Could not load provider status")}}
  useEffect(()=>{void refresh()},[]);

  async function run<T>(task:()=>Promise<T>,success?:string){setBusy(true);setError("");setMessage("");try{const result=await task();if(success)setMessage(success);return result}catch(e){setError(e instanceof Error?e.message:"Request failed");return null}finally{setBusy(false)}}
  async function search(){const result=await run(()=>post("/integrations/search",{query:searchQuery,max_results:5}));if(result)setSearchData(result)}
  async function connectGoogle(){const result=await run(()=>request("/integrations/google/auth-url"));if(result)setAuthUrl(result.authorization_url)}
  async function loadCalendar(){const result=await run(()=>request("/integrations/google/calendar"));if(result)setCalendar(result)}
  async function loadContacts(){const result=await run(()=>request("/integrations/google/contacts"));if(result)setContacts(result)}
  async function loadGmail(){const result=await run(()=>request("/integrations/google/gmail?limit=10&q="+encodeURIComponent(gmailQuery)));if(result)setGmail(result)}
  async function prepareEmail(){const result=await run(()=>post("/integrations/google/gmail/send",{...email,confirmed:false}));if(result?.status==="confirmation_required")setPendingEmail(result.preview)}
  async function confirmEmail(){const result=await run(()=>post("/integrations/google/gmail/send",{...email,confirmed:true}),"Email sent.");if(result?.status==="sent")setPendingEmail(null)}
  async function prepareEvent(){const result=await run(()=>post("/integrations/google/calendar",{...event,start:new Date(event.start).toISOString(),end:new Date(event.end).toISOString(),confirmed:false}));if(result?.status==="confirmation_required")setPendingEvent(result.preview)}
  async function confirmEvent(){const result=await run(()=>post("/integrations/google/calendar",{...event,start:new Date(event.start).toISOString(),end:new Date(event.end).toISOString(),confirmed:true}),"Calendar event created.");if(result?.status==="created")setPendingEvent(null)}

  return <section className="integrations">
    <div className="head"><div><label>AETHER / CONNECTORS</label><h1>Integrations</h1><p>Cloud services are optional. API keys stay on the backend; sensitive actions need your confirmation.</p></div><button className="ghost" onClick={refresh} disabled={busy}><RefreshCw size={15}/> Refresh status</button></div>
    {error&&<div className="error">{error}</div>}{message&&<div className="automation-message">{message}</div>}
    <div className="integration-status">
      <div className="metric"><span>AI Provider</span><strong>{status?.ai?.provider||"Loading"}</strong><small>OpenAI {status?.ai?.openai?"ready":"not configured"} · Gemini {status?.ai?.gemini?"ready":"not configured"} · Groq {status?.ai?.groq?"ready":"not configured"}</small></div>
      <div className="metric"><span>Speech-to-Text</span><strong>{status?.speech?.active_stt||"Loading"}</strong><small>Deepgram {status?.speech?.deepgram_configured?"ready":"not configured"} · Local Whisper stays available</small></div>
      <div className="metric"><span>Web Search</span><strong>{status?.search?.tavily_configured?"Tavily Ready":"Not configured"}</strong><small>Configure TAVILY_API_KEY in .env</small></div>
      <div className="metric"><span>Google Account</span><strong>{status?.google?.connected?"Connected":"Not connected"}</strong><small>{status?.google?.oauth_client_configured?"OAuth client found":"OAuth client JSON needed"}</small></div>
    </div>
    <div className="integration-grid">
      <div className="panel">
        <h2><Search size={18}/> Tavily Web Search</h2><p>Search the web and inspect returned links. Search results are reference data, not executable commands.</p>
        <label className="field">Search query<input value={searchQuery} onChange={e=>setSearchQuery(e.target.value)} placeholder="Search a topic..." maxLength={500}/></label>
        <button disabled={busy||searchQuery.trim().length<2} onClick={search}>Search Web</button>
        {searchData&&<div className="integration-results">{searchData.answer&&<p>{searchData.answer}</p>}{(searchData.results||[]).map((x:any,i:number)=><article key={x.url||i}><a href={x.url} target="_blank" rel="noreferrer">{x.title||x.url}</a><p>{x.content}</p></article>)}</div>}
      </div>
      <div className="panel">
        <h2><Link2 size={18}/> Google Account</h2><p>Connect Calendar, Contacts and Gmail using Google OAuth. The OAuth client JSON belongs in backend/data and must never be committed.</p>
        <button disabled={busy} onClick={connectGoogle}>Generate Google Connect Link</button>
        {authUrl&&<p className="integration-link"><a href={authUrl} target="_blank" rel="noreferrer">Open Google authorization</a></p>}
        <p className="muted">Required redirect URI: http://127.0.0.1:8765/api/integrations/google/callback</p>
      </div>
      <div className="panel">
        <h2><CalendarDays size={18}/> Google Calendar</h2><button className="ghost" disabled={busy} onClick={loadCalendar}>Load upcoming events</button>
        {calendar.map((x:any)=><article className="integration-item" key={x.id}><b>{x.summary}</b><small>{x.start?.dateTime||x.start?.date||""}</small></article>)}
        <h3>Create an event</h3>
        <label className="field">Title<input value={event.summary} onChange={e=>setEvent({...event,summary:e.target.value})} maxLength={200}/></label>
        <div className="integration-two"><label className="field">Start<input type="datetime-local" value={event.start} onChange={e=>setEvent({...event,start:e.target.value})}/></label><label className="field">End<input type="datetime-local" value={event.end} onChange={e=>setEvent({...event,end:e.target.value})}/></label></div>
        <label className="field">Description<input value={event.description} onChange={e=>setEvent({...event,description:e.target.value})} maxLength={4000}/></label>
        {!pendingEvent?<button disabled={busy||!event.summary||!event.start||!event.end} onClick={prepareEvent}>Review event</button>:<div className="confirm-box"><b>Confirm calendar event</b><pre>{JSON.stringify(pendingEvent,null,2)}</pre><button disabled={busy} onClick={confirmEvent}>Confirm Create</button><button className="ghost" onClick={()=>setPendingEvent(null)}>Cancel</button></div>}
      </div>
      <div className="panel">
        <h2><Contact size={18}/> Google Contacts</h2><button className="ghost" disabled={busy} onClick={loadContacts}>Load contacts</button>
        {contacts.map((x:any,i:number)=><article className="integration-item" key={i}><b>{x.name||"Unnamed contact"}</b><small>{x.emails?.join(", ")}</small><small>{x.phones?.join(", ")}</small></article>)}
      </div>
      <div className="panel">
        <h2><Mail size={18}/> Gmail</h2><p>Only message metadata and snippets are loaded by default, not full email bodies.</p>
        <label className="field">Gmail search (optional)<input value={gmailQuery} onChange={e=>setGmailQuery(e.target.value)} placeholder="from:someone@example.com"/></label>
        <button className="ghost" disabled={busy} onClick={loadGmail}>Load messages</button>
        {gmail.map((x:any)=><article className="integration-item" key={x.id}><b>{x.subject||"(No subject)"}</b><small>{x.from} · {x.date}</small><p>{x.snippet}</p></article>)}
        <h3>Send an email</h3>
        <label className="field">To<input type="email" value={email.to} onChange={e=>setEmail({...email,to:e.target.value})}/></label>
        <label className="field">Subject<input value={email.subject} onChange={e=>setEmail({...email,subject:e.target.value})} maxLength={200}/></label>
        <label className="field">Message<input value={email.body} onChange={e=>setEmail({...email,body:e.target.value})} maxLength={10000}/></label>
        {!pendingEmail?<button disabled={busy||!email.to||!email.subject||!email.body} onClick={prepareEmail}>Review email</button>:<div className="confirm-box"><b><ShieldCheck size={16}/> Confirm sending email</b><pre>{JSON.stringify(pendingEmail,null,2)}</pre><button disabled={busy} onClick={confirmEmail}>Confirm Send</button><button className="ghost" onClick={()=>setPendingEmail(null)}>Cancel</button></div>}
      </div>
    </div>
    <p className="muted">Policy Engine محفوظ ہے۔ Google write actions صرف preview دکھانے کے بعد آپ کی الگ confirmation پر چلتے ہیں۔</p>
  </section>
}
