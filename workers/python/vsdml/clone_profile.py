#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="reference audio file")
    ap.add_argument("--out", dest="out", required=True, help="output profile directory")
    ap.add_argument("--owner", default="")
    ap.add_argument("--source", default="Self")
    args = ap.parse_args()

    inp = Path(args.inp)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        print(f"reference audio not found: {inp}", file=sys.stderr)
        sys.exit(2)

    # Copy reference audio into profile for provenance
    ref_dest = out_dir / inp.name
    if inp.resolve() != ref_dest.resolve():
        try:
            shutil.copy2(str(inp), str(ref_dest))
        except Exception as e:
            print(f"failed to copy reference: {e}", file=sys.stderr)

    prov = {
        "profile": out_dir.name,
        "owner": args.owner,
        "source": args.source,
        "consent": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_file": str(ref_dest if ref_dest.exists() else inp),
        "provenance": {
            "tool": "VoiceStudio",
            "version": "1.0.0",
            "method": "clone_profile_ref_audio_only",
        },
    }

    prov_path = out_dir / "provenance.json"
    with open(prov_path, "w", encoding="utf-8") as f:
        json.dump(prov, f, indent=2)

    # Model artifact placeholder to unblock UI/demo
    model_meta = out_dir / "profile.json"
    with open(model_meta, "w", encoding="utf-8") as f:
        json.dump({"name": out_dir.name, "created": prov["timestamp"]}, f, indent=2)

    # Print outputs so host runner can collect paths
    print(str(prov_path))
    print(str(model_meta))


if __name__ == "__main__":
    main()
