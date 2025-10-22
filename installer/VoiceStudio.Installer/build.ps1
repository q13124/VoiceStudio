# WiX build script (uses WiX v3 toolset: candle.exe, light.exe on PATH)
param(
    [string]$Configuration = "Release",
    [string]$OutDir = "$(Join-Path (Split-Path $PSScriptRoot -Parent) 'out\msi')"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$uiProj = Join-Path $root "VoiceStudio.UI\VoiceStudio.UI.csproj"
$svcProj = Join-Path $root "UltraClone.EngineService\UltraClone.EngineService.csproj"
$pubDir = Join-Path $root "out\publish"
$svcOut = Join-Path $pubDir "service"
$uiOut = Join-Path $pubDir "ui"

# publish binaries
dotnet publish $svcProj -c $Configuration -o $svcOut
dotnet publish $uiProj  -c $Configuration -o $uiOut

# ensure programdata folders (models/pyenv will be provisioned on first run or separate content MSI if large)
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$candle = "candle.exe"; $light = "light.exe"
& $candle Product.wxs -dUiOut="$uiOut" -dSvcOut="$svcOut" -o Product.wixobj
& $light Product.wixobj -o (Join-Path $OutDir "VoiceStudioSetup.msi") -ext WixUtilExtension

Write-Host "MSI built to $OutDir" -ForegroundColor Green
