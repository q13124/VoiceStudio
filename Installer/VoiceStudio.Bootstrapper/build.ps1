param(
  [string]$Configuration = 'Release',
  [string]$OutDir = ''
)
$ErrorActionPreference='Stop'

function Require-Tool([string]$t){ if(-not (Get-Command $t -ErrorAction SilentlyContinue)){ throw "Missing tool: $t (install WiX v3 and add to PATH)"} }
Require-Tool candle.exe
Require-Tool light.exe

$here = Split-Path $PSCommandPath -Parent
$msiDir = Join-Path $here '..\..\out\msi'
$out = if($OutDir){ Resolve-Path $OutDir | % Path } else { (Resolve-Path (Join-Path $here '..\..\out\bundle') | % Path) }
New-Item -ItemType Directory -Force -Path $out | Out-Null

# Sanity check MSIs exist
$appMsi = Join-Path $msiDir 'VoiceStudioSetup.msi'
$cntMsi = Join-Path $msiDir 'VoiceStudioContent.msi'
if(!(Test-Path $appMsi)){ throw "App MSI not found: $appMsi. Build Installer\\VoiceStudio.Installer\\build.ps1 first." }
if(!(Test-Path $cntMsi)){ throw "Content MSI not found: $cntMsi. Build Installer\\VoiceStudio.ContentInstaller\\build.ps1 first." }

# Detect optional prereqs (set bundle variables through -d switches)
$vcredist = Test-Path (Join-Path $here '..\3rdparty\VC_redist.x64.exe')
$ffmpeg   = Test-Path (Join-Path $here '..\3rdparty\ffmpeg-setup.exe')

$vars = @()
if($vcredist){ $vars += "-dVCREDISTX64_EXISTS=true" } else { $vars += "-dVCREDISTX64_EXISTS=false" }
if($ffmpeg){ $vars += "-dFFMPEG_EXISTS=true" } else { $vars += "-dFFMPEG_EXISTS=false" }

# Compile
& candle.exe Bundle.wxs -ext WixBalExtension -ext WixUtilExtension @vars -o Bundle.wixobj

# Link → Bundle.exe
& light.exe Bundle.wixobj -ext WixBalExtension -ext WixUtilExtension -o (Join-Path $out 'VoiceStudioSetup.exe')

Write-Host "Bundle built → $out\VoiceStudioSetup.exe" -ForegroundColor Green
