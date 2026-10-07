const API="http://127.0.0.1:8765/api";
export async function health(){const r=await fetch(API+"/health");if(!r.ok)throw Error("Backend unavailable");return r.json()}
export async function systemStatus(){const r=await fetch(API+"/system/status");if(!r.ok)throw Error("System status unavailable");return r.json()}
export async function chat(message:string,history:{role:string;content:string}[]){const r=await fetch(API+"/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message,history})});const d=await r.json();if(!r.ok)throw Error(d.detail||"Chat request failed");return d}
export async function automationActions(){const r=await fetch(API+"/automation/actions");if(!r.ok)throw Error("Automation catalog unavailable");return r.json()}
export async function automationHistory(){const r=await fetch(API+"/automation/history");if(!r.ok)throw Error("Automation history unavailable");return r.json()}
export async function executeAutomation(action:string,params:Record<string,unknown>,confirmed=false){const r=await fetch(API+"/automation/execute",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action,params,confirmed})});const d=await r.json();if(!r.ok)throw Error(d.detail||"Automation request failed");return d}
