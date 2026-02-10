<#
.SYNOPSIS
    FlaUI smoke test runner for VoiceStudio.
.DESCRIPTION
    Runs smoke tests using FlaUI UI automation. Captures screenshots on failure.
    Set VOICESTUDIO_USE_REAL_UI_AUTOMATION=true for real UI testing (requires app to launch).
.PARAMETER Configuration
    Build configuration. Default: Debug
.PARAMETER RealUI
    If specified, enables real UI automation (launches the app).
.EXAMPLE
    .\scripts\smoke.ps1
    .\scripts\smoke.ps1 -RealUI
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
$SmokeDir = Join-Path $RootDir ".buildlogs\smoke"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TrxFile = Join-Path $SmokeDir "smoke_tests_$Timestamp.trx"
$LogFile = Join-Path $SmokeDir "smoke_tests_$Timestamp.log"

# Create smoke test directory
if (-not (Test-Path $SmokeDir)) {
    New-Item -ItemType Directory -Path $SmokeDir -Force | Out-Null
}

# Create screenshots directory
$ScreenshotDir = Join-Path $SmokeDir "screenshots"
if (-not (Test-Path $ScreenshotDir)) {
    New-Item -ItemType Directory -Path $ScreenshotDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

Write-Log "=== VoiceStudio Smoke Test Runner ===" "INFO"
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
$env:VOICESTUDIO_TEST_ARTIFACTS = $SmokeDir

# Run smoke tests
$TestProject = Join-Path $RootDir "src\VoiceStudio.App.Tests\VoiceStudio.App.Tests.csproj"

$testArgs = @(
    "test",
    $TestProject,
    "-c", $Configuration,
    "-p:Platform=x64",
    "--no-build",
    "--filter", "TestCategory=Smoke",
    "--logger", "trx;LogFileName=$TrxFile",
    "--logger", "console;verbosity=normal",
    "--results-directory", $SmokeDir
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
    Write-Log "Smoke tests PASSED" "INFO"
    Write-Log "Results: Passed=$passed, Failed=$failed, Skipped=$skipped" "INFO"
} else {
    Write-Log "Smoke tests FAILED with exit code $TestExitCode" "ERROR"
    Write-Log "Results: Passed=$passed, Failed=$failed, Skipped=$skipped" "ERROR"
    
    # Check for screenshots
    $screenshots = Get-ChildItem -Path $ScreenshotDir -Filter "*.png" -ErrorAction SilentlyContinue
    if ($screenshots) {
        Write-Log "Screenshots captured: $($screenshots.Count)" "INFO"
        foreach ($screenshot in $screenshots) {
            Write-Log "  - $($screenshot.Name)" "INFO"
        }
    }
}

Write-Log "TRX file: $TrxFile" "INFO"
Write-Log "Log file: $LogFile" "INFO"
Write-Log "Screenshots: $ScreenshotDir" "INFO"
Write-Log "=== Smoke Tests Complete ===" "INFO"

# Clean up environment
Remove-Item Env:VOICESTUDIO_USE_REAL_UI_AUTOMATION -ErrorAction SilentlyContinue
Remove-Item Env:VOICESTUDIO_TEST_ARTIFACTS -ErrorAction SilentlyContinue

exit $TestExitCode
