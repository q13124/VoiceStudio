<#
  VS_MigrateToE.ps1

    Safe, idempotent migration of VoiceStudio from C:\VoiceStudio -> E:\VoiceStudio

    - Dry-run supported: add -ListOnly to see what would copy

    - Does NOT delete source; excludes build caches; rewrites absolute paths

    - Recreates clean venv on E:

#>

param(
  [string]$Src = "C:\VoiceStudio",
  [string]$Dst = "E:\VoiceStudio",
  [switch]$ListOnly
)

$ErrorActionPreference = "Stop"
Write-Host "[Preflight] Source: $Src  ->  Dest: $Dst"

if (!(Test-Path $Src)) { throw "Source not found: $Src" }
New-Item -ItemType Directory -Force -Path $Dst | Out-Null

# --- Disk check (needs ~20–80 GB depending on models/assets)
$drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($Dst).TrimEnd('\').TrimEnd(':'))
Write-Host ("[Disk] {0}: Free {1:N1} GB" -f $drive.Name, ($drive.Free/1GB))

# --- Excludes: caches, local venvs, build artifacts
$xd = @(
  ".git",".idea",".vs","node_modules",".venv","venv",".pytest_cache","__pycache__",
  "dist","build","out","bin","obj",".cache",".mypy_cache",".ruff_cache"
)
$xf = @("Thumbs.db","desktop.ini")

# --- Robocopy options
$opts = @("/E","/R:1","/W:1","/NFL","/NDL","/NP","/MT:16")
if ($ListOnly) { $opts += "/L" }

$xdArgs = @(); foreach($d in $xd){ $xdArgs += @("/XD", (Join-Path $Src $d)) }
$xfArgs = @(); foreach($f in $xf){ $xfArgs += @("/XF", $f) }

Write-Host "[Copy] Robocopy starting..." -ForegroundColor Yellow
robocopy $Src $Dst $opts $xdArgs $xfArgs | Out-Null
$robocopyExitCode = $LASTEXITCODE

# Robocopy exit codes: 0-7 are success, 8+ are errors
if ($robocopyExitCode -ge 8 -and -not $ListOnly) {
    Write-Host "[Copy] Robocopy error: $robocopyExitCode" -ForegroundColor Red
    throw "Robocopy error $robocopyExitCode"
} else {
    Write-Host "[Copy] Robocopy completed (exit code: $robocopyExitCode)" -ForegroundColor Green
}

if ($ListOnly) { Write-Host "[ListOnly] Done (no files copied)."; exit 0 }

# --- Create fresh venv on E: (Python 3.10+)
$py = (Get-Command py -ErrorAction SilentlyContinue)
if (!$py) { $py = (Get-Command python -ErrorAction SilentlyContinue) }
if (!$py) { throw "Python not found. Install Python 3.10+ and ensure it's on PATH." }

$venv = Join-Path $Dst ".venv"
if (Test-Path $venv) {
  Write-Host "[Venv] Removing old venv on E:..."
  Remove-Item -Recurse -Force $venv
}
Write-Host "[Venv] Creating venv..."
& $py.Source -3.10 -m venv $venv

$pex = Join-Path $venv "Scripts\python.exe"
$pip = "$pex -m pip"

# Prefer offline wheels if present
$req = @("requirements.lock.txt","requirements.txt") | ForEach-Object {
  $p = Join-Path $Dst $_; if (Test-Path $p) { $p }
} | Select-Object -First 1

Write-Host "[Pip] Upgrading pip..."
Invoke-Expression "$pip install --upgrade pip wheel"

if ($req) {
  Write-Host "[Pip] Installing from $req ..."
  Invoke-Expression "$pip install -r `"$req`""
} else {
  Write-Host "[Pip] No requirements file found. Skipping."
}

# --- Rewrite absolute paths from C:\VoiceStudio -> E:\VoiceStudio (safe for text files)
$find = [Regex]::Escape($Src)
$repl = $Dst
$targets = Get-ChildItem -Path $Dst -Recurse -File -Include *.json,*.yml,*.yaml,*.toml,*.ps1,*.psm1,*.cs,*.csproj,*.sln,*.xaml,*.md,*.py | ForEach-Object {$_.FullName}

# Additional path mappings for datasets and models
$pathMappings = @{
    "$Src\datasets" = "$Dst\library"
    "$Src\models" = "$Dst\models"
    "C:\\VoiceStudio\\datasets" = "E:\\VoiceStudio\\library"
    "C:\\VoiceStudio\\models" = "E:\\VoiceStudio\\models"
}

foreach($file in $targets){
  try {
    $txt = Get-Content -Raw -LiteralPath $file -Encoding UTF8
    $new = $txt
    
    # Replace main workspace path
    $new = [Regex]::Replace($new, $find, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $repl })
    
    # Replace dataset/model paths
    foreach($oldPath in $pathMappings.Keys) {
      $escaped = [Regex]::Escape($oldPath)
      $newPath = $pathMappings[$oldPath]
      $new = [Regex]::Replace($new, $escaped, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $newPath })
    }
    
    if ($new -ne $txt) { 
      [IO.File]::WriteAllText($file, $new, [Text.UTF8Encoding]::new($true))
      Write-Host "[PathRewrite] Updated: $file" -ForegroundColor Gray
    }
  } catch { Write-Host "[PathRewrite] Skipped (binary or locked): $file" -ForegroundColor Yellow }
}
Write-Host "[PathRewrite] Path updates complete" -ForegroundColor Green

# --- Auto-sync Panel Registry (generate a file listing every *View.xaml and *Panel.xaml)
Write-Host "[PanelDiscovery] Searching for all panels..." -ForegroundColor Yellow

$panelPaths = @(
  "ui\Views\Panels",
  "ui\Views",
  "ui\Panels",
  "src\VoiceStudio.App\Views\Panels",
  "src\VoiceStudio.App\Views",
  "src\VoiceStudio.App\Panels",
  "app\ui\panels",
  "app\ui\views",
  "Views\Panels",
  "Views",
  "Panels"
)

$panels = @()
$searchPatterns = @("*View.xaml", "*Panel.xaml")

foreach ($panelPath in $panelPaths) {
  $fullPath = Join-Path $Dst $panelPath
  if (Test-Path $fullPath) {
    foreach ($pattern in $searchPatterns) {
      $found = Get-ChildItem -Path $fullPath -Recurse -Filter $pattern -ErrorAction SilentlyContinue
      if ($found) {
        $panels += $found
        Write-Host "  Found $($found.Count) panels in $panelPath" -ForegroundColor Gray
      }
    }
  }
}

# Also search for ViewModels to find panels that might not have View.xaml naming
$vmFiles = Get-ChildItem -Path $Dst -Recurse -Filter "*ViewModel.cs" -ErrorAction SilentlyContinue | 
  Where-Object { $_.FullName -like "*Panel*" -or $_.FullName -like "*View*" }
foreach ($vm in $vmFiles) {
  $xamlPath = $vm.FullName -replace "\.cs$", ".xaml"
  if (Test-Path $xamlPath) {
    $xamlFile = Get-Item $xamlPath
    if ($panels -notcontains $xamlFile) {
      $panels += $xamlFile
      Write-Host "  Found via ViewModel: $($xamlFile.Name)" -ForegroundColor Gray
    }
  }
}

# Remove duplicates
$panels = $panels | Select-Object -Unique
Write-Host "[PanelDiscovery] Found $($panels.Count) unique panels" -ForegroundColor Green

$regFile = Join-Path $Dst "app\core\PanelRegistry.Auto.cs"
New-Item -ItemType Directory -Force -Path (Split-Path $regFile) | Out-Null

if ($panels) {
  $panelList = $panels | ForEach-Object { 
    $relPath = ($_.FullName -replace [regex]::Escape($Dst),'').TrimStart('\').Replace('\','/')
    "      `"$relPath`","
  }
  
  $code = @"
using System.Collections.Generic;

namespace VoiceStudio.Core {

  public static class PanelRegistryAuto {

    public static IEnumerable<string> AllXaml() => new [] {
$($panelList -join "`n")
    };

  }

}
"@
  $code | Set-Content -Path $regFile -Encoding UTF8
  Write-Host "[PanelRegistry] Generated $regFile with $($panels.Count) panels"
} else {
  Write-Host "[PanelRegistry] No panels found - skipping auto-generation"
}

# --- Run comprehensive panel discovery
$findPanelsScript = Join-Path $Dst "tools\Find-AllPanels.ps1"
if (Test-Path $findPanelsScript) {
  Write-Host "[PanelDiscovery] Running comprehensive panel discovery..."
  & $findPanelsScript -WorkspaceRoot $Dst -OutputFile (Join-Path $Dst "app\core\PanelRegistry.Auto.cs")
} else {
  Write-Host "[PanelDiscovery] Find-AllPanels.ps1 not found, using basic discovery" -ForegroundColor Yellow
}

# --- Run panel catalog discovery if available
$discoverScript = Join-Path $Dst "tools\Discover-Panels.ps1"
if (Test-Path $discoverScript) {
  Write-Host "[PanelCatalog] Generating panel catalog..."
  & $discoverScript -SourcePath $Src -OutputPath (Join-Path $Dst "docs\governance\PANEL_CATALOG.json")
}

Write-Host ""
Write-Host "[Done] Migrated to $Dst" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1) Activate venv: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  2) Run health check: $($pex) app\cli\verify_env.py" -ForegroundColor Yellow
Write-Host "  3) Verify panels: $($pex) app\cli\verify_panels.py" -ForegroundColor Yellow
Write-Host "  4) Build WinUI3: dotnet build src\VoiceStudio.sln" -ForegroundColor Yellow
Write-Host "  5) Launch app and verify Engine Manager & Panel Manager" -ForegroundColor Yellow
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - POST_MIGRATION_CHECKS.md - Full verification checklist" -ForegroundColor Gray
Write-Host "  - PANEL_DISCOVERY_QUICK_REF.md - Find missing panels" -ForegroundColor Gray
Write-Host "  - MIGRATION_COMPLETE_CHECKLIST.md - Complete checklist" -ForegroundColor Gray
Write-Host ""

