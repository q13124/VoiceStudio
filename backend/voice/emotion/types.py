"""
Emotion Types and Definitions.

Task 4.3.1: Emotion classification types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EmotionType(Enum):
    """Types of emotions for voice synthesis."""

    # Primary emotions
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"

    # Secondary emotions
    EXCITED = "excited"
    CALM = "calm"
    SERIOUS = "serious"
    SYMPATHETIC = "sympathetic"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"

    # Speaking styles
    WHISPER = "whisper"
    SHOUTING = "shouting"
    SOFT = "soft"
    LOUD = "loud"


class EmotionIntensity(Enum):
    """Intensity levels for emotions."""

    SUBTLE = 0.25
    MODERATE = 0.5
    STRONG = 0.75
    EXTREME = 1.0


@dataclass
class EmotionProfile:
    """A complex emotion profile with multiple emotions."""

    primary: EmotionType = EmotionType.NEUTRAL
    primary_intensity: float = 1.0

    secondary: EmotionType | None = None
    secondary_intensity: float = 0.0

    # Voice modifiers
    pitch_shift: float = 0.0  # Semitones
    speed_factor: float = 1.0
    energy_level: float = 1.0

    def to_dict(self) -> dict:
        return {
            "primary": self.primary.value,
            "primary_intensity": self.primary_intensity,
            "secondary": self.secondary.value if self.secondary else None,
            "secondary_intensity": self.secondary_intensity,
            "pitch_shift": self.pitch_shift,
            "speed_factor": self.speed_factor,
            "energy_level": self.energy_level,
        }


@dataclass
class EmotionResult:
    """Result of emotion detection or application."""

    detected_emotion: EmotionType
    confidence: float

    # All detected emotions with scores
    emotion_scores: dict[str, float] = field(default_factory=dict)

    # Voice analysis
    pitch_mean: float = 0.0
    pitch_std: float = 0.0
    energy_mean: float = 0.0
    speaking_rate: float = 0.0

    def get_top_emotions(self, n: int = 3) -> list[tuple]:
        """Get top N emotions by score."""
        sorted_emotions = sorted(
            self.emotion_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_emotions[:n]


# Emotion presets for common use cases
EMOTION_PRESETS: dict[str, EmotionProfile] = {
    "narrator_neutral": EmotionProfile(
        primary=EmotionType.NEUTRAL,
        primary_intensity=1.0,
        speed_factor=0.95,
    ),
    "narrator_warm": EmotionProfile(
        primary=EmotionType.HAPPY,
        primary_intensity=0.3,
        secondary=EmotionType.CALM,
        secondary_intensity=0.5,
        speed_factor=0.9,
    ),
    "news_anchor": EmotionProfile(
        primary=EmotionType.SERIOUS,
        primary_intensity=0.7,
        speed_factor=1.0,
        energy_level=0.8,
    ),
    "excited_host": EmotionProfile(
        primary=EmotionType.EXCITED,
        primary_intensity=0.8,
        pitch_shift=2,
        speed_factor=1.15,
        energy_level=1.3,
    ),
    "sad_storyteller": EmotionProfile(
        primary=EmotionType.SAD,
        primary_intensity=0.6,
        pitch_shift=-2,
        speed_factor=0.85,
        energy_level=0.7,
    ),
    "angry_character": EmotionProfile(
        primary=EmotionType.ANGRY,
        primary_intensity=0.8,
        pitch_shift=1,
        speed_factor=1.1,
        energy_level=1.4,
    ),
    "whisper_intimate": EmotionProfile(
        primary=EmotionType.WHISPER,
        primary_intensity=1.0,
        speed_factor=0.9,
        energy_level=0.4,
    ),
}
