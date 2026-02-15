#!/usr/bin/env python
"""
VoiceStudio Complete Model Download Script

Downloads all required models for local operation.
Estimated total size: ~15-20 GB

Models downloaded:
- XTTS v2 (multilingual TTS) - ~2 GB
- Piper voices (fast local TTS) - ~500 MB
- Whisper models (STT) - ~3 GB
- Silero VAD (voice activity detection) - ~10 MB
- Speaker encoder (voice similarity) - ~20 MB

Usage:
    python scripts/download_all_models.py
    python scripts/download_all_models.py --engine xtts
    python scripts/download_all_models.py --list
"""

import argparse
import logging
import sys
import urllib.request
from pathlib import Path

from _env_setup import PROJECT_ROOT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Model registry - all models with download info
MODEL_REGISTRY: dict[str, dict] = {
    # ========== TTS Models ==========
    "xtts_v2": {
        "name": "XTTS v2 (Coqui)",
        "description": "Multilingual voice cloning TTS",
        "size": "~2 GB",
        "method": "coqui_tts",
        "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
        "local_path": "models/xtts",
    },
    "piper_amy": {
        "name": "Piper Amy (US English)",
        "description": "Fast local TTS - Amy medium quality",
        "size": "~65 MB",
        "method": "url",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json",
        "local_path": "models/piper/en_US-amy-medium.onnx",
        "local_json": "models/piper/en_US-amy-medium.onnx.json",
    },
    "piper_lessac": {
        "name": "Piper Lessac (US English)",
        "description": "Fast local TTS - Lessac medium quality",
        "size": "~65 MB",
        "method": "url",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "json_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
        "local_path": "models/piper/en_US-lessac-medium.onnx",
        "local_json": "models/piper/en_US-lessac-medium.onnx.json",
    },

    # ========== STT Models ==========
    "whisper_base": {
        "name": "Whisper Base",
        "description": "Fast transcription model",
        "size": "~150 MB",
        "method": "faster_whisper",
        "model_size": "base",
        "local_path": "models/whisper/base",
    },
    "whisper_small": {
        "name": "Whisper Small",
        "description": "Balanced speed/accuracy",
        "size": "~500 MB",
        "method": "faster_whisper",
        "model_size": "small",
        "local_path": "models/whisper/small",
    },
    "whisper_medium": {
        "name": "Whisper Medium",
        "description": "High accuracy transcription",
        "size": "~1.5 GB",
        "method": "faster_whisper",
        "model_size": "medium",
        "local_path": "models/whisper/medium",
    },
    "whisper_large_v3": {
        "name": "Whisper Large v3",
        "description": "Best accuracy (recommended)",
        "size": "~3 GB",
        "method": "faster_whisper",
        "model_size": "large-v3",
        "local_path": "models/whisper/large-v3",
    },

    # ========== Voice Analysis Models ==========
    "silero_vad": {
        "name": "Silero VAD",
        "description": "Voice activity detection",
        "size": "~10 MB",
        "method": "torch_hub",
        "repo": "snakers4/silero-vad",
        "model": "silero_vad",
        "local_path": "models/silero/vad",
    },
    "resemblyzer": {
        "name": "Resemblyzer Speaker Encoder",
        "description": "Voice similarity and speaker verification",
        "size": "~20 MB",
        "method": "resemblyzer",
        "local_path": "models/resemblyzer",
    },
}


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file with progress."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading {desc or url}...")

        def progress_hook(count, block_size, total_size):
            if total_size > 0:
                percent = min(100, count * block_size * 100 / total_size)
                print(f"\r  Progress: {percent:.1f}%", end="", flush=True)

        urllib.request.urlretrieve(url, dest, progress_hook)
        print()  # Newline after progress
        logger.info(f"  Saved to: {dest}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False


def download_xtts() -> bool:
    """Download XTTS v2 model using Coqui TTS."""
    try:
        from TTS.api import TTS

        logger.info("Downloading XTTS v2 model (this may take a while)...")
        # This will download to ~/.local/share/tts or equivalent
        TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        logger.info("XTTS v2 model downloaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to download XTTS v2: {e}")
        return False


def download_faster_whisper(model_size: str, local_path: Path) -> bool:
    """Download Faster Whisper model."""
    try:
        from faster_whisper import WhisperModel

        logger.info(f"Downloading Whisper {model_size} model...")
        local_path.mkdir(parents=True, exist_ok=True)

        # This downloads to HuggingFace cache and we copy to local
        WhisperModel(model_size, device="cpu", compute_type="int8")
        logger.info(f"Whisper {model_size} model ready!")
        return True
    except Exception as e:
        logger.error(f"Failed to download Whisper {model_size}: {e}")
        return False


def download_silero_vad() -> bool:
    """Download Silero VAD model."""
    try:
        import torch

        logger.info("Downloading Silero VAD model...")
        _model, _utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=False,
        )
        logger.info("Silero VAD model downloaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to download Silero VAD: {e}")
        return False


def download_resemblyzer() -> bool:
    """Download Resemblyzer speaker encoder."""
    try:
        from resemblyzer import VoiceEncoder

        logger.info("Downloading Resemblyzer speaker encoder...")
        VoiceEncoder()
        logger.info("Resemblyzer speaker encoder ready!")
        return True
    except Exception as e:
        logger.error(f"Failed to download Resemblyzer: {e}")
        return False


def download_model(model_id: str) -> bool:
    """Download a specific model by ID."""
    if model_id not in MODEL_REGISTRY:
        logger.error(f"Unknown model: {model_id}")
        return False

    model = MODEL_REGISTRY[model_id]
    logger.info(f"\n{'='*60}")
    logger.info(f"Downloading: {model['name']}")
    logger.info(f"Description: {model['description']}")
    logger.info(f"Size: {model['size']}")
    logger.info(f"{'='*60}")

    method = model["method"]

    if method == "coqui_tts":
        return download_xtts()

    elif method == "url":
        local_path = PROJECT_ROOT / model["local_path"]
        success = download_file(model["url"], local_path, model["name"])
        if success and "json_url" in model:
            json_path = PROJECT_ROOT / model["local_json"]
            download_file(model["json_url"], json_path, f"{model['name']} config")
        return success

    elif method == "faster_whisper":
        local_path = PROJECT_ROOT / model["local_path"]
        return download_faster_whisper(model["model_size"], local_path)

    elif method == "torch_hub":
        return download_silero_vad()

    elif method == "resemblyzer":
        return download_resemblyzer()

    else:
        logger.error(f"Unknown download method: {method}")
        return False


def list_models():
    """List all available models."""
    print("\n" + "=" * 70)
    print("Available Models for VoiceStudio")
    print("=" * 70)

    categories = {
        "TTS (Text-to-Speech)": ["xtts_v2", "piper_amy", "piper_lessac"],
        "STT (Speech-to-Text)": ["whisper_base", "whisper_small", "whisper_medium", "whisper_large_v3"],
        "Voice Analysis": ["silero_vad", "resemblyzer"],
    }

    for category, model_ids in categories.items():
        print(f"\n{category}:")
        print("-" * 50)
        for model_id in model_ids:
            model = MODEL_REGISTRY.get(model_id, {})
            model.get("name", model_id)
            size = model.get("size", "Unknown")
            desc = model.get("description", "")
            print(f"  {model_id:<20} {size:<12} {desc}")

    print("\n" + "=" * 70)
    print("Usage:")
    print("  python scripts/download_all_models.py                # Download all")
    print("  python scripts/download_all_models.py --engine xtts  # Download XTTS only")
    print("  python scripts/download_all_models.py --essential    # Download essential set")
    print("=" * 70 + "\n")


def download_essential():
    """Download essential models for basic operation."""
    essential = ["xtts_v2", "piper_amy", "whisper_base", "silero_vad", "resemblyzer"]

    logger.info("Downloading ESSENTIAL models for basic VoiceStudio operation...")
    logger.info(f"Models: {', '.join(essential)}")

    success = 0
    for model_id in essential:
        if download_model(model_id):
            success += 1

    logger.info(f"\nCompleted: {success}/{len(essential)} essential models downloaded")
    return success == len(essential)


def download_all():
    """Download all models."""
    logger.info("Downloading ALL models (this will take significant time and disk space)...")

    success = 0
    total = len(MODEL_REGISTRY)

    for model_id in MODEL_REGISTRY:
        if download_model(model_id):
            success += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Download Complete: {success}/{total} models downloaded")
    logger.info(f"{'='*60}")
    return success == total


def main():
    parser = argparse.ArgumentParser(description="Download VoiceStudio models")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--engine", type=str, help="Download specific engine model")
    parser.add_argument("--essential", action="store_true", help="Download essential models only")
    parser.add_argument("--all", action="store_true", help="Download all models")

    args = parser.parse_args()

    if args.list:
        list_models()
        return 0

    if args.engine:
        # Map common names to model IDs
        engine_map = {
            "xtts": "xtts_v2",
            "xtts_v2": "xtts_v2",
            "piper": "piper_amy",
            "whisper": "whisper_base",
            "whisper-base": "whisper_base",
            "whisper-small": "whisper_small",
            "whisper-medium": "whisper_medium",
            "whisper-large": "whisper_large_v3",
            "vad": "silero_vad",
            "resemblyzer": "resemblyzer",
        }
        model_id = engine_map.get(args.engine.lower(), args.engine)
        success = download_model(model_id)
        return 0 if success else 1

    if args.essential:
        success = download_essential()
        return 0 if success else 1

    if args.all:
        success = download_all()
        return 0 if success else 1

    # Default: show help
    parser.print_help()
    print("\n💡 Quick start: python scripts/download_all_models.py --essential")
    return 0


if __name__ == "__main__":
    sys.exit(main())
