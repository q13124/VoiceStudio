import argparse
import json
import subprocess
from pathlib import Path


def repair_artifacts(input_wav: str, heatmap_json: str, output_wav: str, threshold: float) -> None:
    heatmap_path = Path(heatmap_json)
    if not heatmap_path.exists():
        # If no heatmap, just re-mux to target format and return
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_wav,
            "-c:a", "pcm_s16le",
            output_wav,
        ], check=True)
        return

    with heatmap_path.open("r", encoding="utf-8") as f:
        heat = json.load(f)

    # Gather suspicious timestamps where synthetic probability exceeds threshold
    suspicious_times = []
    for point in heat:
        try:
            t = float(point.get("t", point.get("time", 0.0)))
            synthetic = float(point.get("synthetic", point.get("p", 0.0)))
            if synthetic >= threshold:
                suspicious_times.append(t)
        except Exception:
            continue

    if not suspicious_times:
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", input_wav,
            "-c:a", "pcm_s16le",
            output_wav,
        ], check=True)
        return

    # Merge short windows around suspicious times (30ms before, 50ms after)
    windows = []
    for t in suspicious_times:
        start = max(0.0, t - 0.03)
        end = t + 0.05
        windows.append((start, end))
    windows.sort()
    merged_windows = []
    for start, end in windows:
        if not merged_windows or start > merged_windows[-1][1]:
            merged_windows.append([start, end])
        else:
            merged_windows[-1][1] = max(merged_windows[-1][1], end)

    # For a first implementation, apply a gentle global cleanup that is safe:
    # - Light FFT denoise
    # - De-esser
    # - Limiter to avoid overs
    # This is intentionally conservative; future versions can splice/xfade windows.
    audio_filter = "afftdn=nf=-20:nt=w, deesser=i=4, alimiter=limit=0.98"

    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_wav,
        "-af", audio_filter,
        "-c:a", "pcm_s16le",
        output_wav,
    ], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Artifact repair using heatmap guidance")
    parser.add_argument("--in", dest="inp", required=True, help="Input WAV path")
    parser.add_argument("--heat", dest="heat", required=True, help="Heatmap JSON path")
    parser.add_argument("--out", dest="out", required=True, help="Output WAV path")
    parser.add_argument("--threshold", type=float, default=0.75, help="Synthetic threshold [0..1]")
    args = parser.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    repair_artifacts(args.inp, args.heat, args.out, args.threshold)
    print(args.out)


if __name__ == "__main__":
    main()
