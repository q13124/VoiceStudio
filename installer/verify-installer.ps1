# VoiceStudio Quantum+ Installer Verification Script
# Verifies installer package completeness and correctness

param(
    [string]$InstallerPath,
    [string]$ExpectedVersion = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoiceStudio Quantum+ Installer Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $InstallerPath) {
    $InstallerPath = Join-Path $PSScriptRoot "Output\VoiceStudio-Setup-v$ExpectedVersion.exe"
}

if (-not (Test-Path $InstallerPath)) {
    Write-Host "Error: Installer not found at: $InstallerPath" -ForegroundColor Red
    Write-Host "Build installer first: .\build-installer.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Verifying installer: $InstallerPath" -ForegroundColor Yellow
Write-Host ""

$errors = @()
$warnings = @()

# Check installer file exists
Write-Host "Checking installer file..." -ForegroundColor Yellow
Write-Host "[OK] Installer file exists" -ForegroundColor Green

# Check file size (should be reasonable)
Write-Host "Checking file size..." -ForegroundColor Yellow
$fileSize = (Get-Item $InstallerPath).Length / 1MB
if ($fileSize -lt 1) {
    $warnings += "Installer file size is very small ($([math]::Round($fileSize, 2)) MB) - may be incomplete"
    Write-Host "[WARN] File size: $([math]::Round($fileSize, 2)) MB (very small)" -ForegroundColor Yellow
}
elseif ($fileSize -gt 500) {
    $warnings += "Installer file size is very large ($([math]::Round($fileSize, 2)) MB) - may include unnecessary files"
    Write-Host "[WARN] File size: $([math]::Round($fileSize, 2)) MB (very large)" -ForegroundColor Yellow
}
else {
    Write-Host "[OK] Installer file size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
}

# Check if installer is executable (basic check)
Write-Host "Checking file type..." -ForegroundColor Yellow
try {
    $fileInfo = Get-Item $InstallerPath
    if ($fileInfo.Extension -ne ".exe" -and $fileInfo.Extension -ne ".msi") {
        $errors += "Installer must be .exe or .msi file"
        Write-Host "[ERROR] Invalid file type: $($fileInfo.Extension)" -ForegroundColor Red
    }
    else {
        Write-Host "[OK] Installer file type: $($fileInfo.Extension)" -ForegroundColor Green
    }
}
catch {
    $errors += "Could not read installer file: $_"
    Write-Host "[ERROR] Error reading file: $_" -ForegroundColor Red
}

# Check file permissions
Write-Host "Checking file permissions..." -ForegroundColor Yellow
try {
    $acl = Get-Acl $InstallerPath
    Write-Host "[OK] File permissions accessible" -ForegroundColor Green
}
catch {
    $warnings += "Could not check file permissions: $_"
    Write-Host "[WARN] Could not verify file permissions" -ForegroundColor Yellow
}

# Check if file is readable
Write-Host "Checking file readability..." -ForegroundColor Yellow
try {
    $stream = [System.IO.File]::OpenRead($InstallerPath)
    $stream.Close()
    Write-Host "[OK] File is readable" -ForegroundColor Green
}
catch {
    $errors += "File is not readable: $_"
    Write-Host "[ERROR] File is not readable" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[OK] Installer verification passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Test installer on clean Windows 10 VM" -ForegroundColor White
    Write-Host "2. Test installer on clean Windows 11 VM" -ForegroundColor White
    Write-Host "3. Test upgrade from previous version" -ForegroundColor White
    Write-Host "4. Test uninstallation" -ForegroundColor White
    Write-Host "5. Code sign installer (if applicable)" -ForegroundColor White
    exit 0
}
else {
    if ($errors.Count -gt 0) {
        Write-Host "Errors found:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "  [ERROR] $error" -ForegroundColor Red
        }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "Warnings:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  [WARN] $warning" -ForegroundColor Yellow
        }
    }
    
    exit 1
}

