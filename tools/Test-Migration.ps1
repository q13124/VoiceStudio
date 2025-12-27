# Test Migration Script
# Verifies prerequisites before running full migration

param(
  [string]$Src = "C:\VoiceStudio",
  [string]$Dst = "E:\VoiceStudio"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Prerequisites Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check source
Write-Host "[1] Checking source..." -ForegroundColor Yellow
if (Test-Path $Src) {
    Write-Host "  ✓ Source exists: $Src" -ForegroundColor Green
    $srcSize = (Get-ChildItem -Path $Src -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    Write-Host "  ✓ Source size: $([math]::Round($srcSize, 2)) GB" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Source not found: $Src" -ForegroundColor Red
    exit 1
}

# Check destination
Write-Host ""
Write-Host "[2] Checking destination..." -ForegroundColor Yellow
if (Test-Path $Dst) {
    Write-Host "  ✓ Destination exists: $Dst" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Destination will be created: $Dst" -ForegroundColor Yellow
}

# Check disk space
Write-Host ""
Write-Host "[3] Checking disk space..." -ForegroundColor Yellow
$drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($Dst).TrimEnd('\').TrimEnd(':'))
$freeGB = [math]::Round($drive.Free / 1GB, 2)
Write-Host "  ✓ Drive $($drive.Name): $freeGB GB free" -ForegroundColor Gray
if ($freeGB -lt 20) {
    Write-Host "  ⚠ Warning: Less than 20 GB free (recommended: 20-80 GB)" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Sufficient disk space" -ForegroundColor Green
}

# Check Python
Write-Host ""
Write-Host "[4] Checking Python..." -ForegroundColor Yellow
$py = Get-Command py -ErrorAction SilentlyContinue
if (!$py) { $py = Get-Command python -ErrorAction SilentlyContinue }
if ($py) {
    $version = & $py.Source --version 2>&1
    Write-Host "  ✓ Python found: $version" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found. Install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check Robocopy
Write-Host ""
Write-Host "[5] Checking Robocopy..." -ForegroundColor Yellow
if (Get-Command robocopy -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ Robocopy available" -ForegroundColor Green
} else {
    Write-Host "  ✗ Robocopy not found" -ForegroundColor Red
    exit 1
}

# Check migration script
Write-Host ""
Write-Host "[6] Checking migration script..." -ForegroundColor Yellow
$scriptPath = Join-Path $PSScriptRoot "VS_MigrateToE.ps1"
if (Test-Path $scriptPath) {
    Write-Host "  ✓ Migration script found: $scriptPath" -ForegroundColor Green
} else {
    Write-Host "  ✗ Migration script not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All prerequisites met!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to run migration:" -ForegroundColor Yellow
Write-Host "  .\tools\VS_MigrateToE.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or test with dry-run:" -ForegroundColor Yellow
Write-Host "  .\tools\VS_MigrateToE.ps1 -ListOnly" -ForegroundColor White
Write-Host ""

