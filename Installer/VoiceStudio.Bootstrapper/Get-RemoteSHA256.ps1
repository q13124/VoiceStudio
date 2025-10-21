param([Parameter(Mandatory=$true)][string]$Url)
$ErrorActionPreference='Stop'
$dst = Join-Path $env:TEMP ("dl_" + [System.IO.Path]::GetFileName($Url))
Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $dst
$sha = (Get-FileHash -Algorithm SHA256 $dst).Hash.ToLowerInvariant()
Write-Host "SHA256  : $sha"
Write-Host "File    : $dst"
