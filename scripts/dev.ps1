$ErrorActionPreference="Stop"
if (!(Test-Path ".venv\Scripts\python.exe")) { & ".\scripts\setup.ps1" }
npm run dev
