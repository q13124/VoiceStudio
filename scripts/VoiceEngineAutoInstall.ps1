param(
  [string]$HandshakeFile,
  [switch]$FromStdin
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $repoRoot 'scripts/Run-VoiceEnginesUpdate.ps1'
if (-not (Test-Path $runner)) { throw "Runner not found: $runner" }

if ($HandshakeFile) {
  & pwsh -File $runner -HandshakeFile $HandshakeFile
  exit $LASTEXITCODE
}
if ($FromStdin) {
  $inputJson = [Console]::In.ReadToEnd()
  $inputJson | & pwsh -File $runner -FromStdin
  exit $LASTEXITCODE
}
# Default: apply pending
& pwsh -File $runner -ApplyPending
exit $LASTEXITCODE
