"""
Real Coqui TTS Engine Adapter for VoiceStudio Router
Compatible with Coqui TTS (non-XTTS models)
"""

from __future__ import annotations
import os
import numpy as np
import soundfile as sf
import io
from pathlib import Path
from typing import Dict, List, Literal, Optional

try:
    import yaml
except Exception:
    yaml = None

try:
    from TTS.api import TTS
    import torch
except ImportError:
    TTS = None
    torch = None

QualityTier = Literal["fast", "balanced", "quality"]


class CoquiRealAdapter:
    id = "coqui"
    languages = ["en", "es", "fr", "de"]
    quality = ["fast", "balanced", "quality"]

    def __init__(self, config_path: Optional[Path] = None):
        self._load = 0.0
        self.cfg = self._load_cfg(config_path)
        self.device = self._pick_device(
            self.cfg.get("device_preference", ["cuda", "cpu"])
        )

        # Initialize Coqui TTS
        self.tts = None
        self._init_model()

    def _init_model(self):
        """Initialize Coqui TTS model"""
        if not TTS:
            print("Warning: Coqui TTS not available, using stub")
            return

        try:
            model_name = self.cfg.get(
                "model_name", "tts_models/en/ljspeech/tacotron2-DDC"
            )
            self.tts = TTS(model_name).to(self.device)

        except Exception as e:
            print(f"Warning: Could not initialize Coqui TTS model: {e}")
            self.tts = None

    def healthy(self) -> bool:
        try:
            return self.tts is not None
        except Exception:
            return False

    def current_load(self) -> float:
        return float(self._load)

    def supports(self, language: str, tier: QualityTier) -> bool:
        return language.lower() in self.languages

    def tts(self, *, text: str, voice_profile: Dict, params: Dict) -> bytes:
        """Generate audio using Coqui TTS"""
        if not self.tts:
            return self._generate_stub_audio(text, params)

        try:
            language = (
                voice_profile.get("language") or params.get("language") or "en"
            ).lower()
            sample_rate = int(
                params.get("sample_rate") or self.cfg.get("sample_rate", 22050)
            )

            # Generate speech
            audio = self.tts.tts(text=text)

            # Convert to WAV bytes
            return self._audio_to_wav_bytes(audio, sample_rate)

        except Exception as e:
            print(f"Coqui TTS generation failed: {e}")
            return self._generate_stub_audio(text, params)

    def _generate_stub_audio(self, text: str, params: Dict) -> bytes:
        """Generate stub audio when Coqui TTS is not available"""
        import math
        import struct

        sample_rate = int(params.get("sample_rate", 22050))
        duration = max(0.5, min(10.0, len(text) / 15.0))
        tone = 330.0  # E4 note

        samples = int(sample_rate * duration)
        buf = bytearray()

        for n in range(samples):
            v = int(32767 * 0.1 * math.sin(2 * math.pi * tone * (n / sample_rate)))
            buf += struct.pack("<h", v)

        return self._pcm16_to_wav(bytes(buf), sample_rate)

    def _audio_to_wav_bytes(self, audio: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy audio array to WAV bytes"""
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()

        # Ensure mono
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.8

        buf = io.BytesIO()
        sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
        return buf.getvalue()

    def _pcm16_to_wav(self, pcm: bytes, sample_rate: int) -> bytes:
        """Convert PCM16 to WAV format"""
        import struct

        byte_rate = sample_rate * 2
        block_align = 2

        riff = io.BytesIO()
        riff.write(b"RIFF")
        riff.write(struct.pack("<I", 36 + len(pcm)))
        riff.write(b"WAVEfmt ")
        riff.write(
            struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, byte_rate, block_align, 16)
        )
        riff.write(b"data")
        riff.write(struct.pack("<I", len(pcm)))
        riff.write(pcm)
        return riff.getvalue()

    def _pick_device(self, pref: List[str]) -> str:
        """Pick the best available device"""
        if not torch:
            return "cpu"

        for p in pref:
            if p == "cuda" and torch.cuda.is_available():
                return "cuda"
            if p == "cpu":
                return "cpu"
        return "cpu"

    def _load_cfg(self, config_path: Optional[Path]) -> Dict:
        """Load configuration"""
        paths = [
            config_path,
            Path("config") / "voicestudio.yaml",
            Path("voicestudio.yaml"),
        ]

        for p in paths:
            if p and p.exists() and yaml is not None:
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return (data.get("engines", {}) or {}).get("coqui", {})

        # Defaults
        return {
            "model_name": "tts_models/en/ljspeech/tacotron2-DDC",
            "device_preference": ["cuda", "cpu"],
            "default_language": "en",
            "sample_rate": 22050,
        }
