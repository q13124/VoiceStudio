"""
Real XTTS v2 Engine Adapter for VoiceStudio Router
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Literal, Optional

try:
    import yaml
except Exception:
    yaml = None

try:
    from TTS.api import TTS  # type: ignore
    import torch
    import numpy as np
    import io

    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

try:
    import soundfile as sf
except Exception:
    sf = None

QualityTier = Literal["fast", "balanced", "quality"]


class XTTSRealAdapter:
    id = "xtts"
    languages = ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru", "ar"]
    quality = ["fast", "balanced", "quality"]

    def __init__(self, config_path: Optional[Path] = None):
        self._load = 0.0
        self.cfg = self._load_cfg(config_path)
        self.device = self._pick_device(
            self.cfg.get("device_preference", ["cuda", "cpu"])
        )

        if TTS_AVAILABLE:
            model_id = self.cfg.get(
                "model_id", "tts_models/multilingual/multi-dataset/xtts_v2"
            )
            try:
                self.tts = TTS(model_id).to(self.device)
                if self.device == "cuda" and self.cfg.get("use_half_precision", True):
                    torch.set_float32_matmul_precision("high")
            except Exception as e:
                print(f"Failed to load XTTS model: {e}")
                self.tts = None
        else:
            self.tts = None

    def healthy(self) -> bool:
        try:
            return self.tts is not None and TTS_AVAILABLE
        except Exception:
            return False

    def current_load(self) -> float:
        return float(self._load)

    def supports(self, language: str, tier: QualityTier) -> bool:
        return language.lower() in self.languages

    def tts(self, *, text: str, voice_profile: Dict, params: Dict) -> bytes:
        if not self.tts:
            # Fallback to synthetic audio
            return self._synthetic_audio(text, params)

        language = (
            voice_profile.get("language")
            or params.get("language")
            or self.cfg.get("default_language")
            or "en"
        ).lower()
        speaker_wavs = (
            voice_profile.get("speaker_wavs")
            or self.cfg.get("default_speaker_refs")
            or []
        )

        if isinstance(speaker_wavs, (str, Path)):
            speaker_wavs = [str(speaker_wavs)]

        sr = int(params.get("sample_rate") or self.cfg.get("sample_rate", 22050))

        try:
            wav = self.tts.tts(
                text=text,
                speaker_wav=speaker_wavs if speaker_wavs else None,
                language=language,
                **{k: v for k, v in params.items() if k != "sample_rate"},
            )
            if isinstance(wav, list):
                wav = wav[0]

            if sf is None:
                return b""
            buf = io.BytesIO()
            sf.write(
                buf,
                np.asarray(wav, dtype=np.float32),
                samplerate=sr,
                format="WAV",
                subtype="PCM_16",
            )
            return buf.getvalue()
        except Exception as e:
            print(f"XTTS generation failed: {e}")
            return self._synthetic_audio(text, params)

    def _synthetic_audio(self, text: str, params: Dict) -> bytes:
        """Generate synthetic audio as fallback"""
        import math, struct

        sr = int(params.get("sample_rate", 22050))
        dur = max(0.2, min(10.0, len(text) / 20.0))
        tone = 440.0
        samples = int(sr * dur)
        buf = bytearray()
        for n in range(samples):
            buf += struct.pack(
                "<h", int(32767 * 0.1 * math.sin(2 * math.pi * tone * (n / sr)))
            )
        return self._pcm16_to_wav(bytes(buf), sr)

    def _pcm16_to_wav(self, pcm: bytes, sample_rate: int) -> bytes:
        import io, struct

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
        for p in pref:
            if p == "cuda" and torch.cuda.is_available():
                return "cuda"
            if p == "cpu":
                return "cpu"
        return "cpu"

    def _load_cfg(self, config_path: Optional[Path]):
        paths = [
            config_path,
            Path("config") / "voicestudio.yaml",
            Path("voicestudio.yaml"),
        ]
        for p in paths:
            if p and p.exists() and yaml is not None:
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                return (data.get("engines", {}) or {}).get("xtts", {})
        return {
            "model_id": "tts_models/multilingual/multi-dataset/xtts_v2",
            "device_preference": ["cuda", "cpu"],
            "default_language": "en",
            "default_speaker_refs": [],
            "sample_rate": 22050,
            "use_half_precision": True,
        }
