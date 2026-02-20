<#
.SYNOPSIS
    VoiceStudio UI Test Preflight Validation

.DESCRIPTION
    Validates all prerequisites for running WinAppDriver-based UI tests.
    Checks WinAppDriver, application build, backend, test data, and Python dependencies.

.PARAMETER Fix
    Attempt to fix issues automatically where possible (e.g., start WinAppDriver, backend).

.PARAMETER Verbose
    Show detailed output for each check.

.EXAMPLE
    .\scripts\preflight_ui_tests.ps1

.EXAMPLE
    .\scripts\preflight_ui_tests.ps1 -Fix -Verbose
#>

param(
    [switch]$Fix,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$script:AllPassed = $true
$script:Results = @()

function Write-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details = "",
        [string]$FixAction = ""
    )

    $status = if ($Passed) { "OK" } else { "FAIL" }
    $color = if ($Passed) { "Green" } else { "Red" }
    
    $statusText = "[$status]".PadLeft(6)
    Write-Host "$statusText " -ForegroundColor $color -NoNewline
    Write-Host $Name
    
    if ($Details -and ($Verbose -or -not $Passed)) {
        Write-Host "       $Details" -ForegroundColor Gray
    }
    
    if (-not $Passed -and $FixAction) {
        Write-Host "       Fix: $FixAction" -ForegroundColor Yellow
    }

    $script:Results += @{
        Name = $Name
        Passed = $Passed
        Details = $Details
    }

    if (-not $Passed) {
        $script:AllPassed = $false
    }
}

# =============================================================================
# Check 1: WinAppDriver
# =============================================================================

Write-Host "`nChecking WinAppDriver..." -ForegroundColor Cyan

$wadPath = "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
$wadInstalled = Test-Path $wadPath

if ($wadInstalled) {
    Write-Check -Name "WinAppDriver installed" -Passed $true -Details $wadPath
    
    # Check if WinAppDriver is running
    $wadProcess = Get-Process -Name "WinAppDriver" -ErrorAction SilentlyContinue
    $wadRunning = $null -ne $wadProcess
    
    if ($wadRunning) {
        Write-Check -Name "WinAppDriver running" -Passed $true -Details "PID: $($wadProcess.Id)"
    } else {
        if ($Fix) {
            Write-Host "       Starting WinAppDriver..." -ForegroundColor Yellow
            Start-Process $wadPath -PassThru | Out-Null
            Start-Sleep -Seconds 2
            $wadProcess = Get-Process -Name "WinAppDriver" -ErrorAction SilentlyContinue
            $wadRunning = $null -ne $wadProcess
        }
        Write-Check -Name "WinAppDriver running" -Passed $wadRunning `
            -Details $(if ($wadRunning) { "Started successfully" } else { "Not running" }) `
            -FixAction "Start-Process '$wadPath'"
    }
} else {
    Write-Check -Name "WinAppDriver installed" -Passed $false `
        -Details "Not found at $wadPath" `
        -FixAction "Download from https://github.com/microsoft/WinAppDriver/releases"
}

# =============================================================================
# Check 2: VoiceStudio Application Build
# =============================================================================

Write-Host "`nChecking application build..." -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $PSScriptRoot
$appPath = Join-Path $projectRoot "src\VoiceStudio.App\bin\x64\Debug\net8.0-windows10.0.19041.0\win-x64\VoiceStudio.App.exe"

if (Test-Path $appPath) {
    $appInfo = Get-Item $appPath
    $buildTime = $appInfo.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
    Write-Check -Name "VoiceStudio.App.exe" -Passed $true -Details "Built: $buildTime"
} else {
    Write-Check -Name "VoiceStudio.App.exe" -Passed $false `
        -Details "Not found at expected location" `
        -FixAction "dotnet build VoiceStudio.sln -c Debug -p:Platform=x64"
}

# =============================================================================
# Check 3: Backend Service
# =============================================================================

Write-Host "`nChecking backend service..." -ForegroundColor Cyan

$backendPort = 8000
$backendUrl = "http://127.0.0.1:$backendPort/api/health"

try {
    $response = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    $backendRunning = $response.StatusCode -eq 200
    Write-Check -Name "Backend health check" -Passed $true -Details "$backendUrl -> 200"
} catch {
    $backendRunning = $false
    
    if ($Fix) {
        Write-Host "       Starting backend..." -ForegroundColor Yellow
        $backendPath = Join-Path $projectRoot "backend"
        $env:PYTHONPATH = $projectRoot
        Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "$backendPort" `
            -WorkingDirectory $backendPath -WindowStyle Hidden
        Start-Sleep -Seconds 5
        
        try {
            $response = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            $backendRunning = $response.StatusCode -eq 200
        } catch {
            $backendRunning = $false
        }
    }
    
    Write-Check -Name "Backend health check" -Passed $backendRunning `
        -Details $(if ($backendRunning) { "Started successfully" } else { "$backendUrl -> Connection refused" }) `
        -FixAction "cd backend && python -m uvicorn api.main:app --host 127.0.0.1 --port 8000"
}

# =============================================================================
# Check 4: Test Audio Files
# =============================================================================

Write-Host "`nChecking test audio files..." -ForegroundColor Cyan

$canonicalAudioDir = Join-Path $projectRoot "tests\assets\canonical\standard"
$canonicalAudioExists = Test-Path $canonicalAudioDir

if ($canonicalAudioExists) {
    $audioFiles = Get-ChildItem -Path $canonicalAudioDir -Filter "*.wav" -ErrorAction SilentlyContinue
    $audioCount = $audioFiles.Count
    
    if ($audioCount -gt 0) {
        Write-Check -Name "Canonical test audio" -Passed $true -Details "$audioCount WAV files in $canonicalAudioDir"
    } else {
        Write-Check -Name "Canonical test audio" -Passed $false `
            -Details "No WAV files in $canonicalAudioDir" `
            -FixAction "Add test audio files to tests/assets/canonical/standard/"
    }
} else {
    Write-Check -Name "Canonical test audio" -Passed $false `
        -Details "Directory not found: $canonicalAudioDir" `
        -FixAction "Create tests/assets/canonical/standard/ and add test audio"
}

# =============================================================================
# Check 5: Python Dependencies
# =============================================================================

Write-Host "`nChecking Python dependencies..." -ForegroundColor Cyan

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    $pythonOk = $pythonVersion -match "Python 3\.(10|11|12)"
    Write-Check -Name "Python version" -Passed $pythonOk -Details $pythonVersion
} catch {
    Write-Check -Name "Python version" -Passed $false `
        -Details "Python not found in PATH" `
        -FixAction "Install Python 3.10+ and add to PATH"
}

# Check required packages
$requiredPackages = @(
    @{ Name = "selenium"; Import = "selenium" },
    @{ Name = "Appium-Python-Client"; Import = "appium" },
    @{ Name = "pytest"; Import = "pytest" },
    @{ Name = "Pillow"; Import = "PIL" }
)

foreach ($pkg in $requiredPackages) {
    $checkResult = python -c "import $($pkg.Import)" 2>&1
    $installed = $LASTEXITCODE -eq 0
    
    if ($installed) {
        $version = python -c "import $($pkg.Import); print(getattr($($pkg.Import), '__version__', 'installed'))" 2>&1
        Write-Check -Name "Package: $($pkg.Name)" -Passed $true -Details $version
    } else {
        if ($Fix) {
            Write-Host "       Installing $($pkg.Name)..." -ForegroundColor Yellow
            pip install $($pkg.Name) --quiet
            $checkResult = python -c "import $($pkg.Import)" 2>&1
            $installed = $LASTEXITCODE -eq 0
        }
        Write-Check -Name "Package: $($pkg.Name)" -Passed $installed `
            -Details $(if ($installed) { "Installed" } else { "Not installed" }) `
            -FixAction "pip install $($pkg.Name)"
    }
}

# Check UI test specific requirements
$uiReqsPath = Join-Path $projectRoot "tests\ui\requirements.txt"
if (Test-Path $uiReqsPath) {
    Write-Check -Name "UI test requirements.txt" -Passed $true -Details $uiReqsPath
} else {
    Write-Check -Name "UI test requirements.txt" -Passed $false `
        -Details "Not found" `
        -FixAction "Create tests/ui/requirements.txt with UI test dependencies"
}

# =============================================================================
# Check 6: Developer Mode (Windows)
# =============================================================================

Write-Host "`nChecking Windows configuration..." -ForegroundColor Cyan

try {
    $devMode = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock" -Name "AllowDevelopmentWithoutDevLicense" -ErrorAction SilentlyContinue
    $devModeEnabled = $devMode.AllowDevelopmentWithoutDevLicense -eq 1
    Write-Check -Name "Developer mode" -Passed $devModeEnabled `
        -Details $(if ($devModeEnabled) { "Enabled" } else { "Disabled" }) `
        -FixAction "Settings > Update & Security > For developers > Developer mode"
} catch {
    Write-Check -Name "Developer mode" -Passed $false `
        -Details "Could not check registry" `
        -FixAction "Enable Developer mode in Windows Settings"
}

# =============================================================================
# Summary
# =============================================================================

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "PREFLIGHT SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

$passed = ($script:Results | Where-Object { $_.Passed }).Count
$failed = ($script:Results | Where-Object { -not $_.Passed }).Count

Write-Host "`nTotal checks: $($script:Results.Count)"
Write-Host "  Passed: $passed" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })

if ($script:AllPassed) {
    Write-Host "`nAll prerequisites met!" -ForegroundColor Green
    Write-Host "Run tests with: pytest tests/ui/ -m smoke -v`n" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`nSome prerequisites are missing." -ForegroundColor Yellow
    Write-Host "Fix the issues above or run with -Fix to attempt auto-fixes.`n" -ForegroundColor Yellow
    exit 1
}
