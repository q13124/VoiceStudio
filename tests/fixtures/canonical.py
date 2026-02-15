"""
Canonical test audio paths, validation, and manifest utilities.

The canonical test audio (Allan Watts) is the standard reference for voice cloning,
transcription, and synthesis tests.
"""

from __future__ import annotations

import json
from pathlib import Path

# Base paths
TESTS_DIR = Path(__file__).resolve().parent.parent
CANONICAL_AUDIO_DIR = TESTS_DIR / "assets" / "canonical"
MANIFEST_PATH = CANONICAL_AUDIO_DIR / "manifest.json"

# Standard paths
CANONICAL_WAV = CANONICAL_AUDIO_DIR / "standard" / "allan_watts.wav"
CANONICAL_WAV_SEGMENT = CANONICAL_AUDIO_DIR / "standard" / "allan_watts_15s.wav"
CANONICAL_ORIGINAL = CANONICAL_AUDIO_DIR / "originals" / "allan_watts.m4a"


class CanonicalAudioError(Exception):
    """Raised when canonical audio files are missing or corrupted."""

    pass


def get_manifest() -> dict:
    """Load and return the canonical audio manifest."""
    if not MANIFEST_PATH.exists():
        raise CanonicalAudioError(f"Manifest not found: {MANIFEST_PATH}")
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_canonical_wav_path(segment: bool = False, validate: bool = True) -> Path:
    """
    Return path to the standard canonical test audio (WAV).

    Args:
        segment: If True, return the 15-second segment instead of full file.
        validate: If True, raise CanonicalAudioError if file doesn't exist.

    Returns:
        Path to the WAV file.

    Raises:
        CanonicalAudioError: If validate=True and file doesn't exist.
    """
    path = CANONICAL_WAV_SEGMENT if segment else CANONICAL_WAV
    if validate and not path.exists():
        raise CanonicalAudioError(
            f"Canonical WAV not found: {path}\n"
            "Run: ffmpeg -i originals/allan_watts.m4a -acodec pcm_s16le -ar 22050 -ac 1 standard/allan_watts.wav"
        )
    return path


def get_canonical_original_path(validate: bool = True) -> Path:
    """
    Return path to the original canonical test audio (M4A).

    WARNING: Do not modify this file.
    """
    if validate and not CANONICAL_ORIGINAL.exists():
        raise CanonicalAudioError(f"Original M4A not found: {CANONICAL_ORIGINAL}")
    return CANONICAL_ORIGINAL


def get_canonical_duration(segment: bool = False) -> float:
    """Return duration in seconds from manifest."""
    manifest = get_manifest()
    key = "wav_segment" if segment else "wav_full"
    return manifest["canonical_audio"]["formats"][key]["duration_seconds"]


def verify_integrity(path: Path | None = None) -> bool:
    """
    Verify file integrity against manifest SHA256 hash.

    Args:
        path: Specific file to verify. If None, verifies all files.

    Returns:
        True if all verified files match their manifest hashes.
    """
    import hashlib

    manifest = get_manifest()
    files_to_check = []

    if path:
        files_to_check.append(path)
    else:
        files_to_check = [CANONICAL_ORIGINAL, CANONICAL_WAV]
        if CANONICAL_WAV_SEGMENT.exists():
            files_to_check.append(CANONICAL_WAV_SEGMENT)

    for file_path in files_to_check:
        if not file_path.exists():
            return False

        # Find expected hash in manifest
        expected_hash = None
        if "originals" in str(file_path):
            expected_hash = manifest["canonical_audio"]["source"]["sha256"]
        else:
            for fmt in manifest["canonical_audio"]["formats"].values():
                if file_path.name in fmt["path"]:
                    expected_hash = fmt.get("sha256")
                    break

        if not expected_hash or expected_hash.startswith("<"):
            continue  # Skip if hash not yet computed

        actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest().upper()
        if actual_hash != expected_hash.upper():
            return False

    return True
