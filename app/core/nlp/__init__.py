"""
Natural Language Processing module for VoiceStudio Quantum+.
Provides text preprocessing for SSML and TTS.
"""

from .text_processing import (
    TextPreprocessor,
    get_text_preprocessor
)

__all__ = [
    'TextPreprocessor',
    'get_text_preprocessor'
]

