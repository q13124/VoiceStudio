param(
  [string]$Out = "$env:ProgramData\VoiceStudio\eval",
  [string]$Engine = "xtts",
  [switch]$WithMetrics
)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $Out | Out-Null

function Get-PythonPath {
  $pyenv = Join-Path $env:ProgramData "VoiceStudio\pyenv\Scripts\python.exe"
  if (Test-Path $pyenv) { return $pyenv }
  return "python"
}

$PY = Get-PythonPath
# Prefer repo-local router if present; fallback to ProgramData
$WR = Join-Path $PSScriptRoot "..\workers\worker_router.py"
if(-not (Test-Path $WR)){
  $WR = Join-Path $env:ProgramData "VoiceStudio\workers\worker_router.py"
}

# Golden lines (edit as needed)
$lines = @(
  "Good morning and welcome to VoiceStudio.",
  "Please schedule a call for Thursday at three fifteen.",
  "The quick brown fox jumps over the lazy dog."
)

$i=0
foreach($l in $lines){
  $i++
  $dst = Join-Path $Out ("line_{0:00}.wav" -f $i)
  & $PY $WR tts --a $l --b $dst --c ("{`"engine`":`"$Engine`",`"stability`":0.62}")
}

if($WithMetrics){
  $metrics = Join-Path $PSScriptRoot "..\workers\ops\eval_metrics.py"
  if(Test-Path $metrics){ & $PY $metrics $Out }
}
Write-Host "Eval clips written to $Out"