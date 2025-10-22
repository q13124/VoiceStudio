"""
Audio metrics computation for VoiceStudio Voice Engine Router
"""
from __future__ import annotations
import json, shutil, subprocess, tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from services.api.voice_engine_router import AudioMetrics, settings

import shutil

def which_path(cmd: str) -> str | None:
    p = shutil.which(cmd)
    return p

def _run(cmd: str, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

def ffmpeg_paths() -> tuple[str, str]:
    """Resolve ffmpeg and ffprobe paths (env override > PATH)."""
    ffmpeg = settings.metrics_ffmpeg_path or which_path("ffmpeg")
    ffprobe = settings.metrics_ffprobe_path or which_path("ffprobe")
    if not ffmpeg or not ffprobe:
        raise FileNotFoundError("ffmpeg/ffprobe not found.")
    return ffmpeg, ffprobe

def compute_metrics_ffmpeg(wav_path: Path) -> AudioMetrics:
    """Preferred: Use ffmpeg loudnorm + astats + silencedetect + ffprobe."""
    ffmpeg, ffprobe = ffmpeg_paths()
    timeout = settings.metrics_timeout_sec

    lufs = lra = true_peak = None
    dc_offset = clip_pct = None
    head_ms = tail_ms = None

    # 1) loudnorm JSON: input_i (LUFS), input_lra, input_tp
    cmd_ln = f'"{ffmpeg}" -hide_banner -nostats -i "{wav_path}" -filter_complex loudnorm=I=-23:TP=-2:LRA=11:print_format=json -f null -'
    try:
        p = _run(cmd_ln, timeout)
        txt = p.stderr
        start, end = txt.find("{"), txt.rfind("}")
        if start != -1 and end != -1 and end > start:
            j = json.loads(txt[start:end+1])
            lufs = float(j.get("input_i")) if j.get("input_i") is not None else None
            lra = float(j.get("input_lra")) if j.get("input_lra") is not None else None
            true_peak = float(j.get("input_tp")) if j.get("input_tp") is not None else None
    except Exception:
        pass

    # 2) astats for DC offset & clip info
    cmd_as = f'"{ffmpeg}" -hide_banner -nostats -i "{wav_path}" -af astats=metadata=1:reset=1 -f null -'
    try:
        p = _run(cmd_as, timeout)
        dc_line = None
        clips_line = None
        for line in p.stderr.splitlines():
            if "DC offset" in line and ":" in line:
                dc_line = line
            if "Number of clips" in line and ":" in line:
                clips_line = line
        if dc_line:
            try:
                dc_val = float(dc_line.split(":")[-1].strip())
                dc_offset = round(dc_val * 100.0, 6)  # %FS
            except Exception:
                pass
        if clips_line:
            try:
                nclips = float(clips_line.split(":")[-1].strip())
                # For most TTS, any clips > 0 is a failure; for a % we need total samples (not cheap).
                clip_pct = 100.0 if nclips > 0 else 0.0
            except Exception:
                pass
    except Exception:
        pass

    # 3) duration via ffprobe
    duration_s = None
    try:
        cmd_dur = f'"{ffprobe}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{wav_path}"'
        q = _run(cmd_dur, timeout)
        duration_s = float(q.stdout.strip())
    except Exception:
        pass

    # 4) silencedetect for head/tail silence
    cmd_sd = f'"{ffmpeg}" -hide_banner -nostats -i "{wav_path}" -af silencedetect=n=-50dB:d=0.02 -f null -'
    try:
        p = _run(cmd_sd, timeout)
        starts, ends = [], []
        for line in p.stderr.splitlines():
            line = line.strip()
            if "silence_start" in line and ":" in line:
                try:
                    starts.append(float(line.split("silence_start:")[1]))
                except Exception:
                    pass
            if "silence_end" in line and ":" in line:
                try:
                    parts = line.split("silence_end:")[1].split(" | ")
                    ends.append(float(parts[0]))
                except Exception:
                    pass
        if duration_s is not None:
            if starts:
                head_ms = int(round(starts[0] * 1000))
            if ends:
                tail = max(0.0, duration_s - ends[-1])
                tail_ms = int(round(tail * 1000))
    except Exception:
        pass

    return AudioMetrics(
        lufs=lufs, lra=lra, true_peak=true_peak,
        clip_pct=clip_pct, dc_offset=dc_offset,
        head_ms=head_ms, tail_ms=tail_ms,
    )

def compute_metrics_fallback(wav_path: Path) -> AudioMetrics:
    """
    Fallback: pyloudnorm (LUFS/LRA) + simple head/tail scan if ffmpeg missing.
    """
    try:
        import soundfile as sf
        import pyloudnorm as pyln
        import numpy as np
    except Exception:
        # No fallback libs installed
        return AudioMetrics()

    try:
        data, sr = sf.read(str(wav_path))
        if data.ndim > 1:
            data = data.mean(axis=1)
        meter = pyln.Meter(sr)  # EBU R128
        lufs = float(meter.integrated_loudness(data))
        lra = float(meter.loudness_range(data))
        # crude head/tail silence (RMS threshold)
        rms = np.sqrt(np.convolve(data**2, np.ones(sr//100)/ (sr//100), mode='same'))
        thr = 1e-4
        nz = np.where(rms > thr)[0]
        if nz.size:
            head_ms = int(1000 * nz[0] / sr)
            tail_ms = int(1000 * (len(data) - nz[-1]) / sr)
        else:
            head_ms = tail_ms = int(1000 * len(data) / sr)
        return AudioMetrics(lufs=lufs, lra=lra, head_ms=head_ms, tail_ms=tail_ms)
    except Exception:
        return AudioMetrics()

def compute_audio_metrics(wav_path: Path) -> AudioMetrics:
    """Top-level—prefer FFmpeg; fall back if unavailable."""
    try:
        return compute_metrics_ffmpeg(wav_path)
    except Exception:
        return compute_metrics_fallback(wav_path)
