#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated VoiceStudio WinUI Launcher
.DESCRIPTION
    Automatically starts the Python backend and launches the WinUI application
#>

param(
    [switch]$SkipBackend = $false,
    [switch]$Debug = $false
)

$ErrorActionPreference = "Stop"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Start-PythonBackend {
    Write-ColorOutput "Starting Python backend..." "Cyan"

    $backendScript = "services\voice_cloning\ultimate_web_server.py"
    if (Test-Path $backendScript) {
        $process = Start-Process -FilePath "python" -ArgumentList "`"$backendScript`" --host 127.0.0.1 --port 8083" -PassThru -WindowStyle Hidden
        Write-ColorOutput "✓ Python backend started (PID: $($process.Id))" "Green"

        # Wait for backend to be ready
        Write-ColorOutput "Waiting for backend to initialize..." "Yellow"
        Start-Sleep -Seconds 5

        # Test backend
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8083/api/status" -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "✓ Backend is ready and responding" "Green"
                return $process
            }
        }
        catch {
            Write-ColorOutput "⚠ Backend may not be ready yet" "Yellow"
        }

        return $process
    }
    else {
        Write-ColorOutput "✗ Backend script not found: $backendScript" "Red"
        return $null
    }
}

function Start-WinUIApp {
    Write-ColorOutput "Starting WinUI application..." "Cyan"

    $winuiPath = "VoiceStudioWinUI"
    if (Test-Path $winuiPath) {
        Set-Location $winuiPath

        if ($Debug) {
            Write-ColorOutput "Building in Debug mode..." "Yellow"
            dotnet build --configuration Debug
        }
        else {
            Write-ColorOutput "Building in Release mode..." "Yellow"
            dotnet build --configuration Release
        }

        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ WinUI application built successfully" "Green"
            Write-ColorOutput "Launching application..." "Cyan"

            if ($Debug) {
                dotnet run --configuration Debug
            }
            else {
                dotnet run --configuration Release
            }
        }
        else {
            Write-ColorOutput "✗ Build failed" "Red"
        }
    }
    else {
        Write-ColorOutput "✗ WinUI project not found: $winuiPath" "Red"
    }
}

function Stop-BackendProcess {
    param($Process)

    if ($Process -and !$Process.HasExited) {
        Write-ColorOutput "Stopping Python backend..." "Yellow"
        $Process.Kill()
        $Process.WaitForExit(5000)
        Write-ColorOutput "✓ Backend stopped" "Green"
    }
}

# Main execution
try {
    Write-ColorOutput "`n" "White"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "  VOICESTUDIO AUTOMATED LAUNCHER" "Magenta"
    Write-ColorOutput "=" * 80 "Magenta"
    Write-ColorOutput "`n" "White"

    $backendProcess = $null

    # Start Python backend if not skipped
    if (-not $SkipBackend) {
        $backendProcess = Start-PythonBackend
    }
    else {
        Write-ColorOutput "Skipping backend startup" "Yellow"
    }

    # Start WinUI application
    Start-WinUIApp

    Write-ColorOutput "`nApplication closed." "Cyan"
}
catch {
    Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
}
finally {
    # Cleanup
    if ($backendProcess) {
        Stop-BackendProcess $backendProcess
    }

    Write-ColorOutput "`nPress any key to exit..." "White"
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
