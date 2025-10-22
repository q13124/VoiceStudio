"""
VoiceStudio — Simple Post-Processing Effect Chain

Defines a small plugin-like system for post-generation processing.
Each effect implements EffectProtocol.process(wav: np.ndarray, sr: int) -> np.ndarray

Available built-ins (lightweight, no GPUs):
  - lufs_normalize (target -16 LUFS, via pyloudnorm)
  - de_ess (very simple high-shelf attenuation around 6-8kHz)
  - noise_gate (naive gate based on RMS threshold)

Use in router endpoints by passing params.post_chain: ["lufs", "de_ess", "noise_gate"].

NOTE: This is intentionally simple and fast. Replace with professional DSP plugins later.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import numpy as np

try:
    import pyloudnorm as pyln
except Exception:  # pragma: no cover
    pyln = None


class EffectProtocol:
    def process(self, wav: np.ndarray, sr: int) -> np.ndarray:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class LufsNormalize(EffectProtocol):
    target_lufs: float = -16.0

    def process(self, wav: np.ndarray, sr: int) -> np.ndarray:
        if pyln is None:
            return wav  # no-op if dep missing
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(wav.astype(float))
        gain = pyln.normalize.loudness(wav.astype(float), loudness, self.target_lufs)
        return np.asarray(gain, dtype=np.float32)


@dataclass
class DeEss(EffectProtocol):
    freq_hz: float = 7000.0
    amount_db: float = -4.0

    def process(self, wav: np.ndarray, sr: int) -> np.ndarray:
        # Super-simple de-ess: low-pass blend to attenuate sibilance region
        from scipy.signal import butter, lfilter
        ny = 0.5 * sr
        fc = min(self.freq_hz / ny, 0.99)
        b, a = butter(2, fc, btype="low")
        low = lfilter(b, a, wav).astype(np.float32)
        # Mix: original + low-passed (negative shelf)
        k = 10 ** (self.amount_db / 20.0)
        out = (wav + k * (low - wav)).astype(np.float32)
        return out


@dataclass
class NoiseGate(EffectProtocol):
    threshold_db: float = -55.0

    def process(self, wav: np.ndarray, sr: int) -> np.ndarray:
        rms = np.sqrt(np.mean(wav**2) + 1e-9)
        thr = 10 ** (self.threshold_db / 20.0)
        if rms < thr:
            return np.zeros_like(wav)
        return wav


def build_chain(names: List[str]) -> List[EffectProtocol]:
    mapping: Dict[str, Callable[[], EffectProtocol]] = {
        "lufs": lambda: LufsNormalize(-16.0),
        "de_ess": lambda: DeEss(),
        "noise_gate": lambda: NoiseGate(),
    }
    chain: List[EffectProtocol] = []
    for n in names:
        f = mapping.get(n)
        if f:
            chain.append(f())
    return chain


def apply_chain(wav: np.ndarray, sr: int, names: List[str]) -> np.ndarray:
    chain = build_chain(names)
    out = wav
    for eff in chain:
        out = eff.process(out, sr)
    # clip to [-1,1]
    out = np.clip(out, -1.0, 1.0).astype(np.float32)
    return out
