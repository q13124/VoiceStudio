"""
Real OpenVoice Engine Adapter for VoiceStudio Router
Compatible with OpenVoice v2.0+
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
    import torch
    import torchaudio
    from openvoice import se_extractor
    from openvoice.api import BaseSpeakerTTS, ToneColorConverter
except ImportError:
    torch = None
    torchaudio = None
    se_extractor = None
    BaseSpeakerTTS = None
    ToneColorConverter = None

QualityTier = Literal["fast", "balanced", "quality"]


class OpenVoiceRealAdapter:
    id = "openvoice"
    languages = ["en", "es", "fr", "de", "it", "pt"]
    quality = ["fast", "balanced", "quality"]

    def __init__(self, config_path: Optional[Path] = None):
        self._load = 0.0
        self.cfg = self._load_cfg(config_path)
        self.device = self._pick_device(
            self.cfg.get("device_preference", ["cuda", "cpu"])
        )

        # Initialize OpenVoice components
        self.tts = None
        self.tone_color_converter = None
        self._init_models()

    def _init_models(self):
        """Initialize OpenVoice models"""
        if not torch or not BaseSpeakerTTS:
            print("Warning: OpenVoice not available, using stub")
            return

        try:
            # Initialize TTS model
            model_path = self.cfg.get(
                "model_path", "checkpoints/base_speakers/EN/config.json"
            )
            self.tts = BaseSpeakerTTS(model_path, device=self.device)

            # Initialize tone color converter
            converter_path = self.cfg.get(
                "converter_path", "checkpoints/base_speakers/EN/config.json"
            )
            self.tone_color_converter = ToneColorConverter(
                converter_path, device=self.device
            )

        except Exception as e:
            print(f"Warning: Could not initialize OpenVoice models: {e}")
            self.tts = None
            self.tone_color_converter = None

    def healthy(self) -> bool:
        try:
            return self.tts is not None and self.tone_color_converter is not None
        except Exception:
            return False

    def current_load(self) -> float:
        return float(self._load)

    def supports(self, language: str, tier: QualityTier) -> bool:
        return language.lower() in self.languages

    def tts(self, *, text: str, voice_profile: Dict, params: Dict) -> bytes:
        """Generate audio using OpenVoice"""
        if not self.tts or not self.tone_color_converter:
            # Fallback to stub audio
            return self._generate_stub_audio(text, params)

        try:
            language = (
                voice_profile.get("language") or params.get("language") or "en"
            ).lower()
            speaker_wavs = voice_profile.get("speaker_wavs", [])

            if not speaker_wavs:
                speaker_wavs = self.cfg.get("default_speaker_refs", [])

            if isinstance(speaker_wavs, (str, Path)):
                speaker_wavs = [str(speaker_wavs)]

            sample_rate = int(
                params.get("sample_rate") or self.cfg.get("sample_rate", 22050)
            )

            # Generate speech
            if speaker_wavs:
                # Extract speaker embedding
                speaker_embedding = se_extractor.get_se(
                    speaker_wavs[0],
                    self.tone_color_converter,
                    target_dir="processed",
                    vad=True,
                    max_chunk=1000000,
                )

                # Generate with speaker embedding
                audio = self.tts.infer(text, speaker_embedding, language=language)
            else:
                # Generate without speaker embedding
                audio = self.tts.infer(text, language=language)

            # Convert to WAV bytes
            return self._audio_to_wav_bytes(audio, sample_rate)

        except Exception as e:
            print(f"OpenVoice generation failed: {e}")
            return self._generate_stub_audio(text, params)

    def _generate_stub_audio(self, text: str, params: Dict) -> bytes:
        """Generate stub audio when OpenVoice is not available"""
        import math
        import struct

        sample_rate = int(params.get("sample_rate", 22050))
        duration = max(0.5, min(10.0, len(text) / 15.0))
        tone = 220.0  # A3 note

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
                return (data.get("engines", {}) or {}).get("openvoice", {})

        # Defaults
        return {
            "model_path": "checkpoints/base_speakers/EN/config.json",
            "converter_path": "checkpoints/base_speakers/EN/config.json",
            "device_preference": ["cuda", "cpu"],
            "default_language": "en",
            "default_speaker_refs": [],
            "sample_rate": 22050,
        }
