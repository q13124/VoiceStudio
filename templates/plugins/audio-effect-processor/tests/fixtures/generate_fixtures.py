"""Generate deterministic WAV fixtures for audio-effect template tests."""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


def _write_wav(path: Path, samples: np.ndarray, sample_rate: int = 44100) -> None:
    samples_i16 = np.clip(samples, -1.0, 1.0)
    samples_i16 = (samples_i16 * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(samples_i16.tobytes())


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    sr = 44100
    t = np.linspace(0, 1, sr, endpoint=False)

    silence = np.zeros_like(t, dtype=np.float32)
    tone = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    speech_like = (0.15 * np.sin(2 * np.pi * 220 * t) * (1 + 0.5 * np.sin(2 * np.pi * 3 * t))).astype(np.float32)

    _write_wav(out_dir / "silence.wav", silence, sr)
    _write_wav(out_dir / "tone_440hz.wav", tone, sr)
    _write_wav(out_dir / "speech_like.wav", speech_like, sr)


if __name__ == "__main__":
    main()
