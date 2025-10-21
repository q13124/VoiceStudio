#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).parent
OPS_DIR = Path(__file__).parent.parent / "workers" / "ops"
ROUTER = Path(__file__).parent.parent / "workers" / "worker_router.py"


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return p.stdout.strip()


def synth(text: str, out_path: Path, stability: float):
    cfg = json.dumps({"engine": "xtts", "stability": stability})
    cmd = [sys.executable, str(ROUTER), "tts", "--a", text, "--b", str(out_path), "--c", cfg]
    run(cmd)


def main():
    ap = argparse.ArgumentParser(description="A/B compare CLI")
    ap.add_argument("text", help="Sample text")
    ap.add_argument("--a", dest="stab_a", type=float, default=0.60)
    ap.add_argument("--b", dest="stab_b", type=float, default=0.75)
    ap.add_argument("--out", dest="out_dir", default=None)
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else Path(tempfile.gettempdir())
    out_dir.mkdir(parents=True, exist_ok=True)
    a = out_dir / "ab_A.wav"
    b = out_dir / "ab_B.wav"
    synth(args.text, a, args.stab_a)
    synth(args.text, b, args.stab_b)

    dst = out_dir / "ab_delta.wav"
    ab_null = OPS_DIR / "ab_null.py"
    run([sys.executable, str(ab_null), str(a), str(b), str(dst)])

    print(json.dumps({
        "A": str(a),
        "B": str(b),
        "delta": str(dst)
    }))


if __name__ == "__main__":
    main()
