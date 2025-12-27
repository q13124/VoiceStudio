"""
Enhanced Audio Enhancement Module for VoiceStudio
Comprehensive audio quality enhancement pipeline

Compatible with:
- Python 3.10+
- librosa>=0.11.0
- scipy>=1.9.0
- numpy>=1.26.0
- pyloudnorm>=0.1.1
- noisereduce>=3.0.2
"""

import logging
from typing import Dict, List, Optional, Tuple, Union

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
    from .audio_utils import enhance_voice_quality, normalize_lufs, remove_artifacts

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    logger.warning("audio_utils not available")

# Import advanced quality enhancement
try:
    from .advanced_quality_enhancement import (
        advanced_denoise,
        enhance_prosody,
        enhance_spectral_quality,
        enhance_voice_quality_advanced,
        preserve_formants,
        remove_artifacts_advanced,
    )

    HAS_ADVANCED_ENHANCEMENT = True
except ImportError:
    HAS_ADVANCED_ENHANCEMENT = False
    logger.warning("advanced_quality_enhancement not available")


class EnhancedAudioEnhancer:
    """
    Enhanced Audio Enhancer for comprehensive quality improvement.

    Supports:
    - Multi-stage enhancement pipeline
    - Adaptive processing based on audio characteristics
    - Spectral enhancement
    - Formant preservation
    - Prosody enhancement
    - Advanced denoising
    - Artifact removal
    - LUFS normalization
    - Enhancement presets
    """

    def __init__(self, sample_rate: int = 24000):
        """
        Initialize Enhanced Audio Enhancer.

        Args:
            sample_rate: Default sample rate for processing
        """
        self.sample_rate = sample_rate

    def enhance(
        self,
        audio: np.ndarray,
        sample_rate: Optional[int] = None,
        preset: Optional[str] = None,
        config: Optional[Dict] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Apply enhanced audio enhancement pipeline.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            preset: Enhancement preset name
            config: Enhancement configuration dictionary:
                - denoise: Apply denoising
                - spectral_enhance: Enhance spectral quality
                - preserve_formants: Preserve formant structure
                - enhance_prosody: Enhance prosody
                - remove_artifacts: Remove artifacts
                - normalize: Normalize to target LUFS
                - adaptive: Use adaptive processing
            **kwargs: Additional enhancement options

        Returns:
            Enhanced audio array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if config is None:
            config = {}

        # Load preset if specified
        if preset:
            preset_config = self.get_preset(preset)
            config.update(preset_config)

        # Use advanced enhancement if available
        if HAS_ADVANCED_ENHANCEMENT:
            try:
                return enhance_voice_quality_advanced(
                    audio,
                    sample_rate,
                    normalize=config.get("normalize", True),
                    denoise=config.get("denoise", True),
                    spectral_enhance=config.get("spectral_enhance", True),
                    preserve_formants=config.get("preserve_formants", True),
                    enhance_prosody=config.get("enhance_prosody", False),
                    remove_artifacts=config.get("remove_artifacts", True),
                    target_lufs=config.get("target_lufs", -23.0),
                    denoise_strength=config.get("denoise_strength", 0.8),
                    spectral_strength=config.get("spectral_strength", 0.5),
                    prosody_strength=config.get("prosody_strength", 0.3),
                    artifact_strength=config.get("artifact_strength", 0.7),
                )
            except Exception as e:
                logger.warning(
                    f"Advanced enhancement failed: {e}, using basic enhancement"
                )

        # Fallback to basic enhancement
        if HAS_AUDIO_UTILS:
            try:
                return enhance_voice_quality(
                    audio,
                    sample_rate,
                    normalize=config.get("normalize", True),
                    denoise=config.get("denoise", True),
                    target_lufs=config.get("target_lufs", -23.0),
                )
            except Exception as e:
                logger.warning(f"Basic enhancement failed: {e}")

        return audio

    def enhance_adaptive(
        self,
        audio: np.ndarray,
        sample_rate: Optional[int] = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Apply adaptive enhancement based on audio characteristics.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            **kwargs: Additional options

        Returns:
            Enhanced audio array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_LIBROSA:
            return self.enhance(audio, sample_rate, **kwargs)

        # Analyze audio characteristics
        try:
            # Convert to mono for analysis
            if len(audio.shape) > 1:
                audio_mono = np.mean(audio, axis=1)
            else:
                audio_mono = audio

            # Calculate RMS (loudness indicator)
            rms = np.sqrt(np.mean(audio_mono**2))

            # Calculate spectral centroid (brightness indicator)
            spectral_centroid = np.mean(
                librosa.feature.spectral_centroid(y=audio_mono, sr=sample_rate)
            )

            # Calculate zero-crossing rate (noise indicator)
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_mono))

            # Adaptive configuration based on characteristics
            config = {}

            # Low RMS = quiet audio, apply more aggressive enhancement
            if rms < 0.1:
                config["denoise"] = True
                config["denoise_strength"] = 0.9
                config["spectral_enhance"] = True
                config["spectral_strength"] = 0.6
            else:
                config["denoise"] = True
                config["denoise_strength"] = 0.5
                config["spectral_enhance"] = True
                config["spectral_strength"] = 0.3

            # High ZCR = noisy, apply more denoising
            if zcr > 0.1:
                config["denoise_strength"] = min(
                    1.0, config.get("denoise_strength", 0.5) + 0.2
                )

            # Low spectral centroid = dull, apply spectral enhancement
            if spectral_centroid < 2000:
                config["spectral_enhance"] = True
                config["spectral_strength"] = min(
                    1.0, config.get("spectral_strength", 0.5) + 0.2
                )

            config["normalize"] = True
            config["remove_artifacts"] = True
            config["preserve_formants"] = True
            config["enhance_prosody"] = False  # Disable by default (slower)

            return self.enhance(audio, sample_rate, config=config, **kwargs)

        except Exception as e:
            logger.warning(f"Adaptive enhancement failed: {e}, using default")
            return self.enhance(audio, sample_rate, **kwargs)

    def get_preset(self, preset_name: str) -> Dict:
        """Get enhancement preset configuration."""
        presets = {
            "voice_cloning": {
                "denoise": True,
                "spectral_enhance": True,
                "preserve_formants": True,
                "enhance_prosody": False,
                "remove_artifacts": True,
                "normalize": True,
                "target_lufs": -23.0,
                "denoise_strength": 0.7,
                "spectral_strength": 0.5,
                "prosody_strength": 0.3,
                "artifact_strength": 0.7,
            },
            "high_quality": {
                "denoise": True,
                "spectral_enhance": True,
                "preserve_formants": True,
                "enhance_prosody": True,
                "remove_artifacts": True,
                "normalize": True,
                "target_lufs": -23.0,
                "denoise_strength": 0.9,
                "spectral_strength": 0.6,
                "prosody_strength": 0.4,
                "artifact_strength": 0.8,
            },
            "fast": {
                "denoise": True,
                "spectral_enhance": False,
                "preserve_formants": False,
                "enhance_prosody": False,
                "remove_artifacts": True,
                "normalize": True,
                "target_lufs": -23.0,
                "denoise_strength": 0.5,
                "artifact_strength": 0.5,
            },
            "broadcast": {
                "denoise": True,
                "spectral_enhance": True,
                "preserve_formants": True,
                "enhance_prosody": False,
                "remove_artifacts": True,
                "normalize": True,
                "target_lufs": -23.0,
                "denoise_strength": 0.8,
                "spectral_strength": 0.4,
                "artifact_strength": 0.7,
            },
            "minimal": {
                "denoise": False,
                "spectral_enhance": False,
                "preserve_formants": False,
                "enhance_prosody": False,
                "remove_artifacts": False,
                "normalize": True,
                "target_lufs": -23.0,
            },
        }

        return presets.get(preset_name.lower(), presets["voice_cloning"])


def create_enhanced_audio_enhancer(sample_rate: int = 24000) -> EnhancedAudioEnhancer:
    """
    Factory function to create an Enhanced Audio Enhancer instance.

    Args:
        sample_rate: Default sample rate for processing

    Returns:
        Initialized EnhancedAudioEnhancer instance
    """
    return EnhancedAudioEnhancer(sample_rate=sample_rate)


def enhance_audio(
    audio: np.ndarray,
    sample_rate: int = 24000,
    preset: Optional[str] = None,
    config: Optional[Dict] = None,
    **kwargs,
) -> np.ndarray:
    """
    Convenience function to enhance audio.

    Args:
        audio: Input audio array
        sample_rate: Sample rate
        preset: Enhancement preset name
        config: Custom enhancement configuration
        **kwargs: Additional enhancement options

    Returns:
        Enhanced audio array
    """
    enhancer = EnhancedAudioEnhancer(sample_rate=sample_rate)
    return enhancer.enhance(audio, sample_rate, preset, config, **kwargs)
