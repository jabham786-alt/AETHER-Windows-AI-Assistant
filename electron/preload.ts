import {contextBridge,ipcRenderer} from "electron";

const allowedCommands=["check_python","install_backend","run_backend_tests","install_frontend","typecheck","build"] as const;
type SafeCommand=typeof allowedCommands[number];

contextBridge.exposeInMainWorld("aether",{
  getAppInfo:()=>ipcRenderer.invoke("app:info"),
  getShellInfo:()=>ipcRenderer.invoke("shell:info"),
  runSafeCommand:(command:SafeCommand)=>{
    if(!allowedCommands.includes(command))return Promise.reject(new Error("Unsupported command."));
    return ipcRenderer.invoke("command:run",command);
  },
});

declare global{
  interface Window{
    aether:{
      getAppInfo:()=>Promise<{name:string;version:string;platform:string}>;
      getShellInfo:()=>Promise<{shell:string;platform:string}>;
      runSafeCommand:(command:SafeCommand)=>Promise<{code:number;stdout:string;stderr:string}>;
    }
  }
}
