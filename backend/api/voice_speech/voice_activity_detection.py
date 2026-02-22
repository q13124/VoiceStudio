"""
Voice Activity Detection Integration
Integrates silero-vad for voice activity detection.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Try importing silero-vad
HAS_SILERO_VAD = False
try:
    import torch
    from silero_vad import get_speech_timestamps, load_model

    HAS_SILERO_VAD = True
except ImportError:
    logger.warning("silero-vad not available.")


class VoiceActivityDetector:
    """
    Voice activity detection using silero-vad.
    """

    def __init__(self):
        """Initialize VAD."""
        self.silero_available = HAS_SILERO_VAD
        self._model = None

    def _load_model(self):
        """Lazy load the VAD model."""
        if not self.silero_available:
            raise ImportError("silero-vad library not available")

        if self._model is None:
            try:
                self._model, _utils = load_model()
                logger.info("Silero VAD model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Silero VAD model: {e}", exc_info=True)
                raise

    def detect_voice_activity(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        threshold: float = 0.5,
    ) -> list[tuple[float, float]]:
        """
        Detect voice activity in audio.

        Args:
            audio: Audio signal (mono, float32)
            sample_rate: Sample rate (should be 8000 or 16000 for silero-vad)
            threshold: Detection threshold (0.0-1.0)

        Returns:
            List of (start_time, end_time) tuples in seconds
        """
        if not self.silero_available:
            raise ImportError("silero-vad library not available")

        try:
            self._load_model()

            # Ensure audio is float32 and correct sample rate
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Resample if needed (silero-vad requires 8000 or 16000 Hz)
            if sample_rate not in [8000, 16000]:
                try:
                    import librosa

                    target_sr = 16000
                    audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=target_sr)
                    sample_rate = target_sr
                except ImportError:
                    logger.warning(
                        "librosa not available for resampling. "
                        "Silero VAD may not work correctly."
                    )

            # Convert to torch tensor
            audio_tensor = torch.from_numpy(audio)

            # Get speech timestamps
            speech_timestamps = get_speech_timestamps(
                audio_tensor,
                self._model,
                threshold=threshold,
                sampling_rate=sample_rate,
            )

            # Convert to list of (start, end) tuples
            segments = [
                (ts["start"] / sample_rate, ts["end"] / sample_rate) for ts in speech_timestamps
            ]

            return segments
        except Exception as e:
            logger.error(f"Error in voice activity detection: {e}", exc_info=True)
            raise

    def get_voice_ratio(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        threshold: float = 0.5,
    ) -> float:
        """
        Get ratio of voice activity in audio.

        Args:
            audio: Audio signal
            sample_rate: Sample rate
            threshold: Detection threshold

        Returns:
            Ratio of voice activity (0.0-1.0)
        """
        segments = self.detect_voice_activity(audio, sample_rate, threshold)
        duration = len(audio) / sample_rate

        if duration == 0:
            return 0.0

        voice_duration = sum(end - start for start, end in segments)
        return float(voice_duration / duration)
