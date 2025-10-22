# tools/run_dashboard.ps1
param([int]$Port=5299)
$ErrorActionPreference='Stop'
$root = Split-Path $PSCommandPath -Parent
$dash = Join-Path $root "launch_metrics_dashboard.py"
if(!(Test-Path $dash)){ throw "Dashboard not found: $dash" }
$py = "python"
& $py $dash --port $Port --host 127.0.0.1