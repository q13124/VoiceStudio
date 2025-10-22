<# 
VoiceStudio-AddOns-Install.ps1
- Windows PowerShell 5.1 compatible
- Idempotent install of "VoiceStudio_AddOns_Drop1.zip" into your VoiceStudio project
- Preflight auto-detects Python & venv; installs FastAPI/uvicorn only if missing
- Safe paths & no prompts (edit variables below if needed)
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
# ------------------------ USER VARIABLES (edit if needed) ------------------------
# Prefer project root under C:\TylersVoiceCloner or C:\VoiceStudio; auto-detect below.
$PreferredRoots = @('C:\TylersVoiceCloner', 'C:\VoiceStudio')
# If you downloaded the ZIP to your Downloads, we'll auto-find it; else set path explicitly:
$ZipCandidateNames = @('VoiceStudio_AddOns_Drop1.zip')
$CommonZipDirs = @("$env:USERPROFILE\Downloads", "C:\Downloads", "C:\Temp")
# Optional venv hint:
$VenvHints = @('.venv','venv','.env')
# --------------------------------------------------------------------------------

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-OK($msg){ Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg){ Write-Warning $msg }
function Write-Err($msg){ Write-Error $msg }

# 1) Detect project root
$ProjectRoot = $null
foreach($root in $PreferredRoots){
  if(Test-Path $root){ $ProjectRoot = $root; break }
}
if(-not $ProjectRoot){
  $ProjectRoot = Join-Path $env:USERPROFILE "VoiceStudio"
  if(-not (Test-Path $ProjectRoot)){ New-Item -ItemType Directory -Force -Path $ProjectRoot | Out-Null }
  Write-Warn "Preferred roots not found. Using $ProjectRoot"
}else{
  Write-Info "Using project root: $ProjectRoot"
}

# 2) Find/Add-Ons ZIP
$ZipPath = $null
foreach($dir in $CommonZipDirs){
  foreach($name in $ZipCandidateNames){
    $p = Join-Path $dir $name
    if(Test-Path $p){ $ZipPath = $p; break }
  }
  if($ZipPath){ break }
}
if(-not $ZipPath){
  # Fallback: look in current directory
  $here = Get-Location
  foreach($name in $ZipCandidateNames){
    $p = Join-Path $here.Path $name
    if(Test-Path $p){ $ZipPath = $p; break }
  }
}
if(-not $ZipPath){
  Write-Err "Could not find VoiceStudio_AddOns_Drop1.zip. Place it in Downloads or set `$ZipPath manually in this script."
  exit 1
}
Write-Info "Found Add-Ons ZIP: $ZipPath"

# 3) Expand ZIP into a staging dir then copy into project
$Staging = Join-Path $env:TEMP "vs_addons_drop1_staging"
if(Test-Path $Staging){ Remove-Item -Recurse -Force $Staging }
New-Item -ItemType Directory -Force -Path $Staging | Out-Null
Expand-Archive -Path $ZipPath -DestinationPath $Staging -Force
Write-OK "Expanded to $Staging"

# Ensure folders exist in project
$targets = @(
  "app\core\pipelines",
  "app\core\api",
  "app\ui\panels\marketplace",
  "schemas",
  "tests"
)
foreach($t in $targets){
  $full = Join-Path $ProjectRoot $t
  if(-not (Test-Path $full)){ New-Item -ItemType Directory -Force -Path $full | Out-Null }
}

# Copy files (idempotent / overwrite safe)
Copy-Item -Path (Join-Path $Staging "app\core\pipelines\quality_report.py") -Destination (Join-Path $ProjectRoot "app\core\pipelines\") -Force
Copy-Item -Path (Join-Path $Staging "app\core\api\ws_stream.py") -Destination (Join-Path $ProjectRoot "app\core\api\") -Force
Copy-Item -Path (Join-Path $Staging "app\ui\panels\marketplace\marketplace_panel.py") -Destination (Join-Path $ProjectRoot "app\ui\panels\marketplace\") -Force
Copy-Item -Path (Join-Path $Staging "schemas\prosody_transform.schema.json") -Destination (Join-Path $ProjectRoot "schemas\") -Force
Copy-Item -Path (Join-Path $Staging "tests\test_quality_report.py") -Destination (Join-Path $ProjectRoot "tests\") -Force
Copy-Item -Path (Join-Path $Staging "tests\test_ws_stream.py") -Destination (Join-Path $ProjectRoot "tests\") -Force

Write-OK "Files installed to $ProjectRoot"

# 4) Python & venv preflight
function Get-PythonExe {
  $candidates = @("python.exe","py.exe")
  foreach($c in $candidates){
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if($cmd){ return (Get-Item $cmd.Path).FullName }
  }
  return $null
}

$python = Get-PythonExe
if(-not $python){ Write-Err "Python not found in PATH. Install Python 3.10 and re-run."; exit 1 }
Write-OK "Python found: $python"

# Try to locate a venv
$VenvRoot = $null
foreach($hint in $VenvHints){
  $candidate = Join-Path $ProjectRoot $hint
  if(Test-Path (Join-Path $candidate "Scripts\python.exe")){
    $VenvRoot = $candidate; break
  }
}
if(-not $VenvRoot){
  $VenvRoot = Join-Path $ProjectRoot ".venv"
  Write-Info "No existing venv found. Creating: $VenvRoot"
  & $python -m venv $VenvRoot
}
Write-OK "Using venv: $VenvRoot"

$venvPy = Join-Path $VenvRoot "Scripts\python.exe"
$venvPip = Join-Path $VenvRoot "Scripts\pip.exe"

# Ensure required packages
$req = @("fastapi","uvicorn[standard]")
foreach($pkg in $req){
  try{
    & $venvPy -c "import importlib; import sys; import subprocess; 
try: importlib.import_module('$pkg'.split('[')[0]); 
except ImportError: sys.exit(2)"
    if($LASTEXITCODE -eq 2){
      Write-Info "Installing $pkg ..."
      & $venvPip install --upgrade "$pkg"
    } else {
      Write-OK "$pkg present"
    }
  } catch {
    Write-Info "Installing $pkg ..."
    & $venvPip install --upgrade "$pkg"
  }
}

Write-OK "Installation complete."
