# Fix Cursor renderer crash - clears all caches and corrupted workspace state
# Run this from a separate PowerShell window (not inside Cursor)
# Moved to tools/ per Arch Review Task 1.3

Write-Host "=== Cursor Crash Fix Script ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all Cursor processes
Write-Host "[1/4] Killing all Cursor processes..." -ForegroundColor Yellow
Get-Process -Name "Cursor","node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
$remaining = (Get-Process -Name "Cursor" -ErrorAction SilentlyContinue).Count
if ($remaining -gt 0) {
    Write-Host "  Some processes still running, force killing..." -ForegroundColor Red
    taskkill /F /IM "Cursor.exe" /T 2>$null
    Start-Sleep -Seconds 2
}
Write-Host "  Done." -ForegroundColor Green

# Step 2: Clear all Electron/Chromium caches
Write-Host "[2/4] Clearing renderer and GPU caches..." -ForegroundColor Yellow
$cacheDirs = @("GPUCache","DawnWebGPUCache","DawnGraphiteCache","Cache","Code Cache","CachedData","Service Worker","Crashpad\reports")
foreach ($d in $cacheDirs) {
    $p = "$env:APPDATA\Cursor\$d"
    if (Test-Path $p) {
        Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  Cleared: $d" -ForegroundColor Gray
    }
}
Write-Host "  Done." -ForegroundColor Green

# Step 3: Rename corrupted workspace storage (preserves it as backup)
Write-Host "[3/4] Resetting workspace storage..." -ForegroundColor Yellow
$wsDir = "$env:APPDATA\Cursor\User\workspaceStorage\95c855ccfd257fe99929d22cc49ecde3"
if (Test-Path $wsDir) {
    $backupName = "95c855ccfd257fe99929d22cc49ecde3.crash-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Rename-Item $wsDir $backupName -Force -ErrorAction SilentlyContinue
    if ($?) {
        Write-Host "  Workspace storage backed up and reset." -ForegroundColor Gray
    } else {
        Write-Host "  Could not rename workspace storage (may still be locked)." -ForegroundColor Red
        Write-Host "  Trying to delete just the database files..." -ForegroundColor Yellow
        Remove-Item "$wsDir\state.vscdb*" -Force -ErrorAction SilentlyContinue
        Get-ChildItem $wsDir -Recurse -Filter "*.vscdb*" | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "  Database files cleared." -ForegroundColor Gray
    }
}
Write-Host "  Done." -ForegroundColor Green

# Step 4: Clear WebStorage (1.2GB - can cause renderer issues)
Write-Host "[4/4] Clearing WebStorage..." -ForegroundColor Yellow
$wsPath = "$env:APPDATA\Cursor\WebStorage"
if (Test-Path $wsPath) {
    Remove-Item $wsPath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Cleared 1.2GB WebStorage." -ForegroundColor Gray
}
Write-Host "  Done." -ForegroundColor Green

Write-Host ""
Write-Host "=== All caches cleared ===" -ForegroundColor Cyan
Write-Host "You will lose: open tabs, some extension state (NOT your code or settings)." -ForegroundColor Yellow
Write-Host ""
Write-Host "Launching Cursor now..." -ForegroundColor Cyan
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$cursorExe = if (Test-Path "E:\cursor\Cursor.exe") { "E:\cursor\Cursor.exe" } else { "${env:LOCALAPPDATA}\Programs\cursor\Cursor.exe" }
Start-Process $cursorExe $projectRoot
Write-Host "If it still crashes, rerun this script and add --disable-gpu:" -ForegroundColor Yellow
Write-Host "  Start-Process '$cursorExe' '--disable-gpu $projectRoot'" -ForegroundColor Gray
