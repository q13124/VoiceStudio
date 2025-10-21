#!/usr/bin/env powershell
# VoiceStudio Enhanced Auto Handoff Launcher
# Quick launcher for generating enhanced Cursor AI handoff reports

param(
    [switch]$SkipBuild,
    [switch]$SkipPython,
    [switch]$NoSnapshot,
    [switch]$LightSBOM,
    [switch]$OpenReport
)

$ErrorActionPreference = "Stop"

# Find VoiceStudio installation
$possibleRoots = @(
    "C:\Program Files\VoiceStudio",
    "C:\VoiceStudio",
    (Split-Path $MyInvocation.MyCommand.Path -Parent)
)

$Root = $null
foreach ($possibleRoot in $possibleRoots) {
    if (Test-Path (Join-Path $possibleRoot "tools\VS-AutoHandoff.ps1")) {
        $Root = $possibleRoot
        break
    }
}

if (-not $Root) {
    Write-Error "VoiceStudio installation not found. Please ensure VoiceStudio is installed."
    exit 1
}

Write-Host "VoiceStudio Enhanced Auto Handoff Launcher"
Write-Host "Root: $Root"
Write-Host "Features: Winget/Choco, SBOM, GPU VRAM testing"
Write-Host ""

# Run the enhanced Auto Handoff script
$HandoffScript = Join-Path $Root "tools\VS-AutoHandoff.ps1"
$params = @()

if ($SkipBuild) { $params += "-SkipBuild" }
if ($SkipPython) { $params += "-SkipPython" }
if ($NoSnapshot) { $params += "-NoSnapshot" }
if ($LightSBOM) { $params += "-LightSBOM" }

Write-Host "Running Enhanced Auto Handoff..."
& $HandoffScript @params

# Open report if requested
if ($OpenReport) {
    $ReportPath = Join-Path $Root "handoff\cursor_handoff.json"
    if (Test-Path $ReportPath) {
        Write-Host "Opening handoff report..."
        Start-Process notepad.exe $ReportPath
    } else {
        Write-Warning "Handoff report not found: $ReportPath"
    }
}

Write-Host "`nEnhanced Auto Handoff completed!"
Write-Host "Report location: $Root\handoff\cursor_handoff.json"
Write-Host "SBOM location: $Root\handoff\sbom_*.json"
Write-Host "Log location: $Root\logs\auto_handoff_*.log"
