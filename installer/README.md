# VoiceStudio Quantum+ Installer

Complete installer solution for VoiceStudio Quantum+.

## Overview

VoiceStudio Quantum+ uses a Windows installer to bundle:

- WinUI 3 frontend application
- Python backend with FastAPI
- Engine manifests and core engine files
- Documentation
- Required dependencies

## Installer Technologies

Two installer options are provided:

1. **WiX Toolset** (Professional, MSI-based)

   - File: `VoiceStudio.wxs`
   - Requires: WiX Toolset v3.11+
   - Output: `.msi` installer

2. **Inno Setup** (Simpler, EXE-based)
   - File: `VoiceStudio.iss`
   - Requires: Inno Setup 6.2+
   - Output: `.exe` installer

## Prerequisites

### For Building WiX Installer

1. **WiX Toolset v3.11+**

   - Download from: https://wixtoolset.org/releases/
   - Install WiX Toolset and WiX Visual Studio Extension

2. **Visual Studio 2022**
   - With WiX extension installed

### For Building Inno Setup Installer

1. **Inno Setup 6.2+**
   - Download from: https://jrsoftware.org/isdl.php
   - Install Inno Setup Compiler

## Installation Paths

### Application Installation

**Default Location:**

```
C:\Program Files\VoiceStudio\
├── App\              # Frontend application
├── Backend\          # Python backend
├── Core\             # Engine core files
├── Engines\          # Engine manifests
└── Docs\             # Documentation
```

### User Data Directories

**Application Data:**

```
%APPDATA%\VoiceStudio\
├── settings.json
├── layouts\
└── logs\
```

**Program Data:**

```
%PROGRAMDATA%\VoiceStudio\
├── models\           # Engine models
└── cache\            # Cache files
```

## Building the Installer

### WiX Installer

**Using Visual Studio:**

1. Open `installer/VoiceStudio.wixproj` in Visual Studio
2. Build → Build Solution
3. Output: `installer\bin\Release\VoiceStudio.msi`

**Using Command Line:**

```powershell
cd installer
candle VoiceStudio.wxs
light VoiceStudio.wixobj -ext WixUIExtension
```

### Inno Setup Installer

**Using Inno Setup Compiler:**

1. Open `installer/VoiceStudio.iss` in Inno Setup Compiler
2. Build → Compile
3. Output: `installer\Output\VoiceStudio-Setup-v<version>.exe`

**Using Command Line:**

```powershell
cd installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VoiceStudio.iss
```

### Build Script

**Automated Build:**

```powershell
.\installer\build-installer.ps1
```

This script:

- Builds the frontend application
- Prepares backend files
- Creates installer package
- Outputs installer to `installer\Output\`

## Installer Features

### Installation Components

1. **Frontend Application**

   - WinUI 3 executable
   - DLLs and dependencies
   - Resources and themes

2. **Backend**

   - Python API files
   - Route handlers
   - WebSocket handlers

3. **Core Engine System**

   - Engine implementations
   - Audio utilities
   - Runtime services

4. **Engine Manifests**

   - Audio engine manifests
   - Image engine manifests
   - Video engine manifests

5. **Documentation**
   - User documentation
   - API documentation
   - Developer documentation

### File Associations

- `.voiceproj` → VoiceStudio Project File
- `.vprofile` → VoiceStudio Voice Profile

### Shortcuts

- **Start Menu:** VoiceStudio Quantum+
- **Desktop:** VoiceStudio Quantum+ (optional)
- **Documentation:** User Manual, Getting Started, API Docs

### Dependencies

**Required:**

- .NET 8.0 Runtime (checked during installation)
- Windows 10 version 1903 or later

**Optional:**

- Python 3.10+ (if not installed, user prompted)
- NVIDIA GPU with CUDA (for GPU acceleration)

### Python Environment Setup

The installer:

1. Checks for Python 3.10+ installation
2. If not found, prompts user to install
3. Creates virtual environment (if needed)
4. Installs Python packages from `backend/requirements.txt`

**Python Installation:**

- User can download from python.org
- Or installer can bundle Python runtime (optional)

## Testing the Installer

### Clean System Testing

**Windows 10:**

1. Create clean Windows 10 VM
2. Install .NET 8 Runtime
3. Run installer
4. Verify installation
5. Test application launch
6. Test uninstallation

**Windows 11:**

1. Create clean Windows 11 VM
2. Install .NET 8 Runtime
3. Run installer
4. Verify installation
5. Test application launch
6. Test uninstallation

### Upgrade Testing

1. Install previous version
2. Run new installer
3. Verify upgrade preserves:
   - User data
   - Settings
   - Projects
   - Profiles

### Uninstallation Testing

1. Install application
2. Create test data
3. Uninstall application
4. Verify:
   - All files removed
   - Shortcuts removed
   - Registry entries removed
   - User data preserved (optional)

## Troubleshooting

### Installer Fails to Build

**WiX:**

- Verify WiX Toolset installed
- Check WiX extension in Visual Studio
- Verify all file paths exist

**Inno Setup:**

- Verify Inno Setup installed
- Check file paths in script
- Verify all source files exist

### Installation Fails

**Missing Dependencies:**

- Install .NET 8 Runtime first
- Install Python 3.10+ if required
- Check Windows version compatibility

**Permission Errors:**

- Run installer as Administrator
- Check antivirus software
- Verify disk space available

### Application Won't Start

**Missing Python:**

- Install Python 3.10+
- Verify Python in PATH
- Check virtual environment

**Missing Dependencies:**

- Run `pip install -r backend/requirements.txt`
- Check Python packages installed
- Verify engine models available

## Customization

### Changing Installation Path

**WiX:**
Edit `VoiceStudio.wxs`:

```xml
<Directory Id="INSTALLFOLDER" Name="VoiceStudio">
```

**Inno Setup:**
Edit `VoiceStudio.iss`:

```ini
DefaultDirName={pf}\VoiceStudio
```

### Adding Components

**WiX:**
Add new `<Component>` elements in `VoiceStudio.wxs`

**Inno Setup:**
Add new `[Files]` sections in `VoiceStudio.iss`

### Custom Actions

**WiX:**
Add `<CustomAction>` elements for post-install tasks

**Inno Setup:**
Add `[Run]` sections for post-install tasks

## Distribution

### Release Package

**Contents:**

- `VoiceStudio-Setup-v1.0.0.exe` (or `.msi`)
- `README.md` (installation instructions)
- `CHANGELOG.md` (version history)
- `LICENSE` (license file)

### Code Signing

**Recommended:**

- Sign installer with code signing certificate
- Verify signature before distribution
- Include signature in release notes

### Release Checklist

- [ ] Installer builds successfully
- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] Tested upgrade from previous version
- [ ] Tested uninstallation
- [ ] Code signed (if applicable)
- [ ] Release notes updated
- [ ] Version number updated

## References

- [WiX Toolset Documentation](https://wixtoolset.org/documentation/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [Windows Installer Best Practices](https://docs.microsoft.com/windows/win32/msi/windows-installer-best-practices)

---

**Last Updated:** 2025-01-27  
**Version:** 1.0
