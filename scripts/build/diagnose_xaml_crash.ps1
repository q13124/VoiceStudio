# XAML Compiler Crash Diagnostic Script

param(
  [int]$MaxIterations = 20,
  [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"
$projectPath = "E:\VoiceStudio\src\VoiceStudio.App\VoiceStudio.App.csproj"
$xamlDir = "E:\VoiceStudio\src\VoiceStudio.App"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "XAML Compiler Crash Diagnostic Tool" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Get all XAML files
$xamlFiles = @()
$xamlFiles += Get-ChildItem -Path "$xamlDir\Controls" -Filter "*.xaml" -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
$xamlFiles += Get-ChildItem -Path "$xamlDir\Views" -Filter "*.xaml" -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
$xamlFiles += Get-ChildItem -Path "$xamlDir\Resources" -Filter "*.xaml" -Recurse -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
$xamlFiles += Get-ChildItem -Path "$xamlDir\App.xaml" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }
$xamlFiles += Get-ChildItem -Path "$xamlDir\MainWindow.xaml" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName }

$xamlFiles = $xamlFiles | Where-Object { $_ } | Sort-Object -Unique

Write-Host "Found $($xamlFiles.Count) XAML files" -ForegroundColor Green
Write-Host ""

# Backup and restore functions
function Backup-ProjectFile {
  $backupPath = "$projectPath.backup"
  if (-not (Test-Path $backupPath)) {
    Copy-Item $projectPath $backupPath
    Write-Host "Backup created" -ForegroundColor Gray
  }
}

function Restore-ProjectFile {
  $backupPath = "$projectPath.backup"
  if (Test-Path $backupPath) {
    Copy-Item $backupPath $projectPath -Force
  }
}

function Test-Build {
  param([string]$TestName)
  Write-Host "Testing: $TestName" -ForegroundColor Yellow
    
  Push-Location E:\VoiceStudio
  $cleanResult = & dotnet clean src\VoiceStudio.App 2>&1 | Out-Null
  $buildOutput = & dotnet build VoiceStudio.sln --configuration Debug 2>&1
  $buildSuccess = $LASTEXITCODE -eq 0
  Pop-Location
    
  if ($buildSuccess) {
    Write-Host "BUILD SUCCEEDED" -ForegroundColor Green
    return $true
  }
  else {
    Write-Host "BUILD FAILED" -ForegroundColor Red
    return $false
  }
}

# STEP 1: Test with all XAML disabled
Write-Host "STEP 1: Testing with all XAML disabled..." -ForegroundColor Cyan
Backup-ProjectFile

$projectContent = Get-Content $projectPath -Raw
$projectNoXaml = $projectContent -replace '(?s)<Page Update=.*?</Page>', ''

Set-Content $projectPath $projectNoXaml -Encoding UTF8

$noXamlSuccess = Test-Build "No XAML files"

if ($noXamlSuccess) {
  Write-Host ""
  Write-Host "SUCCESS: Build works without XAML" -ForegroundColor Green
  Write-Host "Testing each XAML file individually..." -ForegroundColor Cyan
  Write-Host ""
    
  $failingFiles = @()
    
  foreach ($xamlFile in $xamlFiles) {
    $relPath = $xamlFile -replace [regex]::Escape("$xamlDir\"), ""
        
    # Load original
    $origContent = Get-Content "$projectPath.backup" -Raw
        
    # Disable all except this one
    $testContent = $origContent
        
    Set-Content $projectPath $testContent -Encoding UTF8
        
    $result = Test-Build $relPath
        
    if (-not $result) {
      $failingFiles += $relPath
      Write-Host "FOUND PROBLEMATIC FILE!" -ForegroundColor Red
    }
    Write-Host ""
  }
    
  Write-Host "======================================" -ForegroundColor Cyan
  Write-Host "RESULTS" -ForegroundColor Cyan
  Write-Host "======================================" -ForegroundColor Cyan
  Write-Host ""
    
  if ($failingFiles.Count -gt 0) {
    Write-Host "Problematic files found:" -ForegroundColor Yellow
    foreach ($f in $failingFiles) {
      Write-Host "  $f" -ForegroundColor Red
    }
  }
  else {
    Write-Host "Individual files compile OK - problem may be combination" -ForegroundColor Yellow
  }
}
else {
  Write-Host ""
  Write-Host "ISSUE NOT IN XAML - Check C# code and project config" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Restoring project file..." -ForegroundColor Gray
Restore-ProjectFile
Write-Host "Done" -ForegroundColor Green
