"""
Real-Time Emotion Synthesizer.

Task 4.3.1: Dynamic emotion injection for voice synthesis.
Enables real-time emotion control during speech generation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np

logger = logging.getLogger(__name__)


class Emotion(Enum):
    """Supported emotions."""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    CONTEMPT = "contempt"
    EXCITED = "excited"
    CALM = "calm"
    TENDER = "tender"
    BORED = "bored"


@dataclass
class EmotionParams:
    """Parameters for emotion synthesis."""

    # Prosody parameters
    pitch_shift: float = 0.0  # Semitones (-12 to +12)
    pitch_variance: float = 1.0  # Multiplier for pitch variation
    speed: float = 1.0  # Speaking speed multiplier
    energy: float = 1.0  # Volume/energy multiplier

    # Voice quality
    breathiness: float = 0.0  # 0-1
    roughness: float = 0.0  # 0-1
    tension: float = 0.5  # 0-1

    # Articulation
    vowel_duration: float = 1.0  # Multiplier
    consonant_sharpness: float = 0.5  # 0-1

    def blend(self, other: EmotionParams, weight: float) -> EmotionParams:
        """Blend with another emotion params."""
        w1 = 1 - weight
        w2 = weight
        return EmotionParams(
            pitch_shift=self.pitch_shift * w1 + other.pitch_shift * w2,
            pitch_variance=self.pitch_variance * w1 + other.pitch_variance * w2,
            speed=self.speed * w1 + other.speed * w2,
            energy=self.energy * w1 + other.energy * w2,
            breathiness=self.breathiness * w1 + other.breathiness * w2,
            roughness=self.roughness * w1 + other.roughness * w2,
            tension=self.tension * w1 + other.tension * w2,
            vowel_duration=self.vowel_duration * w1 + other.vowel_duration * w2,
            consonant_sharpness=self.consonant_sharpness * w1 + other.consonant_sharpness * w2,
        )


# Preset parameters for each emotion
EMOTION_PRESETS: dict[Emotion, EmotionParams] = {
    Emotion.NEUTRAL: EmotionParams(),
    Emotion.HAPPY: EmotionParams(
        pitch_shift=2.0,
        pitch_variance=1.3,
        speed=1.1,
        energy=1.2,
        breathiness=0.1,
        tension=0.6,
    ),
    Emotion.SAD: EmotionParams(
        pitch_shift=-2.0,
        pitch_variance=0.7,
        speed=0.85,
        energy=0.7,
        breathiness=0.2,
        tension=0.3,
    ),
    Emotion.ANGRY: EmotionParams(
        pitch_shift=1.0,
        pitch_variance=1.5,
        speed=1.15,
        energy=1.4,
        roughness=0.3,
        tension=0.9,
        consonant_sharpness=0.8,
    ),
    Emotion.FEARFUL: EmotionParams(
        pitch_shift=3.0,
        pitch_variance=1.4,
        speed=1.2,
        energy=0.9,
        breathiness=0.3,
        tension=0.8,
    ),
    Emotion.SURPRISED: EmotionParams(
        pitch_shift=4.0,
        pitch_variance=1.6,
        speed=1.1,
        energy=1.3,
        breathiness=0.1,
        tension=0.7,
    ),
    Emotion.EXCITED: EmotionParams(
        pitch_shift=3.0,
        pitch_variance=1.5,
        speed=1.25,
        energy=1.35,
        breathiness=0.15,
        tension=0.7,
    ),
    Emotion.CALM: EmotionParams(
        pitch_shift=-1.0,
        pitch_variance=0.6,
        speed=0.9,
        energy=0.8,
        breathiness=0.15,
        tension=0.3,
    ),
}


class EmotionSynthesizer:
    """
    Real-time emotion synthesis engine.

    Features:
    - Dynamic emotion injection
    - Emotion blending
    - Prosody modification
    - Real-time parameter control
    """

    def __init__(self):
        self._current_emotion = Emotion.NEUTRAL
        self._current_params = EMOTION_PRESETS[Emotion.NEUTRAL]
        self._intensity = 1.0
        self._transition_frames = 0
        self._target_params: EmotionParams | None = None

    def set_emotion(
        self,
        emotion: Emotion,
        intensity: float = 1.0,
        transition_frames: int = 0,
    ) -> None:
        """
        Set target emotion.

        Args:
            emotion: Target emotion
            intensity: Emotion intensity (0-1)
            transition_frames: Frames to transition over
        """
        self._current_emotion = emotion
        self._intensity = max(0.0, min(1.0, intensity))

        # Get preset and scale by intensity
        preset = EMOTION_PRESETS.get(emotion, EmotionParams())
        neutral = EMOTION_PRESETS[Emotion.NEUTRAL]

        # Blend with neutral based on intensity
        target = neutral.blend(preset, self._intensity)

        if transition_frames > 0:
            self._target_params = target
            self._transition_frames = transition_frames
        else:
            self._current_params = target
            self._target_params = None
            self._transition_frames = 0

    def set_custom_params(self, params: EmotionParams) -> None:
        """Set custom emotion parameters."""
        self._current_params = params
        self._target_params = None
        self._transition_frames = 0

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """
        Apply current emotion to audio.

        Args:
            audio: Input audio samples
            sample_rate: Sample rate

        Returns:
            Audio with applied emotion
        """
        # Handle transition
        if self._transition_frames > 0 and self._target_params is not None:
            progress = 1.0 / self._transition_frames
            self._current_params = self._current_params.blend(self._target_params, progress)
            self._transition_frames -= 1
            if self._transition_frames == 0:
                self._current_params = self._target_params
                self._target_params = None

        output = audio.copy().astype(np.float32)
        params = self._current_params

        # Apply energy
        output = output * params.energy

        # Apply pitch shift
        if abs(params.pitch_shift) > 0.1:
            output = self._apply_pitch_shift(output, sample_rate, params.pitch_shift)

        # Apply speed change
        if abs(params.speed - 1.0) > 0.05:
            output = self._apply_speed_change(output, params.speed)

        # Apply breathiness
        if params.breathiness > 0.05:
            output = self._add_breathiness(output, params.breathiness)

        # Apply roughness/distortion
        if params.roughness > 0.05:
            output = self._add_roughness(output, params.roughness)

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0.99:
            output = output * (0.99 / max_val)

        return output

    def _apply_pitch_shift(
        self,
        audio: np.ndarray,
        sample_rate: int,
        semitones: float,
    ) -> np.ndarray:
        """Apply pitch shift using phase vocoder or resampling."""
        try:
            import librosa

            return librosa.effects.pitch_shift(audio, sr=sample_rate, n_steps=semitones)
        except ImportError:
            logger.debug("librosa not available for pitch_shift, using fallback resampling")

        # Fallback: simple resampling
        ratio = 2 ** (semitones / 12)
        original_len = len(audio)
        new_len = int(original_len / ratio)

        if new_len <= 0:
            return audio

        indices = np.linspace(0, original_len - 1, new_len)
        shifted = np.interp(indices, np.arange(original_len), audio)

        # Resample back to original length
        if len(shifted) != original_len:
            indices = np.linspace(0, len(shifted) - 1, original_len)
            shifted = np.interp(indices, np.arange(len(shifted)), shifted)

        return shifted

    def _apply_speed_change(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Change speaking speed (time stretch)."""
        try:
            import librosa

            return librosa.effects.time_stretch(audio, rate=speed)
        except ImportError:
            logger.debug("librosa not available for time_stretch, using fallback resampling")

        # Simple resampling (changes pitch too)
        new_len = int(len(audio) / speed)
        if new_len <= 0:
            return audio

        indices = np.linspace(0, len(audio) - 1, new_len)
        return np.interp(indices, np.arange(len(audio)), audio)

    def _add_breathiness(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Add breathy quality (filtered noise)."""
        noise = np.random.randn(len(audio)) * amount * 0.1

        # Low-pass filter the noise for more natural sound
        try:
            from scipy.signal import butter, filtfilt

            b, a = butter(2, 0.3)
            noise = filtfilt(b, a, noise)
        except ImportError:
            logger.debug("scipy not available for noise filtering, using unfiltered noise")

        return audio + noise

    def _add_roughness(self, audio: np.ndarray, amount: float) -> np.ndarray:
        """Add rough/gravelly quality."""
        # Soft clipping for distortion
        threshold = 1.0 - amount * 0.5
        output = np.tanh(audio / threshold) * threshold
        return output

    @property
    def current_emotion(self) -> Emotion:
        return self._current_emotion

    @property
    def current_params(self) -> EmotionParams:
        return self._current_params

    @property
    def intensity(self) -> float:
        return self._intensity


class EmotionTimeline:
    """
    Manage emotion changes over time.

    Allows scheduling emotion changes at specific timestamps.
    """

    def __init__(self, sample_rate: int = 16000):
        self._sample_rate = sample_rate
        self._events: list[tuple[int, Emotion, float]] = []  # (sample, emotion, intensity)
        self._synthesizer = EmotionSynthesizer()

    def add_event(
        self,
        time_seconds: float,
        emotion: Emotion,
        intensity: float = 1.0,
    ) -> None:
        """Add emotion change event at time."""
        sample = int(time_seconds * self._sample_rate)
        self._events.append((sample, emotion, intensity))
        self._events.sort(key=lambda x: x[0])

    def clear_events(self) -> None:
        """Clear all events."""
        self._events.clear()

    def process(
        self,
        audio: np.ndarray,
        chunk_size: int = 1024,
    ) -> np.ndarray:
        """
        Process audio with timeline emotions.

        Args:
            audio: Full audio to process
            chunk_size: Processing chunk size

        Returns:
            Processed audio with emotions applied
        """
        output = np.zeros_like(audio)
        event_idx = 0

        for start in range(0, len(audio), chunk_size):
            end = min(start + chunk_size, len(audio))
            chunk = audio[start:end]

            # Check for emotion events in this chunk
            while event_idx < len(self._events) and self._events[event_idx][0] <= start:
                _, emotion, intensity = self._events[event_idx]
                self._synthesizer.set_emotion(emotion, intensity, transition_frames=5)
                event_idx += 1

            # Process chunk
            processed = self._synthesizer.process(chunk, self._sample_rate)
            output[start:end] = processed

        return output
