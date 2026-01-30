# File Lock Troubleshooting Guide

**Issue:** `Microsoft.Bcl.AsyncInterfaces.dll` is locked, preventing NuGet restore/build  
**Date:** 2025-01-28

## Diagnosis

The file lock is caused by:

- **dotnet.exe process (PID 27988)** has the DLL loaded in memory
- This process is likely a background build or language server from Cursor IDE
- Multiple Cursor processes are running (20+ instances)

## Root Cause

When IDEs or build tools load DLLs from the NuGet cache, they keep file handles open. This prevents:

- NuGet from cleaning/updating packages
- MSBuild from accessing the files
- Package restore operations

## Solutions (In Order of Preference)

### Option 1: Close Cursor IDE (RECOMMENDED)

1. **Save all work** in Cursor
2. **Close Cursor completely** (all windows)
3. **Wait 10-15 seconds** for processes to terminate
4. **Verify processes are gone:**
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*Cursor*" -or $_.ProcessName -like "*dotnet*"}
   ```
5. **Retry restore:**
   ```powershell
   dotnet restore VoiceStudio.sln
   ```

### Option 2: Kill Specific Process

If Cursor is closed but process persists:

```powershell
Stop-Process -Id 27988 -Force
```

Then retry restore.

### Option 3: Kill All Related Processes

If multiple processes are holding locks:

```powershell
Get-Process | Where-Object {$_.ProcessName -like "*dotnet*" -and $_.Id -ne $PID} | Stop-Process -Force
```

**Warning:** This will kill all dotnet processes except the current PowerShell session.

### Option 4: Restart Computer

If all else fails, restart the computer to release all file handles.

## Prevention

To prevent this issue in the future:

1. **Close IDE before running builds** from command line
2. **Use separate terminal** for builds (not IDE-integrated terminal)
3. **Wait for builds to complete** before starting new ones
4. **Use `dotnet build --no-incremental`** to avoid incremental build locks

## Verification

After releasing the lock, verify with:

```powershell
# Check if file is accessible
$file = "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\tools\net6.0\Microsoft.Bcl.AsyncInterfaces.dll"
try {
    $stream = [System.IO.File]::Open($file, 'Open', 'ReadWrite', 'None')
    $stream.Close()
    Write-Output "✅ File is NOT locked"
} catch {
    Write-Output "❌ File IS still locked: $($_.Exception.Message)"
}
```

## Current Status

- **Locked File:** `Microsoft.Bcl.AsyncInterfaces.dll`
- **Locking Process:** dotnet.exe (PID 27988)
- **Additional Processes:** 20+ Cursor IDE instances
- **Action Required:** Close Cursor IDE or kill process 27988
