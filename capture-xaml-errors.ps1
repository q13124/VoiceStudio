# Script to capture XAML compiler errors to a text file
# Usage: .\capture-xaml-errors.ps1

$ErrorLogFile = "E:\VoiceStudio\xaml-compiler-errors.txt"
$BuildLogFile = "E:\VoiceStudio\xaml-build-full.log"

Write-Host "Building VoiceStudio.App and capturing all output..." -ForegroundColor Cyan
Write-Host "Errors will be saved to: $ErrorLogFile" -ForegroundColor Yellow
Write-Host "Full build log will be saved to: $BuildLogFile" -ForegroundColor Yellow
Write-Host ""

# Clean previous logs
if (Test-Path $ErrorLogFile) { Remove-Item $ErrorLogFile -Force }
if (Test-Path $BuildLogFile) { Remove-Item $BuildLogFile -Force }

# Build with full logging
$buildOutput = dotnet build "E:\VoiceStudio\src\VoiceStudio.App\VoiceStudio.App.csproj" -c Debug /fl "/flp:logfile=$BuildLogFile;verbosity=detailed" 2>&1

# Save full output
$buildOutput | Out-File $BuildLogFile -Encoding utf8

# Also try to run XAML compiler directly to capture its output
Write-Host "`nRunning XAML compiler directly to capture errors..." -ForegroundColor Cyan
$xamlCompiler = "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk\1.5.240627000\tools\net472\XamlCompiler.exe"
$inputJson = "E:\VoiceStudio\src\VoiceStudio.App\obj\Debug\net8.0-windows10.0.19041.0\input.json"
$outputJson = "E:\VoiceStudio\src\VoiceStudio.App\obj\Debug\net8.0-windows10.0.19041.0\output.json"

if ((Test-Path $xamlCompiler) -and (Test-Path $inputJson)) {
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $xamlCompiler
    $processInfo.Arguments = "`"$inputJson`" `"$outputJson`""
    $processInfo.UseShellExecute = $false
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.CreateNoWindow = $true
    $processInfo.WorkingDirectory = "E:\VoiceStudio\src\VoiceStudio.App"
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $process.Start() | Out-Null
    
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    
    Write-Host "XAML Compiler Exit Code: $($process.ExitCode)" -ForegroundColor $(if ($process.ExitCode -eq 0) { "Green" } else { "Red" })
    
    if ($stdout) {
        Write-Host "`n=== XAML COMPILER STDOUT ===" -ForegroundColor Yellow
        $stdout
        "=== XAML COMPILER STDOUT ===" | Out-File $ErrorLogFile -Append -Encoding utf8
        $stdout | Out-File $ErrorLogFile -Append -Encoding utf8
    }
    
    if ($stderr) {
        Write-Host "`n=== XAML COMPILER STDERR ===" -ForegroundColor Red
        $stderr
        "`n=== XAML COMPILER STDERR ===" | Out-File $ErrorLogFile -Append -Encoding utf8
        $stderr | Out-File $ErrorLogFile -Append -Encoding utf8
    }
    
    if (-not $stdout -and -not $stderr) {
        Write-Host "No output from XAML compiler (this is unusual)" -ForegroundColor Yellow
        "No output from XAML compiler (exit code: $($process.ExitCode))" | Out-File $ErrorLogFile -Append -Encoding utf8
    }
} else {
    Write-Host "XAML compiler or input.json not found" -ForegroundColor Yellow
}

# Extract XAML-related errors
$errors = $buildOutput | Select-String -Pattern "error|Error|WMC|\.xaml|XamlCompiler" -Context 5,5

if ($errors) {
    $errors | Out-File $ErrorLogFile -Encoding utf8
    Write-Host "`n=== XAML ERRORS FOUND ===" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    Write-Host "`nFull errors saved to: $ErrorLogFile" -ForegroundColor Yellow
} else {
    Write-Host "`nNo XAML errors found in output (but build may have failed)" -ForegroundColor Yellow
    Write-Host "Check the full build log: $BuildLogFile" -ForegroundColor Yellow
}

# Also try to read the XAML compiler output.json if it exists
$outputJson = "E:\VoiceStudio\src\VoiceStudio.App\obj\Debug\net8.0-windows10.0.19041.0\output.json"
if (Test-Path $outputJson) {
    Write-Host "`nChecking XAML compiler output.json..." -ForegroundColor Cyan
    try {
        $json = Get-Content $outputJson -Raw | ConvertFrom-Json
        if ($json.Errors) {
            Write-Host "Found errors in output.json:" -ForegroundColor Red
            $json.Errors | Format-List | Out-File "$ErrorLogFile.json" -Encoding utf8
            $json.Errors | Format-List
        }
    } catch {
        Write-Host "Could not parse output.json: $_" -ForegroundColor Yellow
    }
}

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "Check these files:" -ForegroundColor Cyan
Write-Host "  - $ErrorLogFile" -ForegroundColor White
Write-Host "  - $BuildLogFile" -ForegroundColor White
