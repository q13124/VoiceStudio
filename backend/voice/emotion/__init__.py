"""Voice emotion module."""

from backend.voice.emotion.engine import EmotionEngine, EmotionConfig
from backend.voice.emotion.types import EmotionType, EmotionIntensity, EmotionResult

__all__ = [
    "EmotionEngine", "EmotionConfig",
    "EmotionType", "EmotionIntensity", "EmotionResult",
]
