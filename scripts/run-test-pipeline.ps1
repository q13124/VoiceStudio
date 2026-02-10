<#
.SYNOPSIS
    Master test pipeline orchestrator for VoiceStudio.
.DESCRIPTION
    Runs the complete test pipeline: build -> unit tests -> smoke tests -> e2e tests.
    Stops on first failure (fail-fast). Generates a summary report.
.PARAMETER Configuration
    Build configuration. Default: Debug
.PARAMETER Clean
    If specified, performs a clean build.
.PARAMETER RealUI
    If specified, enables real UI automation for smoke and E2E tests.
.PARAMETER SkipBuild
    If specified, skips the build step (assumes already built).
.PARAMETER SkipUnit
    If specified, skips unit tests.
.PARAMETER SkipSmoke
    If specified, skips smoke tests.
.PARAMETER SkipE2E
    If specified, skips E2E tests.
.EXAMPLE
    .\scripts\run-test-pipeline.ps1
    .\scripts\run-test-pipeline.ps1 -Clean -RealUI
    .\scripts\run-test-pipeline.ps1 -SkipBuild -SkipE2E
#>
[CmdletBinding()]
param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",
    
    [switch]$Clean,
    [switch]$RealUI,
    [switch]$SkipBuild,
    [switch]$SkipUnit,
    [switch]$SkipSmoke,
    [switch]$SkipE2E
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$PipelineDir = Join-Path $RootDir ".buildlogs\pipeline"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$SummaryFile = Join-Path $PipelineDir "pipeline_summary_$Timestamp.md"
$LogFile = Join-Path $PipelineDir "pipeline_$Timestamp.log"

# Create pipeline directory
if (-not (Test-Path $PipelineDir)) {
    New-Item -ItemType Directory -Path $PipelineDir -Force | Out-Null
}

$StepResults = @()
$OverallStartTime = Get-Date

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Add-StepResult {
    param(
        [string]$Step,
        [string]$Status,
        [int]$ExitCode,
        [TimeSpan]$Duration
    )
    $script:StepResults += [PSCustomObject]@{
        Step = $Step
        Status = $Status
        ExitCode = $ExitCode
        Duration = $Duration.ToString("mm\:ss")
    }
}

function Write-Summary {
    $OverallDuration = (Get-Date) - $OverallStartTime
    $OverallStatus = if ($StepResults | Where-Object { $_.Status -eq "FAILED" }) { "FAILED" } else { "PASSED" }
    
    $summary = @"
# VoiceStudio Test Pipeline Summary

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Configuration:** $Configuration
**Real UI:** $RealUI
**Overall Status:** $OverallStatus
**Total Duration:** $($OverallDuration.ToString("hh\:mm\:ss"))

## Step Results

| Step | Status | Exit Code | Duration |
|------|--------|-----------|----------|
"@
    
    foreach ($result in $StepResults) {
        $statusIcon = if ($result.Status -eq "PASSED") { "✅" } elseif ($result.Status -eq "FAILED") { "❌" } else { "⏭️" }
        $summary += "`n| $($result.Step) | $statusIcon $($result.Status) | $($result.ExitCode) | $($result.Duration) |"
    }
    
    $summary += @"

## Artifacts

- **Pipeline Log:** ``$LogFile``
- **Build Logs:** ``.buildlogs/build/``
- **Test Results:** ``.buildlogs/test-results/``
- **Smoke Tests:** ``.buildlogs/smoke/``
- **E2E Tests:** ``.buildlogs/e2e/``

## How to Run Individual Steps

``````powershell
# Build only
.\scripts\build.ps1 -Configuration $Configuration

# Unit tests only
.\scripts\test.ps1 -Configuration $Configuration

# Smoke tests only
.\scripts\smoke.ps1 -Configuration $Configuration $(if ($RealUI) { '-RealUI' })

# E2E tests only
.\scripts\e2e.ps1 -Configuration $Configuration $(if ($RealUI) { '-RealUI' })
``````
"@
    
    $summary | Out-File -FilePath $SummaryFile -Encoding utf8
    Write-Log "Summary written to: $SummaryFile" "INFO"
}

# ============================================================================
# PIPELINE EXECUTION
# ============================================================================

Write-Log "============================================================" "INFO"
Write-Log "VoiceStudio Test Pipeline" "INFO"
Write-Log "============================================================" "INFO"
Write-Log "Configuration: $Configuration" "INFO"
Write-Log "Clean: $Clean" "INFO"
Write-Log "Real UI: $RealUI" "INFO"
Write-Log "Skip Build: $SkipBuild" "INFO"
Write-Log "Skip Unit: $SkipUnit" "INFO"
Write-Log "Skip Smoke: $SkipSmoke" "INFO"
Write-Log "Skip E2E: $SkipE2E" "INFO"
Write-Log "============================================================" "INFO"

$PipelineFailed = $false

# Step 1: Build
if (-not $SkipBuild) {
    Write-Log "" "INFO"
    Write-Log ">>> STEP 1: BUILD <<<" "INFO"
    Write-Log "" "INFO"
    
    $stepStart = Get-Date
    $buildArgs = @("-Configuration", $Configuration)
    if ($Clean) { $buildArgs += "-Clean" }
    
    & "$ScriptDir\build.ps1" @buildArgs
    $buildExitCode = $LASTEXITCODE
    $stepDuration = (Get-Date) - $stepStart
    
    if ($buildExitCode -eq 0) {
        Add-StepResult -Step "Build" -Status "PASSED" -ExitCode $buildExitCode -Duration $stepDuration
        Write-Log "Build step PASSED" "INFO"
    } else {
        Add-StepResult -Step "Build" -Status "FAILED" -ExitCode $buildExitCode -Duration $stepDuration
        Write-Log "Build step FAILED - stopping pipeline" "ERROR"
        $PipelineFailed = $true
    }
} else {
    Add-StepResult -Step "Build" -Status "SKIPPED" -ExitCode 0 -Duration ([TimeSpan]::Zero)
    Write-Log "Build step SKIPPED" "INFO"
}

# Step 2: Unit Tests
if (-not $PipelineFailed -and -not $SkipUnit) {
    Write-Log "" "INFO"
    Write-Log ">>> STEP 2: UNIT TESTS <<<" "INFO"
    Write-Log "" "INFO"
    
    $stepStart = Get-Date
    & "$ScriptDir\test.ps1" -Configuration $Configuration
    $testExitCode = $LASTEXITCODE
    $stepDuration = (Get-Date) - $stepStart
    
    if ($testExitCode -eq 0) {
        Add-StepResult -Step "Unit Tests" -Status "PASSED" -ExitCode $testExitCode -Duration $stepDuration
        Write-Log "Unit tests step PASSED" "INFO"
    } else {
        Add-StepResult -Step "Unit Tests" -Status "FAILED" -ExitCode $testExitCode -Duration $stepDuration
        Write-Log "Unit tests step FAILED - stopping pipeline" "ERROR"
        $PipelineFailed = $true
    }
} elseif ($SkipUnit) {
    Add-StepResult -Step "Unit Tests" -Status "SKIPPED" -ExitCode 0 -Duration ([TimeSpan]::Zero)
    Write-Log "Unit tests step SKIPPED" "INFO"
}

# Step 3: Smoke Tests
if (-not $PipelineFailed -and -not $SkipSmoke) {
    Write-Log "" "INFO"
    Write-Log ">>> STEP 3: SMOKE TESTS <<<" "INFO"
    Write-Log "" "INFO"
    
    $stepStart = Get-Date
    $smokeArgs = @("-Configuration", $Configuration)
    if ($RealUI) { $smokeArgs += "-RealUI" }
    
    & "$ScriptDir\smoke.ps1" @smokeArgs
    $smokeExitCode = $LASTEXITCODE
    $stepDuration = (Get-Date) - $stepStart
    
    if ($smokeExitCode -eq 0) {
        Add-StepResult -Step "Smoke Tests" -Status "PASSED" -ExitCode $smokeExitCode -Duration $stepDuration
        Write-Log "Smoke tests step PASSED" "INFO"
    } else {
        Add-StepResult -Step "Smoke Tests" -Status "FAILED" -ExitCode $smokeExitCode -Duration $stepDuration
        Write-Log "Smoke tests step FAILED - stopping pipeline" "ERROR"
        $PipelineFailed = $true
    }
} elseif ($SkipSmoke) {
    Add-StepResult -Step "Smoke Tests" -Status "SKIPPED" -ExitCode 0 -Duration ([TimeSpan]::Zero)
    Write-Log "Smoke tests step SKIPPED" "INFO"
}

# Step 4: E2E Tests
if (-not $PipelineFailed -and -not $SkipE2E) {
    Write-Log "" "INFO"
    Write-Log ">>> STEP 4: E2E TESTS <<<" "INFO"
    Write-Log "" "INFO"
    
    $stepStart = Get-Date
    $e2eArgs = @("-Configuration", $Configuration)
    if ($RealUI) { $e2eArgs += "-RealUI" }
    
    & "$ScriptDir\e2e.ps1" @e2eArgs
    $e2eExitCode = $LASTEXITCODE
    $stepDuration = (Get-Date) - $stepStart
    
    if ($e2eExitCode -eq 0) {
        Add-StepResult -Step "E2E Tests" -Status "PASSED" -ExitCode $e2eExitCode -Duration $stepDuration
        Write-Log "E2E tests step PASSED" "INFO"
    } else {
        Add-StepResult -Step "E2E Tests" -Status "FAILED" -ExitCode $e2eExitCode -Duration $stepDuration
        Write-Log "E2E tests step FAILED" "ERROR"
        $PipelineFailed = $true
    }
} elseif ($SkipE2E) {
    Add-StepResult -Step "E2E Tests" -Status "SKIPPED" -ExitCode 0 -Duration ([TimeSpan]::Zero)
    Write-Log "E2E tests step SKIPPED" "INFO"
}

# Write summary
Write-Log "" "INFO"
Write-Log "============================================================" "INFO"
Write-Summary

if ($PipelineFailed) {
    Write-Log "PIPELINE FAILED" "ERROR"
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "PIPELINE FAILED" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "See summary: $SummaryFile" -ForegroundColor Yellow
    exit 1
} else {
    Write-Log "PIPELINE PASSED" "INFO"
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "PIPELINE PASSED" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "See summary: $SummaryFile" -ForegroundColor Cyan
    exit 0
}
