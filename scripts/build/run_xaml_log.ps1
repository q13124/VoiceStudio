$ErrorActionPreference = "Stop"
$log = "E:\VoiceStudio\xaml_compiler_raw.log"
Set-Location "E:\VoiceStudio\src\VoiceStudio.App"
& "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\tools\net472\XamlCompiler.exe" `
  "obj\x64\Release\net8.0-windows10.0.19041.0\win-x64\input.json" `
  "obj\x64\Release\net8.0-windows10.0.19041.0\win-x64\output.json" *>&1 |
  Out-File -LiteralPath $log -Encoding UTF8
"ExitCode $LASTEXITCODE" | Out-File -LiteralPath $log -Encoding UTF8 -Append
