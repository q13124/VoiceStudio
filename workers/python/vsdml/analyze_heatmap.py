#!/usr/bin/env python3
import argparse
import contextlib
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import wave
from pathlib import Path


def get_duration_ffprobe(path: Path):
    try:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        return float(out)
    except Exception:
        return None


def get_duration_wave(path: Path):
    try:
        with contextlib.closing(wave.open(str(path), "rb")) as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--latency-ms", dest="latency_ms", type=int, default=50)
    args = ap.parse_args()

    inp = Path(args.inp)
    out_json = Path(args.out)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        print(f"input audio not found: {inp}", file=sys.stderr)
        sys.exit(2)

    dur = get_duration_ffprobe(inp)
    if dur is None:
        dur = get_duration_wave(inp)
    if dur is None or dur <= 0:
        print("could not read audio duration", file=sys.stderr)
        sys.exit(3)

    # Deterministic pseudo-random based on file path for stable preview
    h = hashlib.sha1(str(inp).encode("utf-8")).hexdigest()
    seed = int(h[:8], 16)
    rng = random.Random(seed)

    # Simple synthetic score: sin-based envelope + light noise
    # Generate ~400 columns max for responsiveness
    num_points = max(50, min(400, int(dur * 50)))  # ~20ms per column
    points = []
    for i in range(num_points):
        t = (i / max(1, num_points - 1)) * dur
        base = 0.5 + 0.4 * math.sin(2 * math.pi * (i / num_points) * 3.0)
        jitter = (rng.random() - 0.5) * 0.1
        synthetic = max(0.0, min(1.0, base + jitter))
        points.append({"t": round(t, 3), "synthetic": round(synthetic, 3)})

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(points, f, indent=2)

    # Print the output path so the host can capture it
    print(str(out_json))


if __name__ == "__main__":
    main()
