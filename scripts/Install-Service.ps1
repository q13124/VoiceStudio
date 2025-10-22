param([string]$Config = "Release")
$root = Split-Path $PSScriptRoot -Parent
$svc = Join-Path $root "UltraClone.EngineService\UltraClone.EngineService.csproj"
$out = Join-Path $root "out\service"
dotnet publish $svc -c $Config -o $out
sc.exe create UltraClone.EngineService binPath= "`"$out\UltraClone.EngineService.exe`"" start= auto | Out-Null
sc.exe start UltraClone.EngineService | Out-Null
Write-Host "Service installed and started." -ForegroundColor Green
