cont$pkg = Get-AppxPackage -Name Microsoft.WindowsAppRuntime.1.8* | Where-Object { $_ .Architecture -eq 'X64' } | Select-Object -First 1
if (-not $pkg) { Write-Error 'No x64 WindowsAppRuntime 1.8 package found.'; exit 1 }
$src = $pkg.InstallLocation
$dest = 'E:\VoiceStudio\.buildlogs\x64\Release\apphost-flat'
Write-Host  Copying from $src to $dest
Copy-Item -Path (Join-Path $src '*.dll') -Destination $dest -Force
Write-Host Copied runtime DLLs from $src
