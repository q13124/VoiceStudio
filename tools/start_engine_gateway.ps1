# tools/start_engine_gateway.ps1
param([int]$Port=59120)

$ErrorActionPreference='Stop'

$py = "python"
$gw = Join-Path $PSScriptRoot "..\workers\ops\engine_gateway.py"

if (-not (Test-Path $py)) {
    Write-Error "Python not found at: $py"
    exit 1
}

if (-not (Test-Path $gw)) {
    Write-Error "Engine gateway not found at: $gw"
    exit 1
}

# Start engine gateway in background
Start-Process -FilePath $py -ArgumentList $gw -WindowStyle Hidden
Write-Host "Engine gateway starting on 127.0.0.1:$Port" -ForegroundColor Green
