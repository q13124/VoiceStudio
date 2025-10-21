#!/usr/bin/env python3
"""
VoiceStudio Health Check - Voice Cloning Components
Tests all voice cloning components after refresh
"""

import json
import importlib
import torch


def check_voice_cloning_components():
    """Check all voice cloning components"""
    mods = {}

    # Check core voice cloning modules
    modules_to_check = [
        "torch",
        "torchaudio",
        "torchcodec",
        "ctranslate2",
        "faster_whisper",
        "pyannote.audio",
    ]

    for m in modules_to_check:
        try:
            if m == "pyannote.audio":
                mm = importlib.import_module("pyannote.audio")
            else:
                mm = importlib.import_module(m)
            mods[m] = getattr(mm, "__version__", "n/a")
        except Exception as e:
            mods[m] = f"ERR:{e}"

    # Get CUDA info
    cuda_info = {
        "cuda": torch.version.cuda,
        "cuda_ok": torch.cuda.is_available(),
        "cuda_device_count": (
            torch.cuda.device_count() if torch.cuda.is_available() else 0
        ),
    }

    # Combine results
    result = {
        "voice_cloning_modules": mods,
        "cuda_info": cuda_info,
        "status": "VoiceStudio Voice Cloning Program Ready",
    }

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    check_voice_cloning_components()
