# VoiceStudio Quantum+ Simple Installer Script
# PowerShell-based installer for development/testing

param(
    [string]$InstallPath = "$env:ProgramFiles\VoiceStudio",
    [switch]$SkipDependencies
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoiceStudio Quantum+ Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Error: Administrator privileges required" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

# Check Windows version
$osVersion = [System.Environment]::OSVersion.Version
if ($osVersion.Major -lt 10) {
    Write-Host "Error: Windows 10 or later required" -ForegroundColor Red
    exit 1
}

# Check .NET 8 Runtime
Write-Host "Checking for .NET 8 Runtime..." -ForegroundColor Yellow
$dotnetPath = Get-Command dotnet -ErrorAction SilentlyContinue
if (-not $dotnetPath) {
    Write-Host "Error: .NET 8 Runtime not found" -ForegroundColor Red
    Write-Host "Please install from: https://dotnet.microsoft.com/download/dotnet/8.0" -ForegroundColor Yellow
    exit 1
}
Write-Host ".NET Runtime found!" -ForegroundColor Green

# Check Python (optional)
Write-Host "Checking for Python..." -ForegroundColor Yellow
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "Warning: Python not found in PATH" -ForegroundColor Yellow
    Write-Host "Python 3.10+ is required for the backend" -ForegroundColor Yellow
    if (-not $SkipDependencies) {
        $installPython = Read-Host "Would you like to install Python? (Y/N)"
        if ($installPython -eq "Y") {
            Write-Host "Please download Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
        }
    }
}
else {
    Write-Host "Python found!" -ForegroundColor Green
}

# Create installation directory
Write-Host ""
Write-Host "Creating installation directory..." -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    Write-Host "Warning: Installation directory already exists" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (Y/N)"
    if ($overwrite -ne "Y") {
        Write-Host "Installation cancelled" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Path $InstallPath -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
Write-Host "Installation directory created: $InstallPath" -ForegroundColor Green

# Copy files
Write-Host ""
Write-Host "Copying application files..." -ForegroundColor Yellow

$RootDir = Split-Path -Parent $PSScriptRoot

# Frontend
$FrontendSource = Join-Path $RootDir "src\VoiceStudio.App\bin\Release\net8.0-windows10.0.19041.0"
$FrontendDest = Join-Path $InstallPath "App"
if (Test-Path $FrontendSource) {
    Copy-Item -Path "$FrontendSource\*" -Destination $FrontendDest -Recurse -Force
    Write-Host "Frontend files copied!" -ForegroundColor Green
}
else {
    Write-Host "Warning: Frontend build not found. Please build the application first." -ForegroundColor Yellow
}

# Backend
$BackendSource = Join-Path $RootDir "backend"
$BackendDest = Join-Path $InstallPath "Backend"
Copy-Item -Path "$BackendSource\*" -Destination $BackendDest -Recurse -Force -Exclude "__pycache__","*.pyc"
Write-Host "Backend files copied!" -ForegroundColor Green

# Core
$CoreSource = Join-Path $RootDir "app\core"
$CoreDest = Join-Path $InstallPath "Core"
Copy-Item -Path "$CoreSource\*" -Destination $CoreDest -Recurse -Force -Exclude "__pycache__","*.pyc"
Write-Host "Core files copied!" -ForegroundColor Green

# Engines
$EnginesSource = Join-Path $RootDir "engines"
$EnginesDest = Join-Path $InstallPath "Engines"
Copy-Item -Path "$EnginesSource\*" -Destination $EnginesDest -Recurse -Force
Write-Host "Engine manifests copied!" -ForegroundColor Green

# Documentation
$DocsSource = Join-Path $RootDir "docs"
$DocsDest = Join-Path $InstallPath "Docs"
Copy-Item -Path "$DocsSource\*" -Destination $DocsDest -Recurse -Force
Write-Host "Documentation copied!" -ForegroundColor Green

# Create Start Menu shortcut
Write-Host ""
Write-Host "Creating Start Menu shortcut..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:ProgramData\Microsoft\Windows\Start Menu\Programs\VoiceStudio Quantum+.lnk")
$Shortcut.TargetPath = Join-Path $InstallPath "App\VoiceStudio.App.exe"
$Shortcut.WorkingDirectory = $InstallPath
$Shortcut.Description = "Professional Voice Cloning Studio"
$Shortcut.Save()
Write-Host "Start Menu shortcut created!" -ForegroundColor Green

# Create Desktop shortcut (optional)
$createDesktop = Read-Host "Create Desktop shortcut? (Y/N)"
if ($createDesktop -eq "Y") {
    $DesktopShortcut = $WshShell.CreateShortcut("$env:Public\Desktop\VoiceStudio Quantum+.lnk")
    $DesktopShortcut.TargetPath = Join-Path $InstallPath "App\VoiceStudio.App.exe"
    $DesktopShortcut.WorkingDirectory = $InstallPath
    $DesktopShortcut.Description = "Professional Voice Cloning Studio"
    $DesktopShortcut.Save()
    Write-Host "Desktop shortcut created!" -ForegroundColor Green
}

# Install Python packages (if Python is available)
if ($pythonPath) {
    Write-Host ""
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    $RequirementsFile = Join-Path $BackendDest "requirements.txt"
    if (Test-Path $RequirementsFile) {
        python -m pip install -r $RequirementsFile
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python packages installed!" -ForegroundColor Green
        }
        else {
            Write-Host "Warning: Python package installation failed" -ForegroundColor Yellow
        }
    }
}

# Create user data directories
Write-Host ""
Write-Host "Creating user data directories..." -ForegroundColor Yellow
$UserDataPath = Join-Path $env:APPDATA "VoiceStudio"
New-Item -ItemType Directory -Path $UserDataPath -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $UserDataPath "layouts") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $UserDataPath "logs") -Force | Out-Null
Write-Host "User data directories created!" -ForegroundColor Green

# Create ProgramData directories
$ProgramDataPath = Join-Path $env:ProgramData "VoiceStudio"
New-Item -ItemType Directory -Path $ProgramDataPath -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ProgramDataPath "models") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ProgramDataPath "cache") -Force | Out-Null
Write-Host "ProgramData directories created!" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Path: $InstallPath" -ForegroundColor White
Write-Host "User Data: $UserDataPath" -ForegroundColor White
Write-Host "Program Data: $ProgramDataPath" -ForegroundColor White
Write-Host ""
Write-Host "You can now launch VoiceStudio Quantum+ from the Start Menu!" -ForegroundColor Cyan
Write-Host ""

