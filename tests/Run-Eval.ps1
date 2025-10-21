param(
  [string]$Out = "C:\VoiceStudio\projects\demo\eval",
  [string]$Voice = "C:\VoiceStudio\tools\piper\voices\en_US-amy-low.onnx",
  [string]$Python = "C:\VoiceStudio\workers\python\vsdml\.venv\Scripts\python.exe",
  [string]$Tts = "C:\VoiceStudio\workers\python\vsdml\tts_piper.py",
  [switch]$WithMetrics
)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$Piper = "C:\VoiceStudio\tools\piper\piper.exe"

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
  & $Python $Tts --text $l --voice $Voice --out $dst --piper $Piper
}

if($WithMetrics){
  & $Python "C:\VoiceStudio\workers\python\ops\eval_metrics.py" $Out
}
Write-Host "Eval clips written to $Out"