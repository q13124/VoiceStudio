# VoiceStudio Ultimate - File Preservation Script
param(
    [string]$BackupDir = "$env:ProgramData\VoiceStudio\backups"
)

Write-Host "VoiceStudio Ultimate - File Preservation System" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Create backup directory
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
Write-Host "Backup directory: $BackupDir" -ForegroundColor Green

# Define essential files
$EssentialFiles = @{
    "TtsOptionsViewModel.cs"       = "VoiceStudioWinUI\ViewModels\TtsOptionsViewModel.cs"
    "MasteringRackControl.xaml"    = "VoiceStudioWinUI\Controls\MasteringRackControl.xaml"
    "MasteringRackControl.xaml.cs" = "VoiceStudioWinUI\Controls\MasteringRackControl.xaml.cs"
    "MasteringRackPage.xaml"       = "VoiceStudioWinUI\Pages\MasteringRackPage.xaml"
    "MasteringRackPage.xaml.cs"    = "VoiceStudioWinUI\Pages\MasteringRackPage.xaml.cs"
    "Generate-SBOM.ps1"            = "scripts\Generate-SBOM.ps1"
    "DashboardPage.xaml"           = "VoiceStudioWinUI\Pages\DashboardPage.xaml"
    "DashboardPage.xaml.cs"        = "VoiceStudioWinUI\Pages\DashboardPage.xaml.cs"
    "MainWindow.xaml"              = "VoiceStudioWinUI\MainWindow.xaml"
    "MainWindow.xaml.cs"           = "VoiceStudioWinUI\MainWindow.xaml.cs"
    "App.xaml"                     = "VoiceStudioWinUI\App.xaml"
    "Implementation_Complete.md"   = "VOICESTUDIO_IMPLEMENTATION_COMPLETE.md"
    "File_Preservation_Rules.md"   = "VOICESTUDIO_FILE_PRESERVATION_RULES.md"
    "Build_Instructions.md"        = ".cursor\tasks\bind-ui-and-sbom.md"
}

$BackupCount = 0
$MissingCount = 0
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "Preserving Essential Files..." -ForegroundColor Yellow

foreach ($backupName in $EssentialFiles.Keys) {
    $filePath = $EssentialFiles[$backupName]
    $fullPath = Join-Path (Get-Location) $filePath

    if (Test-Path $fullPath) {
        try {
            $backupPath = Join-Path $BackupDir "${Timestamp}_${backupName}"
            Copy-Item $fullPath $backupPath -Force
            $BackupCount++
            Write-Host "Preserved: $backupName" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to backup: $backupName" -ForegroundColor Red
        }
    }
    else {
        $MissingCount++
        Write-Host "Missing: $backupName" -ForegroundColor Yellow
    }
}

Write-Host "Preservation Summary:" -ForegroundColor Cyan
Write-Host "Files Preserved: $BackupCount" -ForegroundColor Green
Write-Host "Files Missing: $MissingCount" -ForegroundColor Yellow
Write-Host "Backup Location: $BackupDir" -ForegroundColor Blue

Write-Host "PRESERVATION COMPLETE!" -ForegroundColor Green
