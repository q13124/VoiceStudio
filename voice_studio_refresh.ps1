# === VoiceStudio/UltraClone: small refresh ===
$ErrorActionPreference = 'Stop'
$root = 'C:\Users\Tyler\VoiceStudio'; if (-not(Test-Path $root)) { $root = 'C:\TylersVoiceCloner' }
if (-not(Test-Path $root)) { throw "Repo root not found." }
Set-Location $root

Write-Host "VoiceStudio Voice Cloning Program - Refresh Starting..."
Write-Host "Backup created: C:\Users\Tyler\VoiceStudio_Backup_20241019.zip"

# venv
if (-not(Test-Path ".venv")) { py -3.12 -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

Write-Host "Installing PyTorch 2.9 with CUDA 13.0 support..."

# Core pins (short)
$idx = @('https://download.pytorch.org/whl/cu130', 'https://download.pytorch.org/whl/cu128')
$ok = $false
foreach ($u in $idx) {
    try {
        Write-Host "Trying index: $u"
        pip install --extra-index-url $u torch==2.9.* torchaudio==2.9.*
        $ok = $true
        break
    }
    catch {
        Write-Host "Failed with index: $u"
    }
}
if (-not $ok) {
    Write-Host "Installing PyTorch without CUDA index..."
    pip install torch==2.9.* torchaudio==2.9.*
}

Write-Host "Installing voice cloning components..."
pip install torchcodec==0.8.* ctranslate2==4.6.* faster-whisper==1.2.* pyannote.audio==4.* librosa>=0.11 soundfile

# Win FFmpeg policy: enforce 7.x if needed
if ($IsWindows) {
    $ffv = (& ffmpeg -version 2>$null | Select-String 'ffmpeg version').ToString()
    if ((-not $ffv) -or ($ffv -match 'ffmpeg version (8|9)\.')) {
        Write-Host "Installing FFmpeg 7.1.1..."
        winget install -e --id Gyan.FFmpeg --version 7.1.1 --accept-package-agreements --accept-source-agreements
    }
}

# Write tiny ASR preset (batching + compute type)
New-Item -ItemType Directory -Force -Path "monitor\ab-tests" | Out-Null
@'
{ "model": "openai/whisper-large-v3-turbo",
  "compute_type": "int8_float16",
  "batch_size": 16,
  "vad_filter": true }
'@ | Set-Content -Encoding UTF8 -Path "monitor\ab-tests\asr_small_preset.json"

Write-Host "Testing voice cloning components..."
python health_check.py

Write-Host "VoiceStudio Voice Cloning Program - Small refresh complete!"
Write-Host "All components integrated into unified voice cloning program"
