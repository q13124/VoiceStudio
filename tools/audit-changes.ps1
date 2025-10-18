param(
  [string]$Since = "2 weeks ago"
)

$ErrorActionPreference = "SilentlyContinue"
$OutDir = Join-Path (Get-Location) "logs"
if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }
$Report = Join-Path $OutDir "change-audit.md"

function Safe { param([scriptblock]$b) try { & $b } catch { $null } }

# Create content using array and join
$lines = @()
$lines += "# VoiceStudio Change Audit"
$lines += "Generated: $(Get-Date -Format s)"
$lines += "Repo: $(Get-Location)"
$lines += ""

# Git status & since
$git = Safe { git --version }
if ($git) {
  $lines += "## Git status"
  $lines += "``````"
  $gitStatus = Safe { git status -s }
  if ($gitStatus) { $lines += $gitStatus }
  $lines += "``````"
  $lines += ""

  $lines += "## Commits since '$Since'"
  $lines += "``````"
  $gitLog = Safe { (& git log --since="$Since" --oneline) }
  if ($gitLog) { $lines += $gitLog }
  $lines += "``````"
  $lines += ""

  $lines += "## Diff summary since '$Since'"
  $lines += "``````"
  $gitDiff = Safe { git diff --stat -- ':services/*' ':tools/*' ':config/*' }
  if ($gitDiff) { $lines += $gitDiff }
  $lines += "``````"
  $lines += ""
} else {
  $lines += "> Git not available — using filesystem inventory only."
  $lines += ""
}

# Inventory of touched areas
$areas = @(
  "services",
  "tools",
  "config"
)
$lines += "## File inventory (services/, tools/, config/)"
foreach ($a in $areas) {
  $p = Join-Path (Get-Location) $a
  if (Test-Path $p) {
    $lines += "### $a"
    $files = Get-ChildItem $p -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object FullName,LastWriteTime,Length
    $lines += "``````"
    $files | ForEach-Object {
      $rel = $_.FullName.Replace((Get-Location).Path + "\","").Replace("\","/")
      $lines += ("{0,-60}  {1,20}  {2,10:n0}" -f $rel, $_.LastWriteTime, $_.Length)
    }
    $lines += "``````"
    $lines += ""
  } else {
    $lines += "### $a"
    $lines += "Directory not found"
    $lines += ""
  }
}

# Endpoints check
function Ping($url){
  try {
    $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 2
    return @{ url=$url; status=$r.StatusCode; body=($r.Content | Out-String).Substring(0, [Math]::Min(160, ($r.Content | Out-String).Length)) }
  } catch {
    return @{ url=$url; status=0; body="$($_.Exception.Message)" }
  }
}
$lines += "## Endpoint health"
$checks = @(
  "http://127.0.0.1:5080/health",
  "http://127.0.0.1:5080/autofix/status",
  "http://127.0.0.1:5080/discovery",
  "http://127.0.0.1:5080/metrics",
  "http://127.0.0.1:5081/health",
  "http://127.0.0.1:5081/status",
  "http://127.0.0.1:5090/health",
  "http://127.0.0.1:5090/settings",
  "http://127.0.0.1:5090/weights"
) | ForEach-Object { Ping $_ }
$lines += "``````"
foreach ($check in $checks) {
  $lines += ("{0}  ->  {1}  {2}" -f $check.url, $check.status, $check.body)
}
$lines += "``````"

Set-Content -Encoding UTF8 $Report ($lines -join [Environment]::NewLine)
Write-Host "Wrote $Report" -ForegroundColor Green