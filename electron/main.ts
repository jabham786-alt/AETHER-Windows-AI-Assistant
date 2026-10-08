import {app,BrowserWindow,ipcMain} from "electron";import path from "node:path";import fs from "node:fs";import {spawn,ChildProcessWithoutNullStreams} from "node:child_process";
let win:BrowserWindow|null=null;let backend:ChildProcessWithoutNullStreams|null=null;

type SafeCommand="check_python"|"install_backend"|"run_backend_tests"|"install_frontend"|"typecheck"|"build";

function pythonExecutable(){
  if(process.env.AETHER_PYTHON)return process.env.AETHER_PYTHON;
  if(process.platform==="win32"){
    const local=path.join(app.getAppPath(),".venv","Scripts","python.exe");
    if(fs.existsSync(local))return local;
    return "python.exe";
  }
  const local=path.join(app.getAppPath(),".venv","bin","python");
  if(fs.existsSync(local))return local;
  return "python3";
}
const SAFE_COMMANDS:Record<SafeCommand,{args:string[]}>={
  check_python:{args:["--version"]},
  install_backend:{args:["-m","pip","install","-r",process.platform==="win32"?"backend\\requirements.txt":"backend/requirements.txt"]},
  run_backend_tests:{args:["-m","pytest",process.platform==="win32"?"backend\\tests":"backend/tests","-q"]},
  install_frontend:{args:["install"]},
  typecheck:{args:["run","typecheck"]},
  build:{args:["run","build"]},
};

function startBackend(){backend=spawn(pythonExecutable(),["-m","uvicorn","backend.main:app","--host","127.0.0.1","--port","8765"],{cwd:app.getAppPath(),windowsHide:true,stdio:"pipe"});backend.stderr.on("data",d=>console.error("[AETHER]",d.toString().trim()));}
async function ready(){for(let i=0;i<40;i++){try{if((await fetch("http://127.0.0.1:8765/api/health")).ok)return}catch{}await new Promise(r=>setTimeout(r,250))}throw Error("AETHER Core did not start")}

function detectShell(){
  if(process.env.WSL_DISTRO_NAME)return "wsl";
  const shell=process.env.SHELL?.toLowerCase()||"";
  if(shell.includes("bash"))return "bash";
  if(process.platform==="win32"&&process.env.PSModulePath)return "powershell";
  return process.platform==="win32"?"cmd":"bash";
}

function runSafeCommand(id:SafeCommand){
  const spec=SAFE_COMMANDS[id];if(!spec)throw Error("Unsupported command.");
  const file=id==="install_frontend"||id==="typecheck"||id==="build"?(process.platform==="win32"?"npm.cmd":"npm"):pythonExecutable();
  return new Promise<{code:number;stdout:string;stderr:string}>((resolve,reject)=>{
    const child=spawn(file,spec.args,{cwd:app.getAppPath(),windowsHide:true,shell:false,env:process.env});
    let stdout="",stderr="";
    child.stdout.on("data",d=>stdout+=d.toString());
    child.stderr.on("data",d=>stderr+=d.toString());
    const timer=setTimeout(()=>{child.kill();reject(Error("Command timed out after 5 minutes."))},300000);
    child.on("error",err=>{clearTimeout(timer);reject(err)});
    child.on("close",code=>{clearTimeout(timer);resolve({code:code??1,stdout:stdout.slice(-12000),stderr:stderr.slice(-12000)})});
  });
}

ipcMain.handle("app:info",()=>({name:"AETHER",version:app.getVersion(),platform:process.platform}));
ipcMain.handle("shell:info",()=>({shell:detectShell(),platform:process.platform}));
ipcMain.handle("command:run",async(_,id:SafeCommand)=>runSafeCommand(id));

app.whenReady().then(create);app.on("window-all-closed",()=>{backend?.kill();if(process.platform!=="darwin")app.quit()});app.on("before-quit",()=>backend?.kill());

async function create(){startBackend();await ready();win=new BrowserWindow({width:1440,height:920,minWidth:1100,minHeight:700,backgroundColor:"#070b14",webPreferences:{preload:path.join(__dirname,"preload.js"),contextIsolation:true,nodeIntegration:false,sandbox:true}});const dev=process.env.VITE_DEV_SERVER_URL;if(dev)await win.loadURL(dev);else await win.loadFile(path.join(app.getAppPath(),"dist","index.html"))}
