# Undo-Clean.ps1
# Restores files from quarantine
$ErrorActionPreference = 'Stop'

$pairs = @(
  @{ Source = 'C:\_Quarantine\VoiceClonerCleanup\VoiceStudio'; Dest = 'C:\VoiceStudio' }   @{ Source = 'C:\_Quarantine\VoiceClonerCleanup\Users\Tyler\AppData\Local\VoiceStudio'; Dest = 'C:\Users\Tyler\AppData\Local\VoiceStudio' }   @{ Source = 'C:\_Quarantine\VoiceClonerCleanup\Users\Tyler\AppData\Local\VoiceStudioGodTier'; Dest = 'C:\Users\Tyler\AppData\Local\VoiceStudioGodTier' }
)

foreach ($pair in $pairs) {
  $src = $pair.Source
  $dst = $pair.Dest
  if (Test-Path $src) {
    if (-not (Test-Path (Split-Path $dst))) {
      New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
    }
    Move-Item -LiteralPath $src -Destination $dst -Force
    Write-Host "Restored: $src -> $dst"
  }
}
