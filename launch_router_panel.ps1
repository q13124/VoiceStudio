# Launch VoiceStudio PySide6 Router Panel
# Desktop GUI for VoiceStudio Router with WebSocket support

param(
    [string]$BaseUrl = "http://127.0.0.1:5090",
    [switch]$Help
)

if ($Help) {
    Write-Host "VoiceStudio PySide6 Router Panel Launcher" -ForegroundColor Cyan
    Write-Host "Usage: .\launch_router_panel.ps1 [-BaseUrl <url>]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Green
    Write-Host "  -BaseUrl    Router base URL (default: http://127.0.0.1:5090)" -ForegroundColor White
    Write-Host "  -Help       Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Features:" -ForegroundColor Green
    Write-Host "  • Desktop GUI for VoiceStudio Router" -ForegroundColor White
    Write-Host "  • Real-time WebSocket streaming" -ForegroundColor White
    Write-Host "  • Sync and async TTS generation" -ForegroundColor White
    Write-Host "  • Engine health monitoring" -ForegroundColor White
    Write-Host "  • Audio playback" -ForegroundColor White
    exit 0
}

$ErrorActionPreference = 'Stop'

Write-Host "=== VoiceStudio PySide6 Router Panel ===" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Yellow

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if PySide6 is installed
try {
    python -c "import PySide6; print('PySide6:', PySide6.__version__)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing PySide6..." -ForegroundColor Yellow
        pip install PySide6
    }
} catch {
    Write-Host "Error installing PySide6: $_" -ForegroundColor Red
    exit 1
}

# Check if requests is installed
try {
    python -c "import requests; print('requests:', requests.__version__)" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing requests..." -ForegroundColor Yellow
        pip install requests
    }
} catch {
    Write-Host "Error installing requests: $_" -ForegroundColor Red
    exit 1
}

# Launch the router panel
Write-Host "Launching VoiceStudio Router Panel..." -ForegroundColor Green
python launch_router_panel.py
