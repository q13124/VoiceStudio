# VoiceStudio Quantum+ Silent Installer Test Script
# Tests silent installation and verifies installation completes

param(
    [string]$InstallerPath,
    [string]$InstallPath = "C:\Program Files\VoiceStudio",
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Silent Installer Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $InstallerPath) {
    $InstallerPath = Join-Path $PSScriptRoot "Output\VoiceStudio-Setup-v$Version.exe"
}

if (-not (Test-Path $InstallerPath)) {
    Write-Host "Error: Installer not found at: $InstallerPath" -ForegroundColor Red
    Write-Host "Build installer first: .\build-installer.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Installer: $InstallerPath" -ForegroundColor Yellow
Write-Host "Install Path: $InstallPath" -ForegroundColor Yellow
Write-Host ""

# Check if already installed
if (Test-Path $InstallPath) {
    Write-Host "Warning: Installation directory already exists: $InstallPath" -ForegroundColor Yellow
    $response = Read-Host "Uninstall existing installation? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host "Uninstalling existing installation..." -ForegroundColor Yellow
        $uninstaller = Join-Path $InstallPath "uninstall.exe"
        if (Test-Path $uninstaller) {
            & $uninstaller /SILENT
            Start-Sleep -Seconds 5
        }
        else {
            Write-Host "Warning: Uninstaller not found. Manual uninstallation may be required." -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Skipping test. Please uninstall manually first." -ForegroundColor Yellow
        exit 1
    }
}

# Run silent installation
Write-Host "Running silent installation..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath $InstallerPath -ArgumentList "/S", "/DIR=`"$InstallPath`"" -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✓ Silent installation completed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Silent installation failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "✗ Silent installation failed: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow

$errors = @()
$warnings = @()

# Check installation directory
if (Test-Path $InstallPath) {
    Write-Host "✓ Installation directory exists" -ForegroundColor Green
}
else {
    $errors += "Installation directory not found: $InstallPath"
}

# Check application executable
$appExe = Join-Path $InstallPath "App\VoiceStudioApp.exe"
if (Test-Path $appExe) {
    Write-Host "✓ Application executable exists" -ForegroundColor Green
}
else {
    $errors += "Application executable not found: $appExe"
}

# Check backend files
$backendPath = Join-Path $InstallPath "Backend"
if (Test-Path $backendPath) {
    Write-Host "✓ Backend directory exists" -ForegroundColor Green
    
    $backendMain = Join-Path $backendPath "api\main.py"
    if (Test-Path $backendMain) {
        Write-Host "✓ Backend main.py exists" -ForegroundColor Green
    }
    else {
        $errors += "Backend main.py not found: $backendMain"
    }
}
else {
    $errors += "Backend directory not found: $backendPath"
}

# Check core files
$corePath = Join-Path $InstallPath "Core"
if (Test-Path $corePath) {
    Write-Host "✓ Core directory exists" -ForegroundColor Green
}
else {
    $warnings += "Core directory not found: $corePath"
}

# Check engine manifests
$enginesPath = Join-Path $InstallPath "Engines"
if (Test-Path $enginesPath) {
    Write-Host "✓ Engines directory exists" -ForegroundColor Green
}
else {
    $warnings += "Engines directory not found: $enginesPath"
}

# Check documentation
$docsPath = Join-Path $InstallPath "Docs"
if (Test-Path $docsPath) {
    Write-Host "✓ Documentation directory exists" -ForegroundColor Green
}
else {
    $warnings += "Documentation directory not found: $docsPath"
}

# Check Start Menu shortcut
$startMenuPath = "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\VoiceStudio"
if (Test-Path $startMenuPath) {
    Write-Host "✓ Start Menu shortcut exists" -ForegroundColor Green
}
else {
    $warnings += "Start Menu shortcut not found: $startMenuPath"
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✓ Silent installation test passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation verified successfully." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Test application launch" -ForegroundColor White
    Write-Host "2. Test backend startup" -ForegroundColor White
    Write-Host "3. Test uninstallation" -ForegroundColor White
    exit 0
}
else {
    if ($errors.Count -gt 0) {
        Write-Host "Errors found:" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "  ✗ $error" -ForegroundColor Red
        }
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "Warnings:" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "  ⚠ $warning" -ForegroundColor Yellow
        }
    }
    
    if ($errors.Count -gt 0) {
        Write-Host ""
        Write-Host "Silent installation test failed. Review errors above." -ForegroundColor Red
        exit 1
    }
    else {
        Write-Host ""
        Write-Host "Silent installation test passed with warnings." -ForegroundColor Yellow
        exit 0
    }
}
