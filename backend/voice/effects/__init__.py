"""Voice effects module."""

from backend.voice.effects.chain import EffectsChain
from backend.voice.effects.reverb import ReverbEffect
from backend.voice.effects.equalizer import EqualizerEffect
from backend.voice.effects.compressor import CompressorEffect
from backend.voice.effects.pitch import PitchShiftEffect
from backend.voice.effects.noise import NoiseReductionEffect

__all__ = [
    "EffectsChain",
    "ReverbEffect",
    "EqualizerEffect",
    "CompressorEffect",
    "PitchShiftEffect",
    "NoiseReductionEffect",
]
