# VoiceStudio Quantum+ Installer Preparation Guide

Complete guide for preparing and configuring the VoiceStudio Quantum+ installer.

**Last Updated:** 2025-01-28  
**Version:** 1.0

---

## Overview

VoiceStudio Quantum+ uses Windows installers to bundle:

- WinUI 3 frontend application
- Python backend with FastAPI
- Engine manifests and core engine files
- Documentation
- Required dependencies

Two installer technologies are supported:

1. **Inno Setup** (EXE-based, simpler)
2. **WiX Toolset** (MSI-based, professional)

---

## Installer Structure

### Directory Structure

```
installer/
├── VoiceStudio.iss          # Inno Setup script
├── VoiceStudio.wxs          # WiX Toolset script
├── build-installer.ps1     # Automated build script
├── install.ps1             # Installation helper script
├── README.md               # Installer documentation
└── Output/                 # Build output directory
    ├── VoiceStudio-Setup-v1.0.0.exe  # Inno Setup output
    └── VoiceStudio-Setup-v1.0.0.msi  # WiX output
```

---

## Prerequisites

### For Building Inno Setup Installer

1. **Inno Setup 6.2+**

   - Download from: https://jrsoftware.org/isdl.php
   - Install Inno Setup Compiler
   - Default location: `C:\Program Files (x86)\Inno Setup 6\`

2. **PowerShell 5.1+** (for build scripts)

### For Building WiX Installer

1. **WiX Toolset v3.11+**

   - Download from: https://wixtoolset.org/releases/
   - Install WiX Toolset
   - Install WiX Visual Studio Extension (optional)

2. **Visual Studio 2022** (recommended)
   - With WiX extension installed

---

## Installer Configuration

### Inno Setup Configuration (VoiceStudio.iss)

**Key Configuration Sections:**

1. **Application Information**

   ```ini
   #define MyAppName "VoiceStudio Quantum+"
   #define MyAppVersion "1.0.0"
   #define MyAppPublisher "VoiceStudio"
   #define MyAppURL "https://voicestudio.example"
   #define MyAppExeName "VoiceStudio.App.exe"
   #define MyAppId "A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D"
   ```

2. **Installation Settings**

   ```ini
   DefaultDirName={autopf}\VoiceStudio
   DefaultGroupName=VoiceStudio
   PrivilegesRequired=admin
   MinVersion=10.0.18362
   ```

3. **File Components**

   - Frontend application files
   - Backend Python files
   - Core engine files
   - Engine manifests
   - Documentation files

4. **Registry Entries**

   - File associations (`.voiceproj`, `.vprofile`)
   - Application registry keys
   - Uninstall information

5. **Custom Actions**
   - .NET 8 Runtime check
   - Python installation check
   - Python package installation
   - User data directory creation

### WiX Configuration (VoiceStudio.wxs)

**Key Configuration Sections:**

1. **Product Information**

   ```xml
   <?define ProductName = "VoiceStudio Quantum+" ?>
   <?define ProductVersion = "1.0.0" ?>
   <?define Manufacturer = "VoiceStudio" ?>
   <?define ProductCode = "A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D" ?>
   <?define UpgradeCode = "B2C3D4E5-F6A7-5B6C-9D0E-1F2A3B4C5D6E" ?>
   ```

2. **Package Settings**

   ```xml
   <Package InstallerVersion="200"
            Compressed="yes"
            InstallScope="perMachine" />
   ```

3. **Directory Structure**

   - Installation directory
   - Component organization
   - File references

4. **Features and Components**
   - Frontend application component
   - Backend component
   - Core engine component
   - Documentation component

---

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

---

## Build Process

### Automated Build

**Using Build Script:**

```powershell
.\installer\build-installer.ps1 -InstallerType InnoSetup -Version 1.0.0
```

**Parameters:**

- `-InstallerType`: `InnoSetup` or `WiX` (default: `InnoSetup`)
- `-Configuration`: `Release` or `Debug` (default: `Release`)
- `-Version`: Version number (default: `1.0.0`)

**Build Steps:**

1. Ensure `installer\Output\` exists (the build script preserves existing versioned installers side-by-side)
2. Build frontend application
3. Verify backend files
4. Verify engine manifests
5. Build installer
6. Output to `installer\Output\`

### Manual Build

**Inno Setup:**

```powershell
cd installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VoiceStudio.iss
```

**WiX:**

```powershell
cd installer
candle VoiceStudio.wxs
light VoiceStudio.wixobj -ext WixUIExtension
```

---

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
   - requirements.txt

3. **Core Engine System**

   - Engine implementations
   - Audio utilities
   - Runtime services
   - Training modules

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
- Windows 10 version 1903 or later (64-bit)

**Optional:**

- Python 3.10+ (if not installed, user prompted)
- NVIDIA GPU with CUDA (for GPU acceleration)

### Python Environment Setup

The installer:

1. Checks for Python 3.10+ installation
2. If not found, prompts user to install
3. Creates virtual environment (if needed)
4. Installs Python packages from `backend/requirements.txt`

---

## Customization

### Changing Version Number

**Inno Setup:**
Edit `VoiceStudio.iss`:

```ini
#define MyAppVersion "1.0.1"
```

**WiX:**
Edit `VoiceStudio.wxs`:

```xml
<?define ProductVersion = "1.0.1" ?>
```

### Changing Installation Path

**Inno Setup:**
Edit `VoiceStudio.iss`:

```ini
DefaultDirName={pf}\VoiceStudio
```

**WiX:**
Edit `VoiceStudio.wxs`:

```xml
<Directory Id="INSTALLFOLDER" Name="VoiceStudio">
```

### Adding Components

**Inno Setup:**
Add new `[Files]` sections:

```ini
[Files]
Source: "..\new\component\*"; DestDir: "{app}\NewComponent"; Flags: ignoreversion recursesubdirs
```

**WiX:**
Add new `<Component>` elements:

```xml
<Component Id="NewComponent" Guid="...">
  <File Source="new\component\file.txt" />
</Component>
```

### Custom Actions

**Inno Setup:**
Add `[Run]` sections or Pascal code:

```ini
[Run]
Filename: "powershell"; Parameters: "-Command ""..."""; StatusMsg: "Running custom action..."
```

**WiX:**
Add `<CustomAction>` elements:

```xml
<CustomAction Id="CustomAction" Execute="deferred" ... />
```

---

## Testing

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

---

## Code Signing

### Signing the Installer

**Using SignTool:**

```powershell
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com VoiceStudio-Setup-v1.0.0.exe
```

**Requirements:**

- Code signing certificate
- SignTool (Windows SDK)
- Timestamp server URL

### Verifying Signature

```powershell
signtool verify /pa VoiceStudio-Setup-v1.0.0.exe
```

---

## Distribution

### Release Package Contents

- `VoiceStudio-Setup-v[VERSION].exe` (or `.msi`)
- `SHA256SUMS.txt` (checksums)
- `README.md` (installation instructions)
- `RELEASE_NOTES.md` (release notes)
- `CHANGELOG.md` (version history)
- `LICENSE` (license file)

### Release Checklist

- [ ] Installer builds successfully
- [ ] Tested on Windows 10
- [ ] Tested on Windows 11
- [ ] Tested upgrade from previous version
- [ ] Tested uninstallation
- [ ] Code signed (if applicable)
- [ ] Checksums generated
- [ ] Release notes updated
- [ ] Version number updated
- [ ] Documentation included

---

## Troubleshooting

### Installer Fails to Build

**Inno Setup:**

- Verify Inno Setup installed
- Check file paths in script
- Verify all source files exist
- Check for syntax errors

**WiX:**

- Verify WiX Toolset installed
- Check WiX extension in Visual Studio
- Verify all file paths exist
- Check for XML syntax errors

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

---

## Best Practices

1. **Version Management**

   - Update version numbers in all files
   - Use consistent versioning scheme
   - Document version changes

2. **Testing**

   - Test on clean systems
   - Test upgrade paths
   - Test uninstallation
   - Test all components

3. **Code Signing**

   - Always sign installers
   - Use timestamp server
   - Verify signatures

4. **Documentation**

   - Include installation instructions
   - Document system requirements
   - Provide troubleshooting guide

5. **Distribution**
   - Generate checksums
   - Include release notes
   - Provide support information

---

## References

- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [WiX Toolset Documentation](https://wixtoolset.org/documentation/)
- [Windows Installer Best Practices](https://docs.microsoft.com/windows/win32/msi/windows-installer-best-practices)
- [Code Signing Guide](https://docs.microsoft.com/windows/win32/seccrypto/cryptography-tools)

---

**Last Updated:** 2025-01-28  
**Version:** 1.0
