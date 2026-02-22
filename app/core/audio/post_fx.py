"""
Post-FX Module for VoiceStudio
Post-processing audio effects module for voice synthesis

Compatible with:
- Python 3.10+
- librosa>=0.11.0
- scipy>=1.9.0
- soundfile>=0.12.1
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logger.warning("librosa not installed. Install with: pip install librosa")

try:
    import soundfile as sf

    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    logger.warning("soundfile not installed. Install with: pip install soundfile")

try:
    from scipy import signal

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("scipy not installed. Install with: pip install scipy")

try:
    import pyloudnorm as pyln

    HAS_PYLOUDNORM = True
except ImportError:
    HAS_PYLOUDNORM = False
    logger.warning("pyloudnorm not installed. Install with: pip install pyloudnorm")

try:
    import noisereduce as nr

    HAS_NOISEREDUCE = True
except ImportError:
    HAS_NOISEREDUCE = False
    logger.warning("noisereduce not installed. Install with: pip install noisereduce")

# Try importing pedalboard for professional audio effects
try:
    import pedalboard
    from pedalboard import (
        Chorus,
        Compressor,
        Delay,
        Distortion,
        Gain,
        HighpassFilter,
        Limiter,
        LowpassFilter,
        Pedalboard,
        Phaser,
        Reverb,
    )

    HAS_PEDALBOARD = True
except ImportError:
    HAS_PEDALBOARD = False
    pedalboard = None
    logger.debug(
        "pedalboard not installed. Professional effects will be limited. "
        "Install with: pip install pedalboard"
    )

# Import audio utilities
try:
    from .audio_utils import enhance_voice_quality, normalize_lufs, remove_artifacts

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    logger.warning("audio_utils not available")


class PostFXProcessor:
    """
    Post-FX Processor for applying audio effects to synthesized audio.

    Supports:
    - Normalization (LUFS and peak)
    - Denoising
    - EQ (3-band equalizer)
    - Compressor
    - Reverb
    - Delay
    - Filter (lowpass/highpass/bandpass)
    - Effect chains
    """

    def __init__(self, sample_rate: int = 24000):
        """
        Initialize Post-FX Processor.

        Args:
            sample_rate: Default sample rate for processing
        """
        self.sample_rate = sample_rate

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int | None = None,
        effects: list[dict] | None = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Process audio with effects chain.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            effects: List of effect dictionaries, each with:
                - type: Effect type (normalize, denoise, eq, compressor, etc.)
                - enabled: Whether effect is enabled
                - params: Effect parameters
            **kwargs: Additional processing options

        Returns:
            Processed audio array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if effects is None:
            effects = []

        processed_audio = audio.copy()

        # Sort effects by order if present
        if effects and "order" in effects[0]:
            effects = sorted(effects, key=lambda e: e.get("order", 0))

        # Apply each effect in sequence
        for effect in effects:
            if not effect.get("enabled", True):
                continue

            effect_type = effect.get("type", "").lower()
            params = effect.get("params", {})

            try:
                processed_audio = self.apply_effect(
                    processed_audio, sample_rate, effect_type, params
                )
            except Exception as e:
                logger.warning(f"Failed to apply effect {effect_type}: {e}")
                continue

        return processed_audio

    def apply_effect(
        self,
        audio: np.ndarray,
        sample_rate: int,
        effect_type: str,
        params: dict,
    ) -> np.ndarray:
        """
        Apply a single effect to audio.

        Args:
            audio: Input audio array
            sample_rate: Sample rate
            effect_type: Type of effect to apply
            params: Effect parameters

        Returns:
            Processed audio array
        """
        effect_type = effect_type.lower()

        # Try pedalboard first for professional effects (if available)
        use_pedalboard = params.get("use_pedalboard", False) and HAS_PEDALBOARD
        if use_pedalboard:
            try:
                return self._apply_pedalboard_effect(audio, sample_rate, effect_type, params)
            except Exception as e:
                logger.warning(f"Pedalboard effect failed: {e}. Falling back to standard effect.")

        # Standard effects (fallback or when pedalboard not requested)
        if effect_type == "normalize":
            return self._apply_normalize(audio, sample_rate, params)
        elif effect_type == "denoise":
            return self._apply_denoise(audio, sample_rate, params)
        elif effect_type == "eq":
            return self._apply_eq(audio, sample_rate, params)
        elif effect_type == "compressor":
            return self._apply_compressor(audio, sample_rate, params)
        elif effect_type == "reverb":
            return self._apply_reverb(audio, sample_rate, params)
        elif effect_type == "delay":
            return self._apply_delay(audio, sample_rate, params)
        elif effect_type == "filter":
            return self._apply_filter(audio, sample_rate, params)
        else:
            logger.warning(f"Unknown effect type: {effect_type}")
            return audio

    def _apply_normalize(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply normalization effect."""
        method = params.get("method", "lufs").lower()
        target_lufs = params.get("target_lufs", -23.0)

        if method == "lufs" and HAS_PYLOUDNORM:
            try:
                return normalize_lufs(audio, sample_rate, target_lufs)
            except Exception as e:
                logger.warning(f"LUFS normalization failed: {e}, using peak")
                method = "peak"

        # Peak normalization fallback
        if method == "peak":
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                return audio / max_val * 0.95
            return audio

        return audio

    def _apply_denoise(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply denoising effect."""
        params.get("strength", 0.5)

        if HAS_AUDIO_UTILS:
            try:
                return enhance_voice_quality(audio, sample_rate)
            except Exception:
                ...

        if HAS_NOISEREDUCE:
            try:
                return nr.reduce_noise(y=audio, sr=sample_rate, stationary=False)
            except Exception as e:
                logger.warning(f"Denoising failed: {e}")

        return audio

    def _apply_eq(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply 3-band EQ effect."""
        if not HAS_SCIPY:
            logger.warning("scipy required for EQ")
            return audio

        low_gain_db = params.get("low_gain", 0.0)
        mid_gain_db = params.get("mid_gain", 0.0)
        high_gain_db = params.get("high_gain", 0.0)

        # Convert dB to linear gain
        low_gain = 10.0 ** (low_gain_db / 20.0)
        mid_gain = 10.0 ** (mid_gain_db / 20.0)
        high_gain = 10.0 ** (high_gain_db / 20.0)

        # Process each channel
        if len(audio.shape) == 1:
            audio = audio.reshape(1, -1)
            was_mono = True
        else:
            was_mono = False

        processed_channels = []

        for channel in audio:
            processed = channel.copy()

            # Low shelf (below 500 Hz)
            if low_gain != 1.0:
                nyquist = sample_rate / 2.0
                low_cutoff = 500.0 / nyquist
                b, a = signal.iirfilter(4, low_cutoff, btype="lowpass", ftype="butter")
                low_signal = signal.filtfilt(b, a, processed)
                processed = processed + (low_signal * (low_gain - 1.0))

            # Mid band (500-5000 Hz, centered at 2000 Hz)
            if mid_gain != 1.0:
                nyquist = sample_rate / 2.0
                low_cutoff = 500.0 / nyquist
                high_cutoff = 5000.0 / nyquist
                b, a = signal.iirfilter(
                    4,
                    [low_cutoff, high_cutoff],
                    btype="bandpass",
                    ftype="butter",
                )
                mid_signal = signal.filtfilt(b, a, processed)
                processed = processed + (mid_signal * (mid_gain - 1.0))

            # High shelf (above 5000 Hz)
            if high_gain != 1.0:
                nyquist = sample_rate / 2.0
                high_cutoff = 5000.0 / nyquist
                b, a = signal.iirfilter(4, high_cutoff, btype="highpass", ftype="butter")
                high_signal = signal.filtfilt(b, a, processed)
                processed = processed + (high_signal * (high_gain - 1.0))

            processed_channels.append(processed)

        result = np.array(processed_channels)
        if was_mono:
            result = result[0]

        # Normalize to prevent clipping
        max_val = np.max(np.abs(result))
        if max_val > 0.95:
            result = result / max_val * 0.95

        return result

    def _apply_compressor(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply compressor effect."""
        threshold_db = params.get("threshold", -12.0)
        ratio = params.get("ratio", 4.0)
        attack_ms = params.get("attack", 5.0)
        release_ms = params.get("release", 50.0)

        # Convert threshold to linear
        threshold = 10.0 ** (threshold_db / 20.0)

        # Process each channel
        if len(audio.shape) == 1:
            audio = audio.reshape(1, -1)
            was_mono = True
        else:
            was_mono = False

        processed_channels = []

        for channel in audio:
            # Calculate RMS envelope
            window_size = int(sample_rate * 0.01)  # 10ms window
            rms = np.sqrt(np.convolve(channel**2, np.ones(window_size) / window_size, mode="same"))

            # Calculate gain reduction
            gain_reduction = np.ones_like(rms)
            above_threshold = rms > threshold

            if np.any(above_threshold):
                excess = rms[above_threshold] - threshold
                compressed = threshold + excess / ratio
                gain_reduction[above_threshold] = compressed / rms[above_threshold]

            # Apply attack/release envelope
            attack_samples = int(sample_rate * attack_ms / 1000.0)
            release_samples = int(sample_rate * release_ms / 1000.0)

            envelope = np.ones_like(gain_reduction)
            for i in range(1, len(envelope)):
                if gain_reduction[i] < envelope[i - 1]:
                    # Attack
                    alpha = 1.0 / attack_samples
                else:
                    # Release
                    alpha = 1.0 / release_samples

                envelope[i] = envelope[i - 1] * (1 - alpha) + gain_reduction[i] * alpha

            # Apply compression
            processed = channel * envelope
            processed_channels.append(processed)

        result = np.array(processed_channels)
        if was_mono:
            result = result[0]

        # Normalize
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val * 0.95

        return result

    def _apply_reverb(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply reverb effect."""
        room_size = params.get("room_size", 0.5)
        damping = params.get("damping", 0.5)
        wet_level = params.get("wet_level", 0.3)

        # Create delay taps for early reflections
        delay_times = [
            int(sample_rate * 0.03 * room_size),
            int(sample_rate * 0.05 * room_size),
            int(sample_rate * 0.07 * room_size),
        ]

        reverb_signal = np.zeros_like(audio)

        for delay_time in delay_times:
            if delay_time < len(audio):
                delayed = np.pad(audio[:-delay_time], (delay_time, 0), mode="constant")
                reverb_signal += delayed * (1.0 - damping) * 0.3

        # Mix dry and wet
        result = audio * (1.0 - wet_level) + reverb_signal * wet_level

        # Normalize
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val * 0.95

        return result

    def _apply_delay(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply delay effect."""
        delay_time_ms = params.get("delay_time", 200.0)
        feedback = params.get("feedback", 0.3)
        mix = params.get("mix", 0.3)

        delay_samples = int(sample_rate * delay_time_ms / 1000.0)

        if delay_samples >= len(audio):
            return audio

        delayed = np.pad(audio[:-delay_samples], (delay_samples, 0), mode="constant")

        # Apply feedback
        if feedback > 0:
            feedback_signal = delayed * feedback
            if delay_samples < len(feedback_signal):
                delayed[delay_samples:] += feedback_signal[:-delay_samples]

        # Mix
        result = audio * (1.0 - mix) + delayed * mix

        # Normalize
        max_val = np.max(np.abs(result))
        if max_val > 0:
            result = result / max_val * 0.95

        return result

    def _apply_filter(self, audio: np.ndarray, sample_rate: int, params: dict) -> np.ndarray:
        """Apply filter effect."""
        if not HAS_SCIPY:
            logger.warning("scipy required for filter")
            return audio

        cutoff = params.get("cutoff", 5000.0)
        filter_type = params.get("filter_type", 0)  # 0=lowpass, 1=highpass, 2=bandpass
        resonance = params.get("resonance", 0.5)

        nyquist = sample_rate / 2.0
        normalized_cutoff = cutoff / nyquist

        if normalized_cutoff >= 1.0:
            normalized_cutoff = 0.99

        # Process each channel
        if len(audio.shape) == 1:
            audio = audio.reshape(1, -1)
            was_mono = True
        else:
            was_mono = False

        processed_channels = []

        for channel in audio:
            if filter_type == 0:  # Lowpass
                b, a = signal.iirfilter(4, normalized_cutoff, btype="lowpass", ftype="butter")
            elif filter_type == 1:  # Highpass
                b, a = signal.iirfilter(4, normalized_cutoff, btype="highpass", ftype="butter")
            else:  # Bandpass
                bandwidth = normalized_cutoff * (1.0 - resonance)
                low = max(0.01, normalized_cutoff - bandwidth / 2)
                high = min(0.99, normalized_cutoff + bandwidth / 2)
                b, a = signal.iirfilter(4, [low, high], btype="bandpass", ftype="butter")

            processed = signal.filtfilt(b, a, channel)
            processed_channels.append(processed)

        result = np.array(processed_channels)
        if was_mono:
            result = result[0]

        return result

    def _apply_pedalboard_effect(
        self,
        audio: np.ndarray,
        sample_rate: int,
        effect_type: str,
        params: dict,
    ) -> np.ndarray:
        """
        Apply effect using pedalboard for professional-quality processing.

        Args:
            audio: Input audio array
            sample_rate: Sample rate
            effect_type: Type of effect to apply
            params: Effect parameters

        Returns:
            Processed audio array
        """
        if not HAS_PEDALBOARD:
            raise ImportError("pedalboard not available")

        # Ensure audio is in correct format (float32, shape: [samples] or [channels, samples])
        if len(audio.shape) == 1:
            audio = audio.reshape(1, -1)  # Make it [1, samples] for mono
            was_mono = True
        else:
            was_mono = False

        # Convert to float32 if needed
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Create pedalboard with appropriate effect
        board = Pedalboard([])

        effect_type = effect_type.lower()
        if effect_type == "reverb":
            room_size = params.get("room_size", 0.5)
            damping = params.get("damping", 0.5)
            wet_level = params.get("wet_level", 0.3)
            board.append(
                Reverb(
                    room_size=room_size,
                    damping=damping,
                    wet_level=wet_level,
                    dry_level=1.0 - wet_level,
                )
            )
        elif effect_type == "delay":
            delay_seconds = params.get("delay_time", 200.0) / 1000.0
            feedback = params.get("feedback", 0.3)
            mix = params.get("mix", 0.3)
            board.append(Delay(delay_seconds=delay_seconds, feedback=feedback, mix=mix))
        elif effect_type == "compressor":
            threshold_db = params.get("threshold", -12.0)
            ratio = params.get("ratio", 4.0)
            attack_ms = params.get("attack", 5.0)
            release_ms = params.get("release", 50.0)
            board.append(
                Compressor(
                    threshold_db=threshold_db,
                    ratio=ratio,
                    attack_ms=attack_ms,
                    release_ms=release_ms,
                )
            )
        elif effect_type == "filter":
            cutoff = params.get("cutoff", 5000.0)
            filter_type = params.get("filter_type", 0)  # 0=lowpass, 1=highpass
            if filter_type == 0:
                board.append(LowpassFilter(cutoff_frequency_hz=cutoff))
            elif filter_type == 1:
                board.append(HighpassFilter(cutoff_frequency_hz=cutoff))
        elif effect_type == "chorus":
            rate_hz = params.get("rate", 1.5)
            depth = params.get("depth", 0.5)
            centre_delay_ms = params.get("centre_delay", 7.0)
            feedback = params.get("feedback", 0.0)
            mix = params.get("mix", 0.5)
            board.append(
                Chorus(
                    rate_hz=rate_hz,
                    depth=depth,
                    centre_delay_ms=centre_delay_ms,
                    feedback=feedback,
                    mix=mix,
                )
            )
        elif effect_type == "phaser":
            rate_hz = params.get("rate", 1.0)
            depth = params.get("depth", 0.5)
            centre_frequency_hz = params.get("centre_frequency", 1000.0)
            feedback = params.get("feedback", 0.0)
            mix = params.get("mix", 0.5)
            board.append(
                Phaser(
                    rate_hz=rate_hz,
                    depth=depth,
                    centre_frequency_hz=centre_frequency_hz,
                    feedback=feedback,
                    mix=mix,
                )
            )
        elif effect_type == "distortion":
            drive_db = params.get("drive", 20.0)
            board.append(Distortion(drive_db=drive_db))
        elif effect_type == "gain":
            gain_db = params.get("gain", 0.0)
            board.append(Gain(gain_db=gain_db))
        elif effect_type == "limiter":
            threshold_db = params.get("threshold", -1.0)
            release_ms = params.get("release", 50.0)
            board.append(Limiter(threshold_db=threshold_db, release_ms=release_ms))
        else:
            logger.warning(
                f"Pedalboard effect type '{effect_type}' not supported, " "using standard effect"
            )
            return audio

        # Process audio through pedalboard
        try:
            processed = board(audio, sample_rate)
        except Exception as e:
            logger.warning(f"Pedalboard processing failed: {e}")
            return audio

        # Convert back to original shape
        if was_mono:
            processed = processed[0] if len(processed.shape) > 1 else processed

        # Ensure output is float32
        if processed.dtype != np.float32:
            processed = processed.astype(np.float32)

        return processed


def create_post_fx_processor(sample_rate: int = 24000) -> PostFXProcessor:
    """
    Factory function to create a Post-FX Processor instance.

    Args:
        sample_rate: Default sample rate for processing

    Returns:
        Initialized PostFXProcessor instance
    """
    return PostFXProcessor(sample_rate=sample_rate)


def process_audio_with_post_fx(
    audio: np.ndarray,
    sample_rate: int,
    effects: list[dict] | None = None,
    **kwargs,
) -> np.ndarray:
    """
    Convenience function to process audio with post-FX effects.

    Args:
        audio: Input audio array
        sample_rate: Sample rate
        effects: List of effect dictionaries
        **kwargs: Additional processing options

    Returns:
        Processed audio array
    """
    processor = PostFXProcessor(sample_rate=sample_rate)
    return processor.process(audio, sample_rate, effects, **kwargs)
