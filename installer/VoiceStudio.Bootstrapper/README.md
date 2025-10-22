# VoiceStudio Ultimate - Professional Installer

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
   .\Get-RemoteSHA256.ps1 "https://aka.ms/vs/17/release/vc_redist.x64.exe"
   .\Get-RemoteSHA256.ps1 "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
   .\Get-RemoteSHA256.ps1 "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
   ```

2. **Build the installer:**
   ```powershell
   .\build-remote.ps1 -VCRedistUrl "https://aka.ms/vs/17/release/vc_redist.x64.exe" -VCRedistSha256 "hash" -FfmpegUrl "url" -FfmpegSha256 "hash" -PythonUrl "url" -PythonSha256 "hash"
   ```

3. **Output:** `..\..\out\bundle\VoiceStudioUltimateSetup.exe`

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
