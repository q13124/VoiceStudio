"""
Security Module
Audio watermarking and deepfake detection for VoiceStudio.

This module provides:
- Audio watermarking for content protection and forensic tracking
- Deepfake detection for authenticity verification
- Security database for watermark tracking
"""

from .database import WatermarkDatabase
from .deepfake_detector import DeepfakeDetector
from .watermarking import AudioWatermarker, WatermarkMethod

__all__ = [
    "AudioWatermarker",
    "DeepfakeDetector",
    "WatermarkDatabase",
    "WatermarkMethod",
]

__version__ = "1.0.0"
