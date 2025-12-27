"""
Audio Processing Integration Module
Integrates free libraries for advanced audio processing capabilities.
"""

from .pitch_tracking import PitchTracker
from .resampling import HighQualityResampler
from .metadata import AudioMetadataExtractor
from .wavelet_analysis import WaveletAnalyzer

__all__ = [
    "PitchTracker",
    "HighQualityResampler",
    "AudioMetadataExtractor",
    "WaveletAnalyzer",
]

