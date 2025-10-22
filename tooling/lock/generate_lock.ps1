Param(
  [string]$InFile = "requirements.txt",
  [string]$OutFile = "requirements.lock.txt",
  [string]$Constraints = "constraints.txt"
)

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

Write-Host "==> Generating $OutFile (no upgrades; additive only)"
$baseArgs = @("--generate-hashes","--no-emit-index-url","--no-emit-trusted-host","--no-upgrade","--allow-unsafe","-o",$OutFile,$InFile)

if (Test-Path $Constraints) {
  $args = @("-c",$Constraints) + $baseArgs
} else {
  $args = $baseArgs
}

pip-compile @args
Write-Host "==> Done."
