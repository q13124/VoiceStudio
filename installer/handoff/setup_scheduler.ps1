#!/usr/bin/env powershell
# VoiceStudio Auto Handoff Windows Task Scheduler Setup
# Creates a scheduled task to run Auto Handoff every 15 minutes

param(
    [switch]$Remove,
    [string]$TaskName = "VoiceStudio Auto Handoff"
)

$ErrorActionPreference = "Stop"

if ($Remove) {
    Write-Host "Removing scheduled task: $TaskName"
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Scheduled task removed successfully"
    } catch {
        Write-Warning "Failed to remove scheduled task: $($_.Exception.Message)"
    }
    exit 0
}

Write-Host "Creating scheduled task: $TaskName"

# Create the action
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\VoiceStudio\tools\VS-AutoHandoff.ps1 -SkipBuild -LightSBOM"

# Create the trigger (every 15 minutes)
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration ([TimeSpan]::MaxValue)

# Create task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Builds VoiceStudio Cursor handoff every 15m" -User "$env:USERNAME" -RunLevel Highest
    Write-Host "Scheduled task created successfully"
    Write-Host "Task will run every 15 minutes starting in 1 minute"
    Write-Host "To remove: powershell -ExecutionPolicy Bypass -File $($MyInvocation.MyCommand.Path) -Remove"
} catch {
    Write-Error "Failed to create scheduled task: $($_.Exception.Message)"
    exit 1
}
