"""
VoiceStudio UI Test Fixtures.

Provides standardized test assets including audio files, reference samples,
and text scripts for validation testing.
"""

from __future__ import annotations

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent

# Audio test files
TEST_AUDIO_SHORT = FIXTURES_DIR / "test_audio_short.wav"  # 5 seconds
TEST_AUDIO_LONG = FIXTURES_DIR / "test_audio_long.wav"    # 30 seconds
TEST_AUDIO_NOISY = FIXTURES_DIR / "test_audio_noisy.wav"  # 5 seconds with noise

# Voice reference samples
VOICE_REFERENCE_CLEAN = FIXTURES_DIR / "voice_reference_clean.wav"
VOICE_REFERENCE_MULTI = FIXTURES_DIR / "voice_reference_multi_speaker.wav"

# Text scripts
TEST_SCRIPTS = {
    "short": "Hello, this is a test of the voice synthesis system.",
    "medium": "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and is commonly used for testing.",
    "long": """Welcome to VoiceStudio, the comprehensive voice synthesis and cloning platform.
This text is designed to test longer synthesis capabilities including paragraph handling,
sentence boundaries, and proper intonation across multiple sentences.
The system should handle punctuation, numbers like 123, and special characters correctly.""",
    "multilingual": {
        "en": "Hello, this is English text.",
        "es": "Hola, este es texto en español.",
        "fr": "Bonjour, ceci est du texte français.",
        "de": "Hallo, das ist deutscher Text.",
    },
    "emotions": {
        "happy": "I'm so excited to share this wonderful news with you!",
        "sad": "Unfortunately, things didn't go as planned today.",
        "angry": "This is completely unacceptable behavior!",
        "neutral": "The meeting has been scheduled for tomorrow at 3 PM.",
    }
}


def get_test_audio_path(audio_type: str = "short") -> Path:
    """
    Get path to a test audio file.

    Args:
        audio_type: One of "short", "long", "noisy", "reference_clean", "reference_multi"

    Returns:
        Path to the audio file.
    """
    mapping = {
        "short": TEST_AUDIO_SHORT,
        "long": TEST_AUDIO_LONG,
        "noisy": TEST_AUDIO_NOISY,
        "reference_clean": VOICE_REFERENCE_CLEAN,
        "reference_multi": VOICE_REFERENCE_MULTI,
    }
    return mapping.get(audio_type, TEST_AUDIO_SHORT)


def get_test_script(script_type: str = "short", language: str = "en", emotion: str | None = None) -> str:
    """
    Get test script text.

    Args:
        script_type: One of "short", "medium", "long", "multilingual", "emotions"
        language: Language code for multilingual scripts
        emotion: Emotion type for emotion scripts

    Returns:
        Test script text.
    """
    if script_type == "multilingual":
        return TEST_SCRIPTS["multilingual"].get(language, TEST_SCRIPTS["multilingual"]["en"])
    elif script_type == "emotions":
        return TEST_SCRIPTS["emotions"].get(emotion, TEST_SCRIPTS["emotions"]["neutral"])
    else:
        return TEST_SCRIPTS.get(script_type, TEST_SCRIPTS["short"])
