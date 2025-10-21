param(
  [Parameter(Mandatory=$true)][string]$VCRedistUrl,
  [Parameter(Mandatory=$true)][string]$VCRedistSha256,
  [Parameter(Mandatory=$true)][string]$FfmpegUrl,
  [Parameter(Mandatory=$true)][string]$FfmpegSha256
)
$ErrorActionPreference='Stop'
function Require-Tool([string]$t){ if(-not (Get-Command $t -ErrorAction SilentlyContinue)){ throw "Missing tool: $t (install WiX v3 & add to PATH)"} }
Require-Tool candle.exe
Require-Tool light.exe

$here = Split-Path $PSCommandPath -Parent
$msiDir = Resolve-Path (Join-Path $here '..\..\out\msi') | % Path
$out   = Resolve-Path (Join-Path $here '..\..\out\bundle') -ErrorAction SilentlyContinue
if(-not $out){ $out = Join-Path $here '..\..\out\bundle'; New-Item -ItemType Directory -Force -Path $out | Out-Null }

$appMsi = Join-Path $msiDir 'VoiceStudioSetup.msi'
$cntMsi = Join-Path $msiDir 'VoiceStudioContent.msi'
if(!(Test-Path $appMsi)){ throw "Missing: $appMsi" }
if(!(Test-Path $cntMsi)){ throw "Missing: $cntMsi" }

# Simple detection variables (override true when you detect locally)
$vars = @(
  "-dVCREDIST_URL=\"$VCRedistUrl\"",
  "-dVCREDIST_SHA256=\"$VCRedistSha256\"",
  "-dFFMPEG_URL=\"$FfmpegUrl\"",
  "-dFFMPEG_SHA256=\"$FfmpegSha256\"",
  "-dVC14X64_INSTALLED=false",
  "-dFFMPEG_PRESENT=false"
)

# Compile & link the REMOTE bundle
Push-Location $here
& candle.exe Bundle.Remote.wxs -ext WixBalExtension -ext WixUtilExtension @vars -o Bundle.Remote.wixobj
& light.exe Bundle.Remote.wixobj -ext WixBalExtension -ext WixUtilExtension -o (Join-Path $out 'VoiceStudioSetup.exe')
Pop-Location

Write-Host "Remote bundle built → $out\VoiceStudioSetup.exe" -ForegroundColor Green
Write-Host "Tip: Use Get-RemoteSHA256.ps1 <URL> to compute the exact SHA256 for your payloads." -ForegroundColor Cyan
