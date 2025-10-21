# Simple VoiceCloner Cleanup Script
param([switch]$CleanNow)

$KEEP_ROOT = "C:\Users\Tyler\VoiceStudio"
$QUARANTINE = "C:\_Quarantine\VoiceClonerCleanup"
$REPORT_DIR = Join-Path $KEEP_ROOT "reports\cleanup"

# Create directories
New-Item -ItemType Directory -Force -Path $REPORT_DIR, $QUARANTINE | Out-Null

Write-Host "=== VOICECLONER CLEANUP ==="
Write-Host "Keep Root: $KEEP_ROOT"
Write-Host "Quarantine: $QUARANTINE"

# Find candidates
$candidates = @()

# Check for duplicate VoiceStudio installations
$duplicates = @(
    "C:\TylersVoiceCloner",
    "C:\VoiceStudio",
    "C:\VoiceClone",
    "C:\VoiceCloner"
)

foreach ($dup in $duplicates) {
    if ((Test-Path $dup) -and ($dup -ne $KEEP_ROOT)) {
        $size = 0
        try {
            $size = (Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue -LiteralPath $dup | Measure-Object -Property Length -Sum).Sum
        }
        catch {}

        $candidates += [PSCustomObject]@{
            Path   = $dup
            Reason = "duplicate"
            Bytes  = $size
            Action = "Quarantine"
        }
    }
}

# Check for voice cloning engines in common locations
$enginePaths = @(
    "C:\Program Files\*voice*",
    "C:\Program Files (x86)\*voice*",
    "C:\ProgramData\*voice*",
    "C:\Users\*\AppData\Local\*voice*",
    "C:\Users\*\AppData\Roaming\*voice*"
)

foreach ($pattern in $enginePaths) {
    Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        $full = $_.FullName
        if ($full -like "$KEEP_ROOT*") { return }

        $size = 0
        try {
            $size = (Get-ChildItem -Recurse -Force -ErrorAction SilentlyContinue -LiteralPath $full | Measure-Object -Property Length -Sum).Sum
        }
        catch {}

        $candidates += [PSCustomObject]@{
            Path   = $full
            Reason = "engine"
            Bytes  = $size
            Action = "Quarantine"
        }
    }
}

Write-Host "Found $($candidates.Count) candidates for cleanup"

# Write report
$csv = Join-Path $REPORT_DIR "Audit-VoiceCloner.csv"
$txt = Join-Path $REPORT_DIR "Audit-VoiceCloner.txt"

$candidates | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $csv
$candidates | Format-Table -AutoSize | Out-String | Set-Content -Encoding UTF8 -Path $txt

Write-Host "CSV Report: $csv"
Write-Host "TXT Report: $txt"

if (-not $CleanNow) {
    Write-Host "`nDry-run complete. Run with -CleanNow to perform cleanup."
    exit 0
}

# Perform cleanup
Write-Host "`n=== PERFORMING CLEANUP ==="
$moved = @()

foreach ($candidate in $candidates) {
    $path = $candidate.Path
    if (-not (Test-Path $path)) { continue }

    $rel = $path -replace '^[A-Za-z]:\\', ''
    $dest = Join-Path $QUARANTINE $rel
    $destDir = Split-Path $dest -Parent

    try {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        if (Test-Path $dest) { Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $dest }
        Move-Item -LiteralPath $path -Destination $dest -Force
        $moved += [PSCustomObject]@{ Source = $path; Dest = $dest }
        Write-Host "Moved: $path -> $dest"
    }
    catch {
        Write-Host "Failed to move: $path - $($_.Exception.Message)"
    }
}

Write-Host "`n=== CLEANUP COMPLETE ==="
Write-Host "Moved $($moved.Count) items to quarantine: $QUARANTINE"

# Create undo script
$undoScript = Join-Path (Split-Path $PSCommandPath -Parent) "Undo-Clean.ps1"
$undoContent = @"
# Undo-Clean.ps1
# Restores files from quarantine
`$ErrorActionPreference = 'Stop'

`$pairs = @(
$($moved | ForEach-Object { "  @{ Source = '$($_.Dest)'; Dest = '$($_.Source)' }" })
)

foreach (`$pair in `$pairs) {
  `$src = `$pair.Source
  `$dst = `$pair.Dest
  if (Test-Path `$src) {
    if (-not (Test-Path (Split-Path `$dst))) {
      New-Item -ItemType Directory -Force -Path (Split-Path `$dst) | Out-Null
    }
    Move-Item -LiteralPath `$src -Destination `$dst -Force
    Write-Host "Restored: `$src -> `$dst"
  }
}
"@

$undoContent | Set-Content -Encoding UTF8 -Path $undoScript
Write-Host "Undo script created: $undoScript"
