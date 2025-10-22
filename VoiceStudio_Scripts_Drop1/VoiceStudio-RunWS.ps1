<# 
VoiceStudio-RunWS.ps1
- Launches uvicorn with the /v1/stream WebSocket from app.core.api.ws_stream
- Expects a FastAPI app factory here for demo purposes
#>
[CmdletBinding()]
param(
  [string]$ProjectRoot = $(Join-Path $env:USERPROFILE "VoiceStudio"),
  [int]$Port = 5071
)

$ErrorActionPreference = 'Stop'

function Write-OK($m){ Write-Host "[OK]   $m" -ForegroundColor Green }
function Write-Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Err($m){ Write-Error $m }

# venv python
$venvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if(-not (Test-Path $venvPy)){ Write-Err "Venv python not found at $venvPy. Run the installer script first."; exit 1 }

# create a tiny FastAPI app loader if missing
$appPy = Join-Path $ProjectRoot "app\main_ws_demo.py"
if(-not (Test-Path $appPy)){
  New-Item -ItemType Directory -Force -Path (Split-Path $appPy) | Out-Null
  @"
from fastapi import FastAPI
from app.core.api.ws_stream import router as ws_router

app = FastAPI()
app.include_router(ws_router, prefix="/v1")
"@ | Set-Content -Path $appPy -Encoding UTF8
  Write-OK "Created demo FastAPI app: app/main_ws_demo.py"
}

Push-Location $ProjectRoot
try{
  & $venvPy -m uvicorn app.main_ws_demo:app --host 127.0.0.1 --port $Port --reload
} finally {
  Pop-Location
}
