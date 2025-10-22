# VoiceStudio Ultimate - System Detection Script
param([switch]$Quiet)

$ErrorActionPreference='Stop'

function Write-Status([string]$message, [bool]$success = $true) {
    if(-not $Quiet) {
        $color = if($success) { 'Green' } else { 'Red' }
        Write-Host $message -ForegroundColor $color
    }
}

function Test-VCRedist {
    $regPath = "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
    return (Test-Path $regPath)
}

function Test-FFmpeg {
    try {
        $null = Get-Command ffmpeg -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Test-Python {
    try {
        $python = Get-Command python -ErrorAction Stop
        $version = & python --version 2>&1
        return $version -match "Python 3\.(11|12)"
    } catch {
        return $false
    }
}

function Test-CUDA {
    try {
        $cudaPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA"
        return (Test-Path $cudaPath)
    } catch {
        return $false
    }
}

function Test-SystemRequirements {
    $osVersion = [System.Environment]::OSVersion.Version
    $isWindows10OrLater = $osVersion.Major -ge 10
    
    $totalMemory = (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory
    $hasEnoughRAM = $totalMemory -ge 8000000000  # 8GB
    
    return @{
        Windows10OrLater = $isWindows10OrLater
        HasEnoughRAM = $hasEnoughRAM
        TotalRAM = [math]::Round($totalMemory / 1GB, 2)
    }
}

# Main detection
Write-Status "VoiceStudio Ultimate - System Detection" $true
Write-Status "=======================================" $true

$requirements = Test-SystemRequirements
Write-Status "Windows 10+: $($requirements.Windows10OrLater)" $requirements.Windows10OrLater
Write-Status "RAM (8GB+): $($requirements.HasEnoughRAM) ($($requirements.TotalRAM)GB)" $requirements.HasEnoughRAM

Write-Status "VC++ Redist: $(Test-VCRedist)" (Test-VCRedist)
Write-Status "FFmpeg: $(Test-FFmpeg)" (Test-FFmpeg)
Write-Status "Python 3.11+: $(Test-Python)" (Test-Python)
Write-Status "CUDA: $(Test-CUDA)" (Test-CUDA)

$allGood = $requirements.Windows10OrLater -and $requirements.HasEnoughRAM -and (Test-VCRedist) -and (Test-FFmpeg) -and (Test-Python)

if($allGood) {
    Write-Status "System ready for VoiceStudio Ultimate!" $true
    exit 0
} else {
    Write-Status "System needs updates for optimal VoiceStudio performance." $false
    exit 1
}