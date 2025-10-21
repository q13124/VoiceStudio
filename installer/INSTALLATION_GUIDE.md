# VoiceStudio Ultimate Installation Guide

## Overview

VoiceStudio Ultimate is a professional voice cloning application with real-time capabilities, advanced AI model integration, and enterprise-grade features. This guide covers multiple installation methods and deployment options.

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10 version 19041 or later, Windows 11
- **Processor**: Intel Core i5-8400 or AMD Ryzen 5 2600 (or equivalent)
- **Memory**: 8 GB RAM (16 GB recommended)
- **Storage**: 15 GB available disk space
- **Graphics**: DirectX 12 compatible graphics card
- **Network**: Internet connection for initial setup

### Recommended Requirements

- **Operating System**: Windows 11 22H2 or later
- **Processor**: Intel Core i7-10700K or AMD Ryzen 7 3700X (or equivalent)
- **Memory**: 32 GB RAM
- **Storage**: 50 GB available disk space (SSD recommended)
- **Graphics**: NVIDIA RTX 3060 or AMD RX 6600 XT (or equivalent)
- **Network**: High-speed internet connection

## Installation Methods

### Method 1: Automated Installer (Recommended)

1. **Download the installer**:

   ```bash
   # Download the Python installer
   python installer/voice_studio_installer.py
   ```

2. **Run as Administrator**:

   - Right-click on the installer
   - Select "Run as administrator"
   - Follow the installation wizard

3. **Installation Process**:
   - System requirements check
   - Dependency installation (.NET Runtime, Python packages)
   - Directory structure creation
   - Application files copying
   - Application building
   - Shortcuts creation
   - Windows service registration
   - Configuration setup
   - Post-installation testing

### Method 2: PowerShell Deployment Script

1. **Open PowerShell as Administrator**:

   ```powershell
   # Navigate to the VoiceStudio directory
   cd C:\path\to\VoiceStudio

   # Run the deployment script
   .\installer\Deploy-VoiceStudio.ps1 -BuildType Release
   ```

2. **Advanced Options**:

   ```powershell
   # Custom installation path
   .\installer\Deploy-VoiceStudio.ps1 -InstallPath "C:\VoiceStudio" -DataPath "C:\VoiceStudioData"

   # Create MSI package
   .\installer\Deploy-VoiceStudio.ps1 -CreateMSI

   # Skip post-installation tests
   .\installer\Deploy-VoiceStudio.ps1 -SkipTests
   ```

### Method 3: MSI Package Installation

1. **Build MSI Package**:

   ```bash
   # Using WiX Toolset
   candle installer/VoiceStudio.wxs -out installer/VoiceStudio.wixobj
   light installer/VoiceStudio.wixobj -out installer/VoiceStudio.msi
   ```

2. **Install MSI Package**:
   - Double-click `VoiceStudio.msi`
   - Follow the installation wizard
   - The installer will handle all dependencies automatically

### Method 4: Manual Installation

1. **Install Prerequisites**:

   ```bash
   # Install .NET Desktop Runtime 8.0
   # Download from: https://dotnet.microsoft.com/download/dotnet/8.0

   # Install Python 3.11+
   # Download from: https://www.python.org/downloads/

   # Install Python packages
   pip install fastapi uvicorn numpy torch transformers tokenizers psutil websockets aiohttp
   ```

2. **Create Directory Structure**:

   ```bash
   mkdir "C:\Program Files\VoiceStudio"
   mkdir "C:\Program Files\VoiceStudio\bin"
   mkdir "C:\Program Files\VoiceStudio\services"
   mkdir "C:\Program Files\VoiceStudio\config"
   mkdir "C:\ProgramData\VoiceStudio"
   mkdir "C:\ProgramData\VoiceStudio\workers"
   mkdir "C:\ProgramData\VoiceStudio\workers\ops"
   mkdir "C:\ProgramData\VoiceStudio\models"
   mkdir "C:\ProgramData\VoiceStudio\cache"
   ```

3. **Copy Application Files**:

   ```bash
   # Copy WinUI application
   xcopy VoiceStudioWinUI "C:\Program Files\VoiceStudio\VoiceStudioWinUI" /E /I

   # Copy services
   xcopy services "C:\Program Files\VoiceStudio\services" /E /I

   # Copy workers
   xcopy "C:\ProgramData\VoiceStudio\workers" "C:\ProgramData\VoiceStudio\workers" /E /I

   # Copy solution files
   copy VoiceStudio.sln "C:\Program Files\VoiceStudio\"
   xcopy VoiceStudio.Contracts "C:\Program Files\VoiceStudio\VoiceStudio.Contracts" /E /I
   xcopy UltraClone.EngineService "C:\Program Files\VoiceStudio\UltraClone.EngineService" /E /I
   ```

4. **Build Application**:

   ```bash
   cd "C:\Program Files\VoiceStudio"
   dotnet build VoiceStudio.sln --configuration Release
   dotnet publish VoiceStudioWinUI\VoiceStudioWinUI.csproj --configuration Release --runtime win-x64 --self-contained true --output bin
   ```

5. **Create Shortcuts**:

   - Desktop shortcut: `C:\Program Files\VoiceStudio\bin\VoiceStudioWinUI.exe`
   - Start Menu shortcuts in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\VoiceStudio\`

6. **Register Windows Service**:
   ```bash
   # Create service script
   python "C:\Program Files\VoiceStudio\bin\voice_studio_service.py" install
   ```

## Post-Installation Configuration

### 1. Initial Setup

After installation, VoiceStudio will create default configuration files:

- **Main Config**: `C:\Program Files\VoiceStudio\config\voice_studio_config.json`
- **Service Config**: `C:\Program Files\VoiceStudio\config\appsettings.json`
- **Worker Config**: `C:\ProgramData\VoiceStudio\workers\worker_config.json`

### 2. Service Configuration

```json
{
  "services": {
    "web_server": {
      "host": "127.0.0.1",
      "port": 8083,
      "enabled": true
    },
    "realtime_service": {
      "enabled": true,
      "buffer_size": 100,
      "latency_mode": "low"
    }
  }
}
```

### 3. AI Model Configuration

```json
{
  "ai_models": {
    "gpt_sovits_2": {
      "enabled": true,
      "path": "C:\\ProgramData\\VoiceStudio\\models\\gpt_sovits_2"
    },
    "coqui_xtts_3": {
      "enabled": true,
      "path": "C:\\ProgramData\\VoiceStudio\\models\\coqui_xtts_3"
    }
  }
}
```

### 4. Worker Configuration

```json
{
  "workers": {
    "max_workers": 32,
    "worker_directory": "C:\\ProgramData\\VoiceStudio\\workers",
    "enabled": true
  }
}
```

## Starting VoiceStudio

### 1. Desktop Application

- Double-click the desktop shortcut "VoiceStudio Ultimate"
- Or navigate to Start Menu > VoiceStudio > VoiceStudio Ultimate

### 2. Windows Service

```bash
# Start the service
net start VoiceStudio

# Stop the service
net stop VoiceStudio

# Check service status
sc query VoiceStudio
```

### 3. Command Line

```bash
# Start web server directly
cd "C:\Program Files\VoiceStudio"
python services\voice_cloning\ultimate_web_server.py --host 127.0.0.1 --port 8083

# Start WinUI application
cd "C:\Program Files\VoiceStudio\bin"
VoiceStudioWinUI.exe
```

## Verification

### 1. Check Installation

```bash
# Verify files exist
dir "C:\Program Files\VoiceStudio\bin\VoiceStudioWinUI.exe"
dir "C:\Program Files\VoiceStudio\services\voice_cloning\ultimate_web_server.py"

# Check service status
sc query VoiceStudio

# Test web API
curl http://127.0.0.1:8083/api/status
```

### 2. Test Features

1. **Basic Voice Cloning**:

   - Select a reference audio file
   - Enter target text
   - Choose AI model
   - Click "Clone Voice"

2. **Real-Time Processing**:

   - Enable "Real-time Processing"
   - Select audio input source
   - Adjust buffer size and latency mode
   - Click "Start Real-Time"

3. **Advanced Features**:
   - Configure voice parameters (speed, pitch, volume)
   - Set emotion and accent
   - Adjust processing options
   - Test batch processing

## Troubleshooting

### Common Issues

1. **Service Won't Start**:

   ```bash
   # Check service logs
   eventvwr.msc
   # Look for VoiceStudio service errors

   # Restart service
   net stop VoiceStudio
   net start VoiceStudio
   ```

2. **Web Server Connection Failed**:

   ```bash
   # Check if port 8083 is available
   netstat -an | findstr 8083

   # Check firewall settings
   # Allow VoiceStudio through Windows Firewall
   ```

3. **Python Package Issues**:

   ```bash
   # Reinstall packages
   pip install --upgrade fastapi uvicorn numpy torch transformers tokenizers psutil websockets aiohttp

   # Check Python version
   python --version
   ```

4. **Build Errors**:

   ```bash
   # Clean and rebuild
   dotnet clean VoiceStudio.sln
   dotnet build VoiceStudio.sln --configuration Release

   # Check .NET runtime
   dotnet --list-runtimes
   ```

### Log Files

- **Installation Log**: `installer.log`
- **Application Log**: `C:\Program Files\VoiceStudio\logs\`
- **Service Log**: Windows Event Viewer
- **Web Server Log**: Console output or log files

### Performance Optimization

1. **GPU Acceleration**:

   - Ensure NVIDIA drivers are up to date
   - Enable GPU acceleration in settings
   - Check CUDA compatibility

2. **Memory Optimization**:

   - Adjust worker count based on available RAM
   - Enable result caching
   - Configure buffer sizes appropriately

3. **Storage Optimization**:
   - Use SSD for model storage
   - Enable disk caching
   - Clean temporary files regularly

## Uninstallation

### Method 1: Control Panel

1. Open "Programs and Features"
2. Find "VoiceStudio Ultimate"
3. Click "Uninstall"
4. Follow the uninstaller wizard

### Method 2: Command Line

```bash
# Stop and remove service
net stop VoiceStudio
sc delete VoiceStudio

# Run uninstaller
"C:\Program Files\VoiceStudio\bin\uninstall.exe"
```

### Method 3: Manual Removal

```bash
# Remove directories
rmdir /s "C:\Program Files\VoiceStudio"
rmdir /s "C:\ProgramData\VoiceStudio"
rmdir /s "%USERPROFILE%\VoiceStudio"

# Remove registry entries
reg delete "HKLM\SOFTWARE\VoiceStudio" /f
reg delete "HKCR\.vsproj" /f
reg delete "HKCR\VoiceStudio.Project" /f
```

## Support

For additional support:

- **Documentation**: Check the README.md file
- **Logs**: Review installation and application logs
- **Community**: Join the VoiceStudio community forums
- **Issues**: Report issues on the project repository

## License

VoiceStudio Ultimate is provided under the MIT License. See LICENSE file for details.

---

**VoiceStudio Ultimate v1.0.0**
_Professional Voice Cloning with Real-Time Capabilities_
