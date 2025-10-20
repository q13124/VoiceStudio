#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone


def main() -> int:
    p = argparse.ArgumentParser(description='Create a simple voice clone profile directory with provenance.')
    p.add_argument('--ref', dest='ref_audio', required=True, help='Reference audio file path')
    p.add_argument('--out', dest='out_dir', required=True, help='Output profile directory')
    p.add_argument('--opts', dest='opts_json', default='{}', help='Options JSON string (owner, source, consent)')
    args = p.parse_args()

    ref_audio = os.path.abspath(args.ref_audio)
    out_dir = os.path.abspath(args.out_dir)

    try:
        opts = json.loads(args.opts_json) if args.opts_json else {}
    except Exception:
        opts = {}

    os.makedirs(out_dir, exist_ok=True)

    # Copy reference audio for provenance/debug
    ref_basename = os.path.basename(ref_audio)
    copied_ref = os.path.join(out_dir, ref_basename)
    try:
        shutil.copy2(ref_audio, copied_ref)
    except Exception as e:
        print(f"Warning: failed to copy ref audio: {e}", file=sys.stderr)

    # Write provenance.json
    prov = {
        'profile': os.path.basename(out_dir),
        'owner': opts.get('owner', ''),
        'source': opts.get('source', 'Self'),
        'consent': bool(opts.get('consent', True)),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'input_file': copied_ref if os.path.exists(copied_ref) else ref_audio,
        'provenance': {
            'tool': 'VoiceStudio',
            'version': os.environ.get('VOICESTUDIO_VERSION', '0.1.0'),
            'method': 'clone_profile_ref_audio_only'
        }
    }
    with open(os.path.join(out_dir, 'provenance.json'), 'w', encoding='utf-8') as f:
        json.dump(prov, f, indent=2)

    # Touch a placeholder model manifest to indicate a valid profile
    with open(os.path.join(out_dir, 'profile.manifest.json'), 'w', encoding='utf-8') as f:
        json.dump({'status': 'ready', 'created_utc': prov['timestamp']}, f, indent=2)

    # Print artifact path so the host can capture it
    print(out_dir)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
