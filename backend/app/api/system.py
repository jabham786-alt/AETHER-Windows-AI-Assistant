import platform,sys,psutil
from fastapi import APIRouter
router=APIRouter()
@router.get("/system/status")
def status():
 d=psutil.disk_usage("/")
 return {"cpu_percent":psutil.cpu_percent(interval=0.1),"memory_percent":psutil.virtual_memory().percent,"disk_percent":d.percent,"os":platform.platform(),"python_version":sys.version.split()[0],"hostname":platform.node()}