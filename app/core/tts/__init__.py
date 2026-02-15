"""
Text-to-Speech utilities module for VoiceStudio Quantum+.
Provides utility TTS engines (gTTS, pyttsx3) as fallback options.
"""

from .tts_utilities import (
    GTTSWrapper,
    Pyttsx3Wrapper,
    get_gtts,
    get_pyttsx3,
    synthesize_with_utility,
)

__all__ = [
    'GTTSWrapper',
    'Pyttsx3Wrapper',
    'get_gtts',
    'get_pyttsx3',
    'synthesize_with_utility'
]

