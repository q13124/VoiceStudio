Param(
  [string]$Configuration = "Release",
  [string]$RuntimeIdentifier = "win-x64",
  [string]$BinlogPath = "",
  [string]$PublishDir = "",
  [int]$SmokeSeconds = 10,
  [switch]$NoLaunch
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "== Gate C publish+launch =="

# Ensure model root default is set
if (-not $env:VOICESTUDIO_MODELS_PATH) {
  $env:VOICESTUDIO_MODELS_PATH = "E:\VoiceStudio\models"
}

$repoRoot = Resolve-Path "$PSScriptRoot\.."
if ($repoRoot -is [System.Management.Automation.PathInfo]) {
  $repoRoot = $repoRoot.Path
}

if (-not $PublishDir -or $PublishDir.Trim() -eq "") {
  $PublishDir = Join-Path $repoRoot ".buildlogs\x64\$Configuration\gatec-publish"
}
if (-not $BinlogPath -or $BinlogPath.Trim() -eq "") {
  $BinlogPath = Join-Path $repoRoot ".buildlogs\gatec-publish.binlog"
}
if ($SmokeSeconds -lt 1) { $SmokeSeconds = 1 }

New-Item -ItemType Directory -Path $PublishDir -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $BinlogPath -Parent) -Force | Out-Null
$publishDir = (Resolve-Path $PublishDir).Path
$latestInfoPath = Join-Path $repoRoot ".buildlogs\gatec-latest.txt"

# Publish (unpackaged apphost EXE)
$publishCmd = @(
  "dotnet", "publish", "$($repoRoot)\src\VoiceStudio.App\VoiceStudio.App.csproj",
  "-c", $Configuration,
  "-r", $RuntimeIdentifier,
  "-p:SelfContained=true",
  "-p:WindowsAppSDKSelfContained=true",
  "-p:UseAppHost=true",
  "-p:WindowsPackageType=None",
  "-p:EnableMsixTooling=false",
  "-p:EnableDefaultPriItems=false",
  "-p:PublishDir=$publishDir",
  "/bl:$BinlogPath"
)

Write-Host "Publish: $($publishCmd -join ' ')"
$publish = Start-Process -FilePath $publishCmd[0] -ArgumentList $publishCmd[1..($publishCmd.Length - 1)] -NoNewWindow -Wait -PassThru
if ($publish.ExitCode -ne 0) {
  Write-Host "Publish failed with exit code $($publish.ExitCode). See binlog: $BinlogPath"
  $logLines = @(
    "Gate C publish",
    "Timestamp: $(Get-Date -Format o)",
    "Exe: <not produced>",
    "ExitCode: $($publish.ExitCode)",
    "Binlog: $(Resolve-Path $BinlogPath)"
  )
  $launchLog = Join-Path $publishDir "gatec-launch.log"
  $logLines | Set-Content -Path $launchLog
  exit $publish.ExitCode
}

# Locate apphost
$exe = Get-ChildItem -Path $publishDir -Filter "VoiceStudio.App.exe" -Recurse | Select-Object -First 1
if (-not $exe) {
  Write-Error "VoiceStudio.App.exe not found under $publishDir"
}

$required = @(
  (Join-Path $publishDir "VoiceStudio.App.exe"),
  (Join-Path $publishDir "VoiceStudio.App.dll"),
  (Join-Path $publishDir "VoiceStudio.App.deps.json"),
  (Join-Path $publishDir "VoiceStudio.App.runtimeconfig.json")
)
foreach ($p in $required) {
  if (-not (Test-Path $p)) {
    Write-Error "Publish sanity check failed: missing $p"
  }
}

$launchLog = Join-Path $publishDir "gatec-launch.log"

if ($NoLaunch) {
  Write-Host "Launch skipped (--NoLaunch). exe: $($exe.FullName)"
  @(
    "Gate C publish (no launch)",
    "Timestamp: $(Get-Date -Format o)",
    "Exe: $($exe.FullName)",
    "ExitCode: 0",
    "Binlog: $(Resolve-Path $BinlogPath)"
  ) | Set-Content -Path $launchLog
  @(
    "Timestamp: $(Get-Date -Format o)",
    "Binlog: $(Resolve-Path $BinlogPath)",
    "PublishDir: $publishDir",
    "Exe: $($exe.FullName)",
    "Result: publish_only",
    "ExitCode: 0"
  ) | Set-Content -Path $latestInfoPath
  exit 0
}

Write-Host "Launching $($exe.FullName)..."
$proc = Start-Process -FilePath $exe.FullName -WorkingDirectory $exe.DirectoryName -PassThru
$wait = Wait-Process -Id $proc.Id -Timeout $SmokeSeconds -ErrorAction SilentlyContinue
if ($wait) {
  $launchResult = "exited"
  $exitCode = $proc.ExitCode
}
else {
  # For a UI app, "still running after N seconds" is a PASS for boot smoke.
  $launchResult = "running_after_timeout"
  $exitCode = 0
  Write-Host "App is still running after $SmokeSeconds seconds (PASS). Terminating to keep the shell clean..."
  try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch { }
}

$logLines = @(
  "Gate C publish+launch",
  "Timestamp: $(Get-Date -Format o)",
  "Exe: $($exe.FullName)",
  "Result: $launchResult",
  "ExitCode: $exitCode",
  "Binlog: $(Resolve-Path $BinlogPath)"
)
$logLines | Set-Content -Path $launchLog

Write-Host "Launch exit code: $exitCode"
Write-Host "Launch log: $launchLog"

@(
  "Timestamp: $(Get-Date -Format o)",
  "Binlog: $(Resolve-Path $BinlogPath)",
  "PublishDir: $publishDir",
  "Exe: $($exe.FullName)",
  "Result: $launchResult",
  "SmokeSeconds: $SmokeSeconds",
  "ExitCode: $exitCode"
) | Set-Content -Path $latestInfoPath

exit $exitCode
