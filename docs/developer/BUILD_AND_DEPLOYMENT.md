# VoiceStudio Quantum+ Build and Deployment Guide

Complete guide for building and deploying VoiceStudio Quantum+.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Ready for Use

---

## Table of Contents

1. [Overview](#overview)
2. [Build Process](#build-process)
3. [Deployment Process](#deployment-process)
4. [Installer Creation](#installer-creation)
5. [Update Mechanism](#update-mechanism)
6. [CI/CD](#cicd)
7. [Release Process](#release-process)
8. [Deployment Checklist](#deployment-checklist)

---

## Overview

VoiceStudio Quantum+ consists of:
- **Frontend:** WinUI 3 application (C#/.NET 8)
- **Backend:** Python FastAPI application
- **Engines:** Python-based voice cloning engines
- **Installer:** Windows installer package

### Build Artifacts

- **Frontend:** `src/VoiceStudio.App/bin/Release/net8.0-windows10.0.19041.0/`
- **Backend:** Python files in `backend/`
- **Installer:** `installer/Output/VoiceStudio-Setup.exe` or `.msi`

---

## Build Process

### Prerequisites

**Required Software:**
- Visual Studio 2022 (Community or higher)
- .NET 8 SDK
- Python 3.10+
- WiX Toolset v3.11+ (for MSI installer) OR Inno Setup 6.2+ (for EXE installer)
- Git

**System Requirements:**
- Windows 10 (1903+) or Windows 11
- 16 GB RAM minimum (32 GB recommended)
- 20+ GB free disk space

### Frontend Build

**Using Visual Studio:**
1. Open `src/VoiceStudio.App/VoiceStudio.App.csproj`
2. Select **Release** configuration
3. Build → Build Solution (Ctrl+Shift+B)
4. Output: `src/VoiceStudio.App/bin/Release/net8.0-windows10.0.19041.0/`

**Using Command Line:**
```powershell
cd src/VoiceStudio.App
dotnet clean --configuration Release
dotnet build --configuration Release
```

**Build Output:**
- `VoiceStudio.App.exe` - Main executable
- `*.dll` - Dependencies
- `Assets/` - Resources and assets
- `Resources/` - XAML resources

**Build Options:**
- `--configuration Release` - Release build (optimized)
- `--configuration Debug` - Debug build (with symbols)
- `--no-incremental` - Clean build

### Backend Build

**No Build Step Required** - Python is interpreted.

**Verify Backend:**
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn api.main:app --check
```

**Backend Structure:**
- `api/main.py` - FastAPI application
- `api/routes/` - API route handlers
- `api/models*.py` - Data models

### Core Library Build

**Using Command Line:**
```powershell
cd src/VoiceStudio.Core
dotnet build --configuration Release
```

**Output:** `src/VoiceStudio.Core/bin/Release/net8.0/`

---

## Deployment Process

### Development Deployment

**Local Development:**
1. Build frontend (Debug or Release)
2. Start backend: `python -m uvicorn api.main:app --reload`
3. Run frontend from Visual Studio (F5)

**No installer needed for development.**

### Production Deployment

**Steps:**
1. Build frontend (Release configuration)
2. Verify backend files
3. Create installer package
4. Test installer
5. Sign installer (optional, for distribution)
6. Distribute installer

**See [Installer Creation](#installer-creation) for details.**

---

## Installer Creation

### Installer Types

**Two installer options:**

1. **Inno Setup (EXE)** - Recommended for simplicity
   - File: `installer/VoiceStudio.iss`
   - Output: `VoiceStudio-Setup.exe`
   - Easier to customize

2. **WiX Toolset (MSI)** - Professional, enterprise-grade
   - File: `installer/VoiceStudio.wxs`
   - Output: `VoiceStudio.msi`
   - Better for enterprise deployment

### Automated Build Script

**Using PowerShell Script:**
```powershell
.\installer\build-installer.ps1
```

**Parameters:**
- `-InstallerType`: "InnoSetup" or "WiX" (default: "InnoSetup")
- `-Configuration`: "Release" or "Debug" (default: "Release")
- `-Version`: Version number (default: "1.0.0")

**Example:**
```powershell
.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0
```

**What the Script Does:**
1. Cleans output directory
2. Builds frontend application (Release)
3. Verifies backend files
4. Verifies engine manifests
5. Creates installer package
6. Outputs to `installer/Output/`

### Inno Setup Installer

**Prerequisites:**
- Inno Setup 6.2+ installed
- Frontend built in Release configuration

**Using Inno Setup Compiler:**
1. Open `installer/VoiceStudio.iss` in Inno Setup Compiler
2. Build → Compile (F9)
3. Output: `installer/Output/VoiceStudio-Setup.exe`

**Using Command Line:**
```powershell
cd installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" VoiceStudio.iss
```

**Installer Features:**
- Modern wizard interface
- Automatic .NET 8 Runtime check
- Python environment setup
- File associations (.voiceproj, .vprofile)
- Start menu shortcuts
- Desktop shortcut (optional)
- Uninstaller

### WiX Installer

**Prerequisites:**
- WiX Toolset v3.11+ installed
- WiX Visual Studio Extension
- Frontend built in Release configuration

**Using Visual Studio:**
1. Open `installer/VoiceStudio.wixproj` in Visual Studio
2. Build → Build Solution
3. Output: `installer/bin/Release/VoiceStudio.msi`

**Using Command Line:**
```powershell
cd installer
candle VoiceStudio.wxs
light VoiceStudio.wixobj -ext WixUIExtension
```

**Installer Features:**
- Professional MSI package
- Windows Installer integration
- Group Policy support
- Silent installation support
- Enterprise deployment ready

### Installer Contents

**Frontend Application:**
- `VoiceStudio.App.exe` and dependencies
- Resources and assets
- Core library DLLs

**Backend:**
- Python API files
- Route handlers
- WebSocket handlers

**Core Engine System:**
- Engine implementations
- Audio utilities
- Runtime services

**Engine Manifests:**
- Audio engine manifests
- Image engine manifests
- Video engine manifests

**Documentation:**
- User documentation
- API documentation
- Developer documentation

### Installation Paths

**Application Installation:**
```
C:\Program Files\VoiceStudio\
├── App\              # Frontend application
├── Backend\          # Python backend
├── Core\             # Engine core files
├── Engines\          # Engine manifests
└── Docs\             # Documentation
```

**User Data:**
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

## Update Mechanism

### Update Checking

**Current Implementation:**
- Manual update checking
- Version comparison
- Download notification

**Future Implementation:**
- Automatic update checking
- Background download
- Seamless installation

### Update Process

**Manual Update:**
1. Check for updates (Help → Check for Updates)
2. Download new installer if available
3. Run installer (upgrades existing installation)
4. Restart application

**Automatic Update (Future):**
1. Application checks for updates on startup
2. Downloads update in background
3. Prompts user to install
4. Installs update and restarts

### Version Management

**Version Format:** `MAJOR.MINOR.PATCH` (e.g., 1.0.0)

**Version Location:**
- `installer/VoiceStudio.iss` - `#define MyAppVersion`
- `installer/VoiceStudio.wxs` - Version attribute
- `src/VoiceStudio.App/App.xaml.cs` - Application version

**Update Version:**
1. Update version in installer scripts
2. Update version in application code
3. Update `CHANGELOG.md`
4. Update `RELEASE_NOTES.md`

---

## CI/CD

### Continuous Integration

**Recommended CI/CD Pipeline:**

**GitHub Actions (Example):**
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0.x'
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Build Frontend
        run: dotnet build src/VoiceStudio.App --configuration Release
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
```

**Azure DevOps (Example):**
```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'windows-latest'

steps:
  - task: UseDotNet@2
    inputs:
      version: '8.0.x'
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.10'
  - script: dotnet build src/VoiceStudio.App --configuration Release
    displayName: 'Build Frontend'
  - script: |
      cd backend
      pip install -r requirements.txt
      pytest
    displayName: 'Test Backend'
```

### Continuous Deployment

**Release Pipeline:**
1. **Build:** Compile application
2. **Test:** Run automated tests
3. **Package:** Create installer
4. **Sign:** Code sign installer (optional)
5. **Deploy:** Upload to distribution server

**Deployment Environments:**
- **Development:** Local builds
- **Staging:** Pre-release testing
- **Production:** Public release

---

## Release Process

### Pre-Release Checklist

**Code:**
- [ ] All features complete
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated

**Build:**
- [ ] Frontend builds successfully (Release)
- [ ] Backend verified
- [ ] Installer builds successfully
- [ ] Installer tested on clean system

**Documentation:**
- [ ] Release notes updated
- [ ] Changelog updated
- [ ] User manual updated
- [ ] API documentation updated

**Testing:**
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests passing
- [ ] Manual testing completed

### Release Steps

**1. Prepare Release:**
```powershell
# Update version
# Update CHANGELOG.md
# Update RELEASE_NOTES.md
# Commit changes
git add .
git commit -m "chore: Prepare release v1.0.0"
git tag v1.0.0
```

**2. Build Release:**
```powershell
# Build installer
.\installer\build-installer.ps1 -Configuration Release -Version 1.0.0
```

**3. Test Release:**
- Install on clean Windows system
- Test all features
- Verify file associations
- Test uninstaller

**4. Create Release Package:**
- Installer executable
- Release notes
- Changelog
- Documentation

**5. Publish Release:**
- Upload to distribution server
- Create GitHub release (if applicable)
- Announce release

### Post-Release

**Monitor:**
- Error logs
- User feedback
- Performance metrics
- Update requests

**Hotfix Process:**
1. Create hotfix branch
2. Fix critical issues
3. Build and test
4. Release hotfix version
5. Merge to main

---

## Deployment Checklist

### Pre-Deployment

- [ ] All code changes committed
- [ ] Version number updated
- [ ] Release notes prepared
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Tests passing
- [ ] Code review completed

### Build

- [ ] Frontend builds successfully (Release)
- [ ] Backend files verified
- [ ] Engine manifests verified
- [ ] Installer builds successfully
- [ ] Installer output verified

### Testing

- [ ] Installer tested on clean system
- [ ] Application launches successfully
- [ ] All features functional
- [ ] File associations work
- [ ] Uninstaller works
- [ ] Update mechanism works (if applicable)

### Deployment

- [ ] Installer signed (if applicable)
- [ ] Release package created
- [ ] Distribution server updated
- [ ] Release announcement prepared
- [ ] Support channels notified

### Post-Deployment

- [ ] Monitor error logs
- [ ] Monitor user feedback
- [ ] Monitor performance metrics
- [ ] Address critical issues
- [ ] Plan next release

---

## Build Configuration

### Frontend Build Configuration

**Release Configuration:**
- Optimizations enabled
- Debug symbols disabled
- Trimming enabled (if applicable)
- Single file publish (optional)

**Debug Configuration:**
- Debug symbols enabled
- Optimizations disabled
- Hot reload enabled
- Detailed error messages

### Backend Configuration

**Environment Variables:**
```env
VOICESTUDIO_BACKEND_URL=http://localhost:8000
VOICESTUDIO_LOG_LEVEL=INFO
VOICESTUDIO_ENGINES_PATH=engines
VOICESTUDIO_MODELS_PATH=E:\VoiceStudio\models
```

### Installer Configuration

**Inno Setup:**
- Compression: LZMA
- Privileges: Admin
- Architecture: x64
- Minimum Windows: 10.0.18362

**WiX:**
- Platform: x64
- Minimum Windows: 10.0.18362
- Upgrade code: Unique GUID

---

## Troubleshooting

### Build Issues

**Frontend Won't Build:**
- Check .NET 8 SDK installed
- Verify project file references
- Clean and rebuild
- Check for missing NuGet packages

**Backend Issues:**
- Verify Python 3.10+ installed
- Check virtual environment activated
- Verify dependencies installed
- Check Python path

**Installer Won't Build:**
- Verify Inno Setup/WiX installed
- Check file paths in installer script
- Verify frontend build output exists
- Check for missing files

### Deployment Issues

**Installer Fails:**
- Check Windows version compatibility
- Verify admin privileges
- Check disk space
- Review installer logs

**Application Won't Start:**
- Check .NET 8 Runtime installed
- Verify backend running
- Check firewall settings
- Review application logs

---

## Best Practices

### Build

1. **Always Build Release for Production**
   - Use Release configuration
   - Enable optimizations
   - Disable debug symbols

2. **Test Before Deploying**
   - Test on clean system
   - Test all features
   - Test installer and uninstaller

3. **Version Management**
   - Use semantic versioning
   - Update version in all locations
   - Document version changes

### Deployment

1. **Code Signing**
   - Sign installer for distribution
   - Use trusted certificate
   - Verify signature

2. **Distribution**
   - Use secure distribution server
   - Provide checksums
   - Document installation steps

3. **Monitoring**
   - Monitor error logs
   - Track user feedback
   - Monitor performance

---

## Summary

This guide provides:

1. **Build Process:** Frontend, backend, and installer builds
2. **Deployment Process:** Development and production deployment
3. **Installer Creation:** Inno Setup and WiX installers
4. **Update Mechanism:** Update checking and installation
5. **CI/CD:** Continuous integration and deployment
6. **Release Process:** Complete release workflow
7. **Deployment Checklist:** Pre, during, and post-deployment tasks

**Key Takeaways:**
- Use Release configuration for production
- Test installer on clean system
- Follow release process checklist
- Monitor after deployment

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After major build/deployment changes

