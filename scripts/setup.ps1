$ErrorActionPreference="Stop"
if (!(Get-Command python -ErrorAction SilentlyContinue)) { throw "Python is required." }
if (!(Get-Command npm -ErrorAction SilentlyContinue)) { throw "Node.js/npm is required." }
if (!(Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
npm install
if (!(Test-Path ".env")) { Copy-Item .env.example .env }
Write-Host "Setup complete. Add an AI API key to .env, then run .\scripts\dev.ps1"