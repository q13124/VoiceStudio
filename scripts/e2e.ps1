<#
.SYNOPSIS
    E2E UI test runner for VoiceStudio.
.DESCRIPTION
    Runs end-to-end UI tests using FlaUI. Captures screenshots and UI tree dumps on failure.
.PARAMETER Configuration
    Build configuration. Default: Debug
.PARAMETER RealUI
    If specified, enables real UI automation (launches the app). Required for actual E2E testing.
.EXAMPLE
    .\scripts\e2e.ps1
    .\scripts\e2e.ps1 -RealUI
#>
[CmdletBinding()]
param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",
    
    [switch]$RealUI
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$E2EDir = Join-Path $RootDir ".buildlogs\e2e"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TrxFile = Join-Path $E2EDir "e2e_tests_$Timestamp.trx"
$LogFile = Join-Path $E2EDir "e2e_tests_$Timestamp.log"

# Create E2E test directory
if (-not (Test-Path $E2EDir)) {
    New-Item -ItemType Directory -Path $E2EDir -Force | Out-Null
}

# Create screenshots and uitree directories
$ScreenshotDir = Join-Path $E2EDir "screenshots"
$UITreeDir = Join-Path $E2EDir "uitree"
if (-not (Test-Path $ScreenshotDir)) {
    New-Item -ItemType Directory -Path $ScreenshotDir -Force | Out-Null
}
if (-not (Test-Path $UITreeDir)) {
    New-Item -ItemType Directory -Path $UITreeDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

Write-Log "=== VoiceStudio E2E Test Runner ===" "INFO"
Write-Log "Configuration: $Configuration" "INFO"
Write-Log "Real UI Automation: $RealUI" "INFO"
Write-Log "TRX output: $TrxFile" "INFO"

# Set environment variables
if ($RealUI) {
    $env:VOICESTUDIO_USE_REAL_UI_AUTOMATION = "true"
    Write-Log "Real UI automation ENABLED - app will be launched" "WARN"
} else {
    $env:VOICESTUDIO_USE_REAL_UI_AUTOMATION = "false"
    Write-Log "Simulated mode - no app launch required" "INFO"
}
$env:VOICESTUDIO_TEST_ARTIFACTS = $E2EDir
$env:VOICESTUDIO_UITREE_DIR = $UITreeDir

# Run E2E tests
$TestProject = Join-Path $RootDir "src\VoiceStudio.App.Tests\VoiceStudio.App.Tests.csproj"

$testArgs = @(
    "test",
    $TestProject,
    "-c", $Configuration,
    "-p:Platform=x64",
    "--no-build",
    "--filter", "TestCategory=E2E",
    "--logger", "trx;LogFileName=$TrxFile",
    "--logger", "console;verbosity=normal",
    "--results-directory", $E2EDir
)

Write-Log "Running: dotnet $($testArgs -join ' ')" "INFO"
$testOutput = & dotnet $testArgs 2>&1
$testOutput | Out-File -FilePath $LogFile -Append
$testOutput | Write-Host
$TestExitCode = $LASTEXITCODE

# Parse results
$passed = ($testOutput | Select-String -Pattern "Passed:\s*(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value })
$failed = ($testOutput | Select-String -Pattern "Failed:\s*(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value })
$skipped = ($testOutput | Select-String -Pattern "Skipped:\s*(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value })

if ($TestExitCode -eq 0) {
    Write-Log "E2E tests PASSED" "INFO"
    Write-Log "Results: Passed=$passed, Failed=$failed, Skipped=$skipped" "INFO"
} else {
    Write-Log "E2E tests FAILED with exit code $TestExitCode" "ERROR"
    Write-Log "Results: Passed=$passed, Failed=$failed, Skipped=$skipped" "ERROR"
    
    # Check for screenshots
    $screenshots = Get-ChildItem -Path $ScreenshotDir -Filter "*.png" -ErrorAction SilentlyContinue
    if ($screenshots) {
        Write-Log "Screenshots captured: $($screenshots.Count)" "INFO"
        foreach ($screenshot in $screenshots) {
            Write-Log "  - $($screenshot.Name)" "INFO"
        }
    }
    
    # Check for UI tree dumps
    $uitrees = Get-ChildItem -Path $UITreeDir -Filter "*.xml" -ErrorAction SilentlyContinue
    if ($uitrees) {
        Write-Log "UI tree dumps captured: $($uitrees.Count)" "INFO"
        foreach ($uitree in $uitrees) {
            Write-Log "  - $($uitree.Name)" "INFO"
        }
    }
}

Write-Log "TRX file: $TrxFile" "INFO"
Write-Log "Log file: $LogFile" "INFO"
Write-Log "Screenshots: $ScreenshotDir" "INFO"
Write-Log "UI Trees: $UITreeDir" "INFO"
Write-Log "=== E2E Tests Complete ===" "INFO"

# Clean up environment
Remove-Item Env:VOICESTUDIO_USE_REAL_UI_AUTOMATION -ErrorAction SilentlyContinue
Remove-Item Env:VOICESTUDIO_TEST_ARTIFACTS -ErrorAction SilentlyContinue
Remove-Item Env:VOICESTUDIO_UITREE_DIR -ErrorAction SilentlyContinue

exit $TestExitCode
