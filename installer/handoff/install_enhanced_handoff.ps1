#!/usr/bin/env powershell
# VoiceStudio Enhanced Auto Handoff Installer
# Installs the enhanced Auto Handoff system with all advanced features

param(
    [switch]$Force,
    [string]$Root = "C:\VoiceStudio"
)

$ErrorActionPreference = 'Stop'

# Create directory structure
$tools  = Join-Path $Root 'tools'
$handoff= Join-Path $Root 'handoff'
$logs   = Join-Path $Root 'logs'

Write-Host "Creating VoiceStudio Enhanced Auto Handoff system..."
Write-Host "Root: $Root"

$null = New-Item -ItemType Directory -Force -Path $tools,$handoff,$logs

# Copy handoff files
$sourceDir = Split-Path $MyInvocation.MyCommand.Path
$handoffSource = Join-Path $sourceDir "handoff"

if (Test-Path $handoffSource) {
    Copy-Item -Path "$handoffSource\*" -Destination $handoff -Recurse -Force
    Write-Host "Copied enhanced handoff files to: $handoff"
} else {
    Write-Warning "Handoff source directory not found: $handoffSource"
}

# Create pins.json if it doesn't exist
$pinsPath = Join-Path $Root 'pins.json'
if (-not (Test-Path $pinsPath)) {
    $pinsConfig = @'
{
  "python": "3.10.*",
  "dotnet_sdk": "8.*",
  "torch": "2.2.2",
  "torchaudio": "2.2.2",
  "coqui_tts": "0.24.1",
  "transformers": "4.55.4",
  "faster_whisper": "1.0.3",
  "nv_driver_min": "546.00",
  "cuda_toolkit": "12.1",
  "ffmpeg": ">=6.0"
}
'@
    $pinsConfig | Set-Content $pinsPath -Encoding UTF8
    Write-Host "Created pins.json: $pinsPath"
}

# Copy VS-AutoHandoff.ps1 to tools directory
$handoffScript = Join-Path $handoff "VS-AutoHandoff.ps1"
if (Test-Path $handoffScript) {
    Copy-Item $handoffScript (Join-Path $tools "VS-AutoHandoff.ps1") -Force
    Write-Host "Installed enhanced: $tools\VS-AutoHandoff.ps1"
} else {
    Write-Warning "VS-AutoHandoff.ps1 not found: $handoffScript"
}

Write-Host "`nVoiceStudio Enhanced Auto Handoff system installed successfully!"
Write-Host "Features included:"
Write-Host "• Winget/Choco package management"
Write-Host "• SBOM export with file hashing"
Write-Host "• GPU VRAM pressure testing"
Write-Host "• Enhanced service monitoring"
Write-Host "• Comprehensive risk assessment"
Write-Host ""
Write-Host "Run: powershell -ExecutionPolicy Bypass -File $tools\VS-AutoHandoff.ps1"
Write-Host "Use -LightSBOM for faster runs without file hashing"
