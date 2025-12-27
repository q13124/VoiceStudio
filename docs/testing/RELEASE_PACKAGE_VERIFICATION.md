# Release Package Verification Guide

Complete verification guide for VoiceStudio Quantum+ release package.

## Overview

This guide provides step-by-step instructions for building and verifying the release package.

## Prerequisites

### Build Environment Required

1. **Development System:**
   - Windows 10/11
   - Visual Studio 2022 or later
   - .NET 8 SDK
   - WiX Toolset (for MSI installer)
   - Inno Setup (for EXE installer)
   - Python 3.10+ (for backend)

2. **Build Tools:**
   - `installer/build-installer.ps1` - Build script
   - `installer/VoiceStudio.wxs` - WiX installer script
   - `installer/VoiceStudio.iss` - Inno Setup installer script

## Release Package Contents

### Required Files

1. **Installers:**
   - `VoiceStudio-Setup.msi` - WiX installer
   - `VoiceStudio-Setup.exe` - Inno Setup installer
   - `VoiceStudio-Portable.zip` - Portable version (optional)

2. **Documentation:**
   - `README.md` - Main readme
   - `CHANGELOG.md` - Version changelog
   - `LICENSE` - License file
   - `docs/` - Complete documentation

3. **Release Notes:**
   - `RELEASE_NOTES.md` - Release notes
   - Release notes in GitHub release (if applicable)

4. **Checksums:**
   - `SHA256SUMS.txt` - File checksums
   - `SHA256SUMS.txt.sig` - Checksum signature (optional)

## Build Process

### Step 1: Build Application

```powershell
# Build frontend
cd src/VoiceStudio.App
dotnet build -c Release

# Build backend (if needed)
cd ../../backend
python -m pip install -r requirements.txt
```

### Step 2: Build Installers

```powershell
# Build WiX installer
cd installer
.\build-installer.ps1 -Type WiX

# Build Inno Setup installer
.\build-installer.ps1 -Type InnoSetup

# Build portable version (optional)
.\build-installer.ps1 -Type Portable
```

### Step 3: Generate Checksums

```powershell
# Generate SHA256 checksums
Get-ChildItem *.msi, *.exe, *.zip | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    "$($hash.Hash)  $($_.Name)" | Out-File -Append SHA256SUMS.txt
}
```

### Step 4: Create Release Package

```powershell
# Create release directory
New-Item -ItemType Directory -Path "release/v1.0.0"

# Copy installers
Copy-Item installer/*.msi release/v1.0.0/
Copy-Item installer/*.exe release/v1.0.0/
Copy-Item installer/*.zip release/v1.0.0/

# Copy documentation
Copy-Item README.md release/v1.0.0/
Copy-Item CHANGELOG.md release/v1.0.0/
Copy-Item LICENSE release/v1.0.0/
Copy-Item RELEASE_NOTES.md release/v1.0.0/
Copy-Item -Recurse docs/ release/v1.0.0/docs/

# Copy checksums
Copy-Item SHA256SUMS.txt release/v1.0.0/
```

## Verification Checklist

### File Verification

- [ ] **Installers:**
  - [ ] WiX installer (`.msi`) exists
  - [ ] Inno Setup installer (`.exe`) exists
  - [ ] Portable version (`.zip`) exists (if applicable)
  - [ ] Installer file sizes reasonable
  - [ ] Installer files not corrupted

- [ ] **Documentation:**
  - [ ] README.md included
  - [ ] CHANGELOG.md included
  - [ ] LICENSE included
  - [ ] RELEASE_NOTES.md included
  - [ ] Complete docs/ directory included

- [ ] **Checksums:**
  - [ ] SHA256SUMS.txt included
  - [ ] Checksums match files
  - [ ] Checksum signature included (if applicable)

### Installer Verification

- [ ] **WiX Installer:**
  - [ ] Installs correctly on clean system
  - [ ] Creates shortcuts correctly
  - [ ] Uninstalls completely
  - [ ] No errors during installation

- [ ] **Inno Setup Installer:**
  - [ ] Installs correctly on clean system
  - [ ] Creates shortcuts correctly
  - [ ] Uninstalls completely
  - [ ] No errors during installation

- [ ] **Portable Version:**
  - [ ] Extracts correctly
  - [ ] Application launches
  - [ ] All features work
  - [ ] No installation required

### Application Verification

- [ ] **Launch:**
  - [ ] Application starts without errors
  - [ ] Backend starts automatically
  - [ ] Main window displays correctly

- [ ] **Features:**
  - [ ] Voice synthesis works
  - [ ] Profile management works
  - [ ] Timeline works
  - [ ] Effects work
  - [ ] All panels accessible
  - [ ] Settings work
  - [ ] Update mechanism works

### Documentation Verification

- [ ] **Completeness:**
  - [ ] All documentation files present
  - [ ] Documentation is up-to-date
  - [ ] No broken links
  - [ ] Screenshots included (if applicable)

- [ ] **Accuracy:**
  - [ ] Installation instructions accurate
  - [ ] Feature descriptions accurate
  - [ ] API documentation accurate
  - [ ] Troubleshooting guide accurate

### Version Verification

- [ ] **Version Numbers:**
  - [ ] Version number consistent across files
  - [ ] Version number in installer matches application
  - [ ] Version number in release notes matches
  - [ ] Version number in CHANGELOG matches

- [ ] **Release Notes:**
  - [ ] Release notes complete
  - [ ] New features documented
  - [ ] Bug fixes documented
  - [ ] Breaking changes documented (if any)

## Test Results Template

### Release Package Verification Report

**Release Version:** _______________  
**Build Date:** _______________  
**Verifier:** _______________  

#### File Verification
- [ ] Installers: Pass / Fail
- [ ] Documentation: Pass / Fail
- [ ] Checksums: Pass / Fail

#### Installer Verification
- [ ] WiX Installer: Pass / Fail
- [ ] Inno Setup Installer: Pass / Fail
- [ ] Portable Version: Pass / Fail

#### Application Verification
- [ ] Launch: Pass / Fail
- [ ] Features: Pass / Fail
- [ ] Update Mechanism: Pass / Fail

#### Documentation Verification
- [ ] Completeness: Pass / Fail
- [ ] Accuracy: Pass / Fail

#### Version Verification
- [ ] Version Numbers: Pass / Fail
- [ ] Release Notes: Pass / Fail

### Issues Found

**Issue #1:**
- **Severity:** Critical / High / Medium / Low
- **Description:** _______________
- **Files Affected:** _______________
- **Resolution:** _______________

### Overall Assessment

- [ ] **Accept for Release**
- [ ] **Accept with Minor Issues**
- [ ] **Reject - Major Issues Found**

**Comments:** _______________

---

## Release Checklist

### Pre-Release

- [ ] All code changes committed
- [ ] All tests passing
- [ ] Version numbers updated
- [ ] Release notes written
- [ ] CHANGELOG updated
- [ ] Documentation updated

### Build

- [ ] Application builds successfully
- [ ] Installers build successfully
- [ ] Checksums generated
- [ ] Release package created

### Verification

- [ ] Installers tested on clean systems
- [ ] Application verified after installation
- [ ] All features tested
- [ ] Documentation verified
- [ ] Version numbers verified

### Release

- [ ] Release package uploaded
- [ ] GitHub release created (if applicable)
- [ ] Release notes published
- [ ] Announcement prepared (if applicable)

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0

