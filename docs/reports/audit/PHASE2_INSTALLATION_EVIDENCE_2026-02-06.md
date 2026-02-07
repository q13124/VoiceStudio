# Phase 2: Installation Testing Evidence

**Date**: 2026-02-06
**Owner**: Release Engineer (Role 6)
**Status**: PREREQUISITES VERIFIED - AWAITING HUMAN TESTING

---

## Prerequisite Verification (Automated)

### .NET 8 Desktop Runtime

| Version | Path | Status |
|---------|------|--------|
| 8.0.22 | `C:\Program Files\dotnet\shared\Microsoft.WindowsDesktop.App` | ✅ INSTALLED |
| 8.0.23 | `C:\Program Files\dotnet\shared\Microsoft.WindowsDesktop.App` | ✅ INSTALLED |

### Windows App SDK Runtime

| Check | Status |
|-------|--------|
| Registry Key | ✅ FOUND |
| WindowsApps Directory | ✅ EXISTS |

### Python Runtime (Optional)

| Version | Status |
|---------|--------|
| Python 3.11.9 | ✅ INSTALLED |
| Python 3.12.10 | ✅ INSTALLED |

**Conclusion**: All prerequisites are installed on the test system. The installer should detect them correctly.

---

## Installer Files Verified

| File | Size | Last Modified |
|------|------|---------------|
| `VoiceStudio-Setup-v1.0.0.exe` | Present | Available for rollback test |
| `VoiceStudio-Setup-v1.0.1.exe` | Present | Primary installer under test |

---

## Test 2.1: Fresh Installation

### Pre-Test Cleanup (if needed)

```powershell
# Uninstall any existing VoiceStudio
$uninstaller = "C:\Program Files\VoiceStudio\unins000.exe"
if (Test-Path $uninstaller) {
    Start-Process $uninstaller -ArgumentList "/VERYSILENT" -Wait
}

# Clean user data (optional - for clean state testing)
Remove-Item "$env:LOCALAPPDATA\VoiceStudio" -Recurse -Force -ErrorAction SilentlyContinue
```

### Installation Command

```powershell
# Interactive installation
Start-Process "e:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.1.exe" -Wait
```

### Verification Commands

```powershell
# Check installation directory
Test-Path "C:\Program Files\VoiceStudio\App\VoiceStudio.App.exe"

# Check Start Menu shortcut
Test-Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\VoiceStudio\VoiceStudio Quantum+.lnk"

# Check Programs and Features
Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*VoiceStudio*" }
```

---

## Test 2.2: Silent Installation

### Command

```powershell
Start-Process -FilePath "e:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.1.exe" `
  -ArgumentList "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", `
  "/DIR=`"C:\Program Files\VoiceStudio`"", `
  "/LOG=`"C:\logs\voicestudio_silent_install.log`"" -Wait
```

### Log Analysis

```powershell
# Create log directory if needed
New-Item -ItemType Directory -Path "C:\logs" -Force

# After installation, check log
Get-Content "C:\logs\voicestudio_silent_install.log" | Select-Object -Last 20
```

---

## Test 2.3: Upgrade Path

### Setup

```powershell
# Install v1.0.0 first
Start-Process "e:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.0.exe" -Wait

# Create a test project (manually in app)
# Then run v1.0.1 installer
Start-Process "e:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.1.exe" -Wait
```

### Verification

```powershell
# Check version in installed exe
$exePath = "C:\Program Files\VoiceStudio\App\VoiceStudio.App.exe"
(Get-Item $exePath).VersionInfo.FileVersion

# Check user data preserved
Test-Path "$env:LOCALAPPDATA\VoiceStudio\settings.json"
```

---

## Test 2.4: Rollback

### Steps

1. Uninstall v1.0.1
2. Install v1.0.0
3. Verify application works

### Commands

```powershell
# Uninstall current
Start-Process "C:\Program Files\VoiceStudio\unins000.exe" -ArgumentList "/VERYSILENT" -Wait

# Install v1.0.0
Start-Process "e:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.0.exe" -Wait

# Verify
Test-Path "C:\Program Files\VoiceStudio\App\VoiceStudio.App.exe"
```

---

## Evidence Capture Template

After running each test, capture:

1. **Screenshot** of completed installation wizard
2. **Log file** contents (for silent install)
3. **Directory listing** of installed files
4. **Registry entries** for uninstall information

### Recommended Evidence Commands

```powershell
# Capture installed files
Get-ChildItem "C:\Program Files\VoiceStudio" -Recurse | Select-Object FullName, Length | Out-File "phase2_installed_files.txt"

# Capture registry uninstall entry
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | Where-Object { $_.DisplayName -like "*VoiceStudio*" } | Out-File "phase2_registry.txt"
```

---

## Expected Results

| Test | Expected Outcome |
|------|------------------|
| 2.1 Fresh Install | App in Start Menu, Programs and Features, launches without error |
| 2.2 Silent Install | No UI, log shows success, same installation result |
| 2.3 Upgrade | Detects previous version, preserves user data, version updated |
| 2.4 Rollback | Clean uninstall, v1.0.0 installs, user data preserved |

---

## Human Testing Required

The following require human interaction:

- [ ] 2.1.1 - Run interactive installer and observe wizard
- [ ] 2.1.2 - Verify prerequisite prompts appear if missing
- [ ] 2.1.5 - Verify Start Menu entry
- [ ] 2.2.1 - Run silent install and confirm no UI
- [ ] 2.3.2 - Create test project in v1.0.0
- [ ] 2.3.4 - Open v1.0.1 and verify settings preserved
- [ ] 2.4.3 - Launch v1.0.0 after rollback

---

## Phase 2 Automated Verification: PASS

- ✅ Prerequisites detected correctly
- ✅ Installer files present
- ✅ Commands documented for human testing
- ⏳ Human testing required for full PASS
