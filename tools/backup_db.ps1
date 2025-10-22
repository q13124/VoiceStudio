# tools/backup_db.ps1 — quick backup/restore
param([ValidateSet("backup","restore")][string]$Mode="backup",[string]$Path="voicestudio.db")
$ErrorActionPreference='Stop'
$pd = Join-Path $env:ProgramData "VoiceStudio"
$src = Join-Path $pd $Path
$bak = Join-Path $pd ("backup_"+(Get-Date -Format yyyyMMdd_HHmmss)+"_"+$Path)
if($Mode -eq "backup"){ Copy-Item $src $bak -Force; Write-Host "Backup -> $bak" }
else { Copy-Item $Path $src -Force; Write-Host "Restored $Path -> $src" }