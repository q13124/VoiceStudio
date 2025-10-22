#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Professional Bootstrapper Creator
Advanced installer system with remote prerequisites
"""

import os
import json
import subprocess
from pathlib import Path


class VoiceStudioBootstrapperCreator:
    def __init__(self):
        self.repo_path = Path("C:/Users/Tyler/VoiceStudio")
        self.bootstrapper_path = (
            self.repo_path / "Installer" / "VoiceStudio.Bootstrapper"
        )
        self.out_path = self.repo_path / "out"
        self.msi_path = self.out_path / "msi"
        self.bundle_path = self.out_path / "bundle"

    def create_directories(self):
        """Create necessary directories"""
        self.bootstrapper_path.mkdir(parents=True, exist_ok=True)
        self.msi_path.mkdir(parents=True, exist_ok=True)
        self.bundle_path.mkdir(parents=True, exist_ok=True)

    def create_sha256_utility(self):
        """Create SHA256 utility script"""
        util_content = """param([Parameter(Mandatory=$true)][string]$Url)
$ErrorActionPreference='Stop'
$dst = Join-Path $env:TEMP ("dl_" + [System.IO.Path]::GetFileName($Url))
try {
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $dst
    $sha = (Get-FileHash -Algorithm SHA256 $dst).Hash.ToLowerInvariant()
    Write-Host "SHA256  : $sha"
    Write-Host "File    : $dst"
    Write-Host "Size    : $((Get-Item $dst).Length) bytes"
} finally {
    if (Test-Path $dst) { Remove-Item $dst -Force }
}
"""

        util_path = self.bootstrapper_path / "Get-RemoteSHA256.ps1"
        with open(util_path, "w", encoding="utf-8") as f:
            f.write(util_content)

        print(f"Created SHA256 utility: {util_path}")

    def create_bundle_wxs(self):
        """Create WiX Bundle with remote prerequisites"""
        bundle_content = """<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi"
     xmlns:bal="http://schemas.microsoft.com/wix/BalExtension">
  <Bundle Name="VoiceStudio Ultimate"
          Version="1.0.0.0"
          Manufacturer="UltraClone Technologies"
          UpgradeCode="B6C8CDA7-2B4D-4B6A-893C-9E8D3B9E22B9"
          IconSourceFile="bundle.ico">

    <BootstrapperApplicationRef Id="WixStandardBootstrapperApplication.RtfLicense"
                                SuppressOptionsUI="no" ShowVersion="yes" />

    <Chain>
      <!-- VC++ 2015–2022 x64 (REMOTE) -->
      <ExePackage Id="VCppRedistX64"
                  PerMachine="yes"
                  Vital="yes"
                  Compressed="no"
                  InstallCommand="/quiet /norestart"
                  RepairCommand="/repair /quiet /norestart"
                  DetectCondition="VC14X64_INSTALLED">
        <RemotePayload
          Description="Microsoft Visual C++ 2015-2022 Redistributable (x64)"
          ProductName="Microsoft Visual C++ 2015-2022 Redistributable (x64)"
          DownloadUrl="$(var.VCREDIST_URL)"
          Hash="$(var.VCREDIST_SHA256)" />
      </ExePackage>

      <!-- FFmpeg (REMOTE) -->
      <ExePackage Id="FFmpegWin64"
                  PerMachine="yes"
                  Vital="no"
                  Compressed="no"
                  InstallCommand="/S"
                  DetectCondition="FFMPEG_PRESENT">
        <RemotePayload
          Description="FFmpeg for Windows (x64)"
          ProductName="FFmpeg x64"
          DownloadUrl="$(var.FFMPEG_URL)"
          Hash="$(var.FFMPEG_SHA256)" />
      </ExePackage>

      <!-- Python Runtime (REMOTE) -->
      <ExePackage Id="PythonRuntime"
                  PerMachine="yes"
                  Vital="yes"
                  Compressed="no"
                  InstallCommand="/quiet InstallAllUsers=1 PrependPath=1"
                  DetectCondition="PYTHON_INSTALLED">
        <RemotePayload
          Description="Python 3.11 Runtime"
          ProductName="Python 3.11"
          DownloadUrl="$(var.PYTHON_URL)"
          Hash="$(var.PYTHON_SHA256)" />
      </ExePackage>

      <!-- VoiceStudio Core MSI -->
      <MsiPackage Id="VoiceStudioCoreMsi"
                  SourceFile="..\\..\\out\\msi\\VoiceStudioCore.msi"
                  DisplayInternalUI="no"
                  Compressed="yes"
                  Vital="yes" />

      <!-- VoiceStudio Engines MSI -->
      <MsiPackage Id="VoiceStudioEnginesMsi"
                  SourceFile="..\\..\\out\\msi\\VoiceStudioEngines.msi"
                  DisplayInternalUI="no"
                  Compressed="yes"
                  Vital="yes" />

      <!-- VoiceStudio Content MSI -->
      <MsiPackage Id="VoiceStudioContentMsi"
                  SourceFile="..\\..\\out\\msi\\VoiceStudioContent.msi"
                  DisplayInternalUI="no"
                  Compressed="yes"
                  Vital="yes" />
    </Chain>

    <!-- Detection variables -->
    <Variable Name="VC14X64_INSTALLED" Type="string" Value="false" bal:Overridable="yes" />
    <Variable Name="FFMPEG_PRESENT" Type="string" Value="false" bal:Overridable="yes" />
    <Variable Name="PYTHON_INSTALLED" Type="string" Value="false" bal:Overridable="yes" />

    <!-- Require admin -->
    <bal:Condition Message="Please run as Administrator.">Privileged</bal:Condition>

    <!-- System requirements -->
    <bal:Condition Message="Windows 10 or later is required.">
      <![CDATA[Installed OR (VersionNT >= v6.3)]]>
    </bal:Condition>

    <bal:Condition Message="At least 8GB RAM is recommended for voice cloning.">
      <![CDATA[Installed OR (TotalPhysicalMemory >= 8000000000)]]>
    </bal:Condition>
  </Bundle>
</Wix>"""

        bundle_path = self.bootstrapper_path / "Bundle.Remote.wxs"
        with open(bundle_path, "w", encoding="utf-8") as f:
            f.write(bundle_content)

        print(f"Created Bundle WXS: {bundle_path}")

    def create_build_script(self):
        """Create build script for remote bundle"""
        build_content = """param(
  [Parameter(Mandatory=$true)][string]$VCRedistUrl,
  [Parameter(Mandatory=$true)][string]$VCRedistSha256,
  [Parameter(Mandatory=$true)][string]$FfmpegUrl,
  [Parameter(Mandatory=$true)][string]$FfmpegSha256,
  [Parameter(Mandatory=$true)][string]$PythonUrl,
  [Parameter(Mandatory=$true)][string]$PythonSha256
)
$ErrorActionPreference='Stop'

function Require-Tool([string]$t){
    if(-not (Get-Command $t -ErrorAction SilentlyContinue)){
        throw "Missing tool: $t (install WiX v3 & add to PATH)"
    }
}

Require-Tool candle.exe
Require-Tool light.exe

$here = Split-Path $PSCommandPath -Parent
$msiDir = Resolve-Path (Join-Path $here '..\\..\\out\\msi') | % Path
$out   = Resolve-Path (Join-Path $here '..\\..\\out\\bundle') -ErrorAction SilentlyContinue
if(-not $out){
    $out = Join-Path $here '..\\..\\out\\bundle'
    New-Item -ItemType Directory -Force -Path $out | Out-Null
}

# Check for required MSI files
$requiredMsis = @(
    'VoiceStudioCore.msi',
    'VoiceStudioEngines.msi',
    'VoiceStudioContent.msi'
)

foreach($msi in $requiredMsis) {
    $msiPath = Join-Path $msiDir $msi
    if(!(Test-Path $msiPath)){
        throw "Missing required MSI: $msiPath"
    }
}

# Build variables
$vars = @(
    "-dVCREDIST_URL=`"$VCRedistUrl`"",
    "-dVCREDIST_SHA256=`"$VCRedistSha256`"",
    "-dFFMPEG_URL=`"$FfmpegUrl`"",
    "-dFFMPEG_SHA256=`"$FfmpegSha256`"",
    "-dPYTHON_URL=`"$PythonUrl`"",
    "-dPYTHON_SHA256=`"$PythonSha256`"",
    "-dVC14X64_INSTALLED=false",
    "-dFFMPEG_PRESENT=false",
    "-dPYTHON_INSTALLED=false"
)

# Compile & link the REMOTE bundle
Push-Location $here
try {
    Write-Host "Compiling Bundle.Remote.wxs..." -ForegroundColor Yellow
    & candle.exe Bundle.Remote.wxs -ext WixBalExtension -ext WixUtilExtension @vars -o Bundle.Remote.wixobj

    Write-Host "Linking bundle..." -ForegroundColor Yellow
    & light.exe Bundle.Remote.wixobj -ext WixBalExtension -ext WixUtilExtension -o (Join-Path $out 'VoiceStudioUltimateSetup.exe')

    Write-Host "Remote bundle built successfully!" -ForegroundColor Green
    Write-Host "Output: $out\\VoiceStudioUltimateSetup.exe" -ForegroundColor Cyan
    Write-Host "Tip: Use Get-RemoteSHA256.ps1 <URL> to compute SHA256 hashes." -ForegroundColor Cyan
} finally {
    Pop-Location
}"""

        build_path = self.bootstrapper_path / "build-remote.ps1"
        with open(build_path, "w", encoding="utf-8") as f:
            f.write(build_content)

        print(f"Created build script: {build_path}")

    def create_detection_script(self):
        """Create system detection script"""
        detection_content = """# VoiceStudio Ultimate - System Detection Script
param([switch]$Quiet)

$ErrorActionPreference='Stop'

function Write-Status([string]$message, [bool]$success = $true) {
    if(-not $Quiet) {
        $color = if($success) { 'Green' } else { 'Red' }
        Write-Host $message -ForegroundColor $color
    }
}

function Test-VCRedist {
    $regPath = "HKLM:\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64"
    return (Test-Path $regPath)
}

function Test-FFmpeg {
    try {
        $null = Get-Command ffmpeg -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-Python {
    try {
        $python = Get-Command python -ErrorAction Stop
        $version = & python --version 2>&1
        return $version -match "Python 3\\.(11|12)"
    } catch {
        return $false
    }
}

function Test-CUDA {
    try {
        $cudaPath = "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA"
        return (Test-Path $cudaPath)
    } catch {
        return $false
    }
}

function Test-SystemRequirements {
    $osVersion = [System.Environment]::OSVersion.Version
    $isWindows10OrLater = $osVersion.Major -ge 10

    $totalMemory = (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory
    $hasEnoughRAM = $totalMemory -ge 8000000000  # 8GB

    return @{
        Windows10OrLater = $isWindows10OrLater
        HasEnoughRAM = $hasEnoughRAM
        TotalRAM = [math]::Round($totalMemory / 1GB, 2)
    }
}

# Main detection
Write-Status "VoiceStudio Ultimate - System Detection" $true
Write-Status "=======================================" $true

$requirements = Test-SystemRequirements
Write-Status "Windows 10+: $($requirements.Windows10OrLater)" $requirements.Windows10OrLater
Write-Status "RAM (8GB+): $($requirements.HasEnoughRAM) ($($requirements.TotalRAM)GB)" $requirements.HasEnoughRAM

Write-Status "VC++ Redist: $(Test-VCRedist)" (Test-VCRedist)
Write-Status "FFmpeg: $(Test-FFmpeg)" (Test-FFmpeg)
Write-Status "Python 3.11+: $(Test-Python)" (Test-Python)
Write-Status "CUDA: $(Test-CUDA)" (Test-CUDA)

$allGood = $requirements.Windows10OrLater -and $requirements.HasEnoughRAM -and (Test-VCRedist) -and (Test-FFmpeg) -and (Test-Python)

if($allGood) {
    Write-Status "System ready for VoiceStudio Ultimate!" $true
    exit 0
} else {
    Write-Status "System needs updates for optimal VoiceStudio performance." $false
    exit 1
}"""

        detection_path = self.bootstrapper_path / "Test-SystemRequirements.ps1"
        with open(detection_path, "w", encoding="utf-8") as f:
            f.write(detection_content)

        print(f"Created detection script: {detection_path}")

    def create_installer_config(self):
        """Create installer configuration"""
        config = {
            "installer": {
                "name": "VoiceStudio Ultimate",
                "version": "1.0.0.0",
                "manufacturer": "UltraClone Technologies",
                "upgrade_code": "B6C8CDA7-2B4D-4B6A-893C-9E8D3B9E22B9",
            },
            "prerequisites": {
                "vc_redist": {
                    "name": "Microsoft Visual C++ 2015-2022 Redistributable (x64)",
                    "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
                    "install_command": "/quiet /norestart",
                    "detection_key": "HKLM:\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\x64",
                },
                "ffmpeg": {
                    "name": "FFmpeg for Windows (x64)",
                    "url": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
                    "install_command": "/S",
                    "detection_command": "ffmpeg -version",
                },
                "python": {
                    "name": "Python 3.11 Runtime",
                    "url": "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe",
                    "install_command": "/quiet InstallAllUsers=1 PrependPath=1",
                    "detection_command": "python --version",
                },
            },
            "requirements": {
                "os": "Windows 10 or later",
                "ram": "8GB minimum (16GB recommended)",
                "disk_space": "10GB free space",
                "gpu": "CUDA-compatible GPU (recommended)",
            },
        }

        config_path = self.bootstrapper_path / "installer-config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"Created installer config: {config_path}")

    def create_readme(self):
        """Create README for bootstrapper"""
        readme_content = """# VoiceStudio Ultimate - Professional Installer

This directory contains the WiX Burn bootstrapper for VoiceStudio Ultimate, a professional voice cloning platform.

## Files

- `Bundle.Remote.wxs` - WiX Bundle definition with remote prerequisites
- `build-remote.ps1` - Build script for creating the installer
- `Get-RemoteSHA256.ps1` - Utility to compute SHA256 hashes for remote files
- `Test-SystemRequirements.ps1` - System requirements detection script
- `installer-config.json` - Installer configuration

## Prerequisites

1. **WiX Toolset v3** - Install from https://wixtoolset.org/
2. **PowerShell 5.1+** - Usually pre-installed on Windows 10+

## Building the Installer

1. **Get SHA256 hashes for remote files:**
   ```powershell
   .\\Get-RemoteSHA256.ps1 "https://aka.ms/vs/17/release/vc_redist.x64.exe"
   .\\Get-RemoteSHA256.ps1 "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
   .\\Get-RemoteSHA256.ps1 "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
   ```

2. **Build the installer:**
   ```powershell
   .\\build-remote.ps1 -VCRedistUrl "https://aka.ms/vs/17/release/vc_redist.x64.exe" -VCRedistSha256 "hash" -FfmpegUrl "url" -FfmpegSha256 "hash" -PythonUrl "url" -PythonSha256 "hash"
   ```

3. **Output:** `..\\..\\out\\bundle\\VoiceStudioUltimateSetup.exe`

## System Requirements

- **OS:** Windows 10 or later
- **RAM:** 8GB minimum (16GB recommended)
- **Disk:** 10GB free space
- **GPU:** CUDA-compatible GPU (recommended for voice cloning)

## Features

- **Remote Prerequisites:** Downloads VC++ Redist, FFmpeg, and Python automatically
- **Professional UI:** WiX Standard Bootstrapper with license display
- **System Detection:** Validates system requirements before installation
- **Admin Rights:** Requires administrator privileges for system-wide installation
- **Upgrade Support:** Handles upgrades gracefully with proper versioning

## Voice Cloning Capabilities

VoiceStudio Ultimate includes:

- **XTTS-v2 Engine** - High-quality multilingual voice cloning
- **OpenVoice V2** - Advanced voice synthesis with prosody control
- **CosyVoice 2** - Professional voice generation
- **Whisper ASR** - Automatic speech recognition
- **Pyannote** - Speaker diarization and analysis
- **DSP Chain** - Professional audio mastering pipeline

## Support

For technical support and documentation, visit the VoiceStudio Ultimate project repository.
"""

        readme_path = self.bootstrapper_path / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"Created README: {readme_path}")

    def run_complete_setup(self):
        """Run complete bootstrapper setup"""
        print("VoiceStudio Ultimate - Professional Bootstrapper Creator")
        print("=" * 60)

        self.create_directories()
        self.create_sha256_utility()
        self.create_bundle_wxs()
        self.create_build_script()
        self.create_detection_script()
        self.create_installer_config()
        self.create_readme()

        print("\n" + "=" * 60)
        print("BOOTSTRAPPER SETUP COMPLETE")
        print("=" * 60)
        print(f"Bootstrapper directory: {self.bootstrapper_path}")
        print(f"Output directory: {self.bundle_path}")
        print("\nNext steps:")
        print("1. Install WiX Toolset v3")
        print("2. Run Get-RemoteSHA256.ps1 to get hashes")
        print("3. Run build-remote.ps1 to create installer")
        print("4. Test installer on target systems")


def main():
    creator = VoiceStudioBootstrapperCreator()
    creator.run_complete_setup()


if __name__ == "__main__":
    main()
