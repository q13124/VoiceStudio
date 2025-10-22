param(
  [Parameter(Mandatory=$true)][string]$VCRedistUrl,
  [Parameter(Mandatory=$true)][string]$VCRedistSha256,
  [Parameter(Mandatory=$true)][string]$FfmpegUrl,
  [Parameter(Mandatory=$true)][string]$FfmpegSha256,
  [Parameter(Mandatory=$true)][string]$PythonUrl,
  [Parameter(Mandatory=$true)][string]$PythonSha256
)
$ErrorActionPreference='Stop'

function Require-Tool([string]$t){ 
    if(-not (Get-Command $t -ErrorAction SilentlyContinue)){ 
        throw "Missing tool: $t (install WiX v3 & add to PATH)" 
    } 
}

Require-Tool candle.exe
Require-Tool light.exe

$here = Split-Path $PSCommandPath -Parent
$msiDir = Resolve-Path (Join-Path $here '..\..\out\msi') | % Path
$out   = Resolve-Path (Join-Path $here '..\..\out\bundle') -ErrorAction SilentlyContinue
if(-not $out){ 
    $out = Join-Path $here '..\..\out\bundle'
    New-Item -ItemType Directory -Force -Path $out | Out-Null 
}

# Check for required MSI files
$requiredMsis = @(
    'VoiceStudioCore.msi',
    'VoiceStudioEngines.msi', 
    'VoiceStudioContent.msi'
)

foreach($msi in $requiredMsis) {
    $msiPath = Join-Path $msiDir $msi
    if(!(Test-Path $msiPath)){ 
        throw "Missing required MSI: $msiPath" 
    }
}

# Build variables
$vars = @(
    "-dVCREDIST_URL=`"$VCRedistUrl`"",
    "-dVCREDIST_SHA256=`"$VCRedistSha256`"",
    "-dFFMPEG_URL=`"$FfmpegUrl`"",
    "-dFFMPEG_SHA256=`"$FfmpegSha256`"",
    "-dPYTHON_URL=`"$PythonUrl`"",
    "-dPYTHON_SHA256=`"$PythonSha256`"",
    "-dVC14X64_INSTALLED=false",
    "-dFFMPEG_PRESENT=false",
    "-dPYTHON_INSTALLED=false"
)

# Compile & link the REMOTE bundle
Push-Location $here
try {
    Write-Host "Compiling Bundle.Remote.wxs..." -ForegroundColor Yellow
    & candle.exe Bundle.Remote.wxs -ext WixBalExtension -ext WixUtilExtension @vars -o Bundle.Remote.wixobj
    
    Write-Host "Linking bundle..." -ForegroundColor Yellow
    & light.exe Bundle.Remote.wixobj -ext WixBalExtension -ext WixUtilExtension -o (Join-Path $out 'VoiceStudioUltimateSetup.exe')
    
    Write-Host "Remote bundle built successfully!" -ForegroundColor Green
    Write-Host "Output: $out\VoiceStudioUltimateSetup.exe" -ForegroundColor Cyan
    Write-Host "Tip: Use Get-RemoteSHA256.ps1 <URL> to compute SHA256 hashes." -ForegroundColor Cyan
} finally {
    Pop-Location
}