"""
Tortoise TTS Engine for VoiceStudio
Tortoise TTS integration for ultra-realistic HQ voice synthesis

Compatible with:
- Python 3.10+
- tortoise-tts library
- PyTorch 2.2.2+cu121
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch

# Optional quality metrics import
try:
    from .quality_metrics import calculate_all_metrics

    HAS_QUALITY_METRICS = True
except ImportError:
    HAS_QUALITY_METRICS = False

# Optional audio utilities import for quality enhancement
try:
    from ..audio.audio_utils import (
        enhance_voice_cloning_quality,
        enhance_voice_quality,
        match_voice_profile,
    )

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    enhance_voice_cloning_quality = None

try:
    from tortoise.api import TextToSpeech
except ImportError:
    TextToSpeech = None
    logging.warning(
        "Tortoise TTS not installed. " "Install with: pip install tortoise-tts"
    )

logger = logging.getLogger(__name__)

# Try importing general model cache
try:
    from ..models.cache import get_model_cache

    _model_cache = get_model_cache(
        max_models=3, max_memory_mb=3072.0
    )  # 3GB max (Tortoise models are larger)
    HAS_MODEL_CACHE = True
except ImportError:
    HAS_MODEL_CACHE = False
    _model_cache = None
    logger.debug("General model cache not available, using Tortoise-specific cache")

# Fallback: Tortoise-specific cache (for backward compatibility)
from collections import OrderedDict

_MODEL_CACHE: OrderedDict = OrderedDict()
_VOICE_EMBEDDING_CACHE: Dict[str, np.ndarray] = {}
_QUALITY_PRESET_CACHE: Dict[str, Dict] = {}
_MAX_CACHE_SIZE = 2  # Maximum number of models to cache in memory
_MAX_EMBEDDING_CACHE_SIZE = 50  # Maximum number of voice embeddings to cache


def _get_cache_key(quality_preset: str, device: str) -> str:
    """Generate cache key for model with quality preset."""
    return f"tortoise::{quality_preset}::{device}"


def _get_cached_model(quality_preset: str, device: str):
    """Get cached model if available."""
    # Try general model cache first
    if HAS_MODEL_CACHE and _model_cache is not None:
        cached = _model_cache.get(
            "tortoise", f"tortoise_{quality_preset}", device=device
        )
        if cached is not None:
            return cached

    # Fallback to Tortoise-specific cache
    cache_key = _get_cache_key(quality_preset, device)
    if cache_key in _MODEL_CACHE:
        # Move to end (most recently used)
        _MODEL_CACHE.move_to_end(cache_key)
        return _MODEL_CACHE[cache_key]
    return None


def _cache_model(quality_preset: str, device: str, model):
    """Cache model with LRU eviction."""
    # Try general model cache first
    if HAS_MODEL_CACHE and _model_cache is not None:
        try:
            _model_cache.set(
                "tortoise", f"tortoise_{quality_preset}", model, device=device
            )
            return
        except Exception as e:
            logger.warning(f"Failed to cache in general cache: {e}, using fallback")

    # Fallback to Tortoise-specific cache
    cache_key = _get_cache_key(quality_preset, device)

    # Remove if already exists
    if cache_key in _MODEL_CACHE:
        _MODEL_CACHE.move_to_end(cache_key)
        return

    # Add new model
    _MODEL_CACHE[cache_key] = model

    # Evict oldest if cache full
    if len(_MODEL_CACHE) > _MAX_CACHE_SIZE:
        oldest_key, oldest_model = _MODEL_CACHE.popitem(last=False)
        # Cleanup oldest model
        try:
            del oldest_model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.debug(f"Evicted model from cache: {oldest_key}")
        except Exception as e:
            logger.warning(f"Error evicting model from cache: {e}")

    logger.debug(f"Cached model: {cache_key} (cache size: {len(_MODEL_CACHE)})")


def _get_voice_embedding_cache_key(voice_samples: List[Union[str, Path]]) -> str:
    """Generate cache key for voice embedding."""
    import hashlib

    paths_str = "|".join(sorted(str(p) for p in voice_samples))
    return hashlib.md5(paths_str.encode()).hexdigest()


def _get_cached_voice_embedding(
    voice_samples: List[Union[str, Path]],
) -> Optional[np.ndarray]:
    """Get cached voice embedding if available."""
    cache_key = _get_voice_embedding_cache_key(voice_samples)
    return _VOICE_EMBEDDING_CACHE.get(cache_key)


def _cache_voice_embedding(
    voice_samples: List[Union[str, Path]], embedding: np.ndarray
):
    """Cache voice embedding with LRU eviction."""
    cache_key = _get_voice_embedding_cache_key(voice_samples)

    # Remove if already exists
    if cache_key in _VOICE_EMBEDDING_CACHE:
        return

    # Add new embedding
    _VOICE_EMBEDDING_CACHE[cache_key] = embedding

    # Evict oldest if cache full
    if len(_VOICE_EMBEDDING_CACHE) > _MAX_EMBEDDING_CACHE_SIZE:
        # Remove first item (oldest)
        oldest_key = next(iter(_VOICE_EMBEDDING_CACHE))
        del _VOICE_EMBEDDING_CACHE[oldest_key]
        logger.debug(f"Evicted voice embedding from cache: {oldest_key[:8]}")

    logger.debug(
        f"Cached voice embedding: {cache_key[:8]} (cache size: {len(_VOICE_EMBEDDING_CACHE)})"
    )


# Import base protocol from canonical source
from .base import EngineProtocol


class TortoiseEngine(EngineProtocol):
    """
    Tortoise TTS Engine for ultra-realistic voice synthesis.

    Optimized for quality over speed - ideal for "HQ Render" mode.

    Supports:
    - Multi-voice synthesis
    - High-quality voice cloning
    - Natural prosody and intonation
    - Quality-focused generation
    """

    # Quality presets
    QUALITY_PRESETS = {
        "ultra_fast": {"num_autoregressive_samples": 16, "diffusion_iterations": 30},
        "fast": {"num_autoregressive_samples": 32, "diffusion_iterations": 50},
        "standard": {"num_autoregressive_samples": 96, "diffusion_iterations": 100},
        "high_quality": {
            "num_autoregressive_samples": 256,
            "diffusion_iterations": 200,
        },
        "ultra_quality": {
            "num_autoregressive_samples": 512,
            "diffusion_iterations": 400,
        },
    }

    def __init__(
        self,
        device: Optional[str] = None,
        gpu: bool = True,
        quality_preset: str = "high_quality",
        lazy_load: bool = True,
        batch_size: int = 2,  # Smaller batch size for Tortoise (more memory intensive)
        enable_caching: bool = True,
    ):
        """
        Initialize Tortoise TTS engine.

        Args:
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
            quality_preset: Quality preset ('ultra_fast', 'fast', 'standard', 'high_quality', 'ultra_quality')
            lazy_load: If True, defer model loading until first use
            batch_size: Batch size for batch synthesis operations
            enable_caching: If True, enable model and embedding caching
        """
        if TextToSpeech is None:
            raise ImportError(
                "Tortoise TTS not installed. Install with: pip install tortoise-tts"
            )

        # Initialize base protocol
        super().__init__(device=device, gpu=gpu)

        # Override device if GPU requested and available
        if gpu and torch.cuda.is_available() and self.device == "cpu":
            self.device = "cuda"

        self.quality_preset = quality_preset
        if quality_preset not in self.QUALITY_PRESETS:
            logger.warning(
                f"Unknown quality preset {quality_preset}, using 'high_quality'"
            )
            self.quality_preset = "high_quality"

        self.tts = None
        self.lazy_load = lazy_load
        self.batch_size = batch_size
        self.enable_caching = enable_caching

    def _load_model(self):
        """Load model with caching support."""
        # Check cache first
        if self.enable_caching:
            cached_model = _get_cached_model(self.quality_preset, self.device)
            if cached_model is not None:
                logger.debug(f"Using cached model: {self.quality_preset}")
                self.tts = cached_model
                self._initialized = True
                return True

        # Load model
        logger.info(f"Loading Tortoise TTS model (quality: {self.quality_preset})")

        # Use %PROGRAMDATA%\VoiceStudio\models for model cache if available
        model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
        if not model_cache_dir:
            model_cache_dir = os.path.join(
                os.getenv("PROGRAMDATA", "C:\\ProgramData"),
                "VoiceStudio",
                "models",
                "tortoise",
            )

        # Ensure model cache directory exists
        os.makedirs(model_cache_dir, exist_ok=True)

        # Initialize Tortoise TTS
        # Note: Actual API may vary, this is a template based on common patterns
        self.tts = TextToSpeech()

        # Move to device if available
        if hasattr(self.tts, "to"):
            self.tts.to(self.device)

        # Cache model
        if self.enable_caching:
            _cache_model(self.quality_preset, self.device, self.tts)

        self._initialized = True
        logger.info(
            f"Tortoise TTS model loaded successfully (cache: {model_cache_dir})"
        )
        return True

    def initialize(self) -> bool:
        """
        Initialize the TTS model.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if self._initialized:
                return True

            # Lazy loading: defer until first use
            if self.lazy_load:
                logger.debug("Lazy loading enabled, model will be loaded on first use")
                return True

            return self._load_model()

        except Exception as e:
            logger.error(f"Failed to initialize Tortoise TTS model: {e}")
            self._initialized = False
            return False

    def synthesize(
        self,
        text: str,
        speaker_wav: Union[str, Path, List[Union[str, Path]]],
        voice_samples: Optional[List[Union[str, Path]]] = None,
        output_path: Optional[Union[str, Path]] = None,
        quality_preset: Optional[str] = None,
        enhance_quality: bool = False,
        calculate_quality: bool = False,
        **kwargs,
    ) -> Union[Optional[np.ndarray], Tuple[Optional[np.ndarray], Dict]]:
        """
        Synthesize speech from text using voice cloning.

        Args:
            text: Text to synthesize
            speaker_wav: Path to reference speaker audio file(s) (for voice cloning)
            voice_samples: Optional list of voice samples for multi-voice synthesis
            output_path: Optional path to save output audio
            quality_preset: Override quality preset for this synthesis
            enhance_quality: If True, apply quality enhancement pipeline
            calculate_quality: If True, return quality metrics along with audio
            **kwargs: Additional synthesis parameters

        Returns:
            Audio array (numpy) or None if synthesis failed,
            or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        # Lazy load model if needed
        if not self._initialized:
            if not self._load_model():
                return None

        try:
            # Use provided quality preset or default
            preset = quality_preset or self.quality_preset

            # Cache quality preset parameters for faster lookup
            if self.enable_caching and preset in _QUALITY_PRESET_CACHE:
                quality_params = _QUALITY_PRESET_CACHE[preset]
            else:
                quality_params = self.QUALITY_PRESETS.get(
                    preset, self.QUALITY_PRESETS["high_quality"]
                )
                if self.enable_caching:
                    _QUALITY_PRESET_CACHE[preset] = quality_params

            # Convert speaker_wav to list if single path
            if isinstance(speaker_wav, (str, Path)):
                speaker_wav = [speaker_wav]

            # Ensure all paths are strings
            speaker_wav = [str(path) for path in speaker_wav]

            # Use voice_samples if provided, otherwise use speaker_wav
            voice_refs = voice_samples if voice_samples else speaker_wav
            if voice_refs:
                voice_refs = [str(path) for path in voice_refs]

            # Get or cache voice embedding for multi-voice synthesis
            voice_embedding = None
            if self.enable_caching and voice_refs and len(voice_refs) > 1:
                voice_embedding = _get_cached_voice_embedding(voice_refs)
                if voice_embedding is None and hasattr(self.tts, "get_voice_embedding"):
                    # Extract embedding and cache it
                    try:
                        voice_embedding = self.tts.get_voice_embedding(voice_refs)
                        _cache_voice_embedding(voice_refs, voice_embedding)
                        logger.debug(
                            f"Cached voice embedding for {len(voice_refs)} samples"
                        )
                    except Exception as e:
                        logger.debug(f"Failed to extract/cache voice embedding: {e}")

            # Get sample rate (Tortoise typically uses 22050)
            sample_rate = getattr(self.tts, "output_sample_rate", 22050)

            # Prepare synthesis parameters
            synthesis_params = {
                "text": text,
                "voice_samples": voice_refs,
                **quality_params,
                **kwargs,
            }

            # Use cached embedding if available
            if voice_embedding is not None:
                synthesis_params["voice_embedding"] = voice_embedding

            # Synthesize with inference mode for better performance
            # Note: Actual API may vary, this is a template
            with torch.inference_mode():
                if output_path:
                    output_path = str(output_path)
                    # Save to file
                    if hasattr(self.tts, "tts_to_file"):
                        self.tts.tts_to_file(
                            output_path=output_path, **synthesis_params
                        )
                else:
                    # Fallback: synthesize then save
                    audio = self.tts.tts(**synthesis_params)
                    import soundfile as sf

                    sf.write(output_path, audio, sample_rate)

                logger.info(f"Audio saved to: {output_path}")

                # Load and process if quality enhancement or metrics needed
                if enhance_quality or calculate_quality:
                    import soundfile as sf

                    audio, sr = sf.read(output_path)
                    audio = self._process_audio_quality(
                        audio,
                        sr,
                        speaker_wav[0] if speaker_wav else None,
                        enhance_quality,
                        calculate_quality,
                    )
                    if isinstance(audio, tuple):
                        # Quality metrics returned
                        enhanced_audio, quality_metrics = audio
                        sf.write(output_path, enhanced_audio, sr)
                        return None, quality_metrics
                    else:
                        sf.write(output_path, audio, sr)

                    return None
                else:
                    # Return audio array
                    audio = self.tts.tts(**synthesis_params)
                    audio = (
                        np.array(audio) if isinstance(audio, (list, tuple)) else audio
                    )

                    # Apply quality processing if requested
                    if enhance_quality or calculate_quality:
                        audio = self._process_audio_quality(
                            audio,
                            sample_rate,
                            speaker_wav[0] if speaker_wav else None,
                            enhance_quality,
                            calculate_quality,
                        )
                        if isinstance(audio, tuple):
                            return audio  # (audio, quality_metrics)

                    return audio

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return None

    def _process_audio_quality(
        self,
        audio: np.ndarray,
        sample_rate: int,
        reference_audio: Optional[Union[str, Path]] = None,
        enhance: bool = False,
        calculate_metrics: bool = False,
    ) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
        """
        Process audio with quality enhancement and/or metrics calculation.

        Args:
            audio: Audio array to process
            sample_rate: Sample rate
            reference_audio: Optional reference audio for similarity metrics
            enhance: Whether to apply quality enhancement
            calculate_metrics: Whether to calculate quality metrics

        Returns:
            Enhanced audio, or tuple of (audio, metrics) if calculate_metrics=True
        """
        processed_audio = audio.copy()

        # Apply quality enhancement
        if enhance and HAS_AUDIO_UTILS:
            try:
                # Use advanced voice cloning quality enhancement (if available)
                if enhance_voice_cloning_quality is not None:
                    processed_audio = enhance_voice_cloning_quality(
                        processed_audio,
                        sample_rate,
                        enhancement_level="standard",
                        preserve_prosody=True,
                        target_lufs=-23.0,
                    )
                    logger.debug(
                        "Applied advanced quality enhancement to Tortoise output"
                    )
                elif enhance_voice_quality is not None:
                    # Fallback to standard enhancement
                    processed_audio = enhance_voice_quality(
                        processed_audio,
                        sample_rate,
                        normalize=True,
                        denoise=True,
                        target_lufs=-23.0,
                    )
                    logger.debug("Applied quality enhancement to synthesized audio")
            except Exception as e:
                logger.warning(f"Quality enhancement failed: {e}")

        # Calculate quality metrics
        quality_metrics = {}
        if calculate_metrics:
            if HAS_QUALITY_METRICS:
                try:
                    quality_metrics = calculate_all_metrics(
                        audio=processed_audio,
                        reference_audio=reference_audio,
                        sample_rate=sample_rate,
                        include_ml_prediction=True,  # Include ML-based quality prediction
                    )
                except Exception as e:
                    logger.warning(f"Quality metrics calculation failed: {e}")

            # Add voice profile matching if reference available
            if reference_audio and HAS_AUDIO_UTILS:
                try:
                    import soundfile as sf

                    ref_audio, ref_sr = sf.read(str(reference_audio))
                    profile_match = match_voice_profile(
                        ref_audio, processed_audio, ref_sr, sample_rate
                    )
                    quality_metrics["voice_profile_match"] = profile_match
                except Exception as e:
                    logger.debug(f"Voice profile matching failed: {e}")

        if calculate_metrics:
            return processed_audio, quality_metrics
        return processed_audio

    def clone_voice(
        self,
        reference_audio: Union[str, Path],
        text: str,
        output_path: Optional[Union[str, Path]] = None,
        quality_preset: Optional[str] = None,
        speed: float = 1.0,
        enhance_quality: bool = False,
        calculate_quality: bool = False,
    ) -> Union[Optional[np.ndarray], Tuple[Optional[np.ndarray], Dict]]:
        """
        Clone voice from reference audio and synthesize text.

        Args:
            reference_audio: Path to reference speaker audio
            text: Text to synthesize
            output_path: Optional output file path
            quality_preset: Quality preset override
            speed: Speech speed multiplier (may not be directly supported)
            enhance_quality: If True, apply quality enhancement pipeline
            calculate_quality: If True, return quality metrics along with audio

        Returns:
            Audio array or None, or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        kwargs = {}
        if speed != 1.0:
            kwargs["speed"] = speed

        audio = self.synthesize(
            text=text,
            speaker_wav=reference_audio,
            output_path=output_path,
            quality_preset=quality_preset,
            enhance_quality=enhance_quality,
            calculate_quality=calculate_quality,
            **kwargs,
        )

        # Audio is already processed by synthesize() method
        return audio

    def batch_synthesize(
        self,
        texts: List[str],
        speaker_wav: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        quality_preset: Optional[str] = None,
        **kwargs,
    ) -> List[Optional[np.ndarray]]:
        """
        Synthesize multiple texts in batch with optimized processing.

        Args:
            texts: List of texts to synthesize
            speaker_wav: Path to reference speaker audio
            output_dir: Optional directory to save outputs
            quality_preset: Quality preset override
            **kwargs: Additional synthesis parameters

        Returns:
            List of audio arrays
        """
        # Lazy load model if needed
        if not self._initialized:
            if not self._load_model():
                return [None] * len(texts)

        # Use provided quality preset or default
        preset = quality_preset or self.quality_preset

        # Cache quality preset parameters
        if self.enable_caching and preset in _QUALITY_PRESET_CACHE:
            quality_params = _QUALITY_PRESET_CACHE[preset]
        else:
            quality_params = self.QUALITY_PRESETS.get(
                preset, self.QUALITY_PRESETS["high_quality"]
            )
            if self.enable_caching:
                _QUALITY_PRESET_CACHE[preset] = quality_params

        # Pre-process voice samples once if caching enabled
        voice_refs = [str(speaker_wav)]
        voice_embedding = None
        if self.enable_caching and hasattr(self.tts, "get_voice_embedding"):
            try:
                voice_embedding = _get_cached_voice_embedding(voice_refs)
                if voice_embedding is None:
                    voice_embedding = self.tts.get_voice_embedding(voice_refs)
                    _cache_voice_embedding(voice_refs, voice_embedding)
                    logger.debug(f"Cached voice embedding for batch: {speaker_wav}")
            except Exception as e:
                logger.debug(f"Failed to extract/cache voice embedding: {e}")

        results = []
        sample_rate = getattr(self.tts, "output_sample_rate", 22050)

        # Process in batches for better GPU utilization
        batch_size = self.batch_size
        for batch_start in range(0, len(texts), batch_size):
            batch_texts = texts[batch_start : batch_start + batch_size]
            batch_results = []

            # Use inference mode for better performance
            with torch.inference_mode():
                for i, text in enumerate(batch_texts):
                    output_path = None
                    if output_dir:
                        output_path = (
                            Path(output_dir) / f"output_{batch_start + i:04d}.wav"
                        )

                    # Prepare synthesis parameters
                    synthesis_params = {
                        "text": text,
                        "voice_samples": voice_refs,
                        **quality_params,
                        **kwargs,
                    }

                    # Use cached embedding if available
                    if voice_embedding is not None:
                        synthesis_params["voice_embedding"] = voice_embedding

                    try:
                        if output_path:
                            # Save to file
                            if hasattr(self.tts, "tts_to_file"):
                                self.tts.tts_to_file(
                                    output_path=str(output_path), **synthesis_params
                                )
                                audio = None
                            else:
                                # Fallback: synthesize then save
                                audio = self.tts.tts(**synthesis_params)
                                import soundfile as sf

                                sf.write(str(output_path), audio, sample_rate)
                                audio = None
                        else:
                            # Return audio array
                            audio = self.tts.tts(**synthesis_params)
                            audio = (
                                np.array(audio)
                                if isinstance(audio, (list, tuple))
                                else audio
                            )

                        batch_results.append(audio)
                    except Exception as e:
                        logger.error(
                            f"Batch synthesis failed for text {batch_start + i}: {e}"
                        )
                        batch_results.append(None)

            results.extend(batch_results)

            # Clear GPU cache periodically (Tortoise is memory-intensive)
            if (
                torch.cuda.is_available()
                and (batch_start + batch_size) % batch_size == 0
            ):
                torch.cuda.empty_cache()

        return results

    def enable_caching(self, enable: bool = True):
        """Enable or disable caching."""
        self.enable_caching = enable
        logger.info(f"Model caching {'enabled' if enable else 'disabled'}")

    def set_batch_size(self, batch_size: int):
        """Set batch size for batch operations."""
        self.batch_size = max(1, batch_size)
        logger.info(f"Batch size set to {self.batch_size}")

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get GPU memory usage in MB."""
        if not torch.cuda.is_available():
            return {"gpu_memory_mb": 0.0, "gpu_memory_allocated_mb": 0.0}

        return {
            "gpu_memory_mb": torch.cuda.get_device_properties(0).total_memory / 1024**2,
            "gpu_memory_allocated_mb": torch.cuda.memory_allocated(0) / 1024**2,
        }

    def get_quality_presets(self) -> List[str]:
        """
        Get list of available quality presets.

        Returns:
            List of quality preset names
        """
        return list(self.QUALITY_PRESETS.keys())

    def set_quality_preset(self, preset: str):
        """
        Set quality preset for future synthesis.

        Args:
            preset: Quality preset name
        """
        if preset in self.QUALITY_PRESETS:
            self.quality_preset = preset
            logger.info(f"Quality preset changed to: {preset}")
        else:
            logger.warning(f"Unknown quality preset: {preset}")

    def cleanup(self):
        """Clean up resources."""
        if self.tts is not None:
            del self.tts
            self.tts = None
            self._initialized = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Tortoise Engine cleaned up")


# Factory function for easy instantiation
def create_tortoise_engine(
    device: Optional[str] = None, gpu: bool = True, quality_preset: str = "high_quality"
) -> TortoiseEngine:
    """
    Create and initialize Tortoise TTS engine.

    Args:
        device: Device to use
        gpu: Whether to use GPU
        quality_preset: Quality preset for synthesis

    Returns:
        Initialized TortoiseEngine instance
    """
    engine = TortoiseEngine(device=device, gpu=gpu, quality_preset=quality_preset)
    engine.initialize()
    return engine


# Example usage
if __name__ == "__main__":
    # Initialize engine with high quality preset
    engine = create_tortoise_engine(quality_preset="high_quality")

    # Example: Clone voice and synthesize
    reference_audio = "path/to/reference.wav"
    text = "Hello, this is a test of ultra-realistic voice cloning with Tortoise TTS."

    audio = engine.clone_voice(
        reference_audio=reference_audio, text=text, quality_preset="ultra_quality"
    )

    if audio is not None:
        print(f"Generated audio shape: {audio.shape}")

    # Cleanup
    engine.cleanup()
