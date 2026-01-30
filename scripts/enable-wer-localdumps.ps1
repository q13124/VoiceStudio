Param(
  [ValidateSet("Enable", "Disable", "Status")]
  [string]$Mode = "Enable",
  [string]$AppExe = "VoiceStudio.App.exe",
  [string]$DumpFolder = "",
  [ValidateRange(1, 2)]
  [int]$DumpType = 2,
  [ValidateRange(1, 50)]
  [int]$DumpCount = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $DumpFolder -or $DumpFolder.Trim() -eq "") {
  $DumpFolder = Join-Path $env:LOCALAPPDATA "VoiceStudio\dumps"
}

$baseKey = "HKCU:\Software\Microsoft\Windows\Windows Error Reporting\LocalDumps"
$appKey = Join-Path $baseKey $AppExe

function Write-Status {
  if (-not (Test-Path $appKey)) {
    Write-Host "WER LocalDumps: not configured for $AppExe"
    Write-Host "Registry key: $appKey"
    return
  }

  $props = Get-ItemProperty -Path $appKey -ErrorAction SilentlyContinue
  Write-Host "WER LocalDumps: configured for $AppExe"
  Write-Host "Registry key: $appKey"
  if ($props) {
    if ($props.DumpFolder) { Write-Host "DumpFolder: $($props.DumpFolder)" }
    if ($props.DumpType) { Write-Host "DumpType: $($props.DumpType)" }
    if ($props.DumpCount) { Write-Host "DumpCount: $($props.DumpCount)" }
  }
}

switch ($Mode) {
  "Status" {
    Write-Status
    exit 0
  }
  "Disable" {
    if (Test-Path $appKey) {
      Remove-Item -Path $appKey -Recurse -Force -ErrorAction SilentlyContinue
      Write-Host "Removed WER LocalDumps configuration for $AppExe"
    } else {
      Write-Host "WER LocalDumps was not configured for $AppExe"
    }
    Write-Host "Dump folder (left intact): $DumpFolder"
    exit 0
  }
  "Enable" {
    New-Item -Path $appKey -Force | Out-Null
    New-ItemProperty -Path $appKey -Name "DumpFolder" -Value $DumpFolder -PropertyType ExpandString -Force | Out-Null
    New-ItemProperty -Path $appKey -Name "DumpType" -Value $DumpType -PropertyType DWord -Force | Out-Null
    New-ItemProperty -Path $appKey -Name "DumpCount" -Value $DumpCount -PropertyType DWord -Force | Out-Null

    New-Item -ItemType Directory -Path $DumpFolder -Force | Out-Null

    Write-Host "Enabled WER LocalDumps for $AppExe"
    Write-Host "DumpFolder: $DumpFolder"
    Write-Host "DumpType: $DumpType (1=mini, 2=full)"
    Write-Host "DumpCount: $DumpCount"
    Write-Host ""
    Write-Host "NOTE: full dumps can be large; clean $DumpFolder periodically."
    Write-Status
    exit 0
  }
}

