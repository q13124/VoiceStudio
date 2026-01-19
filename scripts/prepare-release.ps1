# VoiceStudio Quantum+ Release Preparation Script
# Prepares the project for release: version tagging, changelog, distribution package

param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    
    [string]$ReleaseNotes = "",
    [switch]$SkipBuild,
    [switch]$SkipInstaller,
    [switch]$CreateTag
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoiceStudio Quantum+ Release Preparation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor White
Write-Host ""

# Validate version format
if ($Version -notmatch '^\d+\.\d+\.\d+') {
    Write-Error "Invalid version format. Expected format: MAJOR.MINOR.PATCH (e.g., 1.0.0)"
    exit 1
}

$RootDir = Split-Path -Parent $PSScriptRoot
$ReleaseDir = Join-Path $RootDir "release"
$DistDir = Join-Path $ReleaseDir "dist"

# Create release directories
if (-not (Test-Path $ReleaseDir)) {
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
}
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}

Write-Host "Step 1: Updating version numbers..." -ForegroundColor Yellow
& "$RootDir\scripts\update-version.ps1" -NewVersion $Version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to update version numbers"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Building application..." -ForegroundColor Yellow
if (-not $SkipBuild) {
    Push-Location "$RootDir\src\VoiceStudio.App"
    try {
        dotnet clean --configuration Release
        dotnet build --configuration Release
        if ($LASTEXITCODE -ne 0) {
            throw "Build failed"
        }
        Write-Host "[OK] Build successful" -ForegroundColor Green
    }
    catch {
        Write-Error "Build failed: $_"
        exit 1
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "Skipping build (--SkipBuild specified)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Creating installer..." -ForegroundColor Yellow
if (-not $SkipInstaller) {
    & "$RootDir\installer\build-installer.ps1" -Version $Version
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Installer creation failed"
        exit 1
    }
    Write-Host "[OK] Installer created" -ForegroundColor Green
}
else {
    Write-Host "Skipping installer creation (--SkipInstaller specified)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 4: Creating distribution package..." -ForegroundColor Yellow

# Copy installer
$InstallerSource = Join-Path "$RootDir\installer\Output" "VoiceStudio-Setup-v$Version.exe"
$InstallerDest = Join-Path $DistDir "VoiceStudio-Setup-v$Version.exe"
if (Test-Path $InstallerSource) {
    Copy-Item $InstallerSource $InstallerDest -Force
    Write-Host "[OK] Installer copied to distribution package" -ForegroundColor Green
}

# Copy documentation
$DocsFiles = @(
    "README.md",
    "CHANGELOG.md",
    "RELEASE_NOTES.md",
    "LICENSE"
)

foreach ($docFile in $DocsFiles) {
    $sourcePath = Join-Path $RootDir $docFile
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath (Join-Path $DistDir $docFile) -Force
        Write-Host "[OK] $docFile copied" -ForegroundColor Green
    }
}

# Create release package info
$packageInfo = @{
    version     = $Version
    releaseDate = (Get-Date -Format "yyyy-MM-dd")
    installer   = "VoiceStudio-Setup-v$Version.exe"
    files       = @()
}

Get-ChildItem $DistDir | ForEach-Object {
    $packageInfo.files += @{
        name   = $_.Name
        size   = $_.Length
        sizeMB = [math]::Round($_.Length / 1MB, 2)
    }
}

$packageInfo | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $DistDir "package-info.json")

Write-Host ""
Write-Host "Step 5: Creating Git tag..." -ForegroundColor Yellow
if ($CreateTag) {
    $tagName = "v$Version"
    $tagMessage = "Release $Version"
    if ($ReleaseNotes) {
        $tagMessage += "`n`n$ReleaseNotes"
    }
    
    git tag -a $tagName -m $tagMessage
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Git tag created: $tagName" -ForegroundColor Green
        Write-Host "  Note: Push tag with: git push origin $tagName" -ForegroundColor Yellow
    }
    else {
        Write-Warning "Failed to create Git tag (may already exist)"
    }
}
else {
    Write-Host "Skipping Git tag creation (use --CreateTag to create tag)" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Release Preparation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor White
Write-Host "Distribution Directory: $DistDir" -ForegroundColor White
Write-Host ""
Write-Host "Distribution Package Contents:" -ForegroundColor Cyan
Get-ChildItem $DistDir | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  - $($_.Name) ($sizeMB MB)" -ForegroundColor White
}
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review distribution package contents" -ForegroundColor White
Write-Host "2. Test installer on clean VMs" -ForegroundColor White
Write-Host "3. Code sign installer (if applicable)" -ForegroundColor White
Write-Host "4. Upload to distribution platform" -ForegroundColor White
if ($CreateTag) {
    Write-Host "5. Push Git tag: git push origin v$Version" -ForegroundColor White
}
Write-Host ""

