import argparse
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--speaker", required=True, help="reference speaker WAV/FLAC path")
    ap.add_argument("--out", required=True, help="output WAV path")
    ap.add_argument("--lang", default="en", help="language code, e.g. en, es, fr")
    ap.add_argument("--model", default="tts_models/multilingual/multi-dataset/xtts_v2", help="XTTS model id")
    args = ap.parse_args()

    text = args.text
    speaker = Path(args.speaker)
    out = Path(args.out)

    if not speaker.exists():
        print("speaker reference audio not found", file=sys.stderr)
        sys.exit(3)

    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Lazy imports so that parsing/tests don't require heavy deps
        import torch
        from TTS.api import TTS

        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS(args.model).to(device)
        tts.tts_to_file(text=text, speaker_wav=str(speaker), language=args.lang, file_path=str(out))
    except Exception as e:
        print(f"XTTS synthesis failed: {e}", file=sys.stderr)
        sys.exit(4)

    print(str(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
