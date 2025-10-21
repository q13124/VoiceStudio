#!/usr/bin/env powershell
# VoiceStudio CycloneDX + VRAM Telemetry + Cursor Launcher
# Advanced launcher for generating CycloneDX SBOMs, VRAM telemetry, and Cursor AI handoff

param(
    [switch]$SkipBuild,
    [switch]$SkipPython,
    [switch]$NoSnapshot,
    [switch]$LightSBOM,
    [switch]$InstallTelemetry,
    [switch]$OpenCursor,
    [switch]$PurgeOldFiles,
    [switch]$GenerateVRAMChart
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

Write-Host "VoiceStudio CycloneDX + VRAM Telemetry + Cursor Launcher"
Write-Host "Root: $Root"
Write-Host "Features: CycloneDX SBOMs, VRAM telemetry, Cursor AI integration"
Write-Host ""

# Purge old files if requested
if ($PurgeOldFiles) {
    Write-Host "Purging old handoff files (keeping last 10)..."
    $HandoffDir = Join-Path $Root "handoff"
    if (Test-Path $HandoffDir) {
        $oldFiles = Get-ChildItem -Path $HandoffDir -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 10
        foreach ($file in $oldFiles) {
            Remove-Item $file.FullName -Force
            Write-Host "Removed: $($file.Name)"
        }
        
        $oldSnapshots = Get-ChildItem -Path $HandoffDir -Filter "snapshot_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 5
        foreach ($file in $oldSnapshots) {
            Remove-Item $file.FullName -Force
            Write-Host "Removed snapshot: $($file.Name)"
        }
    }
}

# Generate VRAM chart if requested
if ($GenerateVRAMChart) {
    Write-Host "Generating VRAM usage chart..."
    $VRAMCsv = Join-Path $Root "logs\vram_telemetry.csv"
    if (Test-Path $VRAMCsv) {
        $ChartScript = @'
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

csv_path = r"C:\VoiceStudio\logsram_telemetry.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    df['time_utc'] = pd.to_datetime(df['time_utc'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['time_utc'], df['used_mb'], label='Used VRAM (MB)', linewidth=2)
    plt.plot(df['time_utc'], df['total_mb'], label='Total VRAM (MB)', linewidth=2, linestyle='--')
    
    plt.title('VoiceStudio GPU VRAM Usage Over Time')
    plt.xlabel('Time')
    plt.ylabel('VRAM (MB)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    chart_path = r"C:\VoiceStudio\logsram_usage_chart.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"VRAM chart saved: {chart_path}")
else:
    print("VRAM telemetry CSV not found")
'@
        
        $PyVenv = "C:\VoiceStudio\workers\python\vsdml\.venv\Scripts\python.exe"
        if (Test-Path $PyVenv) {
            try {
                $ChartScript | & $PyVenv -c "exec(open(0).read())"
                Write-Host "VRAM chart generated: $Root\logs\vram_usage_chart.png"
            } catch {
                Write-Warning "Failed to generate VRAM chart: $($_.Exception.Message)"
            }
        } else {
            Write-Warning "Python venv not found for chart generation"
        }
    } else {
        Write-Warning "VRAM telemetry CSV not found: $VRAMCsv"
    }
}

# Run the enhanced Auto Handoff script
$HandoffScript = Join-Path $Root "tools\VS-AutoHandoff.ps1"
$params = @()

if ($SkipBuild) { $params += "-SkipBuild" }
if ($SkipPython) { $params += "-SkipPython" }
if ($NoSnapshot) { $params += "-NoSnapshot" }
if ($LightSBOM) { $params += "-LightSBOM" }
if ($InstallTelemetry) { $params += "-InstallTelemetry" }
if ($OpenCursor) { $params += "-OpenCursor" }

Write-Host "Running Enhanced Auto Handoff with CycloneDX + Telemetry..."
& $HandoffScript @params

Write-Host "`nCycloneDX + VRAM Telemetry + Cursor integration completed!"
Write-Host "Report location: $Root\handoff\cursor_handoff.json"
Write-Host "CycloneDX Python: $Root\handoff\sbom_python_cyclonedx_*.json"
Write-Host "CycloneDX .NET: $Root\handoff\sbom_dotnet_cyclonedx_*.json"
Write-Host "VRAM telemetry: $Root\logs\vram_telemetry.csv"
Write-Host "Log location: $Root\logs\auto_handoff_*.log"
