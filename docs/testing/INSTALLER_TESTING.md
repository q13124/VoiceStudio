# Installer Testing Guide

Complete testing guide for VoiceStudio Quantum+ installer on clean Windows systems.

## Overview

This guide provides step-by-step instructions for testing the installer on clean Windows systems to ensure it works correctly.

## Prerequisites

### Test Systems Required

1. **Clean Windows 11 System**
   - Fresh Windows 11 installation
   - No VoiceStudio installed
   - Administrator access

2. **Clean Windows 10 System** (if available)
   - Fresh Windows 10 installation
   - No VoiceStudio installed
   - Administrator access

### Test Files Required

- `installer/VoiceStudio.wxs` - WiX installer script
- `installer/VoiceStudio.iss` - Inno Setup installer script
- `installer/build-installer.ps1` - Build script
- Built installer executable (`.msi` or `.exe`)

## Test Scenarios

### Scenario 1: Fresh Installation (WiX)

**Objective:** Verify WiX installer works on clean system.

**Steps:**
1. Build WiX installer:
   ```powershell
   cd installer
   .\build-installer.ps1 -Type WiX
   ```

2. Copy installer to test system

3. Run installer:
   - Right-click installer → "Run as administrator"
   - Follow installation wizard
   - Verify default installation path: `C:\Program Files\VoiceStudio\`
   - Complete installation

4. Verify Installation:
   - [ ] Application installed in correct location
   - [ ] Start menu shortcut created
   - [ ] Desktop shortcut created (if enabled)
   - [ ] Application launches successfully
   - [ ] Backend starts correctly
   - [ ] All features accessible

5. Test Uninstallation:
   - Open "Add or Remove Programs"
   - Find "VoiceStudio Quantum+"
   - Click "Uninstall"
   - Verify complete removal:
     - [ ] Application folder removed
     - [ ] Start menu shortcut removed
     - [ ] Desktop shortcut removed
     - [ ] Registry entries cleaned (if any)

**Expected Results:**
- ✅ Installation completes without errors
- ✅ Application launches successfully
- ✅ All features work correctly
- ✅ Uninstallation removes all files

---

### Scenario 2: Fresh Installation (Inno Setup)

**Objective:** Verify Inno Setup installer works on clean system.

**Steps:**
1. Build Inno Setup installer:
   ```powershell
   cd installer
   .\build-installer.ps1 -Type InnoSetup
   ```

2. Copy installer to test system

3. Run installer:
   - Double-click installer
   - Follow installation wizard
   - Verify default installation path: `C:\Program Files\VoiceStudio\`
   - Complete installation

4. Verify Installation:
   - [ ] Application installed in correct location
   - [ ] Start menu shortcut created
   - [ ] Desktop shortcut created (if enabled)
   - [ ] Application launches successfully
   - [ ] Backend starts correctly
   - [ ] All features accessible

5. Test Uninstallation:
   - Open "Add or Remove Programs"
   - Find "VoiceStudio Quantum+"
   - Click "Uninstall"
   - Verify complete removal

**Expected Results:**
- ✅ Installation completes without errors
- ✅ Application launches successfully
- ✅ All features work correctly
- ✅ Uninstallation removes all files

---

### Scenario 3: Custom Installation Path

**Objective:** Verify installer works with custom installation path.

**Steps:**
1. Run installer
2. Choose "Custom Installation"
3. Set custom path: `D:\VoiceStudio\`
4. Complete installation
5. Verify:
   - [ ] Application installed in custom location
   - [ ] Application launches successfully
   - [ ] All features work correctly

**Expected Results:**
- ✅ Custom path installation works
- ✅ Application functions correctly from custom location

---

### Scenario 4: Upgrade Installation

**Objective:** Verify installer handles upgrades correctly.

**Steps:**
1. Install previous version (if available)
2. Run new installer
3. Choose upgrade option
4. Complete installation
5. Verify:
   - [ ] Previous version uninstalled
   - [ ] New version installed
   - [ ] User settings preserved (if applicable)
   - [ ] Application launches successfully

**Expected Results:**
- ✅ Upgrade completes without errors
- ✅ User data preserved
- ✅ Application works correctly

---

### Scenario 5: Silent Installation

**Objective:** Verify silent installation works.

**Steps:**
1. Run installer with silent flag:
   ```powershell
   VoiceStudio-Setup.exe /S
   ```

2. Verify:
   - [ ] Installation completes without UI
   - [ ] Application installed correctly
   - [ ] Application launches successfully

**Expected Results:**
- ✅ Silent installation works
- ✅ Application installed correctly

---

## Verification Checklist

### Installation Verification

- [ ] **File Installation:**
  - [ ] All application files installed
  - [ ] All dependencies installed
  - [ ] Configuration files created
  - [ ] Data directories created

- [ ] **Shortcuts:**
  - [ ] Start menu shortcut created
  - [ ] Desktop shortcut created (if enabled)
  - [ ] Shortcuts point to correct location

- [ ] **Registry (if applicable):**
  - [ ] Application registered correctly
  - [ ] Uninstaller registered
  - [ ] File associations registered (if any)

- [ ] **Permissions:**
  - [ ] Application has correct permissions
  - [ ] User can launch application
  - [ ] User can access data directories

### Application Verification

- [ ] **Launch:**
  - [ ] Application starts without errors
  - [ ] Splash screen displays
  - [ ] Main window opens

- [ ] **Backend:**
  - [ ] Backend starts automatically
  - [ ] Backend API accessible
  - [ ] WebSocket connection works

- [ ] **Features:**
  - [ ] Voice synthesis works
  - [ ] Profile management works
  - [ ] Timeline works
  - [ ] Effects work
  - [ ] All panels accessible

### Uninstallation Verification

- [ ] **File Removal:**
  - [ ] Application folder removed
  - [ ] All application files removed
  - [ ] Configuration files removed (or preserved as appropriate)

- [ ] **Shortcut Removal:**
  - [ ] Start menu shortcut removed
  - [ ] Desktop shortcut removed

- [ ] **Registry Cleanup:**
  - [ ] Registry entries removed
  - [ ] Uninstaller entry removed

- [ ] **Data Preservation (if applicable):**
  - [ ] User data preserved (if configured)
  - [ ] Settings preserved (if configured)

---

## Test Results Template

### Test Execution Log

**Date:** _______________  
**Tester:** _______________  
**System:** Windows 11 / Windows 10  
**Installer Type:** WiX / Inno Setup  
**Version:** _______________

#### Installation Test
- [ ] Pass
- [ ] Fail
- [ ] Blocked
- **Notes:** _______________

#### Application Launch Test
- [ ] Pass
- [ ] Fail
- [ ] Blocked
- **Notes:** _______________

#### Feature Test
- [ ] Pass
- [ ] Fail
- [ ] Blocked
- **Notes:** _______________

#### Uninstallation Test
- [ ] Pass
- [ ] Fail
- [ ] Blocked
- **Notes:** _______________

### Issues Found

**Issue #1:**
- **Severity:** Critical / High / Medium / Low
- **Description:** _______________
- **Steps to Reproduce:** _______________
- **Expected:** _______________
- **Actual:** _______________

---

## Troubleshooting

### Common Issues

**Issue: Installer fails to start**
- **Solution:** Run as administrator
- **Solution:** Check Windows Defender / Antivirus
- **Solution:** Verify installer file integrity

**Issue: Installation fails mid-way**
- **Solution:** Check disk space
- **Solution:** Check permissions
- **Solution:** Check Windows Event Viewer for errors

**Issue: Application doesn't launch after installation**
- **Solution:** Check Windows Event Viewer
- **Solution:** Verify .NET 8 runtime installed
- **Solution:** Check backend logs

**Issue: Uninstallation fails**
- **Solution:** Close application first
- **Solution:** Run uninstaller as administrator
- **Solution:** Use Windows "Add or Remove Programs"

---

## Test Report Template

### Installer Test Report

**Test Date:** _______________  
**Test System:** _______________  
**Installer Type:** _______________  
**Installer Version:** _______________

**Test Results:**
- Fresh Installation: Pass / Fail
- Custom Path: Pass / Fail
- Upgrade: Pass / Fail
- Silent Installation: Pass / Fail
- Uninstallation: Pass / Fail

**Issues Found:**
- Issue 1: _______________
- Issue 2: _______________

**Recommendations:**
- _______________

**Overall Assessment:**
- [ ] **Accept for Release**
- [ ] **Accept with Minor Issues**
- [ ] **Reject - Major Issues Found**

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0

