<#
.SYNOPSIS
    Unit test runner for VoiceStudio.
.DESCRIPTION
    Runs unit tests (excluding UI and E2E tests) with TRX output to .buildlogs/test-results/.
.PARAMETER Configuration
    Build configuration. Default: Debug
.PARAMETER Filter
    Additional test filter expression to combine with the default filter.
.EXAMPLE
    .\scripts\test.ps1
    .\scripts\test.ps1 -Filter "FullyQualifiedName~ViewModel"
#>
[CmdletBinding()]
param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug",
    
    [string]$Filter = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$TestResultsDir = Join-Path $RootDir ".buildlogs\test-results"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TrxFile = Join-Path $TestResultsDir "unit_tests_$Timestamp.trx"
$LogFile = Join-Path $TestResultsDir "unit_tests_$Timestamp.log"

# Create test results directory
if (-not (Test-Path $TestResultsDir)) {
    New-Item -ItemType Directory -Path $TestResultsDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

Write-Log "=== VoiceStudio Unit Test Runner ===" "INFO"
Write-Log "Configuration: $Configuration" "INFO"
Write-Log "TRX output: $TrxFile" "INFO"

# Build filter expression (exclude UI and E2E tests)
$BaseFilter = "TestCategory!=UI&TestCategory!=E2E&TestCategory!=Smoke"
if ($Filter) {
    $FullFilter = "($BaseFilter)&($Filter)"
} else {
    $FullFilter = $BaseFilter
}
Write-Log "Filter: $FullFilter" "INFO"

# Run tests
$TestProject = Join-Path $RootDir "src\VoiceStudio.App.Tests\VoiceStudio.App.Tests.csproj"

$testArgs = @(
    "test",
    $TestProject,
    "-c", $Configuration,
    "-p:Platform=x64",
    "--no-build",
    "--filter", $FullFilter,
    "--logger", "trx;LogFileName=$TrxFile",
    "--logger", "console;verbosity=normal",
    "--results-directory", $TestResultsDir
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
    Write-Log "Unit tests PASSED" "INFO"
    Write-Log "Results: Passed=$passed, Failed=$failed, Skipped=$skipped" "INFO"
} else {
    Write-Log "Unit tests FAILED with exit code $TestExitCode" "ERROR"
    Write-Log "Results: Passed=$passed, Failed=$failed, Skipped=$skipped" "ERROR"
}

Write-Log "TRX file: $TrxFile" "INFO"
Write-Log "Log file: $LogFile" "INFO"
Write-Log "=== Unit Tests Complete ===" "INFO"

exit $TestExitCode
