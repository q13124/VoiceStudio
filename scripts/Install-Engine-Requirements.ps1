# Install Voice Cloning Engine Requirements
# This script installs all the Python packages needed for the real voice cloning engines

$ErrorActionPreference = "Stop"

# Set paths
$venv = "$env:ProgramData\VoiceStudio\pyenv\Scripts\python.exe"
$requirements = "$env:ProgramData\VoiceStudio\workers\requirements-engines.txt"

Write-Host "Installing Voice Cloning Engine Requirements..." -ForegroundColor Green
Write-Host "Virtual Environment: $venv" -ForegroundColor Yellow
Write-Host "Requirements File: $requirements" -ForegroundColor Yellow

# Check if virtual environment exists
if (-not (Test-Path $venv)) {
    Write-Host "Virtual environment not found at: $venv" -ForegroundColor Red
    Write-Host "Please run the VoiceStudio installer first to create the Python environment." -ForegroundColor Red
    exit 1
}

# Check if requirements file exists
if (-not (Test-Path $requirements)) {
    Write-Host "Requirements file not found at: $requirements" -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host "Installing engine requirements..." -ForegroundColor Green
try {
    & $venv -m pip install --upgrade pip
    & $venv -m pip install -r $requirements
    Write-Host "Engine requirements installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to install engine requirements: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "Voice Cloning Engine installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Available Engines:" -ForegroundColor Cyan
Write-Host "- XTTS-v2 (Coqui TTS)" -ForegroundColor White
Write-Host "- OpenVoice V2" -ForegroundColor White  
Write-Host "- CosyVoice 2" -ForegroundColor White
Write-Host "- Whisper ASR (faster-whisper)" -ForegroundColor White
Write-Host "- Pyannote Diarization" -ForegroundColor White
Write-Host ""
Write-Host "Test Commands:" -ForegroundColor Cyan
Write-Host "# XTTS Test:" -ForegroundColor Yellow
Write-Host "& `$venv `"`$env:ProgramData\VoiceStudio\workers\worker_router.py`" tts --a `"hello world`" --b `"`$env:TEMP\xtts.wav`" --c '{\`"engine\`":\`"xtts\`",\`"stability\`":0.6,\`"language\`":\`"en\`"}'" -ForegroundColor White
Write-Host ""
Write-Host "# Whisper ASR Test:" -ForegroundColor Yellow
Write-Host "& `$venv `"`$env:ProgramData\VoiceStudio\workers\worker_router.py`" convertText --a `"C:\path\audio.wav`" --b `"`$env:TEMP\asr.json`" --c '{\`"model_size\`":\`"large-v3\`",\`"compute_type\`":\`"float16\`"}'" -ForegroundColor White
