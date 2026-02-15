#!/usr/bin/env python3
# Copyright (c) VoiceStudio. All rights reserved.
# Licensed under the MIT License.

"""
Add Contract Specifications to Engine Manifests.

Adds standardized contract specs to all engine manifests that don't have them.

Usage:
    python scripts/add_engine_contracts.py
    python scripts/add_engine_contracts.py --dry-run  # Preview changes
"""

import json
import sys
from pathlib import Path
from typing import Any

from _env_setup import PROJECT_ROOT

# Default contract templates by engine type
CONTRACT_TEMPLATES = {
    "tts": {
        "input": {
            "audio_formats": ["wav", "mp3", "flac"],
            "sample_rates": [16000, 22050, 24000, 44100],
            "max_duration_seconds": 30,
            "text_max_chars": 5000
        },
        "output": {
            "audio_format": "wav",
            "sample_rate": 22050,
            "bit_depth": 16,
            "channels": 1
        },
        "resources": {
            "vram_mb": 4096,
            "ram_mb": 4096,
            "timeout_seconds": 120
        }
    },
    "stt": {
        "input": {
            "audio_formats": ["wav", "mp3", "flac", "ogg", "m4a"],
            "sample_rates": [8000, 16000, 22050, 44100, 48000],
            "max_duration_seconds": 3600,
            "min_duration_seconds": 0.1
        },
        "output": {
            "format": "json",
            "includes": ["text", "segments", "timestamps"]
        },
        "resources": {
            "vram_mb": 2048,
            "ram_mb": 4096,
            "timeout_seconds": 300
        }
    },
    "voice_conversion": {
        "input": {
            "audio_formats": ["wav", "mp3", "flac"],
            "sample_rates": [16000, 22050, 44100, 48000],
            "max_duration_seconds": 60
        },
        "output": {
            "audio_format": "wav",
            "sample_rate": 44100,
            "bit_depth": 16,
            "channels": 1
        },
        "resources": {
            "vram_mb": 6144,
            "ram_mb": 8192,
            "timeout_seconds": 180
        }
    },
    "image": {
        "input": {
            "image_formats": ["png", "jpg", "webp"],
            "max_resolution": "2048x2048",
            "prompt_max_chars": 2000
        },
        "output": {
            "image_format": "png",
            "default_resolution": "512x512"
        },
        "resources": {
            "vram_mb": 8192,
            "ram_mb": 16384,
            "timeout_seconds": 300
        }
    },
    "video": {
        "input": {
            "video_formats": ["mp4", "webm", "avi"],
            "audio_formats": ["wav", "mp3"],
            "max_duration_seconds": 300
        },
        "output": {
            "video_format": "mp4",
            "codec": "h264",
            "default_fps": 24
        },
        "resources": {
            "vram_mb": 8192,
            "ram_mb": 16384,
            "timeout_seconds": 600
        }
    }
}


def get_engine_type(manifest: dict[str, Any]) -> str:
    """Determine engine type from manifest."""
    engine_type = manifest.get("type", "audio")
    subtype = manifest.get("subtype", "")

    if subtype == "tts":
        return "tts"
    elif subtype == "stt" or subtype == "transcription":
        return "stt"
    elif subtype == "voice_conversion" or subtype == "rvc":
        return "voice_conversion"
    elif engine_type == "image":
        return "image"
    elif engine_type == "video":
        return "video"
    else:
        return "tts"  # Default


def add_contract_to_manifest(manifest_path: Path, dry_run: bool = False) -> bool:
    """
    Add contract to a manifest file if it doesn't have one.

    Returns True if contract was added (or would be added in dry-run).
    """
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"  Error reading {manifest_path}: {e}")
        return False

    # Skip if already has contract
    if "contract" in manifest:
        return False

    # Determine engine type and get template
    engine_type = get_engine_type(manifest)
    contract = CONTRACT_TEMPLATES.get(engine_type, CONTRACT_TEMPLATES["tts"])

    # Customize based on manifest hints
    if "device_requirements" in manifest:
        req = manifest["device_requirements"]
        if "vram_min_gb" in req:
            contract["resources"]["vram_mb"] = req["vram_min_gb"] * 1024
        if "ram_min_gb" in req:
            contract["resources"]["ram_mb"] = req["ram_min_gb"] * 1024

    # Add contract to manifest
    manifest["contract"] = contract

    if dry_run:
        print(f"  Would add contract to {manifest_path.name} ({engine_type})")
        return True

    # Write updated manifest
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
        print(f"  Added contract to {manifest_path.name} ({engine_type})")
        return True
    except Exception as e:
        print(f"  Error writing {manifest_path}: {e}")
        return False


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 70)
    print("Engine Manifest Contract Addition")
    print("=" * 70)
    print()

    if dry_run:
        print("DRY RUN - No files will be modified")
        print()

    engines_dir = PROJECT_ROOT / "engines"
    manifest_files = list(engines_dir.rglob("engine.manifest.json"))

    print(f"Found {len(manifest_files)} engine manifests")
    print()

    added = 0
    skipped = 0

    for manifest_path in sorted(manifest_files):
        if add_contract_to_manifest(manifest_path, dry_run):
            added += 1
        else:
            skipped += 1

    print()
    print("-" * 70)
    print(f"Added contracts: {added}")
    print(f"Already had contracts: {skipped}")
    print("-" * 70)

    if dry_run and added > 0:
        print()
        print("Run without --dry-run to apply changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
