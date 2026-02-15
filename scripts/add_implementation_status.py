#!/usr/bin/env python3
"""
GAP-ENG-001: Add implementation_status to all engine manifests.

This script scans all engine.manifest.json files and adds implementation_status
if missing. The status is determined by analyzing the engine implementation.
"""

import json
from pathlib import Path
from typing import Any


def determine_implementation_status(manifest: dict[str, Any], engine_dir: Path) -> str:
    """
    Determine the implementation status based on manifest and engine files.

    Returns:
        'full' - Fully implemented with all features
        'basic' - Basic functionality, some features missing
        'placeholder' - Stub or minimal implementation
        'external' - Delegates to external tool
    """
    # Check if already has status
    if "implementation_status" in manifest:
        return manifest["implementation_status"]

    engine_id = manifest.get("engine_id", manifest.get("id", ""))

    # Known full implementations
    full_engines = {
        "xtts_v2", "silero", "piper", "whisper", "whisper_cpp", "vosk",
        "openai_tts", "openai_chat", "ollama", "espeak_ng", "rvc", "rvc_v2",
        "bark", "tortoise", "f5_tts", "chatterbox", "aeneas", "so_vits_svc",
    }

    # Known external tool integrations
    external_engines = {
        "comfyui", "automatic1111", "invokeai", "sdnext", "fooocus",
        "deepfacelab", "sadtalker", "deforum", "fomm", "localai",
        "ffmpeg_ai", "moviepy", "svd",
    }

    # Known placeholder/stub implementations
    placeholder_engines = {
        "mars5", "parler_tts", "openvoice_v2", "fish_speech",
        "lyrebird", "voice_ai", "higgs_audio", "voxcpm",
        "video_creator", "openjourney", "realistic_vision",
        "fastsd_cpu", "sd_cpu",
    }

    if engine_id in full_engines:
        return "full"
    elif engine_id in external_engines:
        return "external"
    elif engine_id in placeholder_engines:
        return "placeholder"

    # Check for engine.py file - if substantial, likely at least basic
    engine_py = engine_dir / "engine.py"
    if engine_py.exists():
        try:
            content = engine_py.read_text(encoding="utf-8", errors="ignore")
            lines = len([l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")])
            if lines > 100:
                return "full"
            elif lines > 30:
                return "basic"
            else:
                return "placeholder"
        except Exception as e:
            # Could not read file to determine implementation level
            import logging
            logging.getLogger(__name__).debug(f"Could not analyze file for implementation status: {e}")

    # Default to basic
    return "basic"


def get_implementation_notes(status: str, manifest: dict[str, Any]) -> str:
    """Get implementation notes based on status."""
    engine_id = manifest.get("engine_id", manifest.get("id", ""))

    notes_map = {
        "full": f"Fully implemented {manifest.get('type', 'engine')} engine.",
        "basic": "Basic implementation. Some advanced features may be missing.",
        "placeholder": "Returns default/silence when dependencies unavailable. Requires package installation.",
        "external": f"Delegates to external tool. Requires {engine_id} to be installed and running.",
    }

    return notes_map.get(status, "")


def process_manifest(manifest_path: Path) -> bool:
    """
    Process a single manifest file, adding implementation_status if missing.

    Returns:
        True if file was modified, False otherwise.
    """
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"  ERROR reading {manifest_path}: {e}")
        return False

    # Skip if already has implementation_status
    if "implementation_status" in manifest:
        print(f"  SKIP: Already has implementation_status: {manifest['implementation_status']}")
        return False

    engine_dir = manifest_path.parent
    status = determine_implementation_status(manifest, engine_dir)
    notes = get_implementation_notes(status, manifest)

    # Add implementation_status after the last existing field
    manifest["implementation_status"] = status
    if notes:
        manifest["implementation_notes"] = notes

    # Write back
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"  ADDED: implementation_status={status}")
        return True
    except Exception as e:
        print(f"  ERROR writing {manifest_path}: {e}")
        return False


def main():
    """Main entry point."""
    engines_dir = Path(__file__).parent.parent / "engines"

    if not engines_dir.exists():
        print(f"Engines directory not found: {engines_dir}")
        return

    # Find all manifest files
    manifests = list(engines_dir.rglob("engine.manifest.json"))
    print(f"Found {len(manifests)} engine manifests")

    modified = 0
    skipped = 0
    errors = 0

    for manifest_path in sorted(manifests):
        rel_path = manifest_path.relative_to(engines_dir)
        print(f"\nProcessing: {rel_path}")

        result = process_manifest(manifest_path)
        if result:
            modified += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1

    print(f"\n{'='*50}")
    print("Summary:")
    print(f"  Modified: {modified}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")
    print(f"  Total:    {len(manifests)}")


if __name__ == "__main__":
    main()
