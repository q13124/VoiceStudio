"""
Voice & Speech Processing Integration Module
Integrates free libraries for voice activity detection, phonemization, and speech recognition.
"""

from .phonemization import Phonemizer
from .speech_recognition import SpeechRecognizer
from .voice_activity_detection import VoiceActivityDetector

__all__ = [
    "Phonemizer",
    "VoiceActivityDetector",
    "SpeechRecognizer",
]
