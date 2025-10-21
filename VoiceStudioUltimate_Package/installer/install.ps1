
# VoiceStudio Ultimate Windows Installer
# PowerShell-based installer with full Windows integration

param(
    [switch]$Uninstall,
    [switch]$Silent,
    [string]$InstallPath = "C:\Program Files\VoiceStudio"
)

# Configuration
$AppName = "VoiceStudio Ultimate"
$AppVersion = "1.0.0"
$AppPublisher = "VoiceStudio Team"
$AppURL = "https://voicestudio.ai"
$InstallDir = $InstallPath
$StartMenuFolder = "VoiceStudio Ultimate"

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-VoiceStudio {
    Write-ColorOutput "Installing $AppName $AppVersion..." $Colors.Info
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-ColorOutput "This installer requires administrator privileges." $Colors.Error
        Write-ColorOutput "Please run PowerShell as Administrator and try again." $Colors.Error
        exit 1
    }
    
    # Create installation directory
    if (-not (Test-Path $InstallDir)) {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
        Write-ColorOutput "Created installation directory: $InstallDir" $Colors.Success
    }
    
    # Copy application files
    $SourceDir = Split-Path $MyInvocation.MyCommand.Path
    $AppFiles = @(
        "services",
        "VoiceStudio",
        "*.py",
        "*.bat",
        "*.ps1",
        "requirements*.txt",
        "*.md"
    )
    
    foreach ($pattern in $AppFiles) {
        $sourcePath = Join-Path $SourceDir $pattern
        if (Test-Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $InstallDir -Recurse -Force
            Write-ColorOutput "Copied: $pattern" $Colors.Success
        }
    }
    
    # Create application directories
    $AppDirs = @("logs", "temp", "models", "config", "cache")
    foreach ($dir in $AppDirs) {
        $dirPath = Join-Path $InstallDir $dir
        if (-not (Test-Path $dirPath)) {
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        }
    }
    
    # Install Python dependencies
    Write-ColorOutput "Installing Python dependencies..." $Colors.Info
    $RequirementsFile = Join-Path $InstallDir "requirements-gui.txt"
    if (Test-Path $RequirementsFile) {
        try {
            & python -m pip install -r $RequirementsFile --quiet
            Write-ColorOutput "Python dependencies installed successfully" $Colors.Success
        } catch {
            Write-ColorOutput "Warning: Failed to install some Python dependencies" $Colors.Warning
        }
    }
    
    # Install VSDML dependencies
    $VSDMLRequirements = Join-Path $InstallDir "VoiceStudio\workers\python\vsdml\requirements.txt"
    if (Test-Path $VSDMLRequirements) {
        try {
            & python -m pip install -r $VSDMLRequirements --quiet
            Write-ColorOutput "VSDML dependencies installed successfully" $Colors.Success
        } catch {
            Write-ColorOutput "Warning: Failed to install some VSDML dependencies" $Colors.Warning
        }
    }
    
    # Create Windows Services
    Install-WindowsServices
    
    # Create shortcuts
    Create-Shortcuts
    
    # Register in Control Panel
    Register-ControlPanel
    
    # Pin to taskbar
    if (${self.config['taskbar_pin']}) {
        Pin-ToTaskbar
    }
    
    

# Install Auto Handoff System
Write-ColorOutput "Installing Auto Handoff system..." $Colors.Info
$HandoffInstaller = Join-Path $InstallDir "installer\handoff\install_handoff.ps1"
if (Test-Path $HandoffInstaller) {
    try {
        & $HandoffInstaller -Root $InstallDir
        Write-ColorOutput "Auto Handoff system installed successfully" $Colors.Success
    } catch {
        Write-ColorOutput "Warning: Failed to install Auto Handoff system: $($_.Exception.Message)" $Colors.Warning
    }
} else {
    Write-ColorOutput "Warning: Auto Handoff installer not found" $Colors.Warning
}

    

# Install Enhanced Auto Handoff System
Write-ColorOutput "Installing Enhanced Auto Handoff system..." $Colors.Info
$HandoffInstaller = Join-Path $InstallDir "installer\handoff\install_enhanced_handoff.ps1"
if (Test-Path $HandoffInstaller) {
    try {
        & $HandoffInstaller -Root $InstallDir
        Write-ColorOutput "Enhanced Auto Handoff system installed successfully" $Colors.Success
        Write-ColorOutput "Features: Winget/Choco, SBOM export, GPU VRAM testing" $Colors.Info
    } catch {
        Write-ColorOutput "Warning: Failed to install Enhanced Auto Handoff system: $($_.Exception.Message)" $Colors.Warning
    }
} else {
    Write-ColorOutput "Warning: Enhanced Auto Handoff installer not found" $Colors.Warning
}

    

# Install CycloneDX SBOM + VRAM Telemetry + Cursor Integration
Write-ColorOutput "Installing CycloneDX SBOM + VRAM Telemetry + Cursor system..." $Colors.Info
$CycloneDXInstaller = Join-Path $InstallDir "installer\handoff\install_cyclonedx_telemetry.ps1"
if (Test-Path $CycloneDXInstaller) {
    try {
        & $CycloneDXInstaller -Root $InstallDir
        Write-ColorOutput "CycloneDX SBOM + VRAM Telemetry + Cursor system installed successfully" $Colors.Success
        Write-ColorOutput "Features: CycloneDX SBOMs, VRAM telemetry, Cursor AI auto-open" $Colors.Info
    } catch {
        Write-ColorOutput "Warning: Failed to install CycloneDX + VRAM Telemetry + Cursor system: $($_.Exception.Message)" $Colors.Warning
    }
} else {
    Write-ColorOutput "Warning: CycloneDX + VRAM Telemetry + Cursor installer not found" $Colors.Warning
}

    Write-ColorOutput "`n$AppName installed successfully!" $Colors.Success
    Write-ColorOutput "Installation directory: $InstallDir" $Colors.Info
    Write-ColorOutput "Start Menu: $StartMenuFolder" $Colors.Info
    
    if (-not $Silent) {
        $response = Read-Host "Would you like to launch VoiceStudio now? (Y/N)"
        if ($response -eq "Y" -or $response -eq "y") {
            Launch-VoiceStudio
        }
    }
}

function Install-WindowsServices {
    Write-ColorOutput "Installing Windows Services..." $Colors.Info
    
    $Services = @(
        @{
            Name = "VoiceStudioAssistant"
            DisplayName = "VoiceStudio Assistant Service"
            Description = "AI Assistant with Voice Cloning Capabilities"
            Executable = "assistant_service.exe"
            Port = 5080
        },
        @{
            Name = "VoiceStudioVoiceCloning"
            DisplayName = "VoiceStudio Voice Cloning Service"
            Description = "Advanced Voice Cloning Engine"
            Executable = "voice_cloning_service.exe"
            Port = 5081
        },
        @{
            Name = "VoiceStudioServiceOrchestrator"
            DisplayName = "VoiceStudio Service Orchestrator"
            Description = "Service Management and Orchestration"
            Executable = "service_orchestrator.exe"
            Port = 5082
        }
    )
    
    foreach ($service in $Services) {
        try {
            $exePath = Join-Path $InstallDir $service.Executable
            if (Test-Path $exePath) {
                # Create service
                New-Service -Name $service.Name -BinaryPathName $exePath -DisplayName $service.DisplayName -Description $service.Description -StartupType Automatic | Out-Null
                Write-ColorOutput "Created service: $($service.DisplayName)" $Colors.Success
                
                # Start service
                Start-Service -Name $service.Name
                Write-ColorOutput "Started service: $($service.DisplayName)" $Colors.Success
            } else {
                Write-ColorOutput "Warning: Service executable not found: $($service.Executable)" $Colors.Warning
            }
        } catch {
            Write-ColorOutput "Error creating service $($service.Name): $($_.Exception.Message)" $Colors.Error
        }
    }
}

function Create-Shortcuts {
    Write-ColorOutput "Creating shortcuts..." $Colors.Info
    
    # Desktop shortcut
    if (${self.config['desktop_shortcut']}) {
        $DesktopPath = [Environment]::GetFolderPath("Desktop")
        $ShortcutPath = Join-Path $DesktopPath "$AppName.lnk"
        $TargetPath = Join-Path $InstallDir "voicestudio_launcher.exe"
        
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.WorkingDirectory = $InstallDir
        $Shortcut.Description = "Launch $AppName"
        $Shortcut.Save()
        
        Write-ColorOutput "Created desktop shortcut" $Colors.Success
    }
    
    # Start Menu shortcuts
    $StartMenuPath = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs"
    $AppStartMenuPath = Join-Path $StartMenuPath $StartMenuFolder
    
    if (-not (Test-Path $AppStartMenuPath)) {
        New-Item -ItemType Directory -Path $AppStartMenuPath -Force | Out-Null
    }
    
    $Shortcuts = @(
        @{
            Name = "$AppName"
            Target = "voicestudio_launcher.exe"
            Description = "Launch $AppName"
        },
        @{
            Name = "VoiceStudio Assistant"
            Target = "assistant_service.exe"
            Description = "AI Assistant with Voice Cloning"
        },
        @{
            Name = "Voice Cloning Studio"
            Target = "voice_cloner.exe"
            Description = "Voice Cloning Application"
        },
        @{
            Name = "Service Dashboard"
            Target = "service_dashboard.exe"
            Description = "Service Management Dashboard"
        },
        @{
            Name = "Uninstall $AppName"
            Target = "uninstall.ps1"
            Description = "Uninstall $AppName"
        }
    )
    
    foreach ($shortcut in $Shortcuts) {
        $ShortcutPath = Join-Path $AppStartMenuPath "$($shortcut.Name).lnk"
        $TargetPath = Join-Path $InstallDir $shortcut.Target
        
        if (Test-Path $TargetPath) {
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
            $Shortcut.TargetPath = $TargetPath
            $Shortcut.WorkingDirectory = $InstallDir
            $Shortcut.Description = $shortcut.Description
            $Shortcut.Save()
            
            Write-ColorOutput "Created Start Menu shortcut: $($shortcut.Name)" $Colors.Success
        }
    }
}

function Register-ControlPanel {
    Write-ColorOutput "Registering in Control Panel..." $Colors.Info
    
    $UninstallKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\VoiceStudioUltimate"
    $UninstallerPath = Join-Path $InstallDir "uninstall.ps1"
    
    # Create registry entries
    New-Item -Path $UninstallKey -Force | Out-Null
    Set-ItemProperty -Path $UninstallKey -Name "DisplayName" -Value $AppName
    Set-ItemProperty -Path $UninstallKey -Name "DisplayVersion" -Value $AppVersion
    Set-ItemProperty -Path $UninstallKey -Name "Publisher" -Value $AppPublisher
    Set-ItemProperty -Path $UninstallKey -Name "InstallLocation" -Value $InstallDir
    Set-ItemProperty -Path $UninstallKey -Name "UninstallString" -Value "powershell.exe -ExecutionPolicy Bypass -File `"$UninstallerPath`""
    Set-ItemProperty -Path $UninstallKey -Name "URLInfoAbout" -Value $AppURL
    Set-ItemProperty -Path $UninstallKey -Name "NoModify" -Value 1
    Set-ItemProperty -Path $UninstallKey -Name "NoRepair" -Value 1
    
    Write-ColorOutput "Registered in Control Panel" $Colors.Success
}

function Pin-ToTaskbar {
    Write-ColorOutput "Pinning to taskbar..." $Colors.Info
    
    try {
        $TargetPath = Join-Path $InstallDir "voicestudio_launcher.exe"
        $TaskbarPath = "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"
        
        if (-not (Test-Path $TaskbarPath)) {
            New-Item -ItemType Directory -Path $TaskbarPath -Force | Out-Null
        }
        
        $ShortcutPath = Join-Path $TaskbarPath "$AppName.lnk"
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.WorkingDirectory = $InstallDir
        $Shortcut.Description = "Launch $AppName"
        $Shortcut.Save()
        
        Write-ColorOutput "Pinned to taskbar" $Colors.Success
    } catch {
        Write-ColorOutput "Warning: Could not pin to taskbar" $Colors.Warning
    }
}

function Launch-VoiceStudio {
    Write-ColorOutput "Launching VoiceStudio..." $Colors.Info
    
    $LauncherPath = Join-Path $InstallDir "voicestudio_launcher.exe"
    if (Test-Path $LauncherPath) {
        Start-Process -FilePath $LauncherPath -WorkingDirectory $InstallDir
        Write-ColorOutput "VoiceStudio launched successfully!" $Colors.Success
    } else {
        Write-ColorOutput "Error: Launcher not found" $Colors.Error
    }
}

function Uninstall-VoiceStudio {
    Write-ColorOutput "Uninstalling $AppName..." $Colors.Info
    
    # Check if running as administrator
    if (-not (Test-Administrator)) {
        Write-ColorOutput "This uninstaller requires administrator privileges." $Colors.Error
        Write-ColorOutput "Please run PowerShell as Administrator and try again." $Colors.Error
        exit 1
    }
    
    # Stop and remove services
    $Services = @("VoiceStudioAssistant", "VoiceStudioVoiceCloning", "VoiceStudioServiceOrchestrator")
    foreach ($serviceName in $Services) {
        try {
            if (Get-Service -Name $serviceName -ErrorAction SilentlyContinue) {
                Stop-Service -Name $serviceName -Force
                Remove-Service -Name $serviceName
                Write-ColorOutput "Removed service: $serviceName" $Colors.Success
            }
        } catch {
            Write-ColorOutput "Warning: Could not remove service $serviceName" $Colors.Warning
        }
    }
    
    # Remove shortcuts
    $DesktopPath = [Environment]::GetFolderPath("Desktop")
    $DesktopShortcut = Join-Path $DesktopPath "$AppName.lnk"
    if (Test-Path $DesktopShortcut) {
        Remove-Item $DesktopShortcut -Force
        Write-ColorOutput "Removed desktop shortcut" $Colors.Success
    }
    
    # Remove Start Menu shortcuts
    $StartMenuPath = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs"
    $AppStartMenuPath = Join-Path $StartMenuPath $StartMenuFolder
    if (Test-Path $AppStartMenuPath) {
        Remove-Item $AppStartMenuPath -Recurse -Force
        Write-ColorOutput "Removed Start Menu shortcuts" $Colors.Success
    }
    
    # Remove taskbar pin
    $TaskbarPath = "$env:APPDATA\Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar"
    $TaskbarShortcut = Join-Path $TaskbarPath "$AppName.lnk"
    if (Test-Path $TaskbarShortcut) {
        Remove-Item $TaskbarShortcut -Force
        Write-ColorOutput "Removed taskbar pin" $Colors.Success
    }
    
    # Remove Control Panel entry
    $UninstallKey = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\VoiceStudioUltimate"
    if (Test-Path $UninstallKey) {
        Remove-Item $UninstallKey -Recurse -Force
        Write-ColorOutput "Removed Control Panel entry" $Colors.Success
    }
    
    # Remove installation directory
    if (Test-Path $InstallDir) {
        Remove-Item $InstallDir -Recurse -Force
        Write-ColorOutput "Removed installation directory" $Colors.Success
    }
    
    Write-ColorOutput "`n$AppName uninstalled successfully!" $Colors.Success
}

# Main execution
if ($Uninstall) {
    Uninstall-VoiceStudio
} else {
    Install-VoiceStudio
}
