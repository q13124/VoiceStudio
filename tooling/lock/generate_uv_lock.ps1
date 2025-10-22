param(
  [string]$InFile = "requirements.txt",
  [string]$OutFile = "requirements.lock.txt"
)

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

Write-Host "==> Generating $OutFile with uv (no upgrade; additive only)"
uv pip compile $InFile --no-upgrade --generate-hashes --output-file $OutFile
Write-Host "==> Done."
