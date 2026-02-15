"""
Audio Processing Integration Module
Integrates free libraries for advanced audio processing capabilities.
"""

from .metadata import AudioMetadataExtractor
from .pitch_tracking import PitchTracker
from .resampling import HighQualityResampler
from .wavelet_analysis import WaveletAnalyzer

__all__ = [
    "AudioMetadataExtractor",
    "HighQualityResampler",
    "PitchTracker",
    "WaveletAnalyzer",
]

