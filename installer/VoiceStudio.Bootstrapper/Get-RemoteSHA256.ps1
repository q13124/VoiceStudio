param([Parameter(Mandatory=$true)][string]$Url)
$ErrorActionPreference='Stop'
$dst = Join-Path $env:TEMP ("dl_" + [System.IO.Path]::GetFileName($Url))
try {
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $dst
    $sha = (Get-FileHash -Algorithm SHA256 $dst).Hash.ToLowerInvariant()
    Write-Host "SHA256  : $sha"
    Write-Host "File    : $dst"
    Write-Host "Size    : $((Get-Item $dst).Length) bytes"
} finally {
    if (Test-Path $dst) { Remove-Item $dst -Force }
}
