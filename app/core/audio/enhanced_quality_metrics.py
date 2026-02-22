"""
Enhanced Quality Metrics Module for VoiceStudio
Comprehensive audio quality assessment and metrics calculation

Compatible with:
- Python 3.10+
- librosa>=0.11.0
- numpy>=1.26.0
- pyloudnorm>=0.1.1
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
    import pyloudnorm as pyln

    HAS_PYLOUDNORM = True
except ImportError:
    HAS_PYLOUDNORM = False
    logger.warning("pyloudnorm not installed. Install with: pip install pyloudnorm")

# Import existing quality metrics
try:
    # Import directly to avoid circular import issues
    import importlib.util

    # Try to import quality_metrics module
    spec = importlib.util.find_spec("app.core.engines.quality_metrics")
    if spec is not None:
        quality_metrics_module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(quality_metrics_module)
            calculate_all_metrics = quality_metrics_module.calculate_all_metrics
            calculate_mos_score = quality_metrics_module.calculate_mos_score
            calculate_naturalness = quality_metrics_module.calculate_naturalness
            calculate_similarity = quality_metrics_module.calculate_similarity
            calculate_snr = quality_metrics_module.calculate_snr
            detect_artifacts = quality_metrics_module.detect_artifacts
            load_audio = quality_metrics_module.load_audio
            HAS_QUALITY_METRICS = True
        except Exception as e:
            logger.warning(f"Failed to load quality_metrics: {e}")
            HAS_QUALITY_METRICS = False
    else:
        HAS_QUALITY_METRICS = False
except Exception as e:
    HAS_QUALITY_METRICS = False
    logger.warning(f"quality_metrics not available: {e}")

# Import audio utilities
try:
    from .audio_utils import analyze_voice_characteristics

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    logger.warning("audio_utils not available")

# Import LUFS meter
try:
    from .lufs_meter import LUFSMeter

    HAS_LUFS_METER = True
except ImportError:
    HAS_LUFS_METER = False
    logger.warning("lufs_meter not available")


class EnhancedQualityMetrics:
    """
    Enhanced Quality Metrics for comprehensive audio assessment.

    Supports:
    - Comprehensive quality metrics calculation
    - Voice characteristics analysis
    - Loudness metrics (LUFS)
    - Spectral analysis
    - Prosody analysis
    - Quality scoring
    - Batch processing
    """

    def __init__(self, sample_rate: int = 24000):
        """
        Initialize Enhanced Quality Metrics.

        Args:
            sample_rate: Default sample rate for processing
        """
        self.sample_rate = sample_rate
        self.lufs_meter = None

        if HAS_LUFS_METER:
            try:
                self.lufs_meter = LUFSMeter(sample_rate=sample_rate)
            except Exception as e:
                logger.warning(f"Failed to initialize LUFS meter: {e}")

    def calculate_all(
        self,
        audio: np.ndarray,
        sample_rate: int | None = None,
        reference_audio: str | np.ndarray | None = None,
        include_advanced: bool = True,
    ) -> dict[str, float | dict | list]:
        """
        Calculate all quality metrics for audio.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            reference_audio: Optional reference audio for comparison
            include_advanced: Include advanced metrics (slower)

        Returns:
            Dictionary with all quality metrics
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        metrics = {}

        # Basic metrics (from existing quality_metrics)
        if HAS_QUALITY_METRICS:
            try:
                basic_metrics = calculate_all_metrics(
                    audio, reference_audio, sample_rate, use_cache=True
                )
                metrics.update(basic_metrics)
            except Exception as e:
                logger.warning(f"Basic metrics calculation failed: {e}")

        # LUFS metrics
        if self.lufs_meter:
            try:
                lufs_metrics = self._calculate_lufs_metrics(audio, sample_rate)
                metrics.update(lufs_metrics)
            except Exception as e:
                logger.warning(f"LUFS metrics calculation failed: {e}")

        # Voice characteristics
        if HAS_AUDIO_UTILS:
            try:
                voice_chars = analyze_voice_characteristics(audio, sample_rate)
                metrics["voice_characteristics"] = voice_chars
            except Exception as e:
                logger.warning(f"Voice characteristics analysis failed: {e}")

        # Spectral analysis
        if HAS_LIBROSA and include_advanced:
            try:
                spectral_metrics = self._calculate_spectral_metrics(audio, sample_rate)
                metrics.update(spectral_metrics)
            except Exception as e:
                logger.warning(f"Spectral metrics calculation failed: {e}")

        # Prosody analysis
        if HAS_LIBROSA and include_advanced:
            try:
                prosody_metrics = self._calculate_prosody_metrics(audio, sample_rate)
                metrics.update(prosody_metrics)
            except Exception as e:
                logger.warning(f"Prosody metrics calculation failed: {e}")

        # Overall quality score
        try:
            quality_score = self._calculate_quality_score(metrics)
            metrics["overall_quality_score"] = quality_score
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {e}")

        return metrics

    def _calculate_lufs_metrics(self, audio: np.ndarray, sample_rate: int) -> dict[str, float]:
        """Calculate LUFS-based loudness metrics."""
        if not self.lufs_meter:
            return {}

        try:
            integrated_lufs = self.lufs_meter.measure_integrated_lufs(audio, sample_rate)
            momentary_lufs = self.lufs_meter.measure_momentary_lufs(audio, sample_rate)
            short_term_lufs = self.lufs_meter.measure_short_term_lufs(audio, sample_rate)
            peak_lufs = self.lufs_meter.measure_peak_lufs(audio, sample_rate)

            return {
                "lufs_integrated": integrated_lufs,
                "lufs_momentary": momentary_lufs,
                "lufs_short_term": short_term_lufs,
                "lufs_peak": peak_lufs,
            }
        except Exception as e:
            logger.warning(f"LUFS metrics failed: {e}")
            return {}

    def _calculate_spectral_metrics(self, audio: np.ndarray, sample_rate: int) -> dict[str, float]:
        """Calculate advanced spectral metrics."""
        if not HAS_LIBROSA:
            return {}

        try:
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)

            # MFCC
            mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)

            # Chroma features
            chroma = librosa.feature.chroma(y=audio, sr=sample_rate)

            return {
                "spectral_centroid_mean": float(np.mean(spectral_centroid)),
                "spectral_centroid_std": float(np.std(spectral_centroid)),
                "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                "spectral_rolloff_std": float(np.std(spectral_rolloff)),
                "spectral_bandwidth_mean": float(np.mean(spectral_bandwidth)),
                "spectral_bandwidth_std": float(np.std(spectral_bandwidth)),
                "zero_crossing_rate_mean": float(np.mean(zero_crossing_rate)),
                "zero_crossing_rate_std": float(np.std(zero_crossing_rate)),
                "mfcc_mean": np.mean(mfcc, axis=1).tolist(),
                "mfcc_std": np.std(mfcc, axis=1).tolist(),
                "chroma_mean": np.mean(chroma, axis=1).tolist(),
            }
        except Exception as e:
            logger.warning(f"Spectral metrics failed: {e}")
            return {}

    def _calculate_prosody_metrics(self, audio: np.ndarray, sample_rate: int) -> dict[str, float]:
        """Calculate prosody-related metrics."""
        if not HAS_LIBROSA:
            return {}

        try:
            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Extract F0 (fundamental frequency)
            f0, voiced_flag, _voiced_probs = librosa.pyin(
                audio,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
            )

            # Calculate F0 statistics
            f0_voiced = f0[voiced_flag]
            if len(f0_voiced) > 0:
                f0_mean = float(np.nanmean(f0_voiced))
                f0_std = float(np.nanstd(f0_voiced))
                f0_min = float(np.nanmin(f0_voiced))
                f0_max = float(np.nanmax(f0_voiced))
                f0_range = f0_max - f0_min
            else:
                f0_mean = 0.0
                f0_std = 0.0
                f0_min = 0.0
                f0_max = 0.0
                f0_range = 0.0

            # Voiced ratio
            voiced_ratio = float(np.mean(voiced_flag)) if len(voiced_flag) > 0 else 0.0

            # Tempo estimation
            try:
                tempo, _ = librosa.beat.beat_track(y=audio, sr=sample_rate)
                tempo = float(tempo)
            except Exception:
                tempo = 0.0

            return {
                "f0_mean": f0_mean,
                "f0_std": f0_std,
                "f0_min": f0_min,
                "f0_max": f0_max,
                "f0_range": f0_range,
                "voiced_ratio": voiced_ratio,
                "tempo": tempo,
            }
        except Exception as e:
            logger.warning(f"Prosody metrics failed: {e}")
            return {}

    def _calculate_quality_score(self, metrics: dict) -> float:
        """Calculate overall quality score from all metrics."""
        score = 0.0
        weight_sum = 0.0

        # MOS score (if available)
        if "mos_score" in metrics:
            score += metrics["mos_score"] * 0.3
            weight_sum += 0.3

        # Naturalness (if available)
        if "naturalness" in metrics:
            score += metrics["naturalness"] * 5.0 * 0.2  # Scale to 0-5
            weight_sum += 0.2

        # SNR (if available)
        if "snr" in metrics:
            snr_normalized = min(1.0, max(0.0, (metrics["snr"] + 10) / 40))
            score += snr_normalized * 5.0 * 0.15
            weight_sum += 0.15

        # Artifact score (inverse - lower is better)
        if "artifact_score" in metrics:
            artifact_penalty = (1.0 - metrics["artifact_score"]) * 5.0 * 0.15
            score += artifact_penalty
            weight_sum += 0.15

        # LUFS (if available) - check if within broadcast range
        if "lufs_integrated" in metrics:
            lufs = metrics["lufs_integrated"]
            if -25.0 <= lufs <= -20.0:  # Good broadcast range
                score += 5.0 * 0.1
            elif -30.0 <= lufs <= -15.0:  # Acceptable range
                score += 3.0 * 0.1
            else:
                score += 1.0 * 0.1
            weight_sum += 0.1

        # Voice characteristics (if available)
        if "voice_characteristics" in metrics:
            vc = metrics["voice_characteristics"]
            if "voiced_ratio" in vc and vc["voiced_ratio"] > 0.5:
                score += 5.0 * 0.1
                weight_sum += 0.1

        # Normalize by weight sum
        if weight_sum > 0:
            score = score / weight_sum
        else:
            score = 3.0  # Default neutral score

        # Clamp to 0-5 range
        return float(max(0.0, min(5.0, score)))

    def compare_audio(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        sample_rate: int | None = None,
    ) -> dict[str, float | dict]:
        """
        Compare two audio samples and calculate similarity metrics.

        Args:
            audio1: First audio array
            audio2: Second audio array
            sample_rate: Sample rate (uses instance default if None)

        Returns:
            Dictionary with comparison metrics
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        comparison = {}

        # Calculate metrics for both
        metrics1 = self.calculate_all(audio1, sample_rate, include_advanced=False)
        metrics2 = self.calculate_all(audio2, sample_rate, include_advanced=False)

        # Similarity (if available)
        if HAS_QUALITY_METRICS:
            try:
                similarity = calculate_similarity(audio1, audio2, method="embedding")
                comparison["similarity"] = similarity
            except Exception as e:
                logger.warning(f"Similarity calculation failed: {e}")

        # Difference metrics
        if "mos_score" in metrics1 and "mos_score" in metrics2:
            comparison["mos_difference"] = abs(metrics1["mos_score"] - metrics2["mos_score"])

        if "snr" in metrics1 and "snr" in metrics2:
            comparison["snr_difference"] = abs(metrics1["snr"] - metrics2["snr"])

        if "lufs_integrated" in metrics1 and "lufs_integrated" in metrics2:
            comparison["lufs_difference"] = abs(
                metrics1["lufs_integrated"] - metrics2["lufs_integrated"]
            )

        comparison["metrics1"] = metrics1
        comparison["metrics2"] = metrics2

        return comparison


def create_enhanced_quality_metrics(
    sample_rate: int = 24000,
) -> EnhancedQualityMetrics:
    """
    Factory function to create an Enhanced Quality Metrics instance.

    Args:
        sample_rate: Default sample rate for processing

    Returns:
        Initialized EnhancedQualityMetrics instance
    """
    return EnhancedQualityMetrics(sample_rate=sample_rate)


def calculate_enhanced_quality_metrics(
    audio: np.ndarray,
    sample_rate: int = 24000,
    reference_audio: str | np.ndarray | None = None,
    include_advanced: bool = True,
) -> dict[str, float | dict | list]:
    """
    Convenience function to calculate enhanced quality metrics.

    Args:
        audio: Input audio array
        sample_rate: Sample rate
        reference_audio: Optional reference audio for comparison
        include_advanced: Include advanced metrics (slower)

    Returns:
        Dictionary with all quality metrics
    """
    metrics = EnhancedQualityMetrics(sample_rate=sample_rate)
    return metrics.calculate_all(audio, sample_rate, reference_audio, include_advanced)
