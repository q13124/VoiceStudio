# tools/start_dev_stack.ps1
# Quick start for development: engine gateway + dashboard

$ErrorActionPreference='Stop'

Write-Host "Starting VoiceStudio Development Stack..." -ForegroundColor Green

# Start engine gateway
Write-Host "Starting engine gateway..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\start_engine_gateway.ps1" | Out-Null

# Start dashboard
Write-Host "Starting dashboard..." -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\run_dashboard.ps1" -Port 5299 | Out-Null

Write-Host "Development stack started successfully!" -ForegroundColor Green
Write-Host "Engine Gateway: http://127.0.0.1:59120" -ForegroundColor Cyan
Write-Host "Dashboard: http://localhost:5299" -ForegroundColor Cyan
