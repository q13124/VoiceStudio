#Requires -RunAsAdministrator
<#
.SYNOPSIS
    VoiceStudio Ultimate Deployment Script
.DESCRIPTION
    Comprehensive deployment script for VoiceStudio Ultimate application
.PARAMETER InstallPath
    Installation path for VoiceStudio
.PARAMETER DataPath
    Data path for VoiceStudio
.PARAMETER BuildType
    Build type: Debug, Release, or Production
.PARAMETER SkipTests
    Skip post-installation tests
.EXAMPLE
    .\Deploy-VoiceStudio.ps1 -BuildType Release
.EXAMPLE
    .\Deploy-VoiceStudio.ps1 -InstallPath "C:\VoiceStudio" -SkipTests
#>

param(
    [string]$InstallPath = "C:\Program Files\VoiceStudio",
    [string]$DataPath = "C:\ProgramData\VoiceStudio",
    [string]$BuildType = "Release",
    [switch]$SkipTests,
    [switch]$CreateMSI,
    [switch]$CreateInstaller
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Script configuration
$Script:LogFile = "deployment.log"
$Script:StartTime = Get-Date
$Script:InstallPath = $InstallPath
$Script:DataPath = $DataPath
$Script:BuildType = $BuildType

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"

    Write-Host $LogEntry
    Add-Content -Path $Script:LogFile -Value $LogEntry
}

# Error handling
function Write-Error-Log {
    param(
        [string]$Message,
        [Exception]$Exception
    )

    Write-Log "ERROR: $Message" "ERROR"
    Write-Log "Exception: $($Exception.Message)" "ERROR"
    Write-Log "Stack Trace: $($Exception.StackTrace)" "ERROR"
}

# Check system requirements
function Test-SystemRequirements {
    Write-Log "Checking system requirements..."

    $Requirements = @{
        WindowsVersion      = $false
        DotNetRuntime       = $false
        PythonInstalled     = $false
        SufficientMemory    = $false
        SufficientDiskSpace = $false
    }

    try {
        # Check Windows version
        $OSVersion = [System.Environment]::OSVersion.Version
        if ($OSVersion.Major -ge 10 -and $OSVersion.Build -ge 19041) {
            $Requirements.WindowsVersion = $true
            Write-Log "Windows version check passed"
        }
        else {
            Write-Log "Windows version check failed - requires Windows 10 19041+" "WARNING"
        }

        # Check .NET runtime
        try {
            $DotNetVersion = dotnet --version 2>$null
            if ($DotNetVersion) {
                $Requirements.DotNetRuntime = $true
                Write-Log ".NET runtime check passed - Version: $DotNetVersion"
            }
        }
        catch {
            Write-Log ".NET runtime check failed" "WARNING"
        }

        # Check Python
        try {
            $PythonVersion = python --version 2>$null
            if ($PythonVersion) {
                $Requirements.PythonInstalled = $true
                Write-Log "Python check passed - $PythonVersion"
            }
        }
        catch {
            Write-Log "Python check failed" "WARNING"
        }

        # Check memory (4GB+)
        $Memory = Get-WmiObject -Class Win32_ComputerSystem
        $MemoryGB = [math]::Round($Memory.TotalPhysicalMemory / 1GB, 2)
        if ($MemoryGB -ge 4) {
            $Requirements.SufficientMemory = $true
            Write-Log "Memory check passed - $MemoryGB GB available"
        }
        else {
            Write-Log "Memory check failed - requires 4GB+, found $MemoryGB GB" "WARNING"
        }

        # Check disk space (10GB+)
        $Drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
        $FreeSpaceGB = [math]::Round($Drive.FreeSpace / 1GB, 2)
        if ($FreeSpaceGB -ge 10) {
            $Requirements.SufficientDiskSpace = $true
            Write-Log "Disk space check passed - $FreeSpaceGB GB free"
        }
        else {
            Write-Log "Disk space check failed - requires 10GB+, found $FreeSpaceGB GB" "WARNING"
        }

        $PassedRequirements = ($Requirements.Values | Where-Object { $_ -eq $true }).Count
        $TotalRequirements = $Requirements.Count

        Write-Log "System requirements: $PassedRequirements/$TotalRequirements passed"

        return $Requirements

    }
    catch {
        Write-Error-Log "Error checking system requirements" $_
        return $Requirements
    }
}

# Install dependencies
function Install-Dependencies {
    Write-Log "Installing dependencies..."

    try {
        # Install .NET Desktop Runtime
        Write-Log "Installing .NET Desktop Runtime..."
        $DotNetUrl = "https://download.microsoft.com/download/8/8/5/885e5c8c-4c4b-4b3b-9b0b-1b5b0b0b0b0b/dotnet-desktop-runtime-8.0.0-win-x64.exe"
        $DotNetInstaller = "$env:TEMP\dotnet-desktop-runtime-installer.exe"

        if (-not (Test-Path $DotNetInstaller)) {
            Invoke-WebRequest -Uri $DotNetUrl -OutFile $DotNetInstaller
        }

        Start-Process -FilePath $DotNetInstaller -ArgumentList "/quiet" -Wait

        # Install Python packages
        Write-Log "Installing Python packages..."
        $PythonPackages = @(
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "numpy>=1.24.0",
            "torch>=2.0.0",
            "transformers>=4.38.0",
            "tokenizers>=0.15.0",
            "psutil>=5.9.0",
            "websockets>=12.0",
            "aiohttp>=3.9.0"
        )

        foreach ($Package in $PythonPackages) {
            Write-Log "Installing $Package..."
            python -m pip install $Package --upgrade --quiet
        }

        Write-Log "Dependencies installed successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error installing dependencies" $_
        return $false
    }
}

# Create directory structure
function New-DirectoryStructure {
    Write-Log "Creating directory structure..."

    try {
        $Directories = @(
            $Script:InstallPath,
            "$Script:InstallPath\bin",
            "$Script:InstallPath\services",
            "$Script:InstallPath\config",
            "$Script:InstallPath\logs",
            $Script:DataPath,
            "$Script:DataPath\workers",
            "$Script:DataPath\workers\ops",
            "$Script:DataPath\models",
            "$Script:DataPath\cache",
            "$env:USERPROFILE\VoiceStudio",
            "$env:USERPROFILE\VoiceStudio\outputs",
            "$env:USERPROFILE\VoiceStudio\temp"
        )

        foreach ($Directory in $Directories) {
            if (-not (Test-Path $Directory)) {
                New-Item -Path $Directory -ItemType Directory -Force | Out-Null
                Write-Log "Created directory: $Directory"
            }
        }

        Write-Log "Directory structure created successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error creating directory structure" $_
        return $false
    }
}

# Copy application files
function Copy-ApplicationFiles {
    Write-Log "Copying application files..."

    try {
        # Copy WinUI application
        if (Test-Path "VoiceStudioWinUI") {
            Copy-Item -Path "VoiceStudioWinUI" -Destination $Script:InstallPath -Recurse -Force
            Write-Log "Copied WinUI application"
        }

        # Copy services
        if (Test-Path "services") {
            Copy-Item -Path "services" -Destination $Script:InstallPath -Recurse -Force
            Write-Log "Copied services"
        }

        # Copy workers
        if (Test-Path "C:\ProgramData\VoiceStudio\workers") {
            Copy-Item -Path "C:\ProgramData\VoiceStudio\workers" -Destination $Script:DataPath -Recurse -Force
            Write-Log "Copied workers"
        }

        # Copy solution files
        $SolutionFiles = @("VoiceStudio.sln", "VoiceStudio.Contracts", "UltraClone.EngineService")
        foreach ($File in $SolutionFiles) {
            if (Test-Path $File) {
                if (Test-Path $File -PathType Container) {
                    Copy-Item -Path $File -Destination $Script:InstallPath -Recurse -Force
                }
                else {
                    Copy-Item -Path $File -Destination $Script:InstallPath -Force
                }
                Write-Log "Copied $File"
            }
        }

        # Copy configuration files
        if (Test-Path "config") {
            Copy-Item -Path "config" -Destination $Script:InstallPath -Recurse -Force
            Write-Log "Copied configuration files"
        }

        Write-Log "Application files copied successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error copying application files" $_
        return $false
    }
}

# Build application
function Build-Application {
    Write-Log "Building application..."

    try {
        # Build solution
        $SolutionPath = Join-Path $Script:InstallPath "VoiceStudio.sln"
        if (Test-Path $SolutionPath) {
            Write-Log "Building solution..."
            dotnet build $SolutionPath --configuration $Script:BuildType --verbosity quiet

            if ($LASTEXITCODE -eq 0) {
                Write-Log "Solution built successfully"
            }
            else {
                Write-Log "Solution build failed" "ERROR"
                return $false
            }
        }

        # Publish WinUI application
        $WinUIProject = Join-Path $Script:InstallPath "VoiceStudioWinUI\VoiceStudioWinUI.csproj"
        if (Test-Path $WinUIProject) {
            Write-Log "Publishing WinUI application..."
            $OutputPath = Join-Path $Script:InstallPath "bin"

            dotnet publish $WinUIProject `
                --configuration $Script:BuildType `
                --runtime win-x64 `
                --self-contained true `
                --output $OutputPath `
                --verbosity quiet

            if ($LASTEXITCODE -eq 0) {
                Write-Log "WinUI application published successfully"
            }
            else {
                Write-Log "WinUI application publish failed" "ERROR"
                return $false
            }
        }

        Write-Log "Application built successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error building application" $_
        return $false
    }
}

# Create shortcuts
function New-Shortcuts {
    Write-Log "Creating shortcuts..."

    try {
        $WshShell = New-Object -ComObject WScript.Shell

        # Desktop shortcut
        $DesktopShortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\VoiceStudio Ultimate.lnk")
        $DesktopShortcut.TargetPath = Join-Path $Script:InstallPath "bin\VoiceStudioWinUI.exe"
        $DesktopShortcut.WorkingDirectory = $Script:InstallPath
        $DesktopShortcut.Description = "VoiceStudio Ultimate Voice Cloning Application"
        $DesktopShortcut.Save()
        Write-Log "Created desktop shortcut"

        # Start menu shortcuts
        $StartMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\VoiceStudio"
        if (-not (Test-Path $StartMenuPath)) {
            New-Item -Path $StartMenuPath -ItemType Directory -Force | Out-Null
        }

        $StartMenuShortcuts = @(
            @{Name = "VoiceStudio Ultimate"; Exe = "VoiceStudioWinUI.exe" },
            @{Name = "Service Manager"; Exe = "ServiceManager.exe" },
            @{Name = "Configuration Editor"; Exe = "ConfigEditor.exe" }
        )

        foreach ($Shortcut in $StartMenuShortcuts) {
            $ShortcutPath = Join-Path $StartMenuPath "$($Shortcut.Name).lnk"
            $ShortcutObject = $WshShell.CreateShortcut($ShortcutPath)
            $ShortcutObject.TargetPath = Join-Path $Script:InstallPath "bin\$($Shortcut.Exe)"
            $ShortcutObject.WorkingDirectory = $Script:InstallPath
            $ShortcutObject.Description = $Shortcut.Name
            $ShortcutObject.Save()
            Write-Log "Created start menu shortcut: $($Shortcut.Name)"
        }

        Write-Log "Shortcuts created successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error creating shortcuts" $_
        return $false
    }
}

# Create Windows service
function New-WindowsService {
    Write-Log "Creating Windows service..."

    try {
        $ServiceName = "VoiceStudio"
        $ServiceDisplayName = "VoiceStudio Ultimate Service"
        $ServiceDescription = "VoiceStudio Ultimate Voice Cloning Service"
        $ServiceScript = Join-Path $Script:InstallPath "services\voice_cloning\ultimate_web_server.py"

        # Create service script
        $ServiceInstallScript = @"
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
import subprocess
from pathlib import Path

class VoiceStudioService(win32serviceutil.ServiceFramework):
    _svc_name_ = "$ServiceName"
    _svc_display_name_ = "$ServiceDisplayName"
    _svc_description_ = "$ServiceDescription"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_name_, ''))
        self.main()

    def main(self):
        install_dir = Path("$Script:InstallPath")
        service_script = install_dir / "services" / "voice_cloning" / "ultimate_web_server.py"

        if service_script.exists():
            process = subprocess.Popen([
                sys.executable, str(service_script), "--host", "127.0.0.1", "--port", "8083"
            ])

            while self.is_running:
                time.sleep(1)

            process.terminate()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(VoiceStudioService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(VoiceStudioService)
"@

        $ServiceScriptPath = Join-Path $Script:InstallPath "bin\voice_studio_service.py"
        Set-Content -Path $ServiceScriptPath -Value $ServiceInstallScript

        # Install service
        python $ServiceScriptPath install

        Write-Log "Windows service created successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error creating Windows service" $_
        return $false
    }
}

# Create configuration
function New-Configuration {
    Write-Log "Creating configuration..."

    try {
        $Config = @{
            application = @{
                name              = "VoiceStudio Ultimate"
                version           = "1.0.0"
                install_directory = $Script:InstallPath
                data_directory    = $Script:DataPath
                user_directory    = "$env:USERPROFILE\VoiceStudio"
            }
            services    = @{
                web_server       = @{
                    host    = "127.0.0.1"
                    port    = 8083
                    enabled = $true
                }
                realtime_service = @{
                    enabled      = $true
                    buffer_size  = 100
                    latency_mode = "low"
                }
            }
            ai_models   = @{
                gpt_sovits_2 = @{
                    enabled = $true
                    path    = Join-Path $Script:DataPath "models\gpt_sovits_2"
                }
                coqui_xtts_3 = @{
                    enabled = $true
                    path    = Join-Path $Script:DataPath "models\coqui_xtts_3"
                }
            }
            workers     = @{
                max_workers      = 32
                worker_directory = Join-Path $Script:DataPath "workers"
                enabled          = $true
            }
        }

        $ConfigPath = Join-Path $Script:InstallPath "config\voice_studio_config.json"
        $Config | ConvertTo-Json -Depth 10 | Set-Content -Path $ConfigPath

        Write-Log "Configuration created successfully"
        return $true

    }
    catch {
        Write-Error-Log "Error creating configuration" $_
        return $false
    }
}

# Run post-installation tests
function Test-PostInstallation {
    Write-Log "Running post-installation tests..."

    try {
        # Test web server
        Write-Log "Testing web server..."
        $ServiceScript = Join-Path $Script:InstallPath "services\voice_cloning\ultimate_web_server.py"
        if (Test-Path $ServiceScript) {
            $Process = Start-Process -FilePath "python" -ArgumentList $ServiceScript, "--host", "127.0.0.1", "--port", "8083" -PassThru -WindowStyle Hidden

            Start-Sleep -Seconds 5

            try {
                $Response = Invoke-WebRequest -Uri "http://127.0.0.1:8083/api/status" -TimeoutSec 10
                if ($Response.StatusCode -eq 200) {
                    Write-Log "Web server test passed"
                }
                else {
                    Write-Log "Web server test failed - Status: $($Response.StatusCode)" "WARNING"
                }
            }
            catch {
                Write-Log "Web server test failed - Connection error" "WARNING"
            }

            Stop-Process -Id $Process.Id -Force
        }

        # Test WinUI application
        Write-Log "Testing WinUI application..."
        $WinUIExe = Join-Path $Script:InstallPath "bin\VoiceStudioWinUI.exe"
        if (Test-Path $WinUIExe) {
            Write-Log "WinUI application executable found"
        }
        else {
            Write-Log "WinUI application executable not found" "WARNING"
        }

        # Test Windows service
        Write-Log "Testing Windows service..."
        $Service = Get-Service -Name "VoiceStudio" -ErrorAction SilentlyContinue
        if ($Service) {
            Write-Log "VoiceStudio service found"
        }
        else {
            Write-Log "VoiceStudio service not found" "WARNING"
        }

        Write-Log "Post-installation tests completed"
        return $true

    }
    catch {
        Write-Error-Log "Error running post-installation tests" $_
        return $false
    }
}

# Create MSI package
function New-MSIPackage {
    Write-Log "Creating MSI package..."

    try {
        if (-not (Test-Path "installer\VoiceStudio.wxs")) {
            Write-Log "WiX source file not found" "ERROR"
            return $false
        }

        # Compile WiX source
        Write-Log "Compiling WiX source..."
        candle "installer\VoiceStudio.wxs" -out "installer\VoiceStudio.wixobj"

        if ($LASTEXITCODE -eq 0) {
            Write-Log "WiX source compiled successfully"
        }
        else {
            Write-Log "WiX source compilation failed" "ERROR"
            return $false
        }

        # Link WiX object
        Write-Log "Linking WiX object..."
        light "installer\VoiceStudio.wixobj" -out "installer\VoiceStudio.msi"

        if ($LASTEXITCODE -eq 0) {
            Write-Log "MSI package created successfully: installer\VoiceStudio.msi"
            return $true
        }
        else {
            Write-Log "MSI package creation failed" "ERROR"
            return $false
        }

    }
    catch {
        Write-Error-Log "Error creating MSI package" $_
        return $false
    }
}

# Main deployment function
function Start-Deployment {
    Write-Log "Starting VoiceStudio Ultimate deployment..."
    Write-Log "Installation path: $Script:InstallPath"
    Write-Log "Data path: $Script:DataPath"
    Write-Log "Build type: $Script:BuildType"

    $DeploymentSteps = @(
        @{Name = "System Requirements Check"; Function = { Test-SystemRequirements } },
        @{Name = "Dependency Installation"; Function = { Install-Dependencies } },
        @{Name = "Directory Structure Creation"; Function = { New-DirectoryStructure } },
        @{Name = "Application Files Copy"; Function = { Copy-ApplicationFiles } },
        @{Name = "Application Build"; Function = { Build-Application } },
        @{Name = "Shortcuts Creation"; Function = { New-Shortcuts } },
        @{Name = "Windows Service Creation"; Function = { New-WindowsService } },
        @{Name = "Configuration Creation"; Function = { New-Configuration } }
    )

    if (-not $SkipTests) {
        $DeploymentSteps += @{Name = "Post-Installation Tests"; Function = { Test-PostInstallation } }
    }

    if ($CreateMSI) {
        $DeploymentSteps += @{Name = "MSI Package Creation"; Function = { New-MSIPackage } }
    }

    foreach ($Step in $DeploymentSteps) {
        Write-Log "Executing: $($Step.Name)"

        try {
            $Result = & $Step.Function
            if ($Result -eq $false) {
                Write-Log "Step failed: $($Step.Name)" "ERROR"
                return $false
            }
            Write-Log "Step completed: $($Step.Name)"
        }
        catch {
            Write-Error-Log "Step error: $($Step.Name)" $_
            return $false
        }
    }

    $EndTime = Get-Date
    $Duration = $EndTime - $Script:StartTime

    Write-Log "VoiceStudio Ultimate deployment completed successfully!"
    Write-Log "Total deployment time: $($Duration.TotalMinutes.ToString('F2')) minutes"
    Write-Log "Installation path: $Script:InstallPath"
    Write-Log "Data path: $Script:DataPath"

    return $true
}

# Script execution
try {
    Write-Log "VoiceStudio Ultimate Deployment Script v1.0.0"
    Write-Log "=============================================="

    if (Start-Deployment) {
        Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
        Write-Host "VoiceStudio Ultimate has been installed to: $Script:InstallPath" -ForegroundColor Green
        Write-Host "You can now start VoiceStudio from the Start Menu or Desktop shortcut." -ForegroundColor Green
    }
    else {
        Write-Host "`nDeployment failed. Check $Script:LogFile for details." -ForegroundColor Red
        exit 1
    }

}
catch {
    Write-Error-Log "Deployment script error" $_
    Write-Host "`nDeployment failed with error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
