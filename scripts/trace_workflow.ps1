<#
.SYNOPSIS
    VoiceStudio Workflow Tracer - Launches tests with full tracing enabled.

.DESCRIPTION
    This script starts the VoiceStudio backend, WinAppDriver, and runs pytest
    tests with tracing and screenshot capture enabled. Generates HTML reports
    in .buildlogs/validation/

.PARAMETER Workflow
    Specific workflow to test. Options: all, import, cloning, synthesis, transcribe, realtime
    Default: all

.PARAMETER TraceEnabled
    Enable detailed tracing (default: true)

.PARAMETER ScreenshotsEnabled
    Capture screenshots at each step (default: true)

.PARAMETER BackendPort
    Backend API port (default: 8001)

.PARAMETER SkipBackendStart
    Skip starting the backend (use if already running)

.PARAMETER SkipWinAppDriverStart
    Skip starting WinAppDriver (use if already running)

.EXAMPLE
    .\trace_workflow.ps1 -Workflow import
    Runs only the audio import workflow tests

.EXAMPLE
    .\trace_workflow.ps1 -Workflow all -ScreenshotsEnabled
    Runs all workflow tests with screenshots
#>

param(
    [ValidateSet("all", "import", "cloning", "synthesis", "transcribe", "realtime", "panels")]
    [string]$Workflow = "all",
    
    [switch]$TraceEnabled = $true,
    [switch]$ScreenshotsEnabled = $true,
    [int]$BackendPort = 8001,
    [switch]$SkipBackendStart,
    [switch]$SkipWinAppDriverStart
)

$ErrorActionPreference = "Stop"
$script:startTime = Get-Date

# Colors for output
function Write-Step { param($msg) Write-Host "[STEP] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "[FAIL] $msg" -ForegroundColor Red }

# Ensure we're in the repo root
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
Write-Step "Working directory: $repoRoot"

# Setup output directories
$outputDir = Join-Path $repoRoot ".buildlogs\validation"
$screenshotDir = Join-Path $outputDir "screenshots"
$reportDir = Join-Path $outputDir "reports"
$logDir = Join-Path $outputDir "logs"

foreach ($dir in @($outputDir, $screenshotDir, $reportDir, $logDir)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Success "Output directories ready: $outputDir"

# Workflow to pytest marker mapping
$workflowMarkers = @{
    "all"        = ""
    "import"     = "-m import"
    "cloning"    = "-m cloning"
    "synthesis"  = "-m synthesis"
    "transcribe" = "-m transcribe"
    "realtime"   = "-m realtime"
    "panels"     = "-m panels"
}

# Check Python 3.12
Write-Step "Checking Python 3.12..."
try {
    $pyVersion = py -3.12 --version 2>&1
    Write-Success "Found: $pyVersion"
} catch {
    Write-Fail "Python 3.12 not found. Please install Python 3.12"
    exit 1
}

# Check WinAppDriver
$winAppDriverPath = "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
$winAppDriverRunning = Get-Process -Name WinAppDriver -ErrorAction SilentlyContinue

if (-not $SkipWinAppDriverStart) {
    if (-not $winAppDriverRunning) {
        if (Test-Path $winAppDriverPath) {
            Write-Step "Starting WinAppDriver..."
            Start-Process -FilePath $winAppDriverPath -WindowStyle Minimized
            Start-Sleep -Seconds 2
            Write-Success "WinAppDriver started"
        } else {
            Write-Warn "WinAppDriver not found at $winAppDriverPath"
            Write-Warn "Please install from: https://github.com/Microsoft/WinAppDriver/releases"
        }
    } else {
        Write-Success "WinAppDriver already running"
    }
}

# Start backend if needed
$backendProcess = $null
if (-not $SkipBackendStart) {
    Write-Step "Checking backend on port $BackendPort..."
    $healthCheck = $null
    try {
        $healthCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    } catch {}
    
    if ($healthCheck) {
        Write-Success "Backend already running"
    } else {
        Write-Step "Starting backend..."
        $backendLog = Join-Path $logDir "backend.log"
        $env:PYTHONIOENCODING = "utf-8"
        $backendProcess = Start-Process -FilePath "py" -ArgumentList @(
            "-3.12", "-m", "uvicorn", 
            "backend.api.main:app",
            "--host", "127.0.0.1",
            "--port", $BackendPort,
            "--log-level", "info"
        ) -WorkingDirectory $repoRoot -PassThru -RedirectStandardOutput $backendLog -RedirectStandardError "$backendLog.err" -WindowStyle Hidden
        
        # Wait for backend to be ready
        Write-Step "Waiting for backend to start..."
        $maxWait = 30
        $waited = 0
        while ($waited -lt $maxWait) {
            Start-Sleep -Seconds 1
            $waited++
            try {
                $healthCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($healthCheck) {
                    Write-Success "Backend started (took ${waited}s)"
                    break
                }
            } catch {}
        }
        
        if ($waited -ge $maxWait) {
            Write-Fail "Backend failed to start within ${maxWait}s"
            if ($backendProcess) { Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue }
            exit 1
        }
    }
}

# Build environment variables for pytest
$env:VOICESTUDIO_TRACE_ENABLED = if ($TraceEnabled) { "1" } else { "0" }
$env:VOICESTUDIO_SCREENSHOTS_ENABLED = if ($ScreenshotsEnabled) { "1" } else { "0" }
$env:VOICESTUDIO_OUTPUT_DIR = $outputDir
$env:VOICESTUDIO_BACKEND_URL = "http://127.0.0.1:$BackendPort"

# Run pytest
Write-Step "Running pytest for workflow: $Workflow"
$pytestArgs = @(
    "-3.12", "-m", "pytest",
    "tests/ui",
    "-v",
    "--tb=short",
    "--capture=no"
)

# Add markers if not running all
if ($workflowMarkers[$Workflow]) {
    $pytestArgs += $workflowMarkers[$Workflow]
}

# Add junit output for CI
$junitPath = Join-Path $reportDir "junit_results.xml"
$pytestArgs += "--junit-xml=$junitPath"

Write-Step "Pytest command: py $($pytestArgs -join ' ')"

$testStartTime = Get-Date
$testResult = & py @pytestArgs 2>&1 | Tee-Object -Variable pytestOutput
$testExitCode = $LASTEXITCODE
$testDuration = (Get-Date) - $testStartTime

# Save pytest output
$pytestOutput | Out-File -FilePath (Join-Path $logDir "pytest_output.log") -Encoding utf8

# Cleanup backend if we started it
if ($backendProcess) {
    Write-Step "Stopping backend..."
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
}

# Summary
$totalDuration = (Get-Date) - $script:startTime
Write-Host "`n" + ("=" * 60) -ForegroundColor White
Write-Host "WORKFLOW TRACE SUMMARY" -ForegroundColor White
Write-Host ("=" * 60) -ForegroundColor White

Write-Host "Workflow:        $Workflow"
Write-Host "Test Duration:   $([math]::Round($testDuration.TotalSeconds, 1))s"
Write-Host "Total Duration:  $([math]::Round($totalDuration.TotalSeconds, 1))s"
Write-Host "Output Dir:      $outputDir"
Write-Host "JUnit Report:    $junitPath"

if ($testExitCode -eq 0) {
    Write-Success "`nAll tests PASSED"
} else {
    Write-Fail "`nTests FAILED (exit code: $testExitCode)"
}

Write-Host "`nGenerated Reports:" -ForegroundColor Cyan
Get-ChildItem -Path $reportDir -Recurse -File | ForEach-Object {
    Write-Host "  - $($_.FullName.Replace($repoRoot, '.'))"
}

if ($ScreenshotsEnabled -and (Test-Path $screenshotDir)) {
    $screenshots = Get-ChildItem -Path $screenshotDir -Filter "*.png"
    if ($screenshots.Count -gt 0) {
        Write-Host "`nScreenshots captured: $($screenshots.Count)" -ForegroundColor Cyan
    }
}

exit $testExitCode
