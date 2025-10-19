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

function Ensure-Tool($tool) {
  $null = Get-Command $tool -ErrorAction SilentlyContinue
  if (-not $?) { throw "Required tool not found: $tool" }
}

function Ensure-PipPackage {
  param(
    [Parameter(Mandatory=$true)][string]$name,
    [string]$version
  )
  Ensure-Tool -tool "python3"
  Ensure-Tool -tool "pip3"
  $spec = $name
  if ($version) { $spec = "$name==$version" }
  # Check if installed with exact version when provided
  if ($version) {
    $isInstalled = python3 - <<'PY'
import importlib.metadata, sys
pkg, ver = sys.argv[1].split('==', 1)
try:
    found = importlib.metadata.version(pkg)
    print('OK' if found==ver else 'MISMATCH')
except importlib.metadata.PackageNotFoundError:
    print('MISSING')
PY
    $isInstalled = & python3 - "$spec"
    if ($isInstalled -match '^OK$') { Write-Host "Package $spec already installed"; return }
  } else {
    $check = & python3 - <<'PY'
import importlib.util, sys
name = sys.argv[1]
print('OK' if importlib.util.find_spec(name) else 'MISSING')
PY
    $check = & python3 - "$name"
    if ($check -match '^OK$') { Write-Host "Package $name present"; return }
  }
  Write-Host "Installing $spec"
  & pip3 install "$spec" --upgrade --disable-pip-version-check
  if ($LASTEXITCODE -ne 0) { throw "pip install failed for $spec" }
}

function Get-FileSha256([string]$Path) {
  if (-not (Test-Path $Path)) { return $null }
  $hash = Get-FileHash -Path $Path -Algorithm SHA256
  return $hash.Hash.ToLowerInvariant()
}

function Ensure-ModelAsset {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [Parameter(Mandatory=$true)][string]$Destination,
    [string]$Sha256
  )
  $destPath = $Destination
  $destDir = Split-Path -Parent $destPath
  if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Force -Path $destDir | Out-Null }
  $needDownload = $true
  if (Test-Path $destPath) {
    if ($Sha256) {
      $existing = Get-FileSha256 -Path $destPath
      if ($existing -eq $Sha256.ToLowerInvariant()) { Write-Host "Model up-to-date at $destPath"; $needDownload = $false }
    } else {
      Write-Host "Model exists at $destPath (no hash provided)"; $needDownload = $false
    }
  }
  if ($needDownload) {
    Ensure-Tool -tool "curl"
    Write-Host "Downloading model from $Url"
    & curl -L "$Url" -o "$destPath"
    if ($LASTEXITCODE -ne 0) { throw "Download failed: $Url" }
    if ($Sha256) {
      $dlHash = Get-FileSha256 -Path $destPath
      if ($dlHash -ne $Sha256.ToLowerInvariant()) { throw "SHA256 mismatch for $destPath" }
    }
    Write-Host "Model ready at $destPath"
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
  
  # Optional: pip packages installation (idempotent)
  if ($obj.packages) {
    foreach ($pkg in $obj.packages) {
      $name = $null; $version = $null
      if ($pkg -is [string]) {
        if ($pkg -match '^(?<n>[^=<>!~]+)==(?<v>[^\s]+)$') { $name = $matches['n'].Trim(); $version = $matches['v'].Trim() }
        else { $name = $pkg.Trim() }
      } elseif ($pkg.PSObject.Properties.Name -contains 'name') {
        $name = [string]$pkg.name
        if ($pkg.PSObject.Properties.Name -contains 'version') { $version = [string]$pkg.version }
      }
      if (-not $name) { Write-Warning "Ignoring invalid package entry: $pkg"; continue }
      Ensure-PipPackage -name $name -version $version
    }
  }

  # Optional: model assets (download + hash verify; idempotent)
  if ($obj.models) {
    foreach ($m in $obj.models) {
      if (-not ($m.PSObject.Properties.Name -contains 'url' -and $m.PSObject.Properties.Name -contains 'dest')) {
        Write-Warning "Model entry missing url/dest: $m"; continue
      }
      $url = [string]$m.url
      $dest = [string]$m.dest
      $sha = $null
      if ($m.PSObject.Properties.Name -contains 'sha256') { $sha = [string]$m.sha256 }
      Ensure-ModelAsset -Url $url -Destination $dest -Sha256 $sha
    }
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
