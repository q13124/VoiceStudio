# VoiceStudio Daily Workflow (PowerShell)
# Usage: .\scripts\day.ps1 -DayNum 12 -Feature "Multi-Ref Fusion polish" -Test "python -c 'print OK'"

param(
    [string]$DayNum = (Get-Date).DayOfYear.ToString(),
    [string]$Feature = "TBD",
    [string]$Test = "python -c 'print OK'"
)

Write-Host "Day $DayNum`:$Feature" -ForegroundColor Green
Write-Host "Open Cursor (Ctrl+K) with the plan from docs/15_MINUTE_WORKFLOW.md" -ForegroundColor Yellow
Write-Host "When ready, run quick test:" -ForegroundColor Yellow
Write-Host "  $Test" -ForegroundColor Cyan

# Show ChatGPT prompt template
Write-Host "`n=== ChatGPT Prompt ===" -ForegroundColor Magenta
Write-Host "VoiceStudio Day $DayNum`:$Feature" -ForegroundColor White
Write-Host ""
Write-Host "Output ONLY:" -ForegroundColor White
Write-Host "1. File path" -ForegroundColor White
Write-Host "2. Complete code" -ForegroundColor White
Write-Host "3. Test command" -ForegroundColor White
Write-Host ""
Write-Host "No explanations." -ForegroundColor White
Write-Host ""
Write-Host "(See docs/15_MINUTE_WORKFLOW.md)" -ForegroundColor Gray
