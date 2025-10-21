import argparse
import json
import math
import wave
import struct
from pathlib import Path


def synth_tone_wav(out_path: Path, seconds: float = 1.0, freq_hz: float = 440.0, sample_rate: int = 24000, amplitude: float = 0.2):
    num_samples = int(seconds * sample_rate)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for n in range(num_samples):
            t = n / sample_rate
            s = amplitude * math.sin(2 * math.pi * freq_hz * t)
            wf.writeframes(struct.pack('<h', int(max(-1.0, min(1.0, s)) * 32767)))


def main():
    ap = argparse.ArgumentParser(description="VoiceStudio worker router (minimal)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_tts = sub.add_parser("tts", help="Synthesize TTS to wav")
    ap_tts.add_argument("--a", dest="text", required=True)
    ap_tts.add_argument("--b", dest="out", required=True)
    ap_tts.add_argument("--c", dest="config_json", default="{}")

    args = ap.parse_args()

    if args.cmd == "tts":
        try:
            cfg = json.loads(args.config_json or "{}")
        except Exception:
            cfg = {}
        # Placeholder: synthesize a short tone as the TTS output so the harness works cross-platform
        out = Path(args.out)
        dur = float(cfg.get("dur", 1.0)) if isinstance(cfg, dict) else 1.0
        synth_tone_wav(out, seconds=dur)
        print(str(out))
        return


if __name__ == "__main__":
    main()
