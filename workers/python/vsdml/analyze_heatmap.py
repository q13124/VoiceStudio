#!/usr/bin/env python3
import argparse
import json
import os
import sys
import wave
import contextlib
import struct
from typing import List, Tuple


def read_rms_series(wav_path: str, window_ms: float = 50.0) -> Tuple[List[float], float]:
    """Read a mono or stereo WAV and compute RMS per window.

    Returns a tuple of (rms_values, duration_seconds).
    """
    with contextlib.closing(wave.open(wav_path, 'rb')) as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        duration_s = n_frames / float(sample_rate) if sample_rate > 0 else 0.0

    # Reopen for streaming read
    with contextlib.closing(wave.open(wav_path, 'rb')) as wf:
        hop = max(1, int(sample_rate * (window_ms / 1000.0)))
        frame_format = {1: 'b', 2: 'h', 3: None, 4: 'i'}.get(sample_width)
        if frame_format is None:
            # Fallback: treat 24-bit as 16-bit by truncation
            frame_format = 'h'
        rms_values: List[float] = []
        max_rms = 1e-9
        while True:
            frames = wf.readframes(hop)
            if not frames:
                break
            # Convert frames to samples
            try:
                count = len(frames) // sample_width
                if count == 0:
                    break
                fmt = '<' + frame_format * count
                samples = struct.unpack(fmt, frames[: struct.calcsize(fmt)])
            except Exception:
                # If unpack fails, stop
                break

            # If stereo, downmix to mono by averaging
            if n_channels > 1:
                mono = []
                for i in range(0, len(samples), n_channels):
                    chunk = samples[i:i+n_channels]
                    if not chunk:
                        continue
                    mono.append(sum(chunk) / float(len(chunk)))
            else:
                mono = samples

            # Compute RMS
            acc = 0.0
            for s in mono:
                acc += float(s) * float(s)
            rms = (acc / max(1, len(mono))) ** 0.5
            max_rms = max(max_rms, rms)
            rms_values.append(rms)

        # Normalize to [0,1]
        if max_rms <= 0:
            norm = [0.0 for _ in rms_values]
        else:
            norm = [min(1.0, r / max_rms) for r in rms_values]

        return norm, duration_s


def main() -> int:
    p = argparse.ArgumentParser(description='Compute simple syntheticness heatmap from audio.')
    p.add_argument('--in', dest='in_path', required=True, help='Input WAV file path')
    p.add_argument('--out', dest='out_path', required=True, help='Output JSON path for heatmap array')
    p.add_argument('--latency_ms', dest='latency_ms', type=int, default=50)
    args = p.parse_args()

    in_path = os.path.abspath(args.in_path)
    out_path = os.path.abspath(args.out_path)

    # Compute RMS series as a proxy feature and map to a pseudo "synthetic" score
    # This is a placeholder heuristic intended for visualization only.
    try:
        series, duration = read_rms_series(in_path, window_ms=max(10, min(200, args.latency_ms)))
    except wave.Error as e:
        print(f"Failed to read WAV: {e}", file=sys.stderr)
        series, duration = [], 0.0

    # Map RMS to synthetic score using a non-linear curve to accentuate differences
    # synthetic = sqrt(rms_norm) with light smoothing
    import math

    # Light smoothing with a simple moving average
    smoothed: List[float] = []
    k = 3
    for i in range(len(series)):
        acc = 0.0
        cnt = 0
        for j in range(max(0, i-k), min(len(series), i+k+1)):
            acc += series[j]
            cnt += 1
        smoothed.append(math.sqrt(acc / max(1, cnt)))

    heat = []
    if len(smoothed) > 0 and duration > 0:
        step = duration / float(len(smoothed))
        for idx, val in enumerate(smoothed):
            t = idx * step
            heat.append({'t': float(t), 'synthetic': float(max(0.0, min(1.0, val)))})

    # Ensure directory exists
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(heat, f)

    # Print output path so the host can collect it
    print(out_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
