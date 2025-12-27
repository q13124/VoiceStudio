"""
Advanced Quality Enhancement for Voice Cloning
Provides sophisticated post-processing to improve voice cloning quality

Features:
- Multi-stage denoising
- Spectral enhancement
- Formant preservation
- Prosody enhancement
- Advanced artifact removal
- Adaptive processing
"""

import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    import librosa

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logger.warning(
        "librosa not available. Advanced quality enhancement will be limited."
    )

try:
    import noisereduce as nr

    HAS_NOISEREDUCE = True
except ImportError:
    HAS_NOISEREDUCE = False
    logger.warning("noisereduce not available. Advanced denoising will be limited.")

try:
    from scipy import signal

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("scipy not available. Some advanced features will be limited.")

try:
    import pyloudnorm as pyln

    HAS_PYLOUDNORM = True
except ImportError:
    HAS_PYLOUDNORM = False
    logger.warning("pyloudnorm not available. LUFS normalization will be limited.")


def enhance_spectral_quality(
    audio: np.ndarray, sample_rate: int, strength: float = 0.5
) -> np.ndarray:
    """
    Enhance spectral quality using spectral gating and enhancement.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        strength: Enhancement strength (0.0 to 1.0)

    Returns:
        Enhanced audio array
    """
    if not HAS_LIBROSA:
        return audio

    try:
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=0)

        # Compute STFT
        stft = librosa.stft(audio, hop_length=512, n_fft=2048)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # Spectral enhancement: boost important frequencies
        # Voice frequencies: 85-3400 Hz (fundamental + formants)
        freqs = librosa.fft_frequencies(sr=sample_rate, n_fft=2048)
        voice_mask = (freqs >= 85) & (freqs <= 3400)

        # Apply gentle boost to voice frequencies
        enhancement = np.ones_like(magnitude)
        enhancement[voice_mask, :] += strength * 0.2  # 20% boost max

        # Apply enhancement
        enhanced_magnitude = magnitude * enhancement

        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=512)

        # Match original length
        if len(enhanced_audio) < len(audio):
            enhanced_audio = np.pad(
                enhanced_audio, (0, len(audio) - len(enhanced_audio))
            )
        elif len(enhanced_audio) > len(audio):
            enhanced_audio = enhanced_audio[: len(audio)]

        return enhanced_audio.astype(audio.dtype)

    except Exception as e:
        logger.warning(f"Spectral enhancement failed: {e}")
        return audio


def preserve_formants(
    audio: np.ndarray, sample_rate: int, reference_audio: Optional[np.ndarray] = None
) -> np.ndarray:
    """
    Preserve or enhance formant structure for natural voice quality.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        reference_audio: Optional reference audio for formant matching

    Returns:
        Audio with preserved formants
    """
    if not HAS_LIBROSA:
        return audio

    try:
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=0)

        # Extract formants using LPC (Linear Predictive Coding)
        # This helps preserve natural voice characteristics
        order = 10  # LPC order

        # Apply pre-emphasis
        pre_emph = librosa.effects.preemphasis(audio)

        # Compute LPC coefficients
        lpc_coeffs = librosa.lpc(pre_emph, order=order)

        # Filter audio to preserve formant structure
        # This helps maintain natural voice timbre
        filtered = signal.lfilter([1], lpc_coeffs, audio)

        # Blend original and filtered (preserve dynamics)
        preserved = 0.7 * audio + 0.3 * filtered

        return preserved.astype(audio.dtype)

    except Exception as e:
        logger.warning(f"Formant preservation failed: {e}")
        return audio


def enhance_prosody(
    audio: np.ndarray, sample_rate: int, strength: float = 0.3
) -> np.ndarray:
    """
    Enhance prosody (rhythm, stress, intonation) for more natural speech.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        strength: Enhancement strength (0.0 to 1.0)

    Returns:
        Audio with enhanced prosody
    """
    if not HAS_LIBROSA:
        return audio

    try:
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=0)

        # Extract fundamental frequency (F0)
        f0, voiced_flag = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sample_rate,
        )

        # Smooth F0 contour (reduce jitter)
        if np.any(voiced_flag):
            f0_smooth = np.copy(f0)
            # Simple median filter for smoothing
            for i in range(1, len(f0) - 1):
                if not np.isnan(f0[i]):
                    neighbors = [f0[i - 1], f0[i], f0[i + 1]]
                    neighbors = [f for f in neighbors if not np.isnan(f)]
                    if neighbors:
                        f0_smooth[i] = np.median(neighbors)

            # Apply gentle prosody enhancement
            # This helps make speech more natural
            f0_enhanced = f0_smooth + strength * 0.1 * (
                f0_smooth - np.nanmean(f0_smooth)
            )

            # Re-synthesize with enhanced F0 (simplified)
            # In practice, this would use vocoder
            # For now, apply gentle pitch correction
            enhanced = audio.copy()

            # Apply subtle pitch correction using phase vocoder
            if np.any(~np.isnan(f0_enhanced)):
                # Calculate average F0 shift needed
                f0_mean = np.nanmean(f0_smooth)
                f0_enhanced_mean = np.nanmean(f0_enhanced)
                
                if f0_mean > 0 and abs(f0_enhanced_mean - f0_mean) > 1.0:
                    # Calculate pitch shift in semitones
                    pitch_ratio = f0_enhanced_mean / f0_mean
                    semitones = 12 * np.log2(pitch_ratio)
                    
                    # Limit pitch shift to reasonable range
                    semitones = max(-2.0, min(2.0, semitones))
                    
                    if abs(semitones) > 0.1:
                        # Apply pitch shift using librosa or pyrubberband
                        try:
                            if HAS_LIBROSA:
                                enhanced = librosa.effects.pitch_shift(
                                    audio, sr=sample_rate, n_steps=semitones
                                )
                            else:
                                # Fallback: use simple resampling approximation
                                enhanced = audio.copy()
                        except Exception as e:
                            logger.debug(f"Pitch correction failed: {e}")
                            enhanced = audio.copy()
                    else:
                        enhanced = audio.copy()
                else:
                    enhanced = audio.copy()
            else:
                enhanced = audio.copy()
            
            return enhanced

        return audio

    except Exception as e:
        logger.warning(f"Prosody enhancement failed: {e}")
        return audio


def advanced_denoise(
    audio: np.ndarray, sample_rate: int, strength: float = 0.8, stationary: bool = False
) -> np.ndarray:
    """
    Advanced multi-stage denoising with adaptive processing.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        strength: Denoising strength (0.0 to 1.0)
        stationary: Whether noise is stationary

    Returns:
        Denoised audio array
    """
    if not HAS_NOISEREDUCE:
        return audio

    try:
        # Convert to mono if stereo
        is_stereo = len(audio.shape) > 1
        if is_stereo:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio

        # Multi-stage denoising
        # Stage 1: General noise reduction
        denoised = nr.reduce_noise(
            y=audio_mono, sr=sample_rate, stationary=stationary, prop_decrease=strength
        )

        # Stage 2: Spectral gating for residual noise
        if strength > 0.5:
            # Apply additional spectral gating
            stft = librosa.stft(denoised, hop_length=512, n_fft=2048)
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # Gate low-energy regions (likely noise)
            threshold = np.percentile(magnitude, 10)
            gate = magnitude > threshold
            gated_magnitude = magnitude * gate

            # Reconstruct
            gated_stft = gated_magnitude * np.exp(1j * phase)
            denoised = librosa.istft(gated_stft, hop_length=512)

            # Match length
            if len(denoised) < len(audio_mono):
                denoised = np.pad(denoised, (0, len(audio_mono) - len(denoised)))
            elif len(denoised) > len(audio_mono):
                denoised = denoised[: len(audio_mono)]

        # Restore stereo if original was stereo
        if is_stereo:
            denoised = np.stack([denoised, denoised])

        return denoised.astype(audio.dtype)

    except Exception as e:
        logger.warning(f"Advanced denoising failed: {e}")
        return audio


def remove_artifacts_advanced(
    audio: np.ndarray, sample_rate: int, strength: float = 0.7
) -> np.ndarray:
    """
    Advanced artifact removal for synthesis artifacts.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        strength: Removal strength (0.0 to 1.0)

    Returns:
        Audio with artifacts removed
    """
    if not HAS_LIBROSA:
        return audio

    try:
        # Convert to mono if stereo
        is_stereo = len(audio.shape) > 1
        if is_stereo:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio

        cleaned = audio_mono.copy()

        # Remove clicks (sudden amplitude spikes)
        diff = np.diff(cleaned)
        large_changes = np.abs(diff) > 0.3 * np.max(np.abs(cleaned))

        if np.any(large_changes):
            # Smooth out clicks
            for i in np.where(large_changes)[0]:
                if i > 0 and i < len(cleaned) - 1:
                    # Interpolate over click
                    cleaned[i] = 0.5 * (cleaned[i - 1] + cleaned[i + 1])

        # Remove clipping/distortion
        clipping_threshold = 0.95
        clipped = np.abs(cleaned) > clipping_threshold
        if np.any(clipped):
            # Soft limit instead of hard clipping
            clipped_samples = cleaned[clipped]
            cleaned[clipped] = np.sign(clipped_samples) * (
                clipping_threshold
                + (1 - clipping_threshold)
                * np.tanh(
                    (np.abs(clipped_samples) - clipping_threshold)
                    / (1 - clipping_threshold)
                )
            )

        # Remove high-frequency artifacts (common in synthesis)
        if HAS_SCIPY:
            # High-pass filter to remove low-frequency rumble
            sos = signal.butter(4, 80, "hp", fs=sample_rate, output="sos")
            cleaned = signal.sosfilt(sos, cleaned)

            # Low-pass filter to remove high-frequency artifacts
            sos = signal.butter(4, 8000, "lp", fs=sample_rate, output="sos")
            cleaned = signal.sosfilt(sos, cleaned)

        # Restore stereo if original was stereo
        if is_stereo:
            cleaned = np.stack([cleaned, cleaned])

        return cleaned.astype(audio.dtype)

    except Exception as e:
        logger.warning(f"Advanced artifact removal failed: {e}")
        return audio


def enhance_voice_quality_advanced(
    audio: np.ndarray,
    sample_rate: int,
    reference_audio: Optional[np.ndarray] = None,
    normalize: bool = True,
    denoise: bool = True,
    spectral_enhance: bool = True,
    preserve_formants: bool = True,
    enhance_prosody: bool = False,
    remove_artifacts: bool = True,
    target_lufs: float = -23.0,
    denoise_strength: float = 0.8,
    spectral_strength: float = 0.5,
    prosody_strength: float = 0.3,
    artifact_strength: float = 0.7,
) -> np.ndarray:
    """
    Advanced multi-stage quality enhancement pipeline for voice cloning.

    Applies sophisticated post-processing to maximize voice cloning quality:
    1. Advanced denoising (multi-stage)
    2. Spectral enhancement (voice frequency boost)
    3. Formant preservation (natural timbre)
    4. Prosody enhancement (natural rhythm)
    5. Artifact removal (synthesis artifacts)
    6. LUFS normalization (consistent loudness)

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        reference_audio: Optional reference audio for formant matching
        normalize: Whether to normalize to target LUFS
        denoise: Whether to apply advanced denoising
        spectral_enhance: Whether to enhance spectral quality
        preserve_formants: Whether to preserve formant structure
        enhance_prosody: Whether to enhance prosody (slower)
        remove_artifacts: Whether to remove synthesis artifacts
        target_lufs: Target LUFS for normalization
        denoise_strength: Denoising strength (0.0 to 1.0)
        spectral_strength: Spectral enhancement strength (0.0 to 1.0)
        prosody_strength: Prosody enhancement strength (0.0 to 1.0)
        artifact_strength: Artifact removal strength (0.0 to 1.0)

    Returns:
        Enhanced audio array

    Raises:
        ImportError: If required libraries are not installed
    """
    enhanced = audio.copy()

    # Stage 1: Denoising (early to remove noise before other processing)
    if denoise:
        enhanced = advanced_denoise(enhanced, sample_rate, strength=denoise_strength)

    # Stage 2: Artifact removal (remove synthesis artifacts)
    if remove_artifacts:
        enhanced = remove_artifacts_advanced(
            enhanced, sample_rate, strength=artifact_strength
        )

    # Stage 3: Spectral enhancement (boost voice frequencies)
    if spectral_enhance:
        enhanced = enhance_spectral_quality(
            enhanced, sample_rate, strength=spectral_strength
        )

    # Stage 4: Formant preservation (maintain natural timbre)
    if preserve_formants:
        enhanced = preserve_formants(
            enhanced, sample_rate, reference_audio=reference_audio
        )

    # Stage 5: Prosody enhancement (improve naturalness - optional, slower)
    if enhance_prosody:
        enhanced = enhance_prosody(enhanced, sample_rate, strength=prosody_strength)

    # Stage 6: Normalization (final loudness matching)
    if normalize and HAS_PYLOUDNORM:
        try:
            # Convert to mono for LUFS calculation
            is_stereo = len(enhanced.shape) > 1
            if is_stereo:
                enhanced_mono = np.mean(enhanced, axis=0)
            else:
                enhanced_mono = enhanced

            # Measure loudness
            meter = pyln.Meter(sample_rate)
            loudness = meter.integrated_loudness(enhanced_mono)

            # Normalize to target LUFS
            if not np.isnan(loudness):
                target_lufs_db = target_lufs
                current_lufs_db = loudness
                gain_db = target_lufs_db - current_lufs_db
                gain_linear = 10 ** (gain_db / 20.0)

                # Apply gain
                enhanced_mono = enhanced_mono * gain_linear

                # Prevent clipping
                max_val = np.max(np.abs(enhanced_mono))
                if max_val > 0.95:
                    enhanced_mono = enhanced_mono * (0.95 / max_val)

                # Restore stereo if needed
                if is_stereo:
                    enhanced = np.stack([enhanced_mono, enhanced_mono])
                else:
                    enhanced = enhanced_mono
        except Exception as e:
            logger.warning(f"LUFS normalization failed: {e}")
            # Fallback to peak normalization
            max_val = np.max(np.abs(enhanced))
            if max_val > 0:
                enhanced = enhanced / max_val * 0.95

    return enhanced.astype(audio.dtype)
