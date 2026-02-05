# VoiceStudio - Verify Generated C# Client
# Validates that generated client compiles and matches OpenAPI schema

param(
    [switch]$Quick,          # Skip full build, only compile generated file
    [switch]$Verbose         # Verbose output
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent $scriptDir
$generatedFile = Join-Path $projectRoot "src\VoiceStudio.App\Services\Generated\BackendClient.g.cs"
$openApiPath = Join-Path $projectRoot "docs\api\openapi.json"
$csprojPath = Join-Path $projectRoot "src\VoiceStudio.App\VoiceStudio.App.csproj"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host " VoiceStudio Client Verification" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()

# Check 1: Generated file exists
Write-Host "[1/5] Checking generated file exists..." -ForegroundColor White
if (Test-Path $generatedFile) {
    $size = (Get-Item $generatedFile).Length
    $lines = (Get-Content $generatedFile).Count
    Write-Host "  [OK] Found: $generatedFile" -ForegroundColor Green
    Write-Host "       Size: $([math]::Round($size / 1024, 1)) KB, Lines: $lines" -ForegroundColor Gray
}
else {
    $errors += "Generated file not found: $generatedFile"
    Write-Host "  [FAIL] File not found" -ForegroundColor Red
}

# Check 2: OpenAPI schema exists
Write-Host "[2/5] Checking OpenAPI schema exists..." -ForegroundColor White
if (Test-Path $openApiPath) {
    $schemaContent = Get-Content $openApiPath -Raw | ConvertFrom-Json
    $version = $schemaContent.openapi
    $pathCount = ($schemaContent.paths.PSObject.Properties | Measure-Object).Count
    Write-Host "  [OK] Found: $openApiPath" -ForegroundColor Green
    Write-Host "       OpenAPI Version: $version, Paths: $pathCount" -ForegroundColor Gray
}
else {
    $errors += "OpenAPI schema not found: $openApiPath"
    Write-Host "  [FAIL] Schema not found" -ForegroundColor Red
}

# Check 3: Timestamps are valid (generated after schema)
Write-Host "[3/5] Checking generation timestamps..." -ForegroundColor White
if ((Test-Path $generatedFile) -and (Test-Path $openApiPath)) {
    $schemaTime = (Get-Item $openApiPath).LastWriteTime
    $clientTime = (Get-Item $generatedFile).LastWriteTime
    
    if ($clientTime -gt $schemaTime) {
        Write-Host "  [OK] Client is newer than schema" -ForegroundColor Green
        Write-Host "       Schema: $schemaTime" -ForegroundColor Gray
        Write-Host "       Client: $clientTime" -ForegroundColor Gray
    }
    else {
        $errors += "Client is stale - regeneration needed"
        Write-Host "  [WARN] Client may be stale" -ForegroundColor Yellow
        Write-Host "       Schema: $schemaTime" -ForegroundColor Gray
        Write-Host "       Client: $clientTime" -ForegroundColor Gray
    }
}

# Check 4: Generated file has expected class
Write-Host "[4/5] Checking generated class structure..." -ForegroundColor White
if (Test-Path $generatedFile) {
    $content = Get-Content $generatedFile -Raw
    
    $hasClient = $content -match 'public partial class GeneratedBackendClient'
    $hasInterface = $content -match 'public partial interface IGeneratedBackendClient'
    $hasNamespace = $content -match 'namespace VoiceStudio\.App\.Services\.Generated'
    
    if ($hasClient -and $hasInterface -and $hasNamespace) {
        Write-Host "  [OK] Expected classes and namespace found" -ForegroundColor Green
    }
    else {
        if (-not $hasClient) { $errors += "Missing GeneratedBackendClient class" }
        if (-not $hasInterface) { $errors += "Missing IGeneratedBackendClient interface" }
        if (-not $hasNamespace) { $errors += "Wrong namespace" }
        Write-Host "  [FAIL] Missing expected structure" -ForegroundColor Red
    }
}

# Check 5: Build validation
Write-Host "[5/5] Verifying generated code compiles..." -ForegroundColor White
if ($Quick) {
    Write-Host "  [SKIP] Skipped (--Quick mode)" -ForegroundColor Yellow
}
else {
    try {
        $buildOutput = dotnet build $csprojPath -c Debug -p:Platform=x64 --no-restore 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Build succeeded" -ForegroundColor Green
        }
        else {
            $errors += "Build failed"
            Write-Host "  [FAIL] Build failed" -ForegroundColor Red
            if ($Verbose) {
                Write-Host $buildOutput -ForegroundColor Gray
            }
        }
    }
    catch {
        $errors += "Build exception: $_"
        Write-Host "  [FAIL] Build exception: $_" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host " Verification Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if ($errors.Count -eq 0) {
    Write-Host "[PASS] All checks passed!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "[FAIL] $($errors.Count) error(s) found:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
    exit 1
}
