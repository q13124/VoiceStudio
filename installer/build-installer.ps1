# VoiceStudio Quantum+ Installer Build Script
# Builds the application and creates installer package

param(
    [string]$InstallerType = "InnoSetup",
    [string]$Configuration = "Release",
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoiceStudio Quantum+ Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$RootDir = Split-Path -Parent $PSScriptRoot
$InstallerDir = Join-Path $RootDir "installer"
$OutputDir = Join-Path $InstallerDir "Output"
$FrontendPath = Join-Path $RootDir "src\VoiceStudio.App"
$BackendPath = Join-Path $RootDir "backend"

# Clean output directory
Write-Host "Cleaning output directory..." -ForegroundColor Yellow
if (Test-Path $OutputDir) {
    Remove-Item -Path $OutputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# Build Frontend
Write-Host "Building frontend application..." -ForegroundColor Yellow
Push-Location $FrontendPath
try {
    dotnet clean --configuration $Configuration
    dotnet build --configuration $Configuration
    if ($LASTEXITCODE -ne 0) {
        throw "Frontend build failed"
    }
    Write-Host "Frontend build successful!" -ForegroundColor Green
}
catch {
    Write-Host "Frontend build failed: $_" -ForegroundColor Red
    exit 1
}
finally {
    Pop-Location
}

# Verify backend files exist
Write-Host "Verifying backend files..." -ForegroundColor Yellow
$BackendMain = Join-Path $BackendPath "api\main.py"
if (-not (Test-Path $BackendMain)) {
    Write-Host "Warning: Backend main.py not found at $BackendMain" -ForegroundColor Yellow
}
else {
    Write-Host "Backend files verified!" -ForegroundColor Green
}

# Verify engine manifests
Write-Host "Verifying engine manifests..." -ForegroundColor Yellow
$EngineManifests = Get-ChildItem -Path (Join-Path $RootDir "engines") -Filter "engine.manifest.json" -Recurse
if ($EngineManifests.Count -eq 0) {
    Write-Host "Warning: No engine manifests found" -ForegroundColor Yellow
}
else {
    Write-Host "Found $($EngineManifests.Count) engine manifest(s)!" -ForegroundColor Green
}

# Build Installer
Write-Host ""
Write-Host "Building installer ($InstallerType)..." -ForegroundColor Yellow

if ($InstallerType -eq "InnoSetup") {
    # Build Inno Setup installer
    $InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if (-not (Test-Path $InnoSetupPath)) {
        Write-Host "Error: Inno Setup not found at $InnoSetupPath" -ForegroundColor Red
        Write-Host "Please install Inno Setup 6.2+ from https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
        exit 1
    }
    
    $InnoScript = Join-Path $InstallerDir "VoiceStudio.iss"
    if (-not (Test-Path $InnoScript)) {
        Write-Host "Error: Inno Setup script not found at $InnoScript" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Compiling Inno Setup installer..." -ForegroundColor Yellow
    & $InnoSetupPath $InnoScript
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Inno Setup compilation failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Inno Setup installer created successfully!" -ForegroundColor Green
    Write-Host "Output: $OutputDir" -ForegroundColor Cyan
}
elseif ($InstallerType -eq "WiX") {
    # Build WiX installer
    $WixCandle = "candle.exe"
    $WixLight = "light.exe"
    
    # Check if WiX is in PATH
    $WixPath = Get-Command $WixCandle -ErrorAction SilentlyContinue
    if (-not $WixPath) {
        Write-Host "Error: WiX Toolset not found in PATH" -ForegroundColor Red
        Write-Host "Please install WiX Toolset v3.11+ from https://wixtoolset.org/releases/" -ForegroundColor Yellow
        exit 1
    }
    
    $WixScript = Join-Path $InstallerDir "VoiceStudio.wxs"
    if (-not (Test-Path $WixScript)) {
        Write-Host "Error: WiX script not found at $WixScript" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Compiling WiX installer..." -ForegroundColor Yellow
    Push-Location $InstallerDir
    try {
        & $WixCandle VoiceStudio.wxs
        if ($LASTEXITCODE -ne 0) {
            throw "WiX candle failed"
        }
        
        & $WixLight VoiceStudio.wixobj -ext WixUIExtension -out "Output\VoiceStudio-Setup-v$Version.msi"
        if ($LASTEXITCODE -ne 0) {
            throw "WiX light failed"
        }
        
        Write-Host "WiX installer created successfully!" -ForegroundColor Green
        Write-Host "Output: $OutputDir" -ForegroundColor Cyan
    }
    catch {
        Write-Host "WiX compilation failed: $_" -ForegroundColor Red
        exit 1
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "Error: Unknown installer type: $InstallerType" -ForegroundColor Red
    Write-Host "Supported types: InnoSetup, WiX" -ForegroundColor Yellow
    exit 1
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installer Type: $InstallerType" -ForegroundColor White
Write-Host "Configuration: $Configuration" -ForegroundColor White
Write-Host "Version: $Version" -ForegroundColor White
Write-Host "Output Directory: $OutputDir" -ForegroundColor White
Write-Host ""

# List output files
if (Test-Path $OutputDir) {
    Write-Host "Output Files:" -ForegroundColor Cyan
    Get-ChildItem -Path $OutputDir | ForEach-Object {
        Write-Host "  - $($_.Name) ($([math]::Round($_.Length / 1MB, 2)) MB)" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Test installer on clean Windows 10 VM" -ForegroundColor White
Write-Host "2. Test installer on clean Windows 11 VM" -ForegroundColor White
Write-Host "3. Test upgrade from previous version" -ForegroundColor White
Write-Host "4. Test uninstallation" -ForegroundColor White
Write-Host "5. Code sign installer (if applicable)" -ForegroundColor White
Write-Host ""

