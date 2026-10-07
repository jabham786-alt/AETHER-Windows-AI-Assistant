import {useEffect,useMemo,useState} from "react";

type ShellType="auto"|"powershell"|"cmd"|"bash"|"wsl";
type CommandId="check_python"|"install_backend"|"run_backend_tests"|"install_frontend"|"typecheck"|"build";

const COMMANDS:Array<{id:CommandId;label:string;description:string}>= [
  {id:"check_python",label:"Check Python",description:"Python version اور virtual environment کی جانچ"},
  {id:"install_backend",label:"Install Backend",description:"backend/requirements.txt سے dependencies انسٹال کریں"},
  {id:"run_backend_tests",label:"Run Backend Tests",description:"تمام backend pytest tests چلائیں"},
  {id:"install_frontend",label:"Install Frontend",description:"npm dependencies انسٹال کریں"},
  {id:"typecheck",label:"TypeScript Check",description:"renderer اور Electron TypeScript چیک کریں"},
  {id:"build",label:"Production Build",description:"AETHER کا production build تیار کریں"},
];

function commandText(shell:ShellType,id:CommandId){
  const ps:Record<CommandId,string>={
    check_python:"python --version; if (Test-Path .\\.venv\\Scripts\\python.exe) { .\\.venv\\Scripts\\python.exe --version }",
    install_backend:"python -m pip install -r backend\\requirements.txt",
    run_backend_tests:"python -m pytest backend\\tests -q",
    install_frontend:"npm install",
    typecheck:"npm run typecheck",
    build:"npm run build",
  };
  const cmd:Record<CommandId,string>={
    check_python:"python --version && if exist .venv\\Scripts\\python.exe .venv\\Scripts\\python.exe --version",
    install_backend:"python -m pip install -r backend\\requirements.txt",
    run_backend_tests:"python -m pytest backend\\tests -q",
    install_frontend:"npm install",
    typecheck:"npm run typecheck",
    build:"npm run build",
  };
  const unix:Record<CommandId,string>={
    check_python:"python3 --version; test -x .venv/bin/python && .venv/bin/python --version",
    install_backend:"python3 -m pip install -r backend/requirements.txt",
    run_backend_tests:"python3 -m pytest backend/tests -q",
    install_frontend:"npm install",
    typecheck:"npm run typecheck",
    build:"npm run build",
  };
  if(shell==="powershell")return ps[id];
  if(shell==="cmd")return cmd[id];
  if(shell==="bash"||shell==="wsl")return unix[id];
  return ps[id];
}

export default function CommandCenter(){
  const[shell,setShell]=useState<ShellType>("auto");
  const[detected,setDetected]=useState("Detecting…");
  const[selected,setSelected]=useState<CommandId>("check_python");
  const[message,setMessage]=useState("");
  const[busy,setBusy]=useState(false);

  useEffect(()=>{window.aether.getShellInfo().then(x=>setDetected(x.shell)).catch(()=>setDetected("unknown"))},[]);
  const effectiveShell=useMemo(()=>{
    if(shell!=="auto")return shell;
    if(detected==="cmd"||detected==="bash"||detected==="wsl")return detected;
    return "powershell";
  },[shell,detected]);
  const command=commandText(effectiveShell,selected);

  async function copy(){await navigator.clipboard.writeText(command);setMessage("کمانڈ کلپ بورڈ میں کاپی ہو گئی۔")}
  async function run(){
    setBusy(true);setMessage("");
    try{const r=await window.aether.runSafeCommand(selected);setMessage(r.code===0?"کمانڈ کامیابی سے مکمل ہو گئی۔":`کمانڈ ناکام ہوئی (exit ${r.code})۔`)}
    catch(e){setMessage(e instanceof Error?e.message:"کمانڈ چلانے میں مسئلہ آیا۔")}
    finally{setBusy(false)}
  }

  return <section className="command-center">
    <div className="head"><div><label>COMMAND CENTER</label><h1>Shell-aware tools</h1><p>PowerShell، CMD، Bash اور WSL کے لیے درست path syntax۔ arbitrary shell command execution دستیاب نہیں۔</p></div></div>
    <div className="command-grid">
      <div className="panel">
        <h2>Environment</h2>
        <label className="field">Shell
          <select value={shell} onChange={e=>setShell(e.target.value as ShellType)}>
            <option value="auto">Auto — {detected}</option><option value="powershell">PowerShell</option><option value="cmd">CMD</option><option value="bash">Bash / Git Bash</option><option value="wsl">WSL</option>
          </select>
        </label>
        <div className="shell-badge">Detected shell: <b>{detected}</b></div>
        <p className="muted">AETHER کی execution layer raw text کو shell میں نہیں بھیجتی۔ صرف allowlisted project commands چل سکتے ہیں۔</p>
      </div>
      <div className="panel">
        <h2>Project Commands</h2>
        {COMMANDS.map(c=><button className={selected===c.id?"command-option active":"command-option"} key={c.id} onClick={()=>setSelected(c.id)}><b>{c.label}</b><small>{c.description}</small></button>)}
      </div>
    </div>
    <div className="panel command-preview">
      <div className="head"><div><h2>Command Preview</h2><p>{effectiveShell}</p></div><button className="ghost" onClick={copy}>Copy</button></div>
      <pre>{command}</pre>
      <div className="command-actions"><button onClick={run} disabled={busy}>{busy?"Running…":"Run Safe Command"}</button>{message&&<span>{message}</span>}</div>
    </div>
  </section>
}
