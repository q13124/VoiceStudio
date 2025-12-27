# VoiceStudio Quantum+ Release Packaging Script
# Creates MSIX package and installer for distribution
# Last Updated: 2025-01-28

param(
    [Parameter(Mandatory = $false)]
    [string]$Configuration = "Release",
    
    [Parameter(Mandatory = $false)]
    [string]$Platform = "x64",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipBuild = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipInstaller = $false,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputDir = ".\release"
)

$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$AppProject = Join-Path $RootDir "src\VoiceStudio.App\VoiceStudio.App.csproj"
$InstallerScript = Join-Path $RootDir "installer\build-installer.ps1"
$OutputPath = Join-Path $RootDir $OutputDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoiceStudio Quantum+ Release Packaging" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    Write-Host "Created output directory: $OutputPath" -ForegroundColor Green
}

# Step 1: Build the application
if (-not $SkipBuild) {
    Write-Host "Step 1: Building application..." -ForegroundColor Yellow
    Write-Host "  Configuration: $Configuration" -ForegroundColor Gray
    Write-Host "  Platform: $Platform" -ForegroundColor Gray
    
    Push-Location $RootDir
    
    try {
        $buildArgs = @(
            "build",
            $AppProject,
            "--configuration", $Configuration,
            "--no-incremental"
        )
        
        $buildOutput = dotnet @buildArgs 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Build failed!" -ForegroundColor Red
            Write-Host $buildOutput
            exit 1
        }
        
        Write-Host "Build completed successfully" -ForegroundColor Green
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "Step 1: Skipping build (--SkipBuild specified)" -ForegroundColor Yellow
}

# Step 2: Create MSIX package
Write-Host ""
Write-Host "Step 2: Creating MSIX package..." -ForegroundColor Yellow

$MsixOutputPath = Join-Path $OutputPath "msix"
if (-not (Test-Path $MsixOutputPath)) {
    New-Item -ItemType Directory -Path $MsixOutputPath -Force | Out-Null
}

Push-Location (Join-Path $RootDir "src\VoiceStudio.App")

try {
    # Check if MakeAppx.exe is available (Windows SDK)
    $MakeAppxPath = "${env:ProgramFiles(x86)}\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe"
    if (-not (Test-Path $MakeAppxPath)) {
        # Try alternative paths
        $MakeAppxPath = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter "makeappx.exe" -ErrorAction SilentlyContinue | 
        Select-Object -First 1 -ExpandProperty FullName
    }
    
    if ($MakeAppxPath -and (Test-Path $MakeAppxPath)) {
        Write-Host "  Found MakeAppx.exe: $MakeAppxPath" -ForegroundColor Gray
        
        # Build MSIX using dotnet publish
        $publishArgs = @(
            "publish",
            $AppProject,
            "--configuration", $Configuration,
            "--output", $MsixOutputPath,
            "-p:GenerateAppxPackageOnBuild=true",
            "-p:AppxPackageSigningEnabled=false"
        )
        
        $publishOutput = dotnet @publishArgs 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "MSIX package creation failed!" -ForegroundColor Red
            Write-Host $publishOutput
            Write-Host ""
            Write-Host "Note: MSIX packaging requires Windows SDK and may need manual configuration." -ForegroundColor Yellow
        }
        else {
            Write-Host "MSIX package created successfully" -ForegroundColor Green
            $msixFile = Get-ChildItem $MsixOutputPath -Filter "*.msix" -ErrorAction SilentlyContinue
            if ($msixFile) {
                Write-Host "  Package: $($msixFile.FullName)" -ForegroundColor Gray
            }
        }
    }
    else {
        Write-Host "  MakeAppx.exe not found. Skipping MSIX package creation." -ForegroundColor Yellow
        Write-Host "  Install Windows SDK to enable MSIX packaging." -ForegroundColor Yellow
    }
}
finally {
    Pop-Location
}

# Step 3: Build installer
if (-not $SkipInstaller) {
    Write-Host ""
    Write-Host "Step 3: Building installer..." -ForegroundColor Yellow
    
    if (Test-Path $InstallerScript) {
        Push-Location (Split-Path -Parent $InstallerScript)
        
        try {
            & $InstallerScript -OutputDir $OutputPath
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Installer built successfully" -ForegroundColor Green
            }
            else {
                Write-Host "Installer build failed!" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "Error building installer: $_" -ForegroundColor Red
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Host "  Installer script not found: $InstallerScript" -ForegroundColor Yellow
    }
}
else {
    Write-Host ""
    Write-Host "Step 3: Skipping installer (--SkipInstaller specified)" -ForegroundColor Yellow
}

# Step 4: Copy additional files
Write-Host ""
Write-Host "Step 4: Copying release files..." -ForegroundColor Yellow

$ReleaseFiles = @(
    "CHANGELOG.md",
    "LICENSE",
    "README.md"
)

foreach ($file in $ReleaseFiles) {
    $sourcePath = Join-Path $RootDir $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $OutputPath -Force
        Write-Host "  Copied: $file" -ForegroundColor Gray
    }
}

# Step 5: Create release summary
Write-Host ""
Write-Host "Step 5: Creating release summary..." -ForegroundColor Yellow

$SummaryPath = Join-Path $OutputPath "RELEASE_SUMMARY.txt"
$SummaryContent = @"
VoiceStudio Quantum+ Release Package
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Configuration: $Configuration
Platform: $Platform

Output Directory: $OutputPath

Contents:
$(Get-ChildItem $OutputPath -File | ForEach-Object { "  - $($_.Name)" })

MSIX Package: $(if (Test-Path (Join-Path $MsixOutputPath "*.msix")) { "Created" } else { "Not created" })
Installer: $(if (Test-Path (Join-Path $OutputPath "*.exe")) { "Created" } else { "Not created" })

Next Steps:
1. Test the MSIX package (if created)
2. Test the installer
3. Run smoke tests (see docs/release/SMOKE_CHECKLIST.md)
4. Sign the packages (if code signing is configured)
5. Upload to distribution platform
"@

$SummaryContent | Out-File -FilePath $SummaryPath -Encoding UTF8
Write-Host "  Created: RELEASE_SUMMARY.txt" -ForegroundColor Gray

# Final summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Packaging Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output directory: $OutputPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Files created:" -ForegroundColor Yellow
Get-ChildItem $OutputPath -Recurse -File | ForEach-Object {
    Write-Host "  $($_.FullName.Replace($OutputPath, '.'))" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review RELEASE_SUMMARY.txt" -ForegroundColor Gray
Write-Host "  2. Run smoke tests (docs/release/SMOKE_CHECKLIST.md)" -ForegroundColor Gray
Write-Host "  3. Test installation on clean system" -ForegroundColor Gray
Write-Host ""
