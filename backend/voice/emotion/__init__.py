"""Voice emotion module."""

from backend.voice.emotion.engine import EmotionConfig, EmotionEngine
from backend.voice.emotion.types import EmotionIntensity, EmotionResult, EmotionType

__all__ = [
    "EmotionConfig",
    "EmotionEngine",
    "EmotionIntensity",
    "EmotionResult",
    "EmotionType",
]
