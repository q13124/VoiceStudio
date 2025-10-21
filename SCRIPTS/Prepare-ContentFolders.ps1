# Create placeholder structure for models and pyenv (optional)
$root = "$env:ProgramData\VoiceStudio"
New-Item -ItemType Directory -Force -Path (Join-Path $root 'models\xtts'), (Join-Path $root 'models\openvoice'), (Join-Path $root 'models\cosyvoice2'), (Join-Path $root 'models\whisper'), (Join-Path $root 'models\pyannote') | Out-Null
# Drop readme placeholders
'Place your XTTS model files here.'      | Set-Content -Encoding UTF8 (Join-Path $root 'models\xtts\README.txt')
'Place your OpenVoice model files here.'  | Set-Content -Encoding UTF8 (Join-Path $root 'models\openvoice\README.txt')
'Place your CosyVoice2 model files here.' | Set-Content -Encoding UTF8 (Join-Path $root 'models\cosyvoice2\README.txt')
'Place Whisper cache/models here.'        | Set-Content -Encoding UTF8 (Join-Path $root 'models\whisper\README.txt')
'Place pyannote pipeline here.'           | Set-Content -Encoding UTF8 (Join-Path $root 'models\pyannote\README.txt')
# venv note
'Python venv goes here (pyenv).'          | Set-Content -Encoding UTF8 (Join-Path $root 'pyenv\README.txt')
Write-Host "Prepared content tree at $root" -ForegroundColor Green
