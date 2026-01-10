# Gate C — Crash Log Instrumentation Specification

**Purpose:** Deterministic crash logging for Gate C UI proof runs  
**Owner:** UI Engineer (Role 3)  
**Date Created:** 2025-01-28  
**Status:** ✅ Implemented

---

## Summary

The App.xaml.cs `UnhandledException` handler has been enhanced to write **deterministic, structured crash logs** to a known location. When VS-0012 is resolved and the app boots, if any unhandled exceptions occur, evidence will be automatically captured.

---

## Crash Log Location

### Primary Location

```
%LOCALAPPDATA%\VoiceStudio\crashes\crash_<TIMESTAMP>.log
```

**Example:**
```
C:\Users\Tyler\AppData\Local\VoiceStudio\crashes\crash_2025-01-28_14-32-45-123.log
```

### Latest Crash Link

```
%LOCALAPPDATA%\VoiceStudio\crashes\latest.log
```

Points to the most recent crash log for quick access.

---

## Directory Structure

```
C:\Users\<USERNAME>\AppData\Local\VoiceStudio\
├── crashes/
│   ├── crash_2025-01-28_14-32-45-123.log     (Timestamped logs)
│   ├── crash_2025-01-28_14-33-12-456.log
│   ├── crash_2025-01-28_14-34-01-789.log
│   └── latest.log                             (Symlink to latest)
```

---

## Crash Log Contents

### Example Crash Log

```
═══════════════════════════════════════════════════════════════════
VoiceStudio Unhandled Exception Report
═══════════════════════════════════════════════════════════════════

Timestamp (UTC): 2025-01-28_14-32-45-123
Process ID: 12345
Thread ID: 7

--- Startup Stage ---
App Startup Time: 2025-01-28_14:32:30.456
Uptime at crash: 14.667s
Startup Profiler: Active (within startup phase)

--- Environment ---
OS: Microsoft Windows 10.0.26200
.NET Runtime: .NET 8.0.22
Working Dir: E:\VoiceStudio

--- Exception Details ---
Exception Type: System.Runtime.InteropServices.COMException
Message: Class not registered (REGDB_E_CLASSNOTREG)
HResult: 0x80040154

--- Stack Trace ---
   at Microsoft.UI.Xaml.Application.Start(ApplicationInitializationCallback callback)
   at VoiceStudio.App.Program.Main() in C:\build\App.g.i.cs:line 1
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()

--- Inner Exception ---
Type: System.ComponentModel.Win32Exception
Message: The specified class is not registered
Stack Trace: [inner stack]

═══════════════════════════════════════════════════════════════════
```

---

## Crash Log Fields

| Field | Purpose | Example |
|-------|---------|---------|
| **Timestamp (UTC)** | When crash occurred | `2025-01-28_14-32-45-123` |
| **Process ID** | Process that crashed | `12345` |
| **Thread ID** | Thread that threw exception | `7` |
| **Startup Stage** | App uptime when crash happened | `14.667s` |
| **Environment** | OS, .NET version, working dir | See above |
| **Exception Type** | Full type name of exception | `System.Runtime.InteropServices.COMException` |
| **Message** | Exception message | `Class not registered (REGDB_E_CLASSNOTREG)` |
| **HResult** | Win32 error code (if applicable) | `0x80040154` |
| **Stack Trace** | Full call stack | See above |
| **Inner Exception** | Root cause (if nested) | See above |

---

## Code Implementation

**File:** `src/VoiceStudio.App/App.xaml.cs`  
**Method:** `App_UnhandledException` (lines 31-100)

### Key Features

✅ **Deterministic Path**
- Uses `Environment.SpecialFolder.LocalApplicationData` (always correct)
- Creates directory if missing

✅ **Timestamped Filenames**
- Format: `crash_YYYY-MM-DD_HH-mm-ss-fff.log`
- Preserves crash history (not overwritten)
- Microsecond precision prevents collisions

✅ **Structured Content**
- Startup stage (when during boot)
- Environment details (OS, runtime, paths)
- Exception details (type, message, HResult)
- Full stack trace
- Inner exception details

✅ **Fallback Logging**
- If file write fails, logs to Debug output
- Never crashes the crash handler itself

✅ **Latest Link**
- Writes `latest.log` symlink for quick access
- Helps identify most recent crash

---

## How UI Engineer Uses This

### During Gate C Proof Run

**If app crashes:**

1. **Locate crash log:**
   ```powershell
   Get-Item -Path "$env:LOCALAPPDATA\VoiceStudio\crashes\latest.log"
   ```

2. **Read crash details:**
   ```powershell
   Get-Content "$env:LOCALAPPDATA\VoiceStudio\crashes\latest.log" -Head 50
   ```

3. **Use in proof run:**
   ```
   Evidence captured in: C:\Users\[USERNAME]\AppData\Local\VoiceStudio\crashes\crash_*.log
   Exception type: [from log]
   HResult: [from log]
   Uptime at crash: [from log]
   ```

4. **Document in ledger:**
   - Create VS-#### entry
   - Reference crash log path and filename
   - Include exception type and HResult
   - Update VS-0012 with findings

### After Successful Boot

**If app boots successfully:**
- No crash log will be created
- This is the desired outcome
- Document in proof run: "✅ No crash logs written"

---

## Accessing Crash Logs

### From PowerShell

```powershell
# List all crashes
Get-ChildItem -Path "$env:LOCALAPPDATA\VoiceStudio\crashes\" -Filter "crash_*.log" | 
  Sort-Object LastWriteTime -Descending

# View latest crash
Get-Content -Path "$env:LOCALAPPDATA\VoiceStudio\crashes\latest.log"

# Count crashes
(Get-ChildItem -Path "$env:LOCALAPPDATA\VoiceStudio\crashes\" -Filter "crash_*.log").Count
```

### From File Explorer

1. Press `Win+R`
2. Type: `%LOCALAPPDATA%\VoiceStudio\crashes`
3. Hit Enter
4. Browse crash logs

### From VS Debugger

1. Run app under debugger
2. If crash occurs, Output window shows: `"💥 Unhandled exception logged to: [path]"`
3. Copy path from Output window
4. Ctrl+O → paste path → read log

---

## Integration with VS-0012 Recovery

**When Release Engineer resolves VS-0012:**

1. UI Engineer runs `GATE_C_PROOF_RUN_SCRIPT.md` Part B (Boot Verification)
2. If app boots successfully:
   - Proceed to Part C (Navigation Verification)
   - Document: "✅ No crash logs written"
3. If app crashes:
   - Check crash log at `%LOCALAPPDATA%\VoiceStudio\crashes\latest.log`
   - Provide log to Release Engineer for debugging
   - Update VS-0012 entry with new evidence
   - Create new ledger entry if new issue found

---

## Verification

### Build Verification

```powershell
# Build with updated code
dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Debug -p:Platform=x64 -p:SkipRuleGuard=true

# Expected: 0 errors, 0 warnings
```

**Evidence:**
- [ ] Build succeeded
- [ ] No compilation errors in App.xaml.cs

### Code Review

**Lines changed:** `src/VoiceStudio.App/App.xaml.cs` lines 31-100

**Checklist:**
- ✅ Uses `Environment.SpecialFolder.LocalApplicationData` (deterministic)
- ✅ Creates directory with `CreateDirectory` (idempotent)
- ✅ Timestamps included in filename (preserves history)
- ✅ Captures exception details (type, message, HResult)
- ✅ Captures stack trace and inner exceptions
- ✅ Captures startup stage (uptime)
- ✅ Captures environment (OS, .NET, working dir)
- ✅ Handles file write failures gracefully
- ✅ Writes "latest" symlink for quick access
- ✅ Includes debug output (for Visual Studio troubleshooting)

---

## Example Proof Snippet

When UI Engineer runs Gate C proof run and encounters a crash, this is how evidence is captured:

```
═══════════════════════════════════════════════════════════════════
GATE C UI PROOF RUN — CRASH EVIDENCE
═══════════════════════════════════════════════════════════════════

Date Run: 2025-01-28
Operator: UI Engineer (Role 3)
Gate: C

BOOT VERIFICATION RESULT: ❌ CRASH DETECTED

Crash Log Location:
  C:\Users\Tyler\AppData\Local\VoiceStudio\crashes\crash_2025-01-28_14-32-45-123.log

Exception Details:
  Type: System.Runtime.InteropServices.COMException
  Message: Class not registered (REGDB_E_CLASSNOTREG)
  HResult: 0x80040154
  Uptime: 14.667s (crash during OnLaunched phase)

Stack Trace:
  at Microsoft.UI.Xaml.Application.Start(ApplicationInitializationCallback callback)
  at VoiceStudio.App.Program.Main()

Environment:
  OS: Windows 10.0.26200
  Runtime: .NET 8.0.22
  Process ID: 12345

ACTION: Provide crash log to Release Engineer for VS-0012 debugging
═══════════════════════════════════════════════════════════════════
```

---

## Related Documents

- `docs/governance/overseer/GATE_C_PROOF_RUN_SCRIPT.md` — Executable proof run
- `Recovery Plan/QUALITY_LEDGER.md` — VS-0012 entry
- `src/VoiceStudio.App/App.xaml.cs` — Implementation

