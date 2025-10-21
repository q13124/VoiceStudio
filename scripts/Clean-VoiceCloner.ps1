# scripts\Clean-VoiceCloner.ps1
# Safe, reversible cleanup for voice-cloner junk (Audit first; Clean optional)
[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [switch]$CleanNow
)

$ErrorActionPreference = 'Stop'

function Resolve-KeepRoot {
  $candidates = @('C:\VoiceStudio', 'C:\TylersVoiceCloner')
  foreach ($p in $candidates) { if (Test-Path $p) { return (Resolve-Path $p).Path } }
  throw "No active project root found. Create C:\VoiceStudio or C:\TylersVoiceCloner first."
}

$KEEP_ROOT = Resolve-KeepRoot
$QUARANTINE = 'C:\_Quarantine\VoiceClonerCleanup'
$REPORT_DIR = Join-Path $KEEP_ROOT 'reports\cleanup'
$LOG_PATH = Join-Path ([IO.Path]::GetTempPath()) 'vc_cleanup.log'
$CLEAN_NOW = [bool]$CleanNow

# Create dirs
$null = New-Item -ItemType Directory -Force -Path $REPORT_DIR, $QUARANTINE | Out-Null
"[$(Get-Date -Format s)] KEEP_ROOT=$KEEP_ROOT  CLEAN_NOW=$CLEAN_NOW" | Add-Content $LOG_PATH

# Canonical do-not-touch rules
$DoNotTouch = @(
  "$KEEP_ROOT\**",
  "$env:APPDATA\UltraClone\profiles\**",
  "$env:APPDATA\UltraClone\projects\**",
  "$env:APPDATA\UltraClone\output\**",
  "$env:APPDATA\UltraClone\settings.json",
  "$env:APPDATA\UltraClone\plugins\**"
)

# Junk candidate patterns (scan entire C: drive)
$CandidateRoots = @(
  'C:\',
  'C:\Program Files*',
  'C:\Program Files (x86)*',
  'C:\ProgramData*',
  'C:\Users\*\AppData\Local*',
  'C:\Users\*\AppData\Roaming*',
  'C:\Users\*\Desktop*',
  'C:\Users\*\Documents*',
  'C:\Users\*\Downloads*',
  'C:\tools*',
  'C:\_Dev*',
  'C:\_Models*',
  'C:\temp*',
  'C:\tmp*'
)

$EngineNames = @(
  'piper', 'bark', 'tortoise', 'rvc', 'coqui', 'so-vits', 'xtts', 'tortoise-tts', 'openvoice', 'gpt-sovits',
  'voice-clone', 'voiceclone', 'voice_clone', 'voicecloning', 'voice-cloning', 'voice_cloning',
  'real-time-voice-clone', 'real_time_voice_clone', 'rtvc', 'voice-conversion', 'voice_conversion',
  'voice-synthesis', 'voice_synthesis', 'neural-voice', 'neural_voice', 'voice-ai', 'voice_ai',
  'speech-synthesis', 'speech_synthesis', 'tts', 'text-to-speech', 'text_to_speech',
  'voice-mimic', 'voice_mimic', 'voice-copy', 'voice_copy', 'voice-replication', 'voice_replication',
  'ultraclone', 'ultra-clone', 'ultra_clone', 'voicestudio', 'voice-studio', 'voice_studio',
  'tylersvoicecloner', 'tylers-voice-cloner', 'tylers_voice_cloner'
)

# Gather candidates
$items = New-Object System.Collections.Generic.List[object]
foreach ($root in $CandidateRoots) {
  Get-ChildItem -Path $root -ErrorAction SilentlyContinue -Force | ForEach-Object {
    $full = $_.FullName
    if ($full -like "$KEEP_ROOT*") { return } # keep active tree

    # Heuristics: engine/tool dirs, old copies, temp builds, venvs
    $isEngine = $false
    foreach ($engine in $EngineNames) {
      if ($full -imatch $engine) {
        $isEngine = $true
        break
      }
    }
    $looksLikeOldCopy = ($full -match 'VoiceStudio|UltraClone|TylersVoiceCloner|VoiceClone|VoiceCloner') -and ($full -match '\.old|\.bak|backup|copy|_old|_backup|_copy')
    $isVenv = (Test-Path (Join-Path $full 'Scripts\Activate.ps1')) -or (Test-Path (Join-Path $full 'pyvenv.cfg'))
    $isBuild = ($full -match '\\(bin|obj|dist|node_modules|build|__pycache__|\.git)(\\|$)')
    $isCache = ($full -match '\\(cache|temp|tmp|\.cache|\.tmp)(\\|$)') -and ($full -notlike "$env:APPDATA\UltraClone\output*")
    $isPythonEnv = ($full -match '\\(venv|env|\.venv|\.env|virtualenv)(\\|$)')
    $isModelDir = ($full -match '\\(models|checkpoints|weights|pretrained)(\\|$)') -and ($full -imatch 'voice|speech|tts|audio')

    if ($isEngine -or $looksLikeOldCopy -or $isVenv -or $isBuild -or $isCache -or $isPythonEnv -or $isModelDir) {
      $size = 0
      try { $size = (Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue -LiteralPath $full | Measure-Object -Property Length -Sum).Sum } catch {}
      $items.Add([PSCustomObject]@{
          Path   = $full
          Reason = "detected"
          Bytes  = $size
          Action = "Quarantine"
        })
    }
  }
}

# Filter with DoNotTouch
$ShouldKeep = {
  param($path)
  foreach ($rule in $DoNotTouch) {
    if ([System.Management.Automation.WildcardPattern]::Escape($path) -like $rule.Replace('\**', '\*')) { return $true }
    if ($path -like $rule) { return $true }
  }
  return $false
}

$candidates = $items | Where-Object { -not (& $ShouldKeep $_.Path) } | Sort-Object -Property Bytes -Descending

# PATH / Services / Tasks audit
$EnvDelta = [ordered]@{
  PATH_Remove      = @()
  Services_Disable = @()
  Tasks_Disable    = @()
}

# PATH audit
$pathParts = ($env:PATH -split ';') | Where-Object { $_ -and (Test-Path $_) }
foreach ($p in $pathParts) {
  if ($p -like "$KEEP_ROOT*") { continue }
  if ($EngineNames | Where-Object { $p -imatch $_ }) {
    $EnvDelta.PATH_Remove += $p
  }
}

# Services audit
Get-Service | Where-Object {
  $_.Name -imatch 'UltraClone|VoiceStudio|vsdml|piper|coqui|so-vits|tortoise|rvc'
} | ForEach-Object {
  if ($_.Status -ne 'Running') { $EnvDelta.Services_Disable += $_.Name }
}

# Scheduled Tasks audit
Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
  $_.TaskName -imatch 'UltraClone|VoiceStudio|vsdml|piper|coqui|so-vits|tortoise|rvc'
} | ForEach-Object {
  $EnvDelta.Tasks_Disable += $_.TaskName
}

# Write audit reports
$csv = Join-Path $REPORT_DIR 'Audit-VoiceCloner.csv'
$txt = Join-Path $REPORT_DIR 'Audit-VoiceCloner.txt'
$json = Join-Path $REPORT_DIR 'Environment-Delta.json'
$candidates | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $csv
$candidates | Format-Table -AutoSize | Out-String | Set-Content -Encoding UTF8 -Path $txt
($EnvDelta | ConvertTo-Json -Depth 6) | Set-Content -Encoding UTF8 -Path $json

Write-Host "`n=== AUDIT COMPLETE ==="
Write-Host "Keep Root: $KEEP_ROOT"
Write-Host "Candidates: $($candidates.Count)"
Write-Host "CSV: $csv"
Write-Host "TXT: $txt"
Write-Host "Env Delta: $json"
Write-Host "Log: $LOG_PATH"
if (-not $CLEAN_NOW) {
  Write-Host "`nDry-run only. Re-run with:  powershell -ExecutionPolicy Bypass -File `"$PSCommandPath`" -CleanNow"
  exit 0
}

# === CLEAN EXECUTION (Quarantine) ===
function Move-ToQuarantine {
  param([string]$path)
  $rel = $path -replace '^[A-Za-z]:\\', ''
  $dest = Join-Path $QUARANTINE $rel
  $null = New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
  try {
    if (Test-Path $dest) { Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $dest }
    Move-Item -LiteralPath $path -Destination $dest -Force
    "[$(Get-Date -Format s)] MOVED -> $dest" | Add-Content $LOG_PATH
    return $dest
  }
  catch {
    "[$(Get-Date -Format s)] MOVE-FAIL $path : $_" | Add-Content $LOG_PATH
    return $null
  }
}

$Moved = @()
foreach ($entry in $candidates) {
  $p = $entry.Path
  if (-not (Test-Path $p)) { continue }
  if ($PSCmdlet.ShouldProcess($p, 'Quarantine')) {
    $dest = Move-ToQuarantine -path $p
    if ($dest) { $Moved += [PSCustomObject]@{ Source = $p; Dest = $dest; Reason = $entry.Reason } }
  }
}

# Apply env changes
$UndoScript = Join-Path (Split-Path $PSCommandPath -Parent) 'Undo-Clean.ps1'
$undo = @()
# PATH remove (user-level)
if ($EnvDelta.PATH_Remove.Count -gt 0) {
  $old = [Environment]::GetEnvironmentVariable('Path', 'User')
  $new = ($old -split ';' | Where-Object { $_ -and ($EnvDelta.PATH_Remove -notcontains $_) }) -join ';'
  [Environment]::SetEnvironmentVariable('Path', $new, 'User')
  $undo += "[Environment]::SetEnvironmentVariable('Path', '$old','User')"
}

# Disable services (store prior state)
foreach ($svc in $EnvDelta.Services_Disable) {
  try {
    $prior = (Get-Service $svc).Status
    if ($prior -eq 'Running') { Stop-Service $svc -Force -ErrorAction SilentlyContinue }
    Set-Service $svc -StartupType Disabled
    $undo += "Set-Service '$svc' -StartupType Manual"
  }
  catch {}
}

# Disable tasks
foreach ($t in $EnvDelta.Tasks_Disable) {
  try {
    Disable-ScheduledTask -TaskName $t -ErrorAction SilentlyContinue | Out-Null
    $undo += "Enable-ScheduledTask -TaskName '$t' | Out-Null"
  }
  catch {}
}

# Write Undo script
@"
# scripts\Undo-Clean.ps1
# Restores PATH/services/tasks and moves files back from quarantine.
`$ErrorActionPreference = 'Stop'
# Restore PATH/services/tasks:
$($undo -join [Environment]::NewLine)

# Restore files:
`$pairs = @(
$($Moved | ForEach-Object { "  @{ Source = '$($_.Dest)'; Dest = '$($_.Source)' }" } -join [Environment]::NewLine)
)
foreach (`$pair in `$pairs) {
  `$src = `$pair.Source; `$dst = `$pair.Dest
  if (Test-Path `$src) {
    if (-not (Test-Path (Split-Path `$dst))) { New-Item -ItemType Directory -Force -Path (Split-Path `$dst) | Out-Null }
    Move-Item -LiteralPath `$src -Destination `$dst -Force
  }
}
"@ | Set-Content -Encoding UTF8 -Path $UndoScript

Write-Host "`n=== CLEAN COMPLETE ==="
Write-Host "Moved: $($Moved.Count) -> Quarantine: $QUARANTINE"
Write-Host "Undo script: $UndoScript"
Write-Host "You may need to restart your shell or log off/on for PATH changes."
