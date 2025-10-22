#requires -Version 5.1
<# 
  OVERSEER_Run.ps1 — One‑shot runner for the [OVERSEER] 15‑minute report
  - Validates overseer_config.yaml location
  - Collects local signals (git, ports, tunnel, GPU)
  - Prints a sample report and saves a markdown snapshot
  Usage:
    powershell -ExecutionPolicy Bypass -File .\OVERSEER_Run.ps1 [-ConfigPath .\overseer_config.yaml]
#>

param(
  [string]$ConfigPath = ".\overseer_config.yaml"
)

$ErrorActionPreference = 'SilentlyContinue'

function Write-Section($title) {
  $hr = ('-' * 70)
  Write-Host "`n## $title`n$hr"
}

function Get-RepoRoot([string]$startPath) {
  try {
    $d = Resolve-Path -Path $startPath | Select-Object -ExpandProperty Path
  } catch { $d = (Get-Location).Path }
  $dir = Get-Item -Path $d -ErrorAction SilentlyContinue
  while ($dir -and -not (Test-Path (Join-Path $dir.FullName '.git'))) {
    $parent = $dir.Parent
    if (-not $parent) { break }
    $dir = $parent
  }
  if ($dir -and (Test-Path (Join-Path $dir.FullName '.git'))) { return $dir.FullName }
  return $null
}

function Try-Run($label, [scriptblock]$action) {
  Write-Host "`n[$label]"
  try { & $action } catch { "ERR: $($_.Exception.Message)" }
}

function Read-YamlLoose([string]$path) {
  # Minimal, line-based YAML reader for simple key: value pairs (no nesting arrays parsed beyond one level of indentation)
  $result = @{}
  if (-not (Test-Path $path)) { return $result }
  $lines = Get-Content -Path $path -Raw -ErrorAction SilentlyContinue -Encoding UTF8 -Delimiter "`n" -TotalCount 10000
  $currentSection = $null
  foreach ($line in $lines -split "`n") {
    $trim = $line.Trim()
    if ($trim -match '^\s*#') { continue }
    if ($trim -match '^\s*$') { continue }
    if ($trim -match '^([A-Za-z0-9_]+):\s*$') {
      $currentSection = $matches[1]
      if (-not $result.ContainsKey($currentSection)) { $result[$currentSection] = @{} }
      continue
    }
    if ($trim -match '^([A-Za-z0-9_]+):\s*(.+)$') {
      $k = $matches[1]; $v = $matches[2]
      if ($currentSection -and ($result[$currentSection] -is [hashtable])) {
        $result[$currentSection][$k] = $v.Trim('"')
      } else {
        $result[$k] = $v.Trim('"')
      }
    }
  }
  return $result
}

# 0) Determine repo root and check config placement
$cwd = (Get-Location).Path
$repoRoot = Get-RepoRoot $cwd
$configResolved = Resolve-Path -Path $ConfigPath -ErrorAction SilentlyContinue | ForEach-Object { $_.Path }

$CONFIG_OK = $false
$configMsg = ""
if ($configResolved) {
  if ($repoRoot) {
    if ((Split-Path -Path $configResolved -Parent) -ieq $repoRoot) {
      $CONFIG_OK = $true
      $configMsg = "CONFIG_OK: overseer_config.yaml is in the repo root: $repoRoot"
    } else {
      $configMsg = "CONFIG_WARN: overseer_config.yaml is at '$configResolved' but repo root is '$repoRoot'. Consider moving it to repo root."
    }
  } else {
    $configMsg = "CONFIG_INFO: Repo root (.git) not found; using current directory. Config at '$configResolved'."
    $CONFIG_OK = $true
  }
} else {
  $configMsg = "CONFIG_MISSING: Could not find '$ConfigPath'. Pass -ConfigPath or place overseer_config.yaml in the repo root."
}

# 1) Parse a few keys from YAML (best-effort)
$yaml = @{}
if ($configResolved) { $yaml = Read-YamlLoose $configResolved }
$sched = if ($yaml.ContainsKey('schedule')) { $yaml['schedule'] } else { @{} }
$tz = if ($sched.ContainsKey('timezone')) { $sched['timezone'] } else { 'America/Chicago' }
$freq = if ($sched.ContainsKey('frequency')) { $sched['frequency'] } else { 'PT15M' }
$prefix = if ($sched.ContainsKey('title_prefix')) { $sched['title_prefix'] } else { '[OVERSEER]' }
$escalation = if ($yaml.ContainsKey('escalation')) { $yaml['escalation'] } else { @{} }
$tier = if ($escalation.ContainsKey('tier')) { $escalation['tier'] } else { '2' }

# 2) Collect signals
$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$commitCount = 0
$branch = Try-Run "Git Branch" { git branch --show-current }
$commits = Try-Run "Recent Commits (24h)" { git log --since="24 hours ago" --pretty=format:"%h %ad %an %s" --date=iso }
if ($commits) { $commitCount = ($commits -split "`n").Count }

$status = Try-Run "Working Copy Changes" { git status -s }
$ports = Try-Run "Listening Ports (focus 5071)" { netstat -ano | findstr LISTENING | findstr ":5071" }
$tunnelProc = Try-Run "cloudflared Process" { Get-Process cloudflared -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, Path }
$gpu = Try-Run "GPU Snapshot" { nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader -L }

# 3) Shape sample report
$report = @()
$hdr = "{0} {1} Status @ {2}" -f $prefix, "[OVERSEER DIGEST]", $ts
$report += $hdr
$report += "• Config: $configMsg"
$report += ("• Schedule: freq={0}, tz={1}, escalation_tier={2}" -f $freq, $tz, $tier)
$report += ("• Repo/Build: branch={0}; commits(24h)={1}; changes={2}" -f ($branch -join ' '), $commitCount, (($status -split "`n").Count))
$tunnel = ""
if ($tunnelProc) { $tunnel = "cloudflared running" } else { $tunnel = "no tunnel" }
$report += ("• Security/Tunnel: {0}; port5071={1}" -f $tunnel, (if($ports){'LISTENING'}else{'closed'}))
$gpus = if ($gpu) { ($gpu -split "`n")[0] } else { "no GPU info" }
$report += ("• GPU: {0}" -f $gpus)
$report += "• Next 1-3 actions: 1) Connect CI logs 2) Verify schema migrations 3) Run golden-set eval"

# 4) Output to console and save markdown snapshot
$mdName = "OVERSEER_SAMPLE_{0}.md" -f (Get-Date -Format 'yyyyMMdd_HHmmss')
$mdPath = Join-Path $cwd $mdName

"# $hdr`n`n" | Out-File -FilePath $mdPath -Encoding UTF8
"**$configMsg**`n" | Out-File -FilePath $mdPath -Append -Encoding UTF8
"**Schedule:** freq=`$freq`, tz=`$tz`, escalation_tier=`$tier`" | Out-File -FilePath $mdPath -Append -Encoding UTF8
"### Repo / Build`nBranch:`n$branch`n`nCommits (24h):`n$commits`n`nChanges:`n$status`n" | Out-File -FilePath $mdPath -Append -Encoding UTF8
"### Security / Tunnel`nPorts (5071):`n$ports`n`nTunnel process:`n$tunnelProc`n" | Out-File -FilePath $mdPath -Append -Encoding UTF8
"### GPU Snapshot`n$gpu`n" | Out-File -FilePath $mdPath -Append -Encoding UTF8
"### Next Actions`n1) Connect CI logs`n2) Verify schema migrations`n3) Run golden-set eval`n" | Out-File -FilePath $mdPath -Append -Encoding UTF8

Write-Section "OVERSEER REPORT"
$report | ForEach-Object { Write-Host $_ }

Write-Host "`nReport saved to: $mdPath"
if ($CONFIG_OK) {
  Write-Host "CONFIG_OK ✅ — overseer_config.yaml placement looks good."
} else {
  Write-Host "CONFIG_NEEDS_ATTENTION ⚠ — $configMsg"
}
