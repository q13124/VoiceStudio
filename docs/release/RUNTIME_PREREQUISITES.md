# VoiceStudio Runtime Prerequisites

**Gate:** C (App boot) + H (Packaging)  
**Date:** 2025-01-28  
**Owner:** Release Engineer  

## Overview

VoiceStudio is deployed as an **unpackaged WinUI 3 desktop application** (Option B). This requires specific runtime components to be installed on the target machine.

## Required Prerequisites

### 1. .NET 8 Desktop Runtime
- **Version:** 8.0.0 or later
- **Architecture:** x64 (matches application)
- **Purpose:** Executes the C# .NET code
- **Installation:** Download from Microsoft (.NET 8.0 Desktop Runtime installer)

### 2. Windows App SDK Runtime (WinUI 3)
- **Version:** 1.8.251105000 or later (matches application reference)
- **Architecture:** x64
- **Purpose:** Provides WinUI 3 controls, XAML rendering, and COM activation
- **Installation:** Windows App Runtime installer from Microsoft

## Supported Launch Environments

### Gate C (Development/Testing)
- Machine with both runtimes installed
- Launch via: `Start-Process "C:\Program Files\VoiceStudio\VoiceStudio.App.exe"`
- Process remains running, main window appears

### Gate H (Packaging/Release)
- Installer ensures prerequisites are met before allowing installation
- Post-install launch works without COMException

## Failure Mode (Without Prerequisites)

Launching `VoiceStudio.App.exe` without the Windows App SDK runtime results in:

```
Exit Code: -532462766 (0xE0434352)
Exception: System.Runtime.InteropServices.COMException (0x80040154)
Message: Class not registered (REGDB_E_CLASSNOTREG)
Stack: Microsoft.UI.Xaml.Application.Start(...) → VoiceStudio.App.Program.Main(...)
```

This is expected behavior - the app requires WinUI 3 runtime to function.

## Installation Verification

### Runtime Check Commands

```powershell
# Check .NET 8 Desktop Runtime
Get-ChildItem "HKLM:\SOFTWARE\dotnet\Setup\InstalledVersions\x64\sharedhost" | ForEach-Object {
    $version = (Get-ItemProperty $_.PSPath).Version
    if ($version -ge 8.0.0) { Write-Host "✅ .NET 8.0 Desktop Runtime found: $version" }
}

# Check Windows App SDK Runtime (approximate)
Get-AppxPackage | Where-Object { $_.Name -like "*Microsoft.WindowsAppRuntime*" -and $_.Architecture -eq "X64" }
```

### Gate C Proof Criteria

To pass Gate C (app boot):
1. Machine has required runtimes installed
2. `VoiceStudio.App.exe` launches successfully
3. Process stays running (no immediate exit)
4. Main window becomes visible
5. No COMException in Windows Application log

## Documentation Links

- `docs/release/UPGRADE_ROLLBACK_NOTES.md` - Upgrade behavior
- `docs/release/CRASH_BUNDLE_EXPORT_FEATURE.md` - Diagnostics export
- `installer/README.md` - Installer details

---

**Last Updated:** 2025-01-28  
**Next:** Gate C proof run once prerequisites are verified