# VoiceStudio Master Validation Runner
# Orchestrates comprehensive feature validation across all components

param(
    [Parameter(HelpMessage="Run all test categories")]
    [switch]$All,
    
    [Parameter(HelpMessage="Run smoke tests only (fast)")]
    [switch]$Smoke,
    
    [Parameter(HelpMessage="Run specific test category")]
    [ValidateSet("import", "cloning", "synthesis", "transcription", "realtime", "panels", "engines", "advanced")]
    [string]$Category,
    
    [Parameter(HelpMessage="Skip UI tests (API only)")]
    [switch]$ApiOnly,
    
    [Parameter(HelpMessage="Skip backend startup")]
    [switch]$SkipBackend,
    
    [Parameter(HelpMessage="Skip WinAppDriver startup")]
    [switch]$SkipWinAppDriver,
    
    [Parameter(HelpMessage="Enable detailed tracing")]
    [switch]$Trace,
    
    [Parameter(HelpMessage="Enable screenshots on test steps")]
    [switch]$Screenshots,
    
    [Parameter(HelpMessage="Generate HTML report")]
    [switch]$HtmlReport,
    
    [Parameter(HelpMessage="Backend port")]
    [int]$BackendPort = 8000,
    
    [Parameter(HelpMessage="Output directory")]
    [string]$OutputDir = ".buildlogs/validation"
)

$ErrorActionPreference = "Continue"

# Configuration
$ProjectRoot = (Get-Item $PSScriptRoot).Parent.FullName
$TestDir = Join-Path $ProjectRoot "tests\ui"
$OutputPath = Join-Path $ProjectRoot $OutputDir
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Ensure output directory exists
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
New-Item -ItemType Directory -Force -Path "$OutputPath\reports" | Out-Null
New-Item -ItemType Directory -Force -Path "$OutputPath\screenshots" | Out-Null
New-Item -ItemType Directory -Force -Path "$OutputPath\api_coverage" | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VoiceStudio Validation Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project Root: $ProjectRoot"
Write-Host "Output Dir: $OutputPath"
Write-Host "Timestamp: $Timestamp"
Write-Host ""

# Track processes to clean up
$BackendProcess = $null
$WinAppDriverProcess = $null

function Start-Backend {
    Write-Host "Starting FastAPI backend..." -ForegroundColor Yellow
    
    $backendPath = Join-Path $ProjectRoot "backend\api\main.py"
    if (-not (Test-Path $backendPath)) {
        Write-Host "  Backend not found at: $backendPath" -ForegroundColor Red
        return $null
    }
    
    $env:PYTHONIOENCODING = "utf-8"
    $process = Start-Process -FilePath "py" -ArgumentList @(
        "-3.12", "-m", "uvicorn", 
        "backend.api.main:app",
        "--host", "127.0.0.1",
        "--port", $BackendPort,
        "--log-level", "warning"
    ) -WorkingDirectory $ProjectRoot -PassThru -WindowStyle Hidden
    
    Write-Host "  Backend PID: $($process.Id)"
    
    # Wait for backend to be ready
    $maxWait = 30
    $waited = 0
    while ($waited -lt $maxWait) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "  Backend is ready" -ForegroundColor Green
                return $process
            }
        } catch {
            Start-Sleep -Seconds 1
            $waited++
        }
    }
    
    Write-Host "  Backend failed to start within $maxWait seconds" -ForegroundColor Red
    return $process
}

function Start-WinAppDriver {
    Write-Host "Starting WinAppDriver..." -ForegroundColor Yellow
    
    $wadPath = "C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe"
    if (-not (Test-Path $wadPath)) {
        $wadPath = "C:\Program Files\Windows Application Driver\WinAppDriver.exe"
    }
    
    if (-not (Test-Path $wadPath)) {
        Write-Host "  WinAppDriver not found" -ForegroundColor Red
        Write-Host "  Install from: https://github.com/Microsoft/WinAppDriver/releases" -ForegroundColor Yellow
        return $null
    }
    
    # Check if already running
    $existing = Get-Process -Name "WinAppDriver" -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  WinAppDriver already running (PID: $($existing.Id))" -ForegroundColor Green
        return $null
    }
    
    $process = Start-Process -FilePath $wadPath -PassThru -WindowStyle Minimized
    Write-Host "  WinAppDriver PID: $($process.Id)"
    Start-Sleep -Seconds 2
    
    return $process
}

function Stop-Processes {
    param([switch]$Force)
    
    if ($BackendProcess -and -not $BackendProcess.HasExited) {
        Write-Host "Stopping backend..." -ForegroundColor Yellow
        Stop-Process -Id $BackendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    if ($WinAppDriverProcess -and -not $WinAppDriverProcess.HasExited) {
        Write-Host "Stopping WinAppDriver..." -ForegroundColor Yellow
        Stop-Process -Id $WinAppDriverProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

function Run-Tests {
    param(
        [string]$Markers,
        [string]$Name
    )
    
    Write-Host ""
    Write-Host "Running: $Name" -ForegroundColor Cyan
    Write-Host "-" * 40
    
    # Build pytest command
    $pytestArgs = @(
        "-3.12", "-m", "pytest",
        $TestDir,
        "-v",
        "--tb=short"
    )
    
    if ($Markers) {
        $pytestArgs += @("-m", $Markers)
    }
    
    if ($HtmlReport) {
        $reportPath = Join-Path $OutputPath "reports\${Name}_${Timestamp}.html"
        $pytestArgs += @("--html=$reportPath", "--self-contained-html")
    }
    
    # Set environment variables
    $env:VOICESTUDIO_BACKEND_URL = "http://127.0.0.1:$BackendPort"
    $env:VOICESTUDIO_OUTPUT_DIR = $OutputPath
    $env:VOICESTUDIO_TRACE_ENABLED = if ($Trace) { "1" } else { "0" }
    $env:VOICESTUDIO_SCREENSHOTS_ENABLED = if ($Screenshots) { "1" } else { "0" }
    
    # Run pytest
    $result = & py @pytestArgs 2>&1
    $exitCode = $LASTEXITCODE
    
    # Output results
    $result | ForEach-Object { Write-Host $_ }
    
    return $exitCode
}

function Run-ApiTests {
    Write-Host ""
    Write-Host "Running API-only tests..." -ForegroundColor Cyan
    Write-Host "-" * 40
    
    $pytestArgs = @(
        "-3.12", "-m", "pytest",
        $TestDir,
        "-v",
        "--tb=short",
        "-m", "api or smoke"
    )
    
    $env:VOICESTUDIO_BACKEND_URL = "http://127.0.0.1:$BackendPort"
    $env:VOICESTUDIO_OUTPUT_DIR = $OutputPath
    
    $result = & py @pytestArgs 2>&1
    $exitCode = $LASTEXITCODE
    
    $result | ForEach-Object { Write-Host $_ }
    
    return $exitCode
}

function Generate-FinalReport {
    Write-Host ""
    Write-Host "Generating final validation report..." -ForegroundColor Yellow
    
    $reportPath = Join-Path $OutputPath "VALIDATION_REPORT_$Timestamp.txt"
    
    $report = @"
================================================================================
                    VoiceStudio Validation Report
================================================================================
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Project: $ProjectRoot
Output: $OutputPath

CONFIGURATION
-------------
- Backend Port: $BackendPort
- Tracing: $(if ($Trace) { "Enabled" } else { "Disabled" })
- Screenshots: $(if ($Screenshots) { "Enabled" } else { "Disabled" })
- API Only: $(if ($ApiOnly) { "Yes" } else { "No" })

TEST RESULTS
------------
"@
    
    # Collect results from report files
    $reportFiles = Get-ChildItem -Path "$OutputPath\reports" -Filter "*.html" -ErrorAction SilentlyContinue
    if ($reportFiles) {
        $report += "`nHTML Reports Generated:`n"
        foreach ($file in $reportFiles) {
            $report += "  - $($file.Name)`n"
        }
    }
    
    # Check for matrix reports
    $matrixFiles = @(
        "panel_matrix_report.txt",
        "engine_matrix_report.txt",
        "advanced_features_report.txt"
    )
    
    foreach ($matrixFile in $matrixFiles) {
        $matrixPath = Join-Path $OutputPath $matrixFile
        if (Test-Path $matrixPath) {
            $report += "`n--- $matrixFile ---`n"
            $report += Get-Content $matrixPath -Raw
            $report += "`n"
        }
    }
    
    # Check for API coverage
    $apiLogFiles = Get-ChildItem -Path "$OutputPath\api_coverage" -Filter "*.json" -ErrorAction SilentlyContinue
    if ($apiLogFiles) {
        $report += "`nAPI COVERAGE`n"
        $report += "-" * 40 + "`n"
        foreach ($file in $apiLogFiles) {
            $report += "  - $($file.Name)`n"
        }
    }
    
    $report += @"

================================================================================
                              END OF REPORT
================================================================================
"@
    
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "Final report: $reportPath" -ForegroundColor Green
    
    return $reportPath
}

# Main execution
try {
    # Start services if needed
    if (-not $SkipBackend) {
        $BackendProcess = Start-Backend
    }
    
    if (-not $ApiOnly -and -not $SkipWinAppDriver) {
        $WinAppDriverProcess = Start-WinAppDriver
    }
    
    # Determine what tests to run
    $testResults = @{}
    
    if ($ApiOnly) {
        $testResults["API"] = Run-ApiTests
    }
    elseif ($Smoke) {
        $testResults["Smoke"] = Run-Tests -Markers "smoke" -Name "Smoke Tests"
    }
    elseif ($Category) {
        $categoryMarkers = @{
            "import" = "import"
            "cloning" = "cloning or wizard"
            "synthesis" = "synthesis or voice"
            "transcription" = "transcription or stt"
            "realtime" = "realtime"
            "panels" = "panels or ui"
            "engines" = "engines"
            "advanced" = "advanced or features"
        }
        
        $marker = $categoryMarkers[$Category]
        $testResults[$Category] = Run-Tests -Markers $marker -Name "$Category Tests"
    }
    elseif ($All) {
        # Run all test categories
        $categories = @(
            @{Name="Smoke"; Markers="smoke"},
            @{Name="Import"; Markers="import"},
            @{Name="Cloning"; Markers="cloning or wizard"},
            @{Name="Synthesis"; Markers="synthesis or voice"},
            @{Name="Transcription"; Markers="transcription or stt"},
            @{Name="Realtime"; Markers="realtime"},
            @{Name="Panels"; Markers="panels"},
            @{Name="Engines"; Markers="engines"},
            @{Name="Advanced"; Markers="advanced"}
        )
        
        foreach ($cat in $categories) {
            $testResults[$cat.Name] = Run-Tests -Markers $cat.Markers -Name "$($cat.Name) Tests"
        }
    }
    else {
        # Default: run smoke tests
        Write-Host "No category specified. Running smoke tests." -ForegroundColor Yellow
        Write-Host "Use -All for comprehensive validation, or -Category for specific tests."
        $testResults["Smoke"] = Run-Tests -Markers "smoke" -Name "Smoke Tests"
    }
    
    # Generate final report
    $reportPath = Generate-FinalReport
    
    # Summary
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Validation Complete" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $allPassed = $true
    foreach ($test in $testResults.GetEnumerator()) {
        $status = if ($test.Value -eq 0) { "PASS" } else { "FAIL" }
        $color = if ($test.Value -eq 0) { "Green" } else { "Red" }
        Write-Host "  $($test.Key): $status" -ForegroundColor $color
        if ($test.Value -ne 0) { $allPassed = $false }
    }
    
    Write-Host ""
    Write-Host "Output: $OutputPath" -ForegroundColor Gray
    Write-Host "Report: $reportPath" -ForegroundColor Gray
    Write-Host ""
    
    if ($allPassed) {
        Write-Host "All tests passed!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Some tests failed. Check the report for details." -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
finally {
    Stop-Processes
}
