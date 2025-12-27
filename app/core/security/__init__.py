"""
Security Module
Audio watermarking and deepfake detection for VoiceStudio.

This module provides:
- Audio watermarking for content protection and forensic tracking
- Deepfake detection for authenticity verification
- Security database for watermark tracking
"""

from .watermarking import AudioWatermarker, WatermarkMethod
from .deepfake_detector import DeepfakeDetector
from .database import WatermarkDatabase

__all__ = [
    "AudioWatermarker",
    "WatermarkMethod",
    "DeepfakeDetector",
    "WatermarkDatabase",
]

__version__ = "1.0.0"

