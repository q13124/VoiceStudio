#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated VoiceStudio Testing and Deployment
.DESCRIPTION
    Comprehensive testing, building, and deployment automation for VoiceStudio WinUI
#>

param(
    [switch]$Test = $false,
    [switch]$Build = $false,
    [switch]$Deploy = $false,
    [switch]$All = $false
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-VoiceStudioComponents {
    Write-ColorOutput "Testing VoiceStudio components..." "Cyan"

    $tests = @()

    # Test Python backend
    Write-ColorOutput "Testing Python backend..." "Yellow"
    try {
        $backendScript = "services\voice_cloning\ultimate_web_server.py"
        if (Test-Path $backendScript) {
            Write-ColorOutput "✓ Backend script exists" "Green"
            $tests += @{Name = "Backend Script"; Status = "Pass" }
        }
        else {
            Write-ColorOutput "✗ Backend script missing" "Red"
            $tests += @{Name = "Backend Script"; Status = "Fail" }
        }
    }
    catch {
        Write-ColorOutput "✗ Backend test failed: $($_.Exception.Message)" "Red"
        $tests += @{Name = "Backend Script"; Status = "Fail" }
    }

    # Test WinUI project
    Write-ColorOutput "Testing WinUI project..." "Yellow"
    try {
        $winuiProject = "VoiceStudioWinUI\VoiceStudioWinUI.csproj"
        if (Test-Path $winuiProject) {
            Write-ColorOutput "✓ WinUI project exists" "Green"
            $tests += @{Name = "WinUI Project"; Status = "Pass" }
        }
        else {
            Write-ColorOutput "✗ WinUI project missing" "Red"
            $tests += @{Name = "WinUI Project"; Status = "Fail" }
        }
    }
    catch {
        Write-ColorOutput "✗ WinUI test failed: $($_.Exception.Message)" "Red"
        $tests += @{Name = "WinUI Project"; Status = "Fail" }
    }

    # Test dependencies
    Write-ColorOutput "Testing dependencies..." "Yellow"
    try {
        $dotnetVersion = dotnet --version
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ .NET SDK available: $dotnetVersion" "Green"
            $tests += @{Name = ".NET SDK"; Status = "Pass" }
        }
        else {
            Write-ColorOutput "✗ .NET SDK not available" "Red"
            $tests += @{Name = ".NET SDK"; Status = "Fail" }
        }
    }
    catch {
        Write-ColorOutput "✗ Dependency test failed: $($_.Exception.Message)" "Red"
        $tests += @{Name = ".NET SDK"; Status = "Fail" }
    }

    # Test Python
    try {
        $pythonVersion = python --version
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Python available: $pythonVersion" "Green"
            $tests += @{Name = "Python"; Status = "Pass" }
        }
        else {
            Write-ColorOutput "✗ Python not available" "Red"
            $tests += @{Name = "Python"; Status = "Fail" }
        }
    }
    catch {
        Write-ColorOutput "✗ Python test failed: $($_.Exception.Message)" "Red"
        $tests += @{Name = "Python"; Status = "Fail" }
    }

    # Display test results
    Write-ColorOutput "`nTest Results:" "Cyan"
    foreach ($test in $tests) {
        $statusColor = if ($test.Status -eq "Pass") { "Green" } else { "Red" }
        Write-ColorOutput "  $($test.Status): $($test.Name)" $statusColor
    }

    $passedTests = ($tests | Where-Object { $_.Status -eq "Pass" }).Count
    $totalTests = $tests.Count

    Write-ColorOutput "`nOverall: $passedTests/$totalTests tests passed" "Cyan"
    return $passedTests -eq $totalTests
}

function Build-VoiceStudioWinUI {
    Write-ColorOutput "Building VoiceStudio WinUI..." "Cyan"

    try {
        Set-Location "VoiceStudioWinUI"

        # Clean previous builds
        Write-ColorOutput "Cleaning previous builds..." "Yellow"
        dotnet clean --configuration Release

        # Restore packages
        Write-ColorOutput "Restoring packages..." "Yellow"
        dotnet restore

        # Build project
        Write-ColorOutput "Building project..." "Yellow"
        dotnet build --configuration Release

        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Build successful" "Green"
            return $true
        }
        else {
            Write-ColorOutput "✗ Build failed" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Build error: $($_.Exception.Message)" "Red"
        return $false
    }
    finally {
        Set-Location ".."
    }
}

function Deploy-VoiceStudioWinUI {
    Write-ColorOutput "Deploying VoiceStudio WinUI..." "Cyan"

    try {
        Set-Location "VoiceStudioWinUI"

        # Create deployment package
        Write-ColorOutput "Creating deployment package..." "Yellow"
        dotnet publish --configuration Release --runtime win-x64 --self-contained true --output "bin\Deploy"

        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Deployment package created" "Green"

            # Create installer script
            $installerScript = @"
@echo off
echo Installing VoiceStudio WinUI...
xcopy /E /I /Y "bin\Deploy\*" "%ProgramFiles%\VoiceStudioWinUI\"
echo Installation complete!
echo VoiceStudio WinUI has been installed to: %ProgramFiles%\VoiceStudioWinUI\
pause
"@

            Set-Content -Path "bin\Deploy\install.bat" -Value $installerScript

            # Create uninstaller script
            $uninstallerScript = @"
@echo off
echo Uninstalling VoiceStudio WinUI...
rmdir /S /Q "%ProgramFiles%\VoiceStudioWinUI\"
echo Uninstallation complete!
pause
"@

            Set-Content -Path "bin\Deploy\uninstall.bat" -Value $uninstallerScript

            Write-ColorOutput "✓ Installer scripts created" "Green"
            Write-ColorOutput "Deployment package location: VoiceStudioWinUI\bin\Deploy\" "Cyan"
            return $true
        }
        else {
            Write-ColorOutput "✗ Deployment failed" "Red"
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ Deployment error: $($_.Exception.Message)" "Red"
        return $false
    }
    finally {
        Set-Location ".."
    }
}

function Start-AutomatedTest {
    Write-ColorOutput "Starting automated test..." "Cyan"

    try {
        # Start backend
        Write-ColorOutput "Starting Python backend..." "Yellow"
        $backendProcess = Start-Process -FilePath "python" -ArgumentList "services\voice_cloning\ultimate_web_server.py --host 127.0.0.1 --port 8083" -PassThru -WindowStyle Hidden

        # Wait for backend
        Start-Sleep -Seconds 5

        # Test backend API
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8083/api/status" -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✓ Backend API responding" "Green"
            }
        }
        catch {
            Write-ColorOutput "✗ Backend API not responding" "Red"
        }

        # Start WinUI app
        Write-ColorOutput "Starting WinUI application..." "Yellow"
        Set-Location "VoiceStudioWinUI"
        $winuiProcess = Start-Process -FilePath "dotnet" -ArgumentList "run --configuration Release" -PassThru

        Write-ColorOutput "✓ Automated test started" "Green"
        Write-ColorOutput "Backend PID: $($backendProcess.Id)" "Cyan"
        Write-ColorOutput "WinUI PID: $($winuiProcess.Id)" "Cyan"

        # Wait for user input
        Write-ColorOutput "`nPress any key to stop automated test..." "Yellow"
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

        # Cleanup
        Write-ColorOutput "Stopping processes..." "Yellow"
        $backendProcess.Kill()
        $winuiProcess.Kill()

        Write-ColorOutput "✓ Automated test completed" "Green"
    }
    catch {
        Write-ColorOutput "✗ Automated test error: $($_.Exception.Message)" "Red"
    }
    finally {
        Set-Location ".."
    }
}

# Main execution
try {
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "  VOICESTUDIO AUTOMATED TESTING & DEPLOYMENT" "Magenta"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "`n" "White"

    if ($All -or $Test) {
        $testPassed = Test-VoiceStudioComponents
        if (-not $testPassed) {
            Write-ColorOutput "Tests failed. Stopping execution." "Red"
            exit 1
        }
    }

    if ($All -or $Build) {
        $buildSuccess = Build-VoiceStudioWinUI
        if (-not $buildSuccess) {
            Write-ColorOutput "Build failed. Stopping execution." "Red"
            exit 1
        }
    }

    if ($All -or $Deploy) {
        $deploySuccess = Deploy-VoiceStudioWinUI
        if (-not $deploySuccess) {
            Write-ColorOutput "Deployment failed." "Red"
            exit 1
        }
    }

    if ($All) {
        Start-AutomatedTest
    }

    Write-ColorOutput "`nAll operations completed successfully!" "Green"
}
catch {
    Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
    exit 1
}
