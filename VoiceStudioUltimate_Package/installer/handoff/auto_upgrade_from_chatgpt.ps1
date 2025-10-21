#!/usr/bin/env powershell
# VoiceStudio Auto-Upgrade from ChatGPT Conversations
# Automatically applies upgrades from ChatGPT conversations

param(
    [switch]$ParseConversation,
    [switch]$ApplyUpgrades,
    [switch]$MonitorMode,
    [string]$ConversationFile = "",
    [string]$UpgradeSource = "chatgpt"
)

$ErrorActionPreference = "Stop"

# Find VoiceStudio installation
$possibleRoots = @(
    "C:\Program Files\VoiceStudio",
    "C:\VoiceStudio",
    (Split-Path $MyInvocation.MyCommand.Path -Parent)
)

$Root = $null
foreach ($possibleRoot in $possibleRoots) {
    if (Test-Path (Join-Path $possibleRoot "installer\handoff\auto_upgrade_detector.py")) {
        $Root = $possibleRoot
        break
    }
}

if (-not $Root) {
    Write-Error "VoiceStudio installation not found. Please ensure VoiceStudio is installed."
    exit 1
}

Write-Host "VoiceStudio Auto-Upgrade from ChatGPT Conversations"
Write-Host "Root: $Root"
Write-Host ""

# Parse ChatGPT conversation if requested
if ($ParseConversation -and $ConversationFile) {
    Write-Host "Parsing ChatGPT conversation: $ConversationFile"
    
    $ParserScript = Join-Path $Root "installer\handoff\chatgpt_conversation_parser.py"
    if (Test-Path $ParserScript) {
        try {
            & python $ParserScript $ConversationFile
            Write-Host "Conversation parsed successfully"
        } catch {
            Write-Error "Failed to parse conversation: $($_.Exception.Message)"
            exit 1
        }
    } else {
        Write-Error "ChatGPT conversation parser not found: $ParserScript"
        exit 1
    }
}

# Apply upgrades if requested
if ($ApplyUpgrades) {
    Write-Host "Applying detected upgrades..."
    
    $DetectorScript = Join-Path $Root "installer\handoff\auto_upgrade_detector.py"
    if (Test-Path $DetectorScript) {
        try {
            & python $DetectorScript
            Write-Host "Upgrades applied successfully"
        } catch {
            Write-Error "Failed to apply upgrades: $($_.Exception.Message)"
            exit 1
        }
    } else {
        Write-Error "Auto-upgrade detector not found: $DetectorScript"
        exit 1
    }
}

# Monitor mode - continuous monitoring for upgrades
if ($MonitorMode) {
    Write-Host "Starting continuous upgrade monitoring..."
    Write-Host "Monitoring for ChatGPT conversation files..."
    
    $UpgradesDir = Join-Path $Root "upgrades"
    $ConversationDir = Join-Path $Root "conversations"
    
    # Create directories if they don't exist
    New-Item -ItemType Directory -Force -Path $UpgradesDir, $ConversationDir | Out-Null
    
    # Monitor for new conversation files
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = $ConversationDir
    $watcher.Filter = "*.txt"
    $watcher.EnableRaisingEvents = $true
    
    $action = {
        $path = $Event.SourceEventArgs.FullPath
        $changeType = $Event.SourceEventArgs.ChangeType
        $timestamp = Get-Date
        
        Write-Host "[$timestamp] File $changeType`: $path"
        
        # Parse the new conversation file
        $ParserScript = Join-Path $Root "installer\handoff\chatgpt_conversation_parser.py"
        if (Test-Path $ParserScript) {
            try {
                & python $ParserScript $path
                Write-Host "[$timestamp] Conversation parsed: $path"
                
                # Apply upgrades
                $DetectorScript = Join-Path $Root "installer\handoff\auto_upgrade_detector.py"
                if (Test-Path $DetectorScript) {
                    & python $DetectorScript
                    Write-Host "[$timestamp] Upgrades applied from: $path"
                }
            } catch {
                Write-Warning "[$timestamp] Error processing conversation: $($_.Exception.Message)"
            }
        }
    }
    
    Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action
    
    Write-Host "Monitoring started. Press Ctrl+C to stop."
    
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        $watcher.Dispose()
        Get-EventSubscriber | Unregister-Event
    }
}

Write-Host "`nAuto-upgrade process completed!"
Write-Host "Upgrades directory: $Root\upgrades"
Write-Host "Backups directory: $Root\backups"
Write-Host "Logs directory: $Root\logs"
