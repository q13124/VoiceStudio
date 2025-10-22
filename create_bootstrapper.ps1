# Burn bootstrapper: switch to REMOTE prerequisites (VC++ Redist x64 + FFmpeg)
$ErrorActionPreference = 'Stop'
$repo = @('C:\VoiceStudio', 'C:\TylersVoiceCloner') | ? { Test-Path $_ } | Select-Object -First 1
if (-not $repo) { throw "Repo not found at C:\VoiceStudio or C:\TylersVoiceCloner." }

$boot = Join-Path $repo 'Installer\VoiceStudio.Bootstrapper'
$bundleWxs = Join-Path $boot 'Bundle.Remote.wxs'
$buildPs1 = Join-Path $boot 'build-remote.ps1'
$utilPs1 = Join-Path $boot 'Get-RemoteSHA256.ps1'
New-Item -ItemType Directory -Force -Path $boot | Out-Null

# --- helper to compute SHA256 of a remote file (downloads to temp) ---
@'
param([Parameter(Mandatory=$true)][string]$Url)
$ErrorActionPreference='Stop'
$dst = Join-Path $env:TEMP ("dl_" + [System.IO.Path]::GetFileName($Url))
Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $dst
$sha = (Get-FileHash -Algorithm SHA256 $dst).Hash.ToLowerInvariant()
Write-Host "SHA256  : $sha"
Write-Host "File    : $dst"
'@ | Set-Content -Encoding UTF8 $utilPs1

# --- Bundle.Remote.wxs (WiX Burn with remote ExePackage payloads) ---
@'
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi"
     xmlns:bal="http://schemas.microsoft.com/wix/BalExtension">
  <Bundle Name="VoiceStudio"
          Version="1.0.0.0"
          Manufacturer="UltraClone"
          UpgradeCode="B6C8CDA7-2B4D-4B6A-893C-9E8D3B9E22B9"
          IconSourceFile="bundle.ico">
    <BootstrapperApplicationRef Id="WixStandardBootstrapperApplication.RtfLicense"
                                SuppressOptionsUI="no" ShowVersion="yes" />
    <Chain>
      <!-- VC++ 2015–2022 x64 (REMOTE) -->
      <ExePackage Id="VCppRedistX64"
                  PerMachine="yes"
                  Vital="yes"
                  Compressed="no"
                  InstallCommand="/quiet /norestart"
                  RepairCommand="/repair /quiet /norestart"
                  DetectCondition="VC14X64_INSTALLED">
        <RemotePayload
          Description="Microsoft Visual C++ 2015-2022 Redistributable (x64)"
          ProductName="Microsoft Visual C++ 2015-2022 Redistributable (x64)"
          DownloadUrl="$(var.VCREDIST_URL)"
          Hash="$(var.VCREDIST_SHA256)" />
      </ExePackage>

      <!-- FFmpeg (REMOTE) — silent installer or self-extract; adapt switches if needed -->
      <ExePackage Id="FFmpegWin64"
                  PerMachine="yes"
                  Vital="no"
                  Compressed="no"
                  InstallCommand="/S"
                  DetectCondition="FFMPEG_PRESENT">
        <RemotePayload
          Description="FFmpeg for Windows (x64)"
          ProductName="FFmpeg x64"
          DownloadUrl="$(var.FFMPEG_URL)"
          Hash="$(var.FFMPEG_SHA256)" />
      </ExePackage>

      <!-- App MSI (local, already built) -->
      <MsiPackage Id="VoiceStudioAppMsi"
                  SourceFile="..\..\out\msi\VoiceStudioSetup.msi"
                  DisplayInternalUI="no" Compressed="yes" Vital="yes" />

      <!-- Content MSI (local, already built) -->
      <MsiPackage Id="VoiceStudioContentMsi"
                  SourceFile="..\..\out\msi\VoiceStudioContent.msi"
                  DisplayInternalUI="no" Compressed="yes" Vital="yes" />
    </Chain>

    <!-- Detection variables -->
    <Variable Name="VC14X64_INSTALLED" Type="string" Value="false" bal:Overridable="yes" />
    <Variable Name="FFMPEG_PRESENT"   Type="string" Value="false" bal:Overridable="yes" />

    <!-- Require admin -->
    <bal:Condition Message="Please run as Administrator.">Privileged</bal:Condition>
  </Bundle>
</Wix>
'@ | Set-Content -Encoding UTF8 $bundleWxs

# --- build-remote.ps1 (compile with -d vars for URLs & SHA256s) ---
@"
param(
  [Parameter(Mandatory=`$true)][string]`$VCRedistUrl,
  [Parameter(Mandatory=`$true)][string]`$VCRedistSha256,
  [Parameter(Mandatory=`$true)][string]`$FfmpegUrl,
  [Parameter(Mandatory=`$true)][string]`$FfmpegSha256
)
`$ErrorActionPreference='Stop'
function Require-Tool([string]`$t){ if(-not (Get-Command `$t -ErrorAction SilentlyContinue)){ throw "Missing tool: `$t (install WiX v3 & add to PATH)"} }
Require-Tool candle.exe
Require-Tool light.exe

`$here = Split-Path `$PSCommandPath -Parent
`$msiDir = Resolve-Path (Join-Path `$here '..\..\out\msi') | % Path
`$out   = Resolve-Path (Join-Path `$here '..\..\out\bundle') -ErrorAction SilentlyContinue
if(-not `$out){ `$out = Join-Path `$here '..\..\out\bundle'; New-Item -ItemType Directory -Force -Path `$out | Out-Null }

`$appMsi = Join-Path `$msiDir 'VoiceStudioSetup.msi'
`$cntMsi = Join-Path `$msiDir 'VoiceStudioContent.msi'
if(!(Test-Path `$appMsi)){ throw "Missing: `$appMsi" }
if(!(Test-Path `$cntMsi)){ throw "Missing: `$cntMsi" }

# Simple detection variables (override true when you detect locally)
`$vars = @(
  "-dVCREDIST_URL=`"$VCRedistUrl`"",
  "-dVCREDIST_SHA256=`"$VCRedistSha256`"",
  "-dFFMPEG_URL=`"$FfmpegUrl`"",
  "-dFFMPEG_SHA256=`"$FfmpegSha256`"",
  "-dVC14X64_INSTALLED=false",
  "-dFFMPEG_PRESENT=false"
)

# Compile & link the REMOTE bundle
Push-Location `$here
& candle.exe Bundle.Remote.wxs -ext WixBalExtension -ext WixUtilExtension @vars -o Bundle.Remote.wixobj
& light.exe Bundle.Remote.wixobj -ext WixBalExtension -ext WixUtilExtension -o (Join-Path `$out 'VoiceStudioSetup.exe')
Pop-Location

Write-Host "Remote bundle built → $out\VoiceStudioSetup.exe" -ForegroundColor Green
Write-Host "Tip: Use Get-RemoteSHA256.ps1 <URL> to compute the exact SHA256 for your payloads." -ForegroundColor Cyan
"@ | Set-Content -Encoding UTF8 $buildPs1

Write-Host "Remote-prereq Burn scaffold created. Next step: supply official URLs + SHA256 hashes and run build-remote.ps1." -ForegroundColor Green
