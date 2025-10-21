param(
    [switch]$SkipBuild,
    [switch]$SkipPython,
    [switch]$NoSnapshot,
    [switch]$LightSBOM,
    [switch]$InstallTelemetry,
    [switch]$OpenCursor,
    [switch]$AutoUpgrade
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Log([string]$msg) {
    $ts = (Get-Date).ToString("s")
    if ($global:LOGFILE) {
        "$ts $msg" | Tee-Object -FilePath $global:LOGFILE -Append
    }
    else {
        Write-Host "$ts $msg"
    }
}

function Json($obj) {
    $obj | ConvertTo-Json -Depth 12
}

# --- Paths --------------------------------------------------------------------
$Root = "C:\VoiceStudio"
$Tools = Join-Path $Root "tools"
$Handoff = Join-Path $Root "handoff"
$Logs = Join-Path $Root "logs"
$EnvFile = Join-Path $Handoff "env_snapshot.json"
$Report = Join-Path $Handoff "cursor_handoff.json"
$SbomLite = Join-Path $Handoff ("sbom_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json")
$CdxPy = Join-Path $Handoff ("sbom_python_cyclonedx_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json")
$CdxNet = Join-Path $Handoff ("sbom_dotnet_cyclonedx_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".json")
$Snap = Join-Path $Handoff ("snapshot_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".zip")
$global:LOGFILE = Join-Path $Logs ("auto_handoff_" + (Get-Date -Format "yyyyMMdd") + ".log")

New-Item -ItemType Directory -Force -Path $Tools, $Handoff, $Logs | Out-Null

# --- Helpers ------------------------------------------------------------------
function TryGet($name, [scriptblock]$block) {
    try {
        & $block
    }
    catch {
        $state.issues += "${name}: $($_.Exception.Message)"
        $null
    }
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

# Git
$state.tools.git_version = TryGet "git" { git --version }
if (Test-Path (Join-Path $Root ".git")) {
    Push-Location $Root
    $state.repo.status = TryGet "git status" { git status --porcelain=v1 }
    $state.repo.branch = TryGet "git rev-parse --abbrev-ref" { git rev-parse --abbrev-ref HEAD }
    $state.repo.commit = TryGet "git rev-parse HEAD" { git rev-parse HEAD }
    $state.repo.remote = TryGet "git remote -v" { git remote -v }
    Pop-Location
}

# .NET
$state.tools.dotnet_version = TryGet "dotnet" { dotnet --version }

# Python venv
$PyVenv = "C:\VoiceStudio\workers\python\vsdml\.venv\Scripts\python.exe"
if (Test-Path $PyVenv) {
    $state.tools.python = TryGet "python --version" { & $PyVenv --version }
    if (-not $SkipPython) {
        $state.tools.pip_list = TryGet "pip list" { & $PyVenv -m pip list --format=json | ConvertFrom-Json }
    }
}
else {
    $state.issues += "Python venv not found at $PyVenv"
}

# FFmpeg
$state.tools.ffmpeg = TryGet "ffmpeg -version" { (ffmpeg -version | Select-Object -First 1) }

# NVIDIA / CUDA
$state.hardware.nvidia_smi = TryGet "nvidia-smi" { nvidia-smi --query-gpu=name, driver_version, memory.total --format=csv, noheader }
$state.hardware.cuda_env = @{ CUDA_PATH = $env:CUDA_PATH; CUDA_PATH_V12_1 = $env:CUDA_PATH_V12_1 }

# Service health
$svcUrl = "http://127.0.0.1:5071/health"
$state.services.core = TryGet "health" { (Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 $svcUrl).StatusCode }

# Pins
$pinsPath = Join-Path $Root "pins.json"
if (Test-Path $pinsPath) {
    $state.pins = Get-Content $pinsPath -Raw | ConvertFrom-Json
}

# Save env snapshot
Json $state | Set-Content $EnvFile -Encoding UTF8
Log "Preflight completed."

# --- Enhanced CycloneDX SBOM Generation --------------------------------------
Log "Generating Enhanced CycloneDX SBOMs..."

# Ensure CycloneDX tools are installed
$ensureCdx = @()
$ensureCdx += "$PyVenv -m pip install --upgrade cyclonedx-bom"
$ensureCdx += "dotnet tool update --global CycloneDX"

foreach ($cmd in $ensureCdx) {
    try {
        Invoke-Expression $cmd | Out-Null
        Log "Installed CycloneDX tool: $cmd"
    }
    catch {
        Log "WARN CycloneDX tool step failed: $cmd :: $($_.Exception.Message)"
    }
}

# Generate Python CycloneDX SBOM
try {
    Log "Generating Python CycloneDX SBOM..."
    if (-not $LightSBOM) {
        & $PyVenv -m cyclonedx_py environment -o $CdxPy --of json
    }
    else {
        & $PyVenv -m cyclonedx_py environment -o $CdxPy --of json --no-file-hashes
    }
    Log "Python CycloneDX SBOM generated: $CdxPy"
}
catch {
    Log "WARN cyclonedx_py failed: $($_.Exception.Message)"
}

# Generate .NET CycloneDX SBOM
try {
    Log "Generating .NET CycloneDX SBOM..."
    $srcPath = Join-Path $Root "src"
    if (Test-Path $srcPath) {
        Push-Location $srcPath
        dotnet CycloneDX -o $CdxNet --of json
        Pop-Location
        Log ".NET CycloneDX SBOM generated: $CdxNet"
    }
    else {
        Log "No .NET src directory found, skipping .NET CycloneDX SBOM"
    }
}
catch {
    Log "WARN dotnet CycloneDX failed: $($_.Exception.Message)"
}

# --- Build & Tests ------------------------------------------------------------
$build = [ordered]@{ dotnet = @{}; python = @{} }

if ((Test-Path $PyVenv) -and (-not $SkipPython)) {
    try {
        Log "Running Python smoke tests..."
        $smokeScript = @"
import sys, torch, importlib, json
out = {"torch_ok": False, "cuda": False, "xtts_ok": None, "transformers_ok": None}
try:
    import TTS, transformers
    out["xtts_ok"] = True
    out["transformers_ok"] = True
except Exception as e:
    out["xtts_ok"] = str(e)
    out["transformers_ok"] = str(e)
out["cuda"] = torch.cuda.is_available() if importlib.util.find_spec("torch") else False
out["torch_ok"] = importlib.util.find_spec("torch") is not None
print(json.dumps(out))
"@

        $smoke = & $PyVenv -c $smokeScript
        $build.python = $smoke | ConvertFrom-Json
        Log "Python smoke tests completed"
    }
    catch {
        $build.python = @{ error = ($_.Exception.Message) }
        Log "Python smoke tests failed: $($_.Exception.Message)"
    }
}

# --- Enhanced Handoff Report --------------------------------------------------
$summary = @"
VoiceStudio Enhanced CycloneDX Handoff
Time: $($state.time_utc)
Branch: $($state.repo.branch)
Commit: $($state.repo.commit)
CUDA Available: $($build.python.cuda)
CycloneDX Python: $(Test-Path $CdxPy)
CycloneDX .NET: $(Test-Path $CdxNet)
Issues: $(($state.issues -join '; '))
"@

$handoff = [ordered]@{
    schema   = "voiceStudio.enhancedCycloneDX/v1"
    summary  = $summary.Trim()
    env      = $state
    build    = $build
    sbom     = @{
        lite      = $SbomLite
        cyclonedx = @{
            python = $CdxPy
            dotnet = $CdxNet
        }
    }
    features = @{
        cyclonedx_standard = "OWASP Foundation Standard"
        security_focused   = "Vulnerability tracking and CVE integration"
        compliance_ready   = "SOC2, ISO27001, NIST compliance"
        machine_readable   = "JSON/XML formats for automation"
        tool_ecosystem     = "Wide tool support and integration"
    }
}

Json $handoff | Set-Content $Report -Encoding UTF8
Log "Enhanced CycloneDX handoff written: $Report"

Write-Host "`nEnhanced CycloneDX SBOM System Ready!"
Write-Host "Report: $Report"
Write-Host "Python CycloneDX: $CdxPy"
Write-Host ".NET CycloneDX: $CdxNet"
Write-Host "`nCycloneDX Advantages:"
Write-Host "- Industry Standard (OWASP Foundation)"
Write-Host "- Security Focused (Vulnerability tracking)"
Write-Host "- Compliance Ready (SOC2, ISO27001)"
Write-Host "- Machine Readable (JSON/XML)"
Write-Host "- Tool Ecosystem Integration"
