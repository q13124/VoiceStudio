# VoiceStudio Restart with HuggingFace Fix
# This script ensures all HF endpoint issues are resolved

Write-Host "VoiceStudio HuggingFace Fix & Restart" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Force environment variables
Write-Host "Setting environment variables..." -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("HF_INFERENCE_API_BASE", "https://router.huggingface.co", "Process")
[Environment]::SetEnvironmentVariable("HF_ENDPOINT", "https://router.huggingface.co", "Process")
[Environment]::SetEnvironmentVariable("HF_HUB_ENDPOINT", "https://router.huggingface.co", "Process")

# Kill any existing processes
Write-Host "Stopping existing VoiceStudio processes..." -ForegroundColor Yellow
Get-Process -Name "*VoiceStudio*", "*python*" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*backend*" -or
    $_.CommandLine -like "*uvicorn*" -or
    $_.CommandLine -like "*main.py*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Clear caches
Write-Host "Clearing caches..." -ForegroundColor Yellow
Remove-Item "$env:LOCALAPPDATA\transformers" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\transformers" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "E:\VoiceStudio\models\hf_cache\*" -Recurse -Force -ErrorAction SilentlyContinue

# Run the force router script
Write-Host "Applying endpoint fixes..." -ForegroundColor Cyan
python force_hf_router.py

Write-Host ""
Write-Host "Starting VoiceStudio backend..." -ForegroundColor Green
Write-Host "The HuggingFace endpoint error should now be resolved!" -ForegroundColor Green
Write-Host ""

# Start backend
.\start_backend.ps1