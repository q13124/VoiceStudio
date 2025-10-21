import argparse
import hashlib
import subprocess
from pathlib import Path


def embed_watermark(input_wav: str, output_wav: str, key: str) -> None:
    # Deterministic seed from key
    seed_int = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16)

    # Generate a very low-level high-frequency noise bed and mix with original
    # - Use anoisesrc with fixed sample rate; mix using shortest duration
    # - Highpass to keep it out of the audible voice band mostly
    # - Keep level extremely low (~ -30 to -40 dB)
    # Note: anoisesrc duration is long; mix uses shortest to clamp to input length.
    filter_complex = (
        f"anoisesrc=r=48000:c=pink:seed={seed_int},volume=0.02,highpass=f=9000[wm];"
        f"[0:a][wm]amix=inputs=2:weights=1 0.03:duration=shortest,alimiter=limit=0.98"
    )

    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_wav,
        "-filter_complex", filter_complex,
        "-metadata", f"comment=wm-key:{key}",
        "-c:a", "pcm_s16le",
        output_wav,
    ], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed a subtle watermark keyed by a policy key")
    parser.add_argument("--in", dest="inp", required=True, help="Input WAV path")
    parser.add_argument("--out", dest="out", required=True, help="Output WAV path")
    parser.add_argument("--key", dest="key", required=True, help="Policy watermark key")
    args = parser.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    embed_watermark(args.inp, args.out, args.key)
    print(args.out)


if __name__ == "__main__":
    main()
