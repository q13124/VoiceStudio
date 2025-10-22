sc.exe stop UltraClone.EngineService | Out-Null
sc.exe delete UltraClone.EngineService | Out-Null
Write-Host "Service stopped and removed." -ForegroundColor Yellow
