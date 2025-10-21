#!/usr/bin/env powershell
# VoiceStudio Ultimate Uninstaller

param([switch]$Silent)

# Run the main installer with uninstall flag
$InstallerPath = Join-Path $PSScriptRoot "install.ps1"
if (Test-Path $InstallerPath) {
    & $InstallerPath -Uninstall -Silent:$Silent
} else {
    Write-Error "Installer not found. Cannot uninstall."
    exit 1
}
