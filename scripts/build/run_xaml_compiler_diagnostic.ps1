# XAML Compiler Diagnostic Script
# Runs XamlCompiler.exe directly with maximum diagnostics and captures all output

param(
  [string]$OutputDir = "e:\VoiceStudio\.buildlogs\xaml-diag",
  [switch]$CleanFirst = $false
)

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
  New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $OutputDir "xaml_compiler_run_$timestamp.log"
$errorFile = Join-Path $OutputDir "xaml_compiler_errors_$timestamp.log"
$diagnosticFile = Join-Path $OutputDir "xaml_diagnostic_$timestamp.txt"

Write-Host "=== XAML Compiler Diagnostic Run ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Cyan
Write-Host "Log File: $logFile" -ForegroundColor Cyan
Write-Host "Diagnostic File: $diagnosticFile" -ForegroundColor Cyan
Write-Host ""

# Function to write to both console and log files
function Write-Log {
  param(
    [string]$Message,
    [ConsoleColor]$Color = "White"
  )
  Write-Host $Message -ForegroundColor $Color
  Add-Content -Path $diagnosticFile -Value $Message
}

# === PHASE 1: Environment Diagnostics ===
Write-Log "=== PHASE 1: ENVIRONMENT DIAGNOSTICS ===" "Yellow"

Write-Log "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Log "OS: $(Get-ComputerInfo | Select-Object -ExpandProperty WindowsProductName)"

# Check .NET SDK
$dotnetInfo = & dotnet --version 2>&1
Write-Log ".NET SDK Version: $dotnetInfo"

# Check XamlCompiler.exe location
$xamlCompilerPath = "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\buildTransitive\..\tools\net472\XamlCompiler.exe"
Write-Log ""
Write-Log "XamlCompiler.exe Path: $xamlCompilerPath"
Write-Log "XamlCompiler.exe Exists: $(Test-Path $xamlCompilerPath)"

if (Test-Path $xamlCompilerPath) {
  $xamlCompilerInfo = Get-Item $xamlCompilerPath
  Write-Log "XamlCompiler.exe Size: $($xamlCompilerInfo.Length) bytes"
  Write-Log "XamlCompiler.exe Modified: $($xamlCompilerInfo.LastWriteTime)"
}

# === PHASE 2: File System Diagnostics ===
Write-Log ""
Write-Log "=== PHASE 2: FILE SYSTEM DIAGNOSTICS ===" "Yellow"

$buildDir = "e:\VoiceStudio\.buildlogs\xaml-dump"
Write-Log "Build Output Dir: $buildDir"
Write-Log "Build Output Dir Exists: $(Test-Path $buildDir)"

if (Test-Path $buildDir) {
  $diskSpace = Get-Volume -DriveLetter E
  Write-Log "Disk Space - Total: $([Math]::Round($diskSpace.Size / 1GB, 2)) GB"
  Write-Log "Disk Space - Free: $([Math]::Round($diskSpace.SizeRemaining / 1GB, 2)) GB"
  Write-Log "Disk Space - Used: $([Math]::Round(($diskSpace.Size - $diskSpace.SizeRemaining) / 1GB, 2)) GB"
}

# Check input.json and output.json
$inputJsonPath = "e:\VoiceStudio\.buildlogs\xaml-dump\input.json"
$outputJsonPath = "e:\VoiceStudio\.buildlogs\xaml-dump\output.json"

Write-Log ""
Write-Log "input.json Exists: $(Test-Path $inputJsonPath)"
if (Test-Path $inputJsonPath) {
  $inputSize = (Get-Item $inputJsonPath).Length
  Write-Log "input.json Size: $($inputSize) bytes"
    
  # Validate JSON
  try {
    $inputJson = Get-Content $inputJsonPath | ConvertFrom-Json
    Write-Log "input.json Valid: Yes"
    Write-Log "  - XamlPages Count: $($inputJson.XamlPages.Count)"
    Write-Log "  - ReferenceAssemblies Count: $($inputJson.ReferenceAssemblies.Count)"
    Write-Log "  - OutputPath: $($inputJson.OutputPath)"
  }
  catch {
    Write-Log "input.json Valid: No - $($_.Exception.Message)" "Red"
  }
}

Write-Log ""
Write-Log "output.json Exists: $(Test-Path $outputJsonPath)"
if (Test-Path $outputJsonPath) {
  $outputSize = (Get-Item $outputJsonPath).Length
  Write-Log "output.json Size: $($outputSize) bytes"
    
  # Validate JSON
  try {
    $outputJson = Get-Content $outputJsonPath | ConvertFrom-Json
    Write-Log "output.json Valid: Yes"
    Write-Log "  - GeneratedCodeFiles Count: $($outputJson.GeneratedCodeFiles.Count)"
    Write-Log "  - GeneratedXamlFiles Count: $($outputJson.GeneratedXamlFiles.Count)"
    Write-Log "  - Has Errors Key: $($outputJson.PSObject.Properties.Name -contains 'Errors')"
    Write-Log "  - Has Warnings Key: $($outputJson.PSObject.Properties.Name -contains 'Warnings')"
    Write-Log "  - MSBuildLogEntries Count: $($outputJson.MSBuildLogEntries.Count)"
  }
  catch {
    Write-Log "output.json Valid: No - $($_.Exception.Message)" "Red"
  }
}

# === PHASE 3: File Permission Check ===
Write-Log ""
Write-Log "=== PHASE 3: FILE PERMISSION DIAGNOSTICS ===" "Yellow"

if (Test-Path $buildDir) {
  try {
    $acl = Get-Acl $buildDir
    Write-Log "Build Directory ACL Owner: $($acl.Owner)"
    Write-Log "Build Directory Access Rules Count: $($acl.Access.Count)"
        
    # Test write permissions
    $testFile = Join-Path $buildDir "permission_test_$(Get-Random).tmp"
    try {
      "test" | Out-File -FilePath $testFile -Force
      Remove-Item $testFile -Force
      Write-Log "Write Permission Test: PASSED"
    }
    catch {
      Write-Log "Write Permission Test: FAILED - $($_.Exception.Message)" "Red"
    }
  }
  catch {
    Write-Log "ACL Check Failed: $($_.Exception.Message)" "Red"
  }
}

# === PHASE 4: Sample .g.cs and .g.i.cs Files ===
Write-Log ""
Write-Log "=== PHASE 4: GENERATED FILE INSPECTION ===" "Yellow"

$gcsFile = Join-Path $buildDir "App.g.cs"
$gicsFile = Join-Path $buildDir "App.g.i.cs"

Write-Log "Sample .g.cs File: $gcsFile"
Write-Log "  - Exists: $(Test-Path $gcsFile)"
if (Test-Path $gcsFile) {
  $gcsSize = (Get-Item $gcsFile).Length
  Write-Log "  - Size: $gcsSize bytes"
  if ($gcsSize -eq 0) {
    Write-Log "  - Status: EMPTY (0 bytes)" "Red"
  }
  else {
    $gcsFirstLines = Get-Content $gcsFile -TotalCount 5
    Write-Log "  - First 5 lines:"
    $gcsFirstLines | ForEach-Object { Write-Log "    $_" }
  }
}

Write-Log ""
Write-Log "Sample .g.i.cs File: $gicsFile"
Write-Log "  - Exists: $(Test-Path $gicsFile)"
if (Test-Path $gicsFile) {
  $gicsSize = (Get-Item $gicsFile).Length
  Write-Log "  - Size: $gicsSize bytes"
  if ($gicsSize -gt 0) {
    Write-Log "  - Status: HAS CONTENT" "Green"
    $gicsFirstLines = Get-Content $gicsFile -TotalCount 10
    Write-Log "  - First 10 lines:"
    $gicsFirstLines | ForEach-Object { Write-Log "    $_" }
  }
}

# Count empty vs non-empty .g.cs files
Write-Log ""
Write-Log "Analyzing all .g.cs and .g.i.cs files..."
$gcsFiles = Get-ChildItem -Path $buildDir -Filter "*.g.cs" -Recurse
$gicsFiles = Get-ChildItem -Path $buildDir -Filter "*.g.i.cs" -Recurse

$emptyGcs = @($gcsFiles | Where-Object { $_.Length -eq 0 })
$nonEmptyGcs = @($gcsFiles | Where-Object { $_.Length -gt 0 })

Write-Log ".g.cs File Count Summary:"
Write-Log "  - Total .g.cs files: $($gcsFiles.Count)"
Write-Log "  - Empty .g.cs files: $($emptyGcs.Count)"
Write-Log "  - Non-empty .g.cs files: $($nonEmptyGcs.Count)"

$emptyGics = @($gicsFiles | Where-Object { $_.Length -eq 0 })
$nonEmptyGics = @($gicsFiles | Where-Object { $_.Length -gt 0 })

Write-Log ".g.i.cs File Count Summary:"
Write-Log "  - Total .g.i.cs files: $($gicsFiles.Count)"
Write-Log "  - Empty .g.i.cs files: $($emptyGics.Count)"
Write-Log "  - Non-empty .g.i.cs files: $($nonEmptyGics.Count)"

if ($nonEmptyGcs.Count -eq 0 -and $nonEmptyGics.Count -gt 0) {
  Write-Log ""
  Write-Log "OBSERVATION: All .g.cs files are empty, but .g.i.cs files have content." "Cyan"
  Write-Log "This suggests Pass 2 is not writing to .g.cs files properly." "Cyan"
}

# === PHASE 5: Run XamlCompiler ===
Write-Log ""
Write-Log "=== PHASE 5: RUNNING XAML COMPILER ===" "Yellow"

if (-not (Test-Path $xamlCompilerPath)) {
  Write-Log "ERROR: XamlCompiler.exe not found at $xamlCompilerPath" "Red"
  Write-Log "Cannot proceed with compiler run."
  exit 1
}

if (-not (Test-Path $inputJsonPath)) {
  Write-Log "ERROR: input.json not found at $inputJsonPath" "Red"
  Write-Log "Cannot proceed with compiler run."
  exit 1
}

Write-Log "Starting XamlCompiler.exe..."
Write-Log "Command: & '$xamlCompilerPath' '$inputJsonPath' '$outputJsonPath'"

# Run the compiler and capture all output
$startTime = Get-Date
$process = Start-Process -FilePath $xamlCompilerPath `
  -ArgumentList @("`"$inputJsonPath`"", "`"$outputJsonPath`"") `
  -RedirectStandardOutput $logFile `
  -RedirectStandardError $errorFile `
  -NoNewWindow `
  -PassThru `
  -WorkingDirectory $buildDir

Write-Log "Process ID: $($process.Id)"
Write-Log "Waiting for compiler to complete..."

# Wait for process with timeout
$process.WaitForExit(120000)  # 2 minute timeout
$exitCode = $process.ExitCode
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Log ""
Write-Log "Compiler Exit Code: $exitCode" $(if ($exitCode -eq 0) { "Green" } else { "Red" })
Write-Log "Duration: $($duration) seconds"

# === PHASE 6: Output Analysis ===
Write-Log ""
Write-Log "=== PHASE 6: COMPILER OUTPUT ANALYSIS ===" "Yellow"

if (Test-Path $logFile) {
  $logContent = Get-Content $logFile
  $logSize = (Get-Item $logFile).Length
  Write-Log "stdout Log Size: $logSize bytes"
  Write-Log "stdout Line Count: $($logContent.Count)"
    
  if ($logContent.Count -gt 0) {
    Write-Log ""
    Write-Log "First 20 lines of stdout:"
    $logContent | Select-Object -First 20 | ForEach-Object { Write-Log "  $_" }
        
    if ($logContent.Count -gt 20) {
      Write-Log ""
      Write-Log "Last 20 lines of stdout:"
      $logContent | Select-Object -Last 20 | ForEach-Object { Write-Log "  $_" }
    }
  }
  else {
    Write-Log "stdout is empty" "Yellow"
  }
}

if (Test-Path $errorFile) {
  $errorContent = Get-Content $errorFile
  $errorSize = (Get-Item $errorFile).Length
  Write-Log ""
  Write-Log "stderr Log Size: $errorSize bytes"
  Write-Log "stderr Line Count: $($errorContent.Count)"
    
  if ($errorContent.Count -gt 0) {
    Write-Log ""
    Write-Log "All stderr output:" "Red"
    $errorContent | ForEach-Object { Write-Log "  $_" }
  }
  else {
    Write-Log "stderr is empty" "Yellow"
  }
}

# === PHASE 7: Post-Run File Inspection ===
Write-Log ""
Write-Log "=== PHASE 7: POST-RUN FILE INSPECTION ===" "Yellow"

if (Test-Path $outputJsonPath) {
  $outputSize = (Get-Item $outputJsonPath).Length
  Write-Log "output.json Size: $outputSize bytes"
    
  try {
    $outputJson = Get-Content $outputJsonPath | ConvertFrom-Json
    Write-Log "output.json Valid: Yes"
    Write-Log "  - GeneratedCodeFiles Count: $($outputJson.GeneratedCodeFiles.Count)"
    Write-Log "  - GeneratedXamlFiles Count: $($outputJson.GeneratedXamlFiles.Count)"
    Write-Log "  - MSBuildLogEntries Count: $($outputJson.MSBuildLogEntries.Count)"
        
    if ($outputJson.MSBuildLogEntries) {
      Write-Log ""
      Write-Log "MSBuild Log Entries:"
      $outputJson.MSBuildLogEntries | ForEach-Object {
        Write-Log "  - $($_.Message)"
      }
    }
  }
  catch {
    Write-Log "output.json Parse Error: $($_.Exception.Message)" "Red"
  }
}

# === Summary ===
Write-Log ""
Write-Log "=== DIAGNOSTIC SUMMARY ===" "Yellow"
Write-Log "Exit Code: $exitCode"
Write-Log "Status: $(if ($exitCode -eq 0) { 'COMPILER SUCCEEDED' } else { 'COMPILER FAILED' })" $(if ($exitCode -eq 0) { "Green" } else { "Red" })
Write-Log ""
Write-Log "Diagnostic logs saved to:"
Write-Log "  - Full diagnostic: $diagnosticFile"
Write-Log "  - Compiler stdout: $logFile"
Write-Log "  - Compiler stderr: $errorFile"
Write-Log ""
Write-Log "=== END DIAGNOSTIC RUN ===" "Cyan"

# Open diagnostic file
Write-Host ""
Write-Host "Opening diagnostic file..." -ForegroundColor Cyan
& notepad.exe $diagnosticFile
