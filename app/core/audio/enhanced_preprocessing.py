"""
Enhanced Preprocessing Module for VoiceStudio
Advanced audio preprocessing pipeline for voice cloning workflows

Compatible with:
- Python 3.10+
- librosa>=0.11.0
- scipy>=1.9.0
- numpy>=1.26.0
- pyloudnorm>=0.1.1
- noisereduce>=3.0.2
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

# Import audio utilities
try:
    from .audio_utils import (
        enhance_voice_quality,
        normalize_lufs,
        remove_artifacts,
        resample_audio,
    )

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    logger.warning("audio_utils not available")


class EnhancedPreprocessor:
    """
    Enhanced Preprocessor for advanced audio preprocessing.

    Supports:
    - Automatic sample rate conversion
    - Advanced denoising
    - Voice activity detection (VAD)
    - Silence trimming
    - DC offset removal
    - High-pass filtering
    - Automatic gain control (AGC)
    - Spectral gating
    - Multi-stage processing pipeline
    """

    def __init__(self, sample_rate: int = 24000, target_sample_rate: int = 24000):
        """
        Initialize Enhanced Preprocessor.

        Args:
            sample_rate: Default input sample rate
            target_sample_rate: Target output sample rate
        """
        self.sample_rate = sample_rate
        self.target_sample_rate = target_sample_rate

    def preprocess(
        self,
        audio: np.ndarray,
        sample_rate: int | None = None,
        config: dict | None = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Apply enhanced preprocessing pipeline to audio.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            config: Preprocessing configuration dictionary:
                - resample: Resample to target rate
                - remove_dc: Remove DC offset
                - highpass: Apply high-pass filter
                - denoise: Apply denoising
                - vad: Apply voice activity detection
                - trim_silence: Trim silence from start/end
                - agc: Apply automatic gain control
                - spectral_gate: Apply spectral gating
                - normalize: Normalize to target LUFS
            **kwargs: Additional processing options

        Returns:
            Preprocessed audio array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if config is None:
            config = {}

        processed = audio.copy()

        # 1. Remove DC offset
        if config.get("remove_dc", True):
            processed = self._remove_dc_offset(processed)

        # 2. High-pass filter (remove low-frequency noise)
        if config.get("highpass", True):
            processed = self._apply_highpass(processed, sample_rate)

        # 3. Resample if needed
        if config.get("resample", True) and sample_rate != self.target_sample_rate:
            if HAS_LIBROSA:
                processed = librosa.resample(
                    processed, orig_sr=sample_rate, target_sr=self.target_sample_rate
                )
                sample_rate = self.target_sample_rate
            elif HAS_AUDIO_UTILS:
                processed = resample_audio(
                    processed, sample_rate, self.target_sample_rate
                )
                sample_rate = self.target_sample_rate

        # 4. Voice activity detection and silence trimming
        if config.get("trim_silence", True):
            processed = self._trim_silence(processed, sample_rate)

        # 5. Denoising
        if config.get("denoise", True):
            processed = self._apply_denoising(processed, sample_rate, config)

        # 6. Spectral gating (remove non-voice frequencies)
        if config.get("spectral_gate", False):
            processed = self._apply_spectral_gate(processed, sample_rate)

        # 7. Automatic gain control
        if config.get("agc", False):
            processed = self._apply_agc(processed, sample_rate)

        # 8. Normalize to target LUFS
        if config.get("normalize", True):
            target_lufs = config.get("target_lufs", -23.0)
            processed = self._apply_normalization(processed, sample_rate, target_lufs)

        # 9. Final artifact removal
        if config.get("remove_artifacts", True) and HAS_AUDIO_UTILS:
            processed = remove_artifacts(processed, sample_rate)

        return processed

    def _remove_dc_offset(self, audio: np.ndarray) -> np.ndarray:
        """Remove DC offset from audio (optimized with vectorized operations)."""
        if len(audio.shape) == 1:
            # Vectorized for mono
            return audio - np.mean(audio)
        else:
            # Vectorized for multi-channel (process all channels at once)
            dc_offsets = np.mean(audio, axis=0, keepdims=True)
            return audio - dc_offsets

    def _apply_highpass(
        self, audio: np.ndarray, sample_rate: int, cutoff: float = 80.0
    ) -> np.ndarray:
        """Apply high-pass filter to remove low-frequency noise."""
        if not HAS_SCIPY:
            logger.warning("scipy required for high-pass filtering")
            return audio

        nyquist = sample_rate / 2.0
        normalized_cutoff = cutoff / nyquist

        if normalized_cutoff >= 1.0:
            return audio

        try:
            b, a = signal.iirfilter(
                4, normalized_cutoff, btype="highpass", ftype="butter"
            )

            if len(audio.shape) == 1:
                return signal.filtfilt(b, a, audio)
            else:
                # Process all channels (vectorized where possible)
                # Note: filtfilt doesn't support multi-channel directly, but we can optimize
                processed = np.zeros_like(audio)
                for ch in range(audio.shape[1]):
                    processed[:, ch] = signal.filtfilt(b, a, audio[:, ch])
                return processed
        except Exception as e:
            logger.warning(f"High-pass filtering failed: {e}")
            return audio

    def _trim_silence(
        self,
        audio: np.ndarray,
        sample_rate: int,
        threshold_db: float = -40.0,
        frame_length: int = 2048,
        hop_length: int = 512,
    ) -> np.ndarray:
        """Trim silence from start and end of audio."""
        if not HAS_LIBROSA:
            logger.warning("librosa required for silence trimming")
            return audio

        # Convert to mono for VAD
        audio_mono = np.mean(audio, axis=1) if len(audio.shape) > 1 else audio

        try:
            # Use librosa's trim function
            trimmed, _ = librosa.effects.trim(
                audio_mono,
                top_db=abs(threshold_db),
                frame_length=frame_length,
                hop_length=hop_length,
            )

            # Apply same trimming to original audio
            trim_start = len(audio_mono) - len(trimmed)
            trim_end = len(audio_mono)

            # Find actual trim points
            if len(audio.shape) == 1:
                return audio[trim_start:trim_end]
            else:
                return audio[trim_start:trim_end, :]

        except Exception as e:
            logger.warning(f"Silence trimming failed: {e}")
            return audio

    def _apply_denoising(
        self, audio: np.ndarray, sample_rate: int, config: dict
    ) -> np.ndarray:
        """Apply advanced denoising."""
        if HAS_AUDIO_UTILS:
            try:
                return enhance_voice_quality(
                    audio,
                    sample_rate,
                    normalize=False,  # Normalization done separately
                    denoise=True,
                )
            except Exception:
                ...

        if HAS_NOISEREDUCE:
            try:
                strength = config.get("denoise_strength", 0.5)
                if len(audio.shape) == 1:
                    return nr.reduce_noise(
                        y=audio,
                        sr=sample_rate,
                        stationary=False,
                        prop_decrease=strength,
                    )
                else:
                    processed = audio.copy()
                    for ch in range(audio.shape[1]):
                        processed[:, ch] = nr.reduce_noise(
                            y=audio[:, ch],
                            sr=sample_rate,
                            stationary=False,
                            prop_decrease=strength,
                        )
                    return processed
            except Exception as e:
                logger.warning(f"Denoising failed: {e}")

        return audio

    def _apply_spectral_gate(
        self,
        audio: np.ndarray,
        sample_rate: int,
        voice_freq_min: float = 80.0,
        voice_freq_max: float = 8000.0,
    ) -> np.ndarray:
        """Apply spectral gating to remove non-voice frequencies."""
        if not HAS_LIBROSA or not HAS_SCIPY:
            logger.warning("librosa and scipy required for spectral gating")
            return audio

        try:
            # Compute STFT
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Get frequency bins
            freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=2048)

            # Create mask for voice frequencies
            voice_mask = (freqs >= voice_freq_min) & (freqs <= voice_freq_max)
            gate_mask = np.zeros_like(magnitude)
            gate_mask[voice_mask, :] = 1.0

            # Apply gate
            gated_magnitude = magnitude * gate_mask

            # Reconstruct audio
            gated_stft = gated_magnitude * np.exp(1j * phase)
            gated_audio = librosa.istft(gated_stft, hop_length=512)

            # Match length
            if len(gated_audio) < len(audio):
                gated_audio = np.pad(
                    gated_audio, (0, len(audio) - len(gated_audio)), mode="constant"
                )
            elif len(gated_audio) > len(audio):
                gated_audio = gated_audio[: len(audio)]

            return gated_audio

        except Exception as e:
            logger.warning(f"Spectral gating failed: {e}")
            return audio

    def _apply_agc(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_level: float = -23.0,
        attack_time: float = 0.01,
        release_time: float = 0.1,
    ) -> np.ndarray:
        """Apply automatic gain control."""
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        # Calculate RMS envelope
        window_size = int(sample_rate * 0.01)  # 10ms window
        rms = np.sqrt(
            np.convolve(audio**2, np.ones(window_size) / window_size, mode="same")
        )

        # Convert target level to linear
        target_linear = 10.0 ** (target_level / 20.0)

        # Calculate gain adjustment
        gain = np.ones_like(rms)
        gain[rms > 0] = target_linear / rms[rms > 0]

        # Apply attack/release envelope
        attack_samples = int(sample_rate * attack_time)
        release_samples = int(sample_rate * release_time)

        envelope = np.ones_like(gain)
        for i in range(1, len(envelope)):
            if gain[i] < envelope[i - 1]:
                # Attack
                alpha = 1.0 / attack_samples
            else:
                # Release
                alpha = 1.0 / release_samples

            envelope[i] = envelope[i - 1] * (1 - alpha) + gain[i] * alpha

        # Limit gain range
        envelope = np.clip(envelope, 0.1, 3.0)

        # Apply AGC
        processed = audio * envelope

        # Normalize to prevent clipping
        max_val = np.max(np.abs(processed))
        if max_val > 0.95:
            processed = processed / max_val * 0.95

        return processed

    def _apply_normalization(
        self, audio: np.ndarray, sample_rate: int, target_lufs: float
    ) -> np.ndarray:
        """Apply LUFS normalization."""
        if HAS_AUDIO_UTILS:
            try:
                return normalize_lufs(audio, sample_rate, target_lufs)
            except Exception as e:
                logger.warning(f"LUFS normalization failed: {e}")
                # Fallback to peak normalization
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    return audio / max_val * 0.95
                return audio

        # Fallback to peak normalization
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * 0.95
        return audio

    def get_preset(self, preset_name: str) -> dict:
        """Get preprocessing preset configuration."""
        presets = {
            "voice_cloning": {
                "resample": True,
                "remove_dc": True,
                "highpass": True,
                "denoise": True,
                "trim_silence": True,
                "agc": False,
                "spectral_gate": False,
                "normalize": True,
                "remove_artifacts": True,
                "target_lufs": -23.0,
                "denoise_strength": 0.5,
            },
            "broadcast": {
                "resample": True,
                "remove_dc": True,
                "highpass": True,
                "denoise": True,
                "trim_silence": True,
                "agc": True,
                "spectral_gate": False,
                "normalize": True,
                "remove_artifacts": True,
                "target_lufs": -23.0,
                "denoise_strength": 0.7,
            },
            "podcast": {
                "resample": True,
                "remove_dc": True,
                "highpass": True,
                "denoise": True,
                "trim_silence": True,
                "agc": False,
                "spectral_gate": False,
                "normalize": True,
                "remove_artifacts": True,
                "target_lufs": -19.0,
                "denoise_strength": 0.6,
            },
            "minimal": {
                "resample": True,
                "remove_dc": True,
                "highpass": False,
                "denoise": False,
                "trim_silence": False,
                "agc": False,
                "spectral_gate": False,
                "normalize": True,
                "remove_artifacts": False,
                "target_lufs": -23.0,
            },
        }

        return presets.get(preset_name.lower(), presets["voice_cloning"])


def create_enhanced_preprocessor(
    sample_rate: int = 24000, target_sample_rate: int = 24000
) -> EnhancedPreprocessor:
    """
    Factory function to create an Enhanced Preprocessor instance.

    Args:
        sample_rate: Default input sample rate
        target_sample_rate: Target output sample rate

    Returns:
        Initialized EnhancedPreprocessor instance
    """
    return EnhancedPreprocessor(
        sample_rate=sample_rate, target_sample_rate=target_sample_rate
    )


def preprocess_audio(
    audio: np.ndarray,
    sample_rate: int = 24000,
    preset: str | None = None,
    config: dict | None = None,
    **kwargs,
) -> np.ndarray:
    """
    Convenience function to preprocess audio.

    Args:
        audio: Input audio array
        sample_rate: Sample rate
        preset: Preprocessing preset name
        config: Custom preprocessing configuration
        **kwargs: Additional processing options

    Returns:
        Preprocessed audio array
    """
    preprocessor = EnhancedPreprocessor(sample_rate=sample_rate)
    if preset:
        preset_config = preprocessor.get_preset(preset)
        if config:
            preset_config.update(config)
        config = preset_config
    return preprocessor.preprocess(audio, sample_rate, config, **kwargs)
