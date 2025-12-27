# VoiceStudio Backend Server Startup Script
# Handles port conflicts and starts the backend API

param(
    [int]$Port = 8001
)

Write-Host "=== VoiceStudio Backend Server Startup ===" -ForegroundColor Cyan

# Check if port is available
$portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Port $Port is already in use!" -ForegroundColor Yellow
    Write-Host "Process ID: $($portInUse.OwningProcess)" -ForegroundColor Yellow
    
    # Try alternative ports
    $alternativePorts = @(8001, 8002, 8080, 8888)
    $availablePort = $null
    
    foreach ($altPort in $alternativePorts) {
        $check = Get-NetTCPConnection -LocalPort $altPort -ErrorAction SilentlyContinue
        if (-not $check) {
            $availablePort = $altPort
            break
        }
    }
    
    if ($availablePort) {
        Write-Host "Using alternative port: $availablePort" -ForegroundColor Green
        $Port = $availablePort
    } else {
        Write-Host "No available ports found. Please free up a port or stop the process using port $Port" -ForegroundColor Red
        Write-Host "To stop the process: Stop-Process -Id $($portInUse.OwningProcess) -Force" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "Starting backend server on port $Port..." -ForegroundColor Green
Write-Host "Backend URL: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:$Port/docs" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to project root
$env:PYTHONPATH = "$PSScriptRoot"

# Start uvicorn from project root using module path
Set-Location "$PSScriptRoot"
uvicorn backend.api.main:app --reload --port $Port --host 0.0.0.0

