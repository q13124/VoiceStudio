param(
  [switch]$SkipBuild,
  [switch]$SkipPython,
  [switch]$NoSnapshot,
  [switch]$LightSBOM,          # skip hashing for speed
  [switch]$InstallTelemetry,   # create/update Scheduled Task to sample VRAM every 5 min
  [switch]$OpenCursor          # open Cursor with handoff file after generation
,
  [switch]$AutoUpgrade          # apply upgrades from ChatGPT conversations)

$ErrorActionPreference = "Stop"
$ProgressPreference    = "SilentlyContinue"

function Log([string]$msg){ $ts = (Get-Date).ToString("s"); "$ts $msg" | Tee-Object -FilePath "$env:LOGFILE" -Append }
function Json($obj){ $obj | ConvertTo-Json -Depth 12 }

# --- Paths --------------------------------------------------------------------
$Root     = "C:\VoiceStudio"
$Tools    = Join-Path $Root "tools"
$Handoff  = Join-Path $Root "handoff"
$Logs     = Join-Path $Root "logs"
$EnvFile  = Join-Path $Handoff "env_snapshot.json"
$Report   = Join-Path $Handoff "cursor_handoff.json"
$SbomLite = Join-Path $Handoff ("sbom_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json")
$CdxPy    = Join-Path $Handoff ("sbom_python_cyclonedx_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json")
$CdxNet   = Join-Path $Handoff ("sbom_dotnet_cyclonedx_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json")
$Snap     = Join-Path $Handoff ("snapshot_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".zip")
$global:LOGFILE = Join-Path $Logs ("auto_handoff_" + (Get-Date -Format "yyyyMMdd") + ".log")

New-Item -ItemType Directory -Force -Path $Tools,$Handoff,$Logs | Out-Null

# --- Helpers ------------------------------------------------------------------
function TryGet($name, [scriptblock]$block){
  try { & $block } catch { $script:state.issues += "$name: $($_.Exception.Message)"; $null }
}

# --- Preflight ----------------------------------------------------------------
$state = [ordered]@{
  time_utc = (Get-Date).ToUniversalTime().ToString("s") + "Z"
  host     = [ordered]@{
    os         = (Get-CimInstance Win32_OperatingSystem).Caption
    build      = (Get-ComputerInfo).OsVersion
    ps_version = $PSVersionTable.PSVersion.ToString()
    user       = "$env:UserDomain\$env:UserName"
  }
  tools    = [ordered]@{}
  repo     = [ordered]@{}
  hardware = [ordered]@{}
  services = [ordered]@{}
  pins     = $null
  issues   = @()
}

# Git / .NET / managers
$state.tools.git_version    = TryGet "git --version" { git --version }
$state.tools.dotnet_version = TryGet "dotnet --version" { dotnet --version }
$state.tools.winget_version = TryGet "winget --version" { winget --version }
$state.tools.choco_version  = TryGet "choco --version"  { choco --version }

if (Test-Path (Join-Path $Root ".git")) {
  Push-Location $Root
  $state.repo.status = TryGet "git status" { git status --porcelain=v1 }
  $state.repo.branch = TryGet "git branch" { git rev-parse --abbrev-ref HEAD }
  $state.repo.commit = TryGet "git rev parse" { git rev-parse HEAD }
  $state.repo.remote = TryGet "git remotes" { git remote -v }
  Pop-Location
}

# Python venv
$PyVenv = "C:\VoiceStudio\workers\python\vsdml\.venv\Scripts\python.exe"
if (Test-Path $PyVenv) {
  $state.tools.python = TryGet "python --version" { & $PyVenv --version }
  if (-not $SkipPython) {
    $state.tools.pip_list = TryGet "pip list" { & $PyVenv -m pip list --format=json | ConvertFrom-Json }
  }
} else {
  $state.issues += "Python venv not found at $PyVenv"
}

# FFmpeg
$state.tools.ffmpeg = TryGet "ffmpeg -version" { (ffmpeg -version | Select-Object -First 1) }

# NVIDIA / CUDA
$state.hardware.nvidia_smi = TryGet "nvidia-smi" { nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used --format=csv,noheader }
$state.hardware.cuda_env   = @{ CUDA_PATH = $env:CUDA_PATH; CUDA_PATH_V12_1 = $env:CUDA_PATH_V12_1 }

# VoiceStudio service health
$services = @(
  @{ name = "Assistant"; url = "http://127.0.0.1:5080/health" },
  @{ name = "VoiceCloning"; url = "http://127.0.0.1:5081/health" },
  @{ name = "Orchestrator"; url = "http://127.0.0.1:5082/health" }
)

foreach ($svc in $services) {
  $state.services[$svc.name] = TryGet "health $($svc.name)" { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 $svc.url).StatusCode }
}

# Pins (optional)
$pinsPath = Join-Path $Root "pins.json"
if (Test-Path $pinsPath) { $state.pins = Get-Content $pinsPath -Raw | ConvertFrom-Json }

Json $state | Set-Content $EnvFile -Encoding UTF8
Log "Preflight completed."

# --- Build & smoke ------------------------------------------------------------
$build = [ordered]@{ dotnet=@{}; python=@{} }

if (-not $SkipBuild) {
  Push-Location (Join-Path $Root "src")
  try {
    Log "dotnet restore/build/test…"
    $restore = dotnet restore 2>&1
    $buildOut= dotnet build -c Release 2>&1
    $testOut = dotnet test -c Release --no-build 2>&1
    $build.dotnet = [ordered]@{
      restore = $restore -join "`n"
      build   = $buildOut -join "`n"
      test    = $testOut -join "`n"
      ok      = $LASTEXITCODE -eq 0
    }
  } catch { $build.dotnet.error = $_ | Out-String }
  Pop-Location
}

if (Test-Path $PyVenv -and -not $SkipPython) {
  try {
    Log "python smoke…"
    $smoke = & $PyVenv - <<'PY'
import json
out={"torch_ok":False,"cuda":False,"xtts_ok":None,"transformers_ok":None}
try:
    import torch
    out["torch_ok"]=True
    out["cuda"]=torch.cuda.is_available()
except Exception as e:
    out["torch_error"]=str(e)
for m in ("TTS","transformers"):
    try:
        __import__(m); out[f"{m.lower()}_ok"]=True
    except Exception as e:
        out[f"{m.lower()}_ok"]=f"ERR {e}"
print(json.dumps(out))
PY
    $build.python = $smoke | ConvertFrom-Json
  } catch { $build.python = @{ error = ($_.Exception.Message) } }
}

# --- Lightweight SBOM (house format) ------------------------------------------
$sbom = [ordered]@{ schema="voiceStudio.sbom/v1"; created=$state.time_utc; components=@(); notes=@() }
if ($state.tools.pip_list) {
  $sbom.components += [ordered]@{ type="python"; items=($state.tools.pip_list | % { [ordered]@{ name=$_.name; version=$_.version }}) }
}
try {
  Push-Location (Join-Path $Root "src")
  $dotnetList = dotnet list package --include-transitive 2>$null
  Pop-Location
  if ($dotnetList) { $sbom.components += [ordered]@{ type="dotnet"; raw=$dotnetList -join "`n" } }
} catch { $sbom.notes += "dotnet list package failed: $($_.Exception.Message)" }

if (-not $LightSBOM) {
  try {
    $appDirs = @((Join-Path $Root 'src'),(Join-Path $Root 'workers\python\vsdml'),(Join-Path $Root 'plugins'),(Join-Path $Root 'build')) | ? { Test-Path $_ }
    $hashes=@()
    foreach($d in $appDirs){
      Get-ChildItem -Path $d -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -lt 50MB } | ForEach-Object {
          try { $h=Get-FileHash -Algorithm SHA256 -Path $_.FullName; $hashes += [ordered]@{ path=$_.FullName; sha256=$h.Hash; size=$_.Length } } catch {}
        }
    }
    $sbom.components += [ordered]@{ type="files"; count=$hashes.Count; items=$hashes }
  } catch { $sbom.notes += "file hashing failed: $($_.Exception.Message)" }
}
Json $sbom | Set-Content $SbomLite -Encoding UTF8

# --- CycloneDX SBOMs (Python & .NET) ------------------------------------------
# Ensure tools: cyclonedx-py (Python) and dotnet CycloneDX (global tool)
$ensureCdx = @()
if (Test-Path $PyVenv) {
  $ensureCdx += "$PyVenv -m pip install --upgrade cyclonedx-bom"
}
$ensureCdx += "dotnet tool update --global CycloneDX"
foreach($cmd in $ensureCdx){
  try { Invoke-Expression $cmd | Out-Null } catch { Log "WARN cyclonedx tool step failed: $cmd :: $($_.Exception.Message)" }
}

# Generate Python CycloneDX (env-based)
if (Test-Path $PyVenv) {
  try {
    $env:PATH = (Split-Path $PyVenv) + ';' + $env:PATH
    & $PyVenv -m cyclonedx_py --format json --output $CdxPy 2>$null
  } catch { Log "WARN cyclonedx_py failed: $($_.Exception.Message)" }
}

# Generate .NET CycloneDX (solution in src or repo root)
try {
  $dotnetCwd = if (Test-Path (Join-Path $Root 'src')) { (Join-Path $Root 'src') } else { $Root }
  Push-Location $dotnetCwd
  # emits bom.json by default; move to target path
  dotnet CycloneDX --json | Out-File -Encoding UTF8 $CdxNet
  Pop-Location
} catch { Log "WARN dotnet CycloneDX failed: $($_.Exception.Message)" }

# --- Snapshot (rollback) ------------------------------------------------------
$rollback = $null
if (-not $NoSnapshot) {
  try {
    if (Test-Path $Snap) { Remove-Item $Snap -Force }
    Compress-Archive -Path (Join-Path $Root "*") -DestinationPath $Snap -Force -CompressionLevel Optimal
    $rollback = @{ snapshot_zip = $Snap }
  } catch { Log "WARN snapshot failed: $($_.Exception.Message)" }
}

# --- Action Plan for Cursor ---------------------------------------------------
$actions = @()

# Ensure ffmpeg (winget/choco)
$actions += @{
  id="ensure-ffmpeg"; kind="shell"; cwd=$Root;
  commands=@(
    'if(!(ffmpeg -version 2>$null)){ if((winget --version) -ne $null){ winget install --id=Gyan.FFmpeg --accept-package-agreements --accept-source-agreements -e || winget install --id=FFmpeg.FFmpeg -e } elseif((choco --version) -ne $null){ choco install ffmpeg -y } else { Write-Error "No winget/choco to install ffmpeg"; exit 1 } }'
  );
  success_hint="ffmpeg -version prints a version line"
}

# Build/test if requested
if (-not $SkipBuild) {
  $actions += @{ id="dotnet-build-test"; kind="shell"; cwd=(Join-Path $Root "src"); commands=@("dotnet restore","dotnet build -c Release","dotnet test -c Release --no-build"); success_hint="All tests passed" }
}

# Python pins (optional)
if (Test-Path $PyVenv -and -not $SkipPython) {
  $actions += @{
    id="sync-python-deps"; kind="shell"; cwd=$Root;
    commands=@(
      "$PyVenv -m pip install --upgrade pip",
      "$PyVenv -m pip install --upgrade --only-binary=:all: torch==2.2.2 torchaudio==2.2.2",
      "$PyVenv -m pip install coqui-tts==0.24.1 transformers==4.55.4 faster-whisper==1.0.3"
    );
    success_hint="pip list shows pinned versions and smoke test passes"
  }
}

# VoiceStudio service bringup
$actions += @{
  id="bringup-voicestudio-services"; kind="shell"; cwd=$Root;
  commands=@(
    "powershell -ExecutionPolicy Bypass -File .\installer\install.ps1 -Silent",
    "Start-Sleep 10",
    "Invoke-WebRequest http://127.0.0.1:5080/health | % StatusCode",
    "Invoke-WebRequest http://127.0.0.1:5081/health | % StatusCode",
    "Invoke-WebRequest http://127.0.0.1:5082/health | % StatusCode"
  );
  success_hint="All VoiceStudio services return 200"
}

# Voice cloning pipeline validation
$actions += @{
  id="validate-voice-cloning"; kind="shell"; cwd=$Root;
  commands=@(
    "$PyVenv -m python VoiceStudio\workers\python\vsdml\test_voice_cloning_pipeline.py",
    "$PyVenv -m python VoiceStudio\workers\python\vsdml\voice_cloning_optimizer.py"
  );
  success_hint="Voice cloning pipeline tests pass and optimization completes"
}

# Regenerate IPC (if present)
$proto = Join-Path $Root "src\IPC\proto"
if (Test-Path $proto) {
  $actions += @{ id="regen-ipc"; kind="shell"; cwd=$Root; commands=@(".\scripts\regen-proto.ps1"); success_hint="IPC codegen completes and compiles" }
}



# --- Auto-Upgrade from ChatGPT Conversations ----------------------------------
if ($AutoUpgrade) {
  Log "Starting auto-upgrade from ChatGPT conversations..."
  
  $AutoUpgradeScript = Join-Path $Root "installer\handoff\auto_upgrade_from_chatgpt.ps1"
  if (Test-Path $AutoUpgradeScript) {
    try {
      & $AutoUpgradeScript -ApplyUpgrades
      Log "Auto-upgrade completed successfully"
    } catch {
      Log "WARN auto-upgrade failed: $($_.Exception.Message)"
      $state.issues += "Auto-upgrade failed: $($_.Exception.Message)"
    }
  } else {
    Log "WARN auto-upgrade script not found: $AutoUpgradeScript"
    $state.issues += "Auto-upgrade script not found"
  }
}

# --- Summary & Handoff --------------------------------------------------------
$summary = @"
VoiceStudio Auto Handoff (CycloneDX + Telemetry)
Time: $($state.time_utc)
Branch: $($state.repo.branch)
Commit: $($state.repo.commit)
DotNetOK: $([bool]($build.dotnet.ok))
TorchCUDA: $($build.python.cuda)
SBOM(lite): $(Split-Path -Leaf $SbomLite)
SBOM(Py CDX): $(Split-Path -Leaf $CdxPy)
SBOM(.NET CDX): $(Split-Path -Leaf $CdxNet)
"@

$handoff = [ordered]@{
  schema    = "voiceStudio.cursorHandoff/v1"
  summary   = $summary.Trim()
  env       = $state
  build     = $build
  sbom      = @{ lite=$SbomLite; cyclonedx = @{ python=$CdxPy; dotnet=$CdxNet } }
  rollback  = $rollback
  actions   = $actions
}

Json $handoff | Set-Content $Report -Encoding UTF8
Log "Handoff written: $Report"

# --- Optional: install/update VRAM telemetry task -----------------------------
if ($InstallTelemetry) {
  $taskName = "VoiceStudio VRAM Telemetry"
  $py = "C:\VoiceStudio\workers\python\vsdml\.venv\Scripts\pythonw.exe"
  if (-not (Test-Path $py)) { $py = "C:\VoiceStudio\workers\python\vsdml\.venv\Scripts\python.exe" }
  if (-not (Test-Path $py)) { throw "Python venv not found for telemetry: $py" }
  $teleScript = "C:\VoiceStudio\tools\gpu_telemetry.py"
  $action  = New-ScheduledTaskAction -Execute $py -Argument "`"$teleScript`""
  $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)
  try {
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
      Unregister-ScheduledTask -TaskName $taskName -Confirm:$false | Out-Null
    }
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Description "Logs GPU VRAM every 5 min to logs\vram_telemetry.csv" -User "$env:USERNAME" -RunLevel Highest | Out-Null
    Log "Scheduled VRAM telemetry task: $taskName"
  } catch { Log "WARN telemetry scheduler: $($_.Exception.Message)" }
}

# --- Optional: open Cursor with handoff file ----------------------------------
if ($OpenCursor) {
  $cursorCandidates = @(
    "$env:LocalAppData\Programs\cursor\Cursor.exe",
    "$env:ProgramFiles\Cursor\Cursor.exe",
    "$env:ProgramFiles(x86)\Cursor\Cursor.exe"
  )
  $cursorExe = $cursorCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($null -ne $cursorExe) {
    Start-Process -FilePath $cursorExe -ArgumentList "`"$Report`""
    Log "Opened Cursor: $cursorExe $Report"
  } else {
    # Fallback: open folder and file in Explorer
    Start-Process explorer.exe "/select,`"$Report`""
    Log "Cursor not found; opened folder in Explorer."
  }
}

Write-Host "`nOK — cursor handoff is ready:`n$Report`nCycloneDX (Py): $CdxPy`nCycloneDX (.NET): $CdxNet`n"
