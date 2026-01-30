# VoiceStudio Quantum+ Installer Build Verification Script
# Verifies that installer can be built and all source files exist

param(
    [string]$InstallerType = "InnoSetup",
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installer Build Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$RootDir = Split-Path -Parent $PSScriptRoot
$InstallerDir = $PSScriptRoot
$errors = @()
$warnings = @()

# Check build script exists
Write-Host "Checking build script..." -ForegroundColor Yellow
$buildScript = Join-Path $InstallerDir "build-installer.ps1"
if (-not (Test-Path $buildScript)) {
    $errors += "Build script not found: $buildScript"
}
else {
    Write-Host "[OK] Build script exists" -ForegroundColor Green
}

# Check installer script exists
Write-Host "Checking installer script..." -ForegroundColor Yellow
if ($InstallerType -eq "InnoSetup") {
    $installerScript = Join-Path $InstallerDir "VoiceStudio.iss"
    if (-not (Test-Path $installerScript)) {
        $errors += "Inno Setup script not found: $installerScript"
    }
    else {
        Write-Host "[OK] Inno Setup script exists" -ForegroundColor Green
    }
}
elseif ($InstallerType -eq "WiX") {
    $installerScript = Join-Path $InstallerDir "VoiceStudio.wxs"
    if (-not (Test-Path $installerScript)) {
        $errors += "WiX script not found: $installerScript"
    }
    else {
        Write-Host "[OK] WiX script exists" -ForegroundColor Green
    }
}

# Check Gate C publish output (canonical frontend artifact)
Write-Host "Checking Gate C publish output..." -ForegroundColor Yellow
$publishDir = Join-Path $RootDir ".buildlogs\x64\Release\gatec-publish"
if (-not (Test-Path $publishDir)) {
    $warnings += "Gate C publish output not found: $publishDir (run scripts\\gatec-publish-launch.ps1 -NoLaunch)"
}
else {
    $missing = @()
    $required = @(
        (Join-Path $publishDir "VoiceStudio.App.exe"),
        (Join-Path $publishDir "VoiceStudio.App.dll"),
        (Join-Path $publishDir "VoiceStudio.App.deps.json"),
        (Join-Path $publishDir "VoiceStudio.App.runtimeconfig.json")
    )
    foreach ($p in $required) {
        if (-not (Test-Path $p)) {
            $missing += $p
        }
    }
    if ($missing.Count -eq 0) {
        Write-Host "[OK] Gate C publish output looks complete" -ForegroundColor Green
    }
    else {
        foreach ($p in $missing) {
            $warnings += "Missing publish output file: $p"
        }
    }
}

# Check core build output
Write-Host "Checking core build output..." -ForegroundColor Yellow
$corePath = Join-Path $RootDir "src\VoiceStudio.Core\bin\Release\net8.0"
if (-not (Test-Path $corePath)) {
    $warnings += "Core build output not found: $corePath (may need to build first)"
}
else {
    Write-Host "[OK] Core build output exists" -ForegroundColor Green
}

# Check backend files
Write-Host "Checking backend files..." -ForegroundColor Yellow
$backendMain = Join-Path $RootDir "backend\api\main.py"
if (-not (Test-Path $backendMain)) {
    $errors += "Backend main.py not found: $backendMain"
}
else {
    Write-Host "[OK] Backend main.py exists" -ForegroundColor Green
}

$backendRoutes = Join-Path $RootDir "backend\api\routes"
if (-not (Test-Path $backendRoutes)) {
    $warnings += "Backend routes directory not found: $backendRoutes"
}
else {
    $routeFiles = Get-ChildItem -Path $backendRoutes -Filter "*.py" -Recurse
    if ($routeFiles.Count -eq 0) {
        $warnings += "No route files found in backend\api\routes"
    }
    else {
        Write-Host "[OK] Backend routes exist ($($routeFiles.Count) files)" -ForegroundColor Green
    }
}

$backendRequirements = Join-Path $RootDir "backend\requirements.txt"
if (-not (Test-Path $backendRequirements)) {
    $warnings += "Backend requirements.txt not found: $backendRequirements"
}
else {
    Write-Host "[OK] Backend requirements.txt exists" -ForegroundColor Green
}

# Check core engine files
Write-Host "Checking core engine files..." -ForegroundColor Yellow
$enginePath = Join-Path $RootDir "app\core\engines"
if (-not (Test-Path $enginePath)) {
    $warnings += "Core engines directory not found: $enginePath"
}
else {
    $engineFiles = Get-ChildItem -Path $enginePath -Filter "*.py" -Recurse
    if ($engineFiles.Count -eq 0) {
        $warnings += "No engine files found in app\core\engines"
    }
    else {
        Write-Host "[OK] Core engine files exist ($($engineFiles.Count) files)" -ForegroundColor Green
    }
}

$audioPath = Join-Path $RootDir "app\core\audio"
if (-not (Test-Path $audioPath)) {
    $warnings += "Core audio directory not found: $audioPath"
}
else {
    Write-Host "[OK] Core audio files exist" -ForegroundColor Green
}

$runtimePath = Join-Path $RootDir "app\core\runtime"
if (-not (Test-Path $runtimePath)) {
    $warnings += "Core runtime directory not found: $runtimePath"
}
else {
    Write-Host "[OK] Core runtime files exist" -ForegroundColor Green
}

$trainingPath = Join-Path $RootDir "app\core\training"
if (-not (Test-Path $trainingPath)) {
    $warnings += "Core training directory not found: $trainingPath"
}
else {
    Write-Host "[OK] Core training files exist" -ForegroundColor Green
}

# Check engine manifests
Write-Host "Checking engine manifests..." -ForegroundColor Yellow
$enginesPath = Join-Path $RootDir "engines"
if (-not (Test-Path $enginesPath)) {
    $warnings += "Engines directory not found: $enginesPath"
}
else {
    $manifests = Get-ChildItem -Path $enginesPath -Filter "engine.manifest.json" -Recurse
    if ($manifests.Count -eq 0) {
        $warnings += "No engine manifests found in engines directory"
    }
    else {
        Write-Host "[OK] Engine manifests exist ($($manifests.Count) manifests)" -ForegroundColor Green
    }
}

# Check documentation
Write-Host "Checking documentation..." -ForegroundColor Yellow
$docsUser = Join-Path $RootDir "docs\user"
if (-not (Test-Path $docsUser)) {
    $warnings += "User documentation directory not found: $docsUser"
}
else {
    $userDocs = Get-ChildItem -Path $docsUser -Filter "*.md"
    if ($userDocs.Count -eq 0) {
        $warnings += "No user documentation files found"
    }
    else {
        Write-Host "[OK] User documentation exists ($($userDocs.Count) files)" -ForegroundColor Green
    }
}

$docsApi = Join-Path $RootDir "docs\api"
if (-not (Test-Path $docsApi)) {
    $warnings += "API documentation directory not found: $docsApi"
}
else {
    Write-Host "[OK] API documentation exists" -ForegroundColor Green
}

$docsDeveloper = Join-Path $RootDir "docs\developer"
if (-not (Test-Path $docsDeveloper)) {
    $warnings += "Developer documentation directory not found: $docsDeveloper"
}
else {
    Write-Host "[OK] Developer documentation exists" -ForegroundColor Green
}

# Check license file
Write-Host "Checking license file..." -ForegroundColor Yellow
$licenseFile = Join-Path $RootDir "LICENSE"
if (-not (Test-Path $licenseFile)) {
    $warnings += "LICENSE file not found: $licenseFile"
}
else {
    Write-Host "[OK] LICENSE file exists" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "[OK] All checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installer is ready to build." -ForegroundColor Cyan
    Write-Host "Run: .\build-installer.ps1 -InstallerType $InstallerType -Version $Version" -ForegroundColor White
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
    
    if ($errors.Count -gt 0) {
        Write-Host ""
        Write-Host "Build verification failed. Fix errors before building installer." -ForegroundColor Red
        exit 1
    }
    else {
        Write-Host ""
        Write-Host "Build verification passed with warnings. Review warnings before building." -ForegroundColor Yellow
        exit 0
    }
}
