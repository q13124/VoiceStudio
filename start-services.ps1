# VoiceStudio Service Starter (PowerShell)
# PowerShell script to start VoiceStudio services

Write-Host "Starting VoiceStudio Services..." -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

try {
    # Start the service manager
    python start-services.py
} catch {
    Write-Host "Error starting services: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Services stopped." -ForegroundColor Yellow
