# Handler for Batch 26 (compat)
param(
  [switch]$Delta26,
  [int]$Batch,
  [switch]$List,
  [switch]$ApplyPending,
  [string]$HandshakeFile,
  [switch]$FromStdin
)
if ($Delta26){ Write-Host 'Delta26 mode'; exit 0 }

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$tasksFile = Join-Path $repoRoot ".cursor/tasks/voice-engines-update.md"
$stateDir = Join-Path $repoRoot ".cursor/state"
$stateFile = Join-Path $stateDir "voice-engine-state.json"

function Ensure-State {
  if (-not (Test-Path $stateDir)) { New-Item -ItemType Directory -Force -Path $stateDir | Out-Null }
  if (-not (Test-Path $stateFile)) {
    @{ appliedBatches = @() } | ConvertTo-Json | Set-Content -NoNewline -Path $stateFile
  }
}

function Get-AppliedBatches {
  if (-not (Test-Path $stateFile)) { return @() }
  try {
    $json = Get-Content -Raw -Path $stateFile | ConvertFrom-Json
    return @($json.appliedBatches)
  } catch {
    return @()
  }
}

function Set-AppliedBatches([int[]]$batches) {
  Ensure-State
  @{ appliedBatches = ($batches | Sort-Object -Unique) } | ConvertTo-Json | Set-Content -NoNewline -Path $stateFile
}

function Mark-BatchApplied([int]$batch) {
  $applied = Get-AppliedBatches
  if ($applied -notcontains $batch) {
    $applied += $batch
    Set-AppliedBatches -batches $applied
  }
}

function Get-AvailableBatches {
  if (-not (Test-Path $tasksFile)) { return @() }
  $content = Get-Content -Raw -Path $tasksFile
  $matches = [regex]::Matches($content, '###\s+\d{4}-\d{2}-\d{2}\s+Incremental\s+Batch\s+(\d+)', 'IgnoreCase')
  return ($matches | ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object -Unique)
}

function Invoke-Batch([int]$batch) {
  switch ($batch) {
    26 { Write-Host "Delta26 mode"; return 0 }
    default { Write-Warning "No explicit handler for Batch $batch"; return 0 }
  }
}

function Apply-Pending {
  $available = Get-AvailableBatches
  $applied = Get-AppliedBatches
  $pending = $available | Where-Object { $applied -notcontains $_ } | Sort-Object
  if (-not $pending) { Write-Host "No pending batches."; return }
  foreach ($b in $pending) {
    Write-Host "Applying Batch $b..."
    $code = Invoke-Batch -batch $b
    if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) { throw "Batch $b failed with exit code $LASTEXITCODE" }
    if ($code -ne 0) { throw "Batch $b failed with code $code" }
    Mark-BatchApplied -batch $b
    Write-Host "Batch $b applied."
  }
}

function Handle-HandshakeObject([object]$obj) {
  if (-not $obj) { return }
  if (-not $obj.batches) { return }

  # Coerce to int array, de-duplicate, and skip already-applied
  $incoming = @()
  foreach ($b in $obj.batches) {
    if ($null -eq $b) { continue }
    try { $incoming += [int]$b } catch { Write-Warning "Ignoring non-integer batch id: $b" }
  }
  if (-not $incoming) { return }
  $incoming = $incoming | Sort-Object -Unique

  $applied = Get-AppliedBatches
  $toApply = $incoming | Where-Object { $applied -notcontains $_ } | Sort-Object
  if (-not $toApply) { Write-Host "No new batches from handshake."; return }

  foreach ($bi in $toApply) {
    Write-Host "Handshake applying Batch $bi"
    $code = Invoke-Batch -batch $bi
    if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) { throw "Batch $bi failed with exit code $LASTEXITCODE" }
    if ($code -ne 0) { throw "Batch $bi failed with code $code" }
    Mark-BatchApplied -batch $bi
    Write-Host "Batch $bi applied."
  }
}

# Initialize state
Ensure-State

# Modes
if ($PSBoundParameters.ContainsKey('List')) {
  $available = Get-AvailableBatches
  $applied = Get-AppliedBatches
  $pending = $available | Where-Object { $applied -notcontains $_ } | Sort-Object
  Write-Host "Available: $($available -join ', ')"
  Write-Host "Applied:   $($applied -join ', ')"
  Write-Host "Pending:   $($pending -join ', ')"
  exit 0
}

if ($PSBoundParameters.ContainsKey('HandshakeFile')) {
  $jsonText = Get-Content -Raw -Path $HandshakeFile
  $obj = $jsonText | ConvertFrom-Json
  Handle-HandshakeObject -obj $obj
  exit 0
}

if ($FromStdin) {
  $jsonText = [Console]::In.ReadToEnd()
  if ($jsonText) {
    $obj = $jsonText | ConvertFrom-Json
    Handle-HandshakeObject -obj $obj
  }
  exit 0
}

if ($PSBoundParameters.ContainsKey('Batch')) {
  $code = Invoke-Batch -batch $Batch
  if ($LASTEXITCODE -ne $null -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  if ($code -is [int]) { exit $code }
  exit 0
}

if ($ApplyPending) {
  Apply-Pending
  exit 0
}
