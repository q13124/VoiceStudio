# VoiceEnginesUpdate.ps1
# Updates all voice cloning engines to latest versions
param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "=== VOICE ENGINES UPDATE ===" -ForegroundColor Cyan
Write-Host "Force: $Force | DryRun: $DryRun" -ForegroundColor Yellow

# Define voice engines and their update commands
$engines = @{
    "TTS"            = @{
        "cmd"   = "pip install --upgrade TTS"
        "check" = "python -c 'import TTS; print(TTS.__version__)'"
    }
    "pyannote-audio" = @{
        "cmd"   = "pip install --upgrade pyannote.audio"
        "check" = "python -c 'import pyannote.audio; print(pyannote.audio.__version__)'"
    }
    "whisper"        = @{
        "cmd"   = "pip install --upgrade openai-whisper"
        "check" = "python -c 'import whisper; print(whisper.__version__)'"
    }
    "faster-whisper" = @{
        "cmd"   = "pip install --upgrade faster-whisper"
        "check" = "python -c 'import faster_whisper; print(faster_whisper.__version__)'"
    }
    "ctranslate2"    = @{
        "cmd"   = "pip install --upgrade ctranslate2"
        "check" = "python -c 'import ctranslate2; print(ctranslate2.__version__)'"
    }
    "librosa"        = @{
        "cmd"   = "pip install --upgrade librosa"
        "check" = "python -c 'import librosa; print(librosa.__version__)'"
    }
    "soundfile"      = @{
        "cmd"   = "pip install --upgrade soundfile"
        "check" = "python -c 'import soundfile; print(soundfile.__version__)'"
    }
    "transformers"   = @{
        "cmd"   = "pip install --upgrade transformers"
        "check" = "python -c 'import transformers; print(transformers.__version__)'"
    }
}

# Check current versions
Write-Host "`n=== CURRENT VERSIONS ===" -ForegroundColor Green
$currentVersions = @{}

foreach ($engine in $engines.Keys) {
    try {
        $version = Invoke-Expression $engines[$engine].check 2>$null
        if ($version) {
            $currentVersions[$engine] = $version.Trim()
            Write-Host "✅ $engine`: $($version.Trim())" -ForegroundColor Green
        }
        else {
            Write-Host "❌ $engine`: Not installed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ $engine`: Error checking version" -ForegroundColor Red
    }
}

if ($DryRun) {
    Write-Host "`n=== DRY RUN - NO UPDATES PERFORMED ===" -ForegroundColor Yellow
    exit 0
}

# Update engines
Write-Host "`n=== UPDATING ENGINES ===" -ForegroundColor Cyan
$updateResults = @{}

foreach ($engine in $engines.Keys) {
    Write-Host "`n🔄 Updating $engine..." -ForegroundColor Yellow

    try {
        if ($Force) {
            $cmd = $engines[$engine].cmd + " --force-reinstall"
        }
        else {
            $cmd = $engines[$engine].cmd
        }

        $result = Invoke-Expression $cmd 2>&1
        $updateResults[$engine] = @{
            "success" = $true
            "output"  = $result
        }
        Write-Host "✅ $engine updated successfully" -ForegroundColor Green

    }
    catch {
        $updateResults[$engine] = @{
            "success" = $false
            "error"   = $_.Exception.Message
        }
        Write-Host "❌ $engine update failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Verify updated versions
Write-Host "`n=== VERIFICATION ===" -ForegroundColor Green
$newVersions = @{}

foreach ($engine in $engines.Keys) {
    try {
        Start-Sleep -Seconds 2  # Give time for installation to complete
        $version = Invoke-Expression $engines[$engine].check 2>$null
        if ($version) {
            $newVersions[$engine] = $version.Trim()
            $oldVersion = $currentVersions[$engine]
            $newVersion = $version.Trim()

            if ($oldVersion -and $oldVersion -ne $newVersion) {
                Write-Host "🔄 $engine`: $oldVersion → $newVersion" -ForegroundColor Cyan
            }
            elseif ($oldVersion -eq $newVersion) {
                Write-Host "✅ $engine`: $newVersion (unchanged)" -ForegroundColor Green
            }
            else {
                Write-Host "✅ $engine`: $newVersion (newly installed)" -ForegroundColor Green
            }
        }
        else {
            Write-Host "❌ $engine`: Still not available" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ $engine`: Error verifying version" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
$successCount = ($updateResults.Values | Where-Object { $_.success }).Count
$totalCount = $updateResults.Count

Write-Host "Updates attempted: $totalCount" -ForegroundColor White
Write-Host "Updates successful: $successCount" -ForegroundColor Green
Write-Host "Updates failed: $($totalCount - $successCount)" -ForegroundColor Red

if ($successCount -eq $totalCount) {
    Write-Host "`n🎉 All voice engines updated successfully!" -ForegroundColor Green
}
else {
    Write-Host "`n⚠️ Some updates failed. Check the output above." -ForegroundColor Yellow
}

# Test CUDA availability
Write-Host "`n=== CUDA TEST ===" -ForegroundColor Cyan
try {
    $cudaTest = python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('CUDA Version:', torch.version.cuda); print('GPU Count:', torch.cuda.device_count())" 2>$null
    Write-Host $cudaTest -ForegroundColor Green
}
catch {
    Write-Host "❌ CUDA test failed" -ForegroundColor Red
}

Write-Host "`n=== VOICE ENGINES UPDATE COMPLETE ===" -ForegroundColor Cyan
