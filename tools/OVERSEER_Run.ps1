
param([string]$ConfigPath = ".\config\overseer_config.yaml")
Write-Host "VoiceStudio Overseer — quick digest"
if (-not (Test-Path $ConfigPath)) { Write-Host "CONFIG_MISSING: $ConfigPath" -ForegroundColor Yellow } else { Write-Host "CONFIG_OK: $ConfigPath" -ForegroundColor Green }
python -m workers.orchestrator --once
