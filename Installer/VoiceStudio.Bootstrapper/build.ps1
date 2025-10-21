param(
  [string]$Configuration = "Release",
  [string]$Version = "1.0.0",
  [string]$Arch = "win-x64"
)

$ErrorActionPreference = 'Stop'

# Resolve paths
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$OutDir = Join-Path $RepoRoot 'out/bundle'
$PublishRoot = Join-Path $RepoRoot 'publish'
$ClientProj = Join-Path $RepoRoot 'src/Client/VoiceStudio.Client.csproj'
$PluginHostProj = Join-Path $RepoRoot 'src/PluginHost/VoiceStudio.PluginHost.csproj'
$InnoScript = Join-Path $PSScriptRoot 'VoiceStudio.iss'

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $PublishRoot 'Client') | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $PublishRoot 'PluginHost') | Out-Null

Write-Host "Publishing .NET apps ($Configuration, $Arch)..."

dotnet publish $ClientProj -c $Configuration -r $Arch --self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=false -o (Join-Path $PublishRoot 'Client')

dotnet publish $PluginHostProj -c $Configuration -r $Arch --self-contained true -p:PublishSingleFile=false -p:PublishTrimmed=false -o (Join-Path $PublishRoot 'PluginHost')

Write-Host "Building installer with Inno Setup..."

# Find ISCC.exe (Inno Setup) if available via PATH or default location
function Resolve-Iscc {
  $candidate = (Get-Command iscc.exe -ErrorAction SilentlyContinue)?.Source
  if ($candidate) { return $candidate }
  $default = "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"
  if (Test-Path $default) { return $default }
  throw "ISCC.exe (Inno Setup) not found. Please install Inno Setup 6 and ensure iscc.exe is on PATH."
}

$Iscc = Resolve-Iscc

# Set version define on compile
& $Iscc $InnoScript /DMyAppVersion=$Version /O$OutDir

$OutputExe = Join-Path $OutDir 'VoiceStudioSetup.exe'

if (-not (Test-Path $OutputExe)) {
  throw "Expected installer not found at $OutputExe"
}

Write-Host "Installer built: $OutputExe"
