param(
    [switch]$WithMetrics
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ProgramDataVoiceStudioPath {
    $base = $env:PROGRAMDATA
    if ([string]::IsNullOrWhiteSpace($base)) { $base = [Environment]::GetFolderPath('CommonApplicationData') }
    if ([string]::IsNullOrWhiteSpace($base)) { $base = (Get-Location).Path }
    $vs = Join-Path $base 'VoiceStudio'
    if (-not (Test-Path $vs)) { New-Item -Path $vs -ItemType Directory | Out-Null }
    return $vs
}

function New-SineWaveWav {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [int]$SampleRate = 48000,
        [int]$Channels = 1,
        [int]$BitsPerSample = 16,
        [double]$DurationSec = 1.0,
        [double]$FrequencyHz = 440.0,
        [double]$Amplitude = 0.2
    )
    $numSamples = [int]([math]::Round($SampleRate * $DurationSec))
    $bytesPerSample = [int]($BitsPerSample / 8)
    $blockAlign = $Channels * $bytesPerSample
    $byteRate = $SampleRate * $blockAlign
    $dataSize = $numSamples * $blockAlign

    $fs = [System.IO.File]::Open($Path, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
    $bw = New-Object System.IO.BinaryWriter($fs)

    # RIFF header
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes('RIFF'))
    $bw.Write([int]($dataSize + 36))
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes('WAVE'))

    # fmt chunk
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes('fmt '))
    $bw.Write([int]16)                   # PCM fmt chunk size
    $bw.Write([short]1)                  # PCM format
    $bw.Write([short]$Channels)
    $bw.Write([int]$SampleRate)
    $bw.Write([int]$byteRate)
    $bw.Write([short]$blockAlign)
    $bw.Write([short]$BitsPerSample)

    # data chunk
    $bw.Write([System.Text.Encoding]::ASCII.GetBytes('data'))
    $bw.Write([int]$dataSize)

    for ($i = 0; $i -lt $numSamples; $i++) {
        $t = $i / [double]$SampleRate
        $val = [math]::Sin(2 * [math]::PI * $FrequencyHz * $t) * $Amplitude
        $sample = [int][math]::Round($val * 32767)
        $bw.Write([int16]$sample)
        for ($c = 1; $c -lt $Channels; $c++) { $bw.Write([int16]$sample) }
    }

    $bw.Flush(); $bw.Dispose(); $fs.Dispose()
}

function Get-RmsDelta {
    param([byte[]]$A, [byte[]]$B)
    if ($A.Length -ne $B.Length) { return 1.0 }
    $sum = 0.0
    for ($i = 44; $i -lt $A.Length; $i += 2) {
        $sa = [BitConverter]::ToInt16($A, $i)
        $sb = [BitConverter]::ToInt16($B, $i)
        $d = $sa - $sb
        $sum += ($d * $d)
    }
    $n = [double](([math]::Max(0, $A.Length - 44)) / 2)
    if ($n -le 0) { return 0.0 }
    return [math]::Sqrt($sum / $n) / 32767.0
}

$root = Get-ProgramDataVoiceStudioPath
$eval = Join-Path $root 'eval'
if (-not (Test-Path $eval)) { New-Item -Path $eval -ItemType Directory | Out-Null }

$wavA = Join-Path $eval 'A.wav'
$wavB = Join-Path $eval 'B.wav'

New-SineWaveWav -Path $wavA -DurationSec 2 -FrequencyHz 440 -Amplitude 0.25
New-SineWaveWav -Path $wavB -DurationSec 2 -FrequencyHz 440 -Amplitude 0.20

if ($WithMetrics) {
    $ba = [System.IO.File]::ReadAllBytes($wavA)
    $bb = [System.IO.File]::ReadAllBytes($wavB)
    $rms = Get-RmsDelta -A $ba -B $bb
    $metrics = @{ timestamp = (Get-Date).ToString('s'); rmsDelta = [math]::Round($rms,6) } | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText((Join-Path $eval 'metrics.json'), $metrics)
}

Write-Host "Eval WAVs created in $eval"
