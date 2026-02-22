"""
Chatterbox TTS Engine for VoiceStudio
Resemble AI Chatterbox TTS integration for state-of-the-art voice cloning

Compatible with:
- Python 3.11+
- chatterbox-tts library
- PyTorch 2.2.2+cu121
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import numpy as np
import torch

# Optional quality metrics import
try:
    from .quality_metrics import (
        calculate_all_metrics,
        calculate_mos_score,
        calculate_naturalness,
        calculate_similarity,
    )

    HAS_QUALITY_METRICS = True
except ImportError:
    HAS_QUALITY_METRICS = False

# Optional audio utilities import for quality enhancement
enhance_voice_cloning_quality: Any = None
enhance_voice_quality: Any = None
match_voice_profile: Any = None
normalize_lufs: Any = None
remove_artifacts: Any = None

try:
    from app.core.audio.audio_utils import (
        enhance_voice_cloning_quality,
        enhance_voice_quality,
        match_voice_profile,
        normalize_lufs,
        remove_artifacts,
    )

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False

try:
    from chatterbox.tts import ChatterboxTTS
except ImportError:
    ChatterboxTTS = None
    logging.warning("Chatterbox TTS not installed. Install with: pip install chatterbox-tts")

logger = logging.getLogger(__name__)

# Try importing general model cache
_model_cache: Any = None
HAS_MODEL_CACHE = False

try:
    from app.core.models.cache import get_model_cache

    _model_cache = get_model_cache(max_models=5, max_memory_mb=2048.0)  # 2GB max
    HAS_MODEL_CACHE = True
except ImportError:
    logger.debug("General model cache not available, using Chatterbox-specific cache")

# Fallback: Chatterbox-specific cache (for backward compatibility)
from collections import OrderedDict

_MODEL_CACHE: OrderedDict = OrderedDict()
_EMBEDDING_CACHE: dict[str, np.ndarray] = {}
_MAX_CACHE_SIZE = 2  # Maximum number of models to cache in memory
_MAX_EMBEDDING_CACHE_SIZE = 100  # Maximum number of embeddings to cache


def _get_cache_key(model_name: str, device: str) -> str:
    """Generate cache key for model."""
    return f"{model_name}::{device}"


def _get_cached_model(model_name: str, device: str):
    """Get cached model if available."""
    # Try general model cache first
    if HAS_MODEL_CACHE and _model_cache is not None:
        cached = _model_cache.get("chatterbox", model_name, device=device)
        if cached is not None:
            return cached

    # Fallback to Chatterbox-specific cache
    cache_key = _get_cache_key(model_name, device)
    if cache_key in _MODEL_CACHE:
        # Move to end (most recently used)
        _MODEL_CACHE.move_to_end(cache_key)
        return _MODEL_CACHE[cache_key]
    return None


def _cache_model(model_name: str, device: str, model):
    """Cache model with LRU eviction."""
    # Try general model cache first
    if HAS_MODEL_CACHE and _model_cache is not None:
        try:
            _model_cache.set("chatterbox", model_name, model, device=device)
            return
        except Exception as e:
            logger.warning(f"Failed to cache in general cache: {e}, using fallback")

    # Fallback to Chatterbox-specific cache
    cache_key = _get_cache_key(model_name, device)

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


def _get_embedding_cache_key(speaker_wav: str | Path) -> str:
    """Generate cache key for speaker embedding."""
    import hashlib

    path_str = str(speaker_wav)
    return hashlib.md5(path_str.encode()).hexdigest()


def _get_cached_embedding(speaker_wav: str | Path) -> np.ndarray | None:
    """Get cached speaker embedding if available."""
    cache_key = _get_embedding_cache_key(speaker_wav)
    return _EMBEDDING_CACHE.get(cache_key)


def _cache_embedding(speaker_wav: str | Path, embedding: np.ndarray):
    """Cache speaker embedding with LRU eviction."""
    cache_key = _get_embedding_cache_key(speaker_wav)

    # Remove if already exists
    if cache_key in _EMBEDDING_CACHE:
        return

    # Add new embedding
    _EMBEDDING_CACHE[cache_key] = embedding

    # Evict oldest if cache full
    if len(_EMBEDDING_CACHE) > _MAX_EMBEDDING_CACHE_SIZE:
        # Remove first item (oldest)
        oldest_key = next(iter(_EMBEDDING_CACHE))
        del _EMBEDDING_CACHE[oldest_key]
        logger.debug(f"Evicted embedding from cache: {oldest_key[:8]}")

    logger.debug(f"Cached embedding: {cache_key[:8]} (cache size: {len(_EMBEDDING_CACHE)})")


# Import base protocol from canonical source
from .base import EngineProtocol


class ChatterboxEngine(EngineProtocol):
    """
    Chatterbox TTS Engine for state-of-the-art voice cloning and synthesis.

    Supports:
    - Zero-shot voice cloning
    - Multilingual synthesis (23 languages)
    - Emotion control
    - Expressive speech generation
    """

    # Supported languages (23 languages as per documentation)
    SUPPORTED_LANGUAGES = [
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "pl",
        "tr",
        "ru",
        "nl",
        "cs",
        "ar",
        "zh-cn",
        "ja",
        "ko",
        "hi",
        "sv",
        "da",
        "no",
        "fi",
        "el",
        "hu",
        "ro",
    ]

    # Supported emotions
    SUPPORTED_EMOTIONS = [
        "neutral",
        "happy",
        "sad",
        "angry",
        "excited",
        "calm",
        "fearful",
        "disgusted",
        "surprised",
    ]

    def __init__(
        self,
        model_name: str = "chatterbox-tts/base",
        device: str | None = None,
        gpu: bool = True,
        lazy_load: bool = True,
        batch_size: int = 4,
        enable_caching: bool = True,
    ):
        """
        Initialize Chatterbox TTS engine.

        Args:
            model_name: Chatterbox model identifier
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
            lazy_load: If True, defer model loading until first use
            batch_size: Batch size for batch synthesis operations
            enable_caching: If True, enable model and embedding caching
        """
        if ChatterboxTTS is None:
            raise ImportError(
                "Chatterbox TTS not installed. Install with: pip install chatterbox-tts"
            )

        # Initialize base protocol
        super().__init__(device=device, gpu=gpu)

        self.model_name = model_name
        # Override device if GPU requested and available
        if gpu and torch.cuda.is_available() and self.device == "cpu":
            self.device = "cuda"
        self.tts: Any = None
        self.lazy_load = lazy_load
        self.batch_size = batch_size
        self._caching_enabled = enable_caching

    def _load_model(self) -> bool:
        """Load model with caching support."""
        # Check cache first
        if self._caching_enabled:
            cached_model = _get_cached_model(self.model_name, self.device)
            if cached_model is not None:
                logger.debug(f"Using cached model: {self.model_name}")
                self.tts = cached_model
                self._initialized = True
                return True

        # Load model
        logger.info(f"Loading Chatterbox TTS model: {self.model_name}")

        # Use %PROGRAMDATA%\VoiceStudio\models for model cache if available
        model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
        if not model_cache_dir:
            model_cache_dir = os.path.join(
                os.getenv("PROGRAMDATA", "C:\\ProgramData"),
                "VoiceStudio",
                "models",
                "chatterbox",
            )

        # Ensure model cache directory exists
        os.makedirs(model_cache_dir, exist_ok=True)

        self.tts = ChatterboxTTS.from_pretrained(device=self.device)

        # Cache model
        if self._caching_enabled:
            _cache_model(self.model_name, self.device, self.tts)

        self._initialized = True
        logger.info(f"Chatterbox TTS model loaded successfully (cache: {model_cache_dir})")
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
            logger.error(f"Failed to initialize Chatterbox TTS model: {e}")
            self._initialized = False
            return False

    def synthesize(
        self,
        text: str,
        speaker_wav: str | Path | list[str | Path],
        language: str = "en",
        emotion: str | None = None,
        output_path: str | Path | None = None,
        enhance_quality: bool = False,
        calculate_quality: bool = False,
        **kwargs,
    ) -> np.ndarray | None | tuple[np.ndarray | None, dict]:
        """
        Synthesize speech from text using zero-shot voice cloning.

        Args:
            text: Text to synthesize
            speaker_wav: Path to reference speaker audio file(s)
            language: Language code (e.g., 'en', 'es', 'fr', etc.)
            emotion: Emotion/style control (e.g., 'happy', 'sad', 'neutral')
            output_path: Optional path to save output audio
            enhance_quality: If True, apply quality enhancement pipeline
            calculate_quality: If True, return quality metrics along with audio
            **kwargs: Additional synthesis parameters

        Returns:
            Audio array (numpy) or None if synthesis failed,
            or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        # Lazy load model if needed
        if not self._initialized and not self._load_model():
            return None

        try:
            # Validate language
            if language not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Language {language} not in supported list, using 'en'")
                language = "en"

            # Validate emotion
            if emotion and emotion not in self.SUPPORTED_EMOTIONS:
                logger.warning(f"Emotion {emotion} not in supported list, using 'neutral'")
                emotion = "neutral"

            # Convert speaker_wav to list if single path
            if isinstance(speaker_wav, (str, Path)):
                speaker_wav = [speaker_wav]

            # Ensure all paths are strings
            speaker_wav = [str(path) for path in speaker_wav]

            sample_rate = getattr(self.tts, "sr", 24000)

            exaggeration = 0.5
            if emotion and emotion != "neutral":
                emotion_intensity = {
                    "happy": 0.8,
                    "excited": 1.0,
                    "sad": 0.3,
                    "angry": 1.2,
                    "calm": 0.2,
                    "surprised": 0.9,
                }
                exaggeration = emotion_intensity.get(emotion, 0.5)

            audio_prompt = str(speaker_wav[0]) if speaker_wav else None

            gen_kwargs = {
                "text": text,
                "audio_prompt_path": audio_prompt,
                "exaggeration": exaggeration,
            }
            for k in ("cfg_weight", "temperature", "repetition_penalty", "top_p"):
                if k in kwargs:
                    gen_kwargs[k] = kwargs[k]

            with torch.inference_mode():
                wav = self.tts.generate(**gen_kwargs)

            audio = wav.squeeze(0).cpu().numpy()

            if output_path:
                import torchaudio

                torchaudio.save(str(output_path), wav.cpu(), sample_rate)
                logger.info(f"Audio saved to: {output_path}")

                if enhance_quality or calculate_quality:
                    audio = self._process_audio_quality(
                        audio,
                        sample_rate,
                        speaker_wav[0] if speaker_wav else None,
                        enhance_quality,
                        calculate_quality,
                    )
                    if isinstance(audio, tuple):
                        enhanced_audio, quality_metrics = audio
                        import soundfile as sf

                        sf.write(str(output_path), enhanced_audio, sample_rate)
                        return None, quality_metrics

                return None
            else:
                if enhance_quality or calculate_quality:
                    audio = self._process_audio_quality(
                        audio,
                        sample_rate,
                        speaker_wav[0] if speaker_wav else None,
                        enhance_quality,
                        calculate_quality,
                    )
                    if isinstance(audio, tuple):
                        return audio

                return np.asarray(audio)

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return None

    def _process_audio_quality(
        self,
        audio: np.ndarray,
        sample_rate: int,
        reference_audio: str | Path | None = None,
        enhance: bool = False,
        calculate_metrics: bool = False,
    ) -> np.ndarray | tuple[np.ndarray, dict]:
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
                    logger.debug("Applied advanced quality enhancement to Chatterbox output")
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
        reference_audio: str | Path,
        text: str,
        language: str = "en",
        emotion: str | None = None,
        output_path: str | Path | None = None,
        speed: float = 1.0,
        calculate_quality: bool = False,
    ) -> np.ndarray | None | tuple[np.ndarray | None, dict]:
        """
        Clone voice from reference audio and synthesize text.

        Args:
            reference_audio: Path to reference speaker audio
            text: Text to synthesize
            language: Language code
            emotion: Optional emotion/style control
            output_path: Optional output file path
            speed: Speech speed multiplier
            calculate_quality: If True, return quality metrics along with audio

        Returns:
            Audio array or None, or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        synth_kwargs: dict[str, Any] = {}
        if speed != 1.0:
            synth_kwargs["speed"] = speed

        result = self.synthesize(
            text=text,
            speaker_wav=reference_audio,
            language=language,
            emotion=emotion,
            output_path=output_path,
            **synth_kwargs,
        )

        # Process audio quality (enhancement + metrics)
        if result is not None and isinstance(result, np.ndarray):
            quality_out = self._process_audio_quality(
                result,
                getattr(self.tts, "output_sample_rate", 22050),
                reference_audio,
                enhance=False,
                calculate_metrics=calculate_quality,
            )
            if isinstance(quality_out, tuple):
                return quality_out
            return quality_out

        return result

    def batch_synthesize(
        self,
        texts: list[str],
        speaker_wav: str | Path,
        language: str = "en",
        emotion: str | None = None,
        output_dir: str | Path | None = None,
        **kwargs,
    ) -> list[np.ndarray | None]:
        """
        Synthesize multiple texts in batch with optimized processing.

        Args:
            texts: List of texts to synthesize
            speaker_wav: Path to reference speaker audio
            language: Language code
            emotion: Optional emotion/style control
            output_dir: Optional directory to save outputs
            **kwargs: Additional synthesis parameters

        Returns:
            List of audio arrays
        """
        # Lazy load model if needed
        if not self._initialized and not self._load_model():
            return [None] * len(texts)

        # Pre-process speaker audio once if caching enabled
        speaker_embedding = None
        if self._caching_enabled:
            speaker_embedding = _get_cached_embedding(speaker_wav)
            if speaker_embedding is None and hasattr(self.tts, "get_speaker_embedding"):
                try:
                    speaker_embedding = self.tts.get_speaker_embedding(str(speaker_wav))
                    _cache_embedding(speaker_wav, speaker_embedding)
                    logger.debug(f"Cached speaker embedding for batch: {speaker_wav}")
                except Exception as e:
                    logger.debug(f"Failed to extract/cache embedding: {e}")

        results = []

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
                        output_path = Path(output_dir) / f"output_{batch_start + i:04d}.wav"

                    # Prepare synthesis parameters
                    synthesis_params = {
                        "text": text,
                        "speaker_audio": str(speaker_wav),
                        "language": language,
                        **kwargs,
                    }

                    # Use cached embedding if available
                    if speaker_embedding is not None:
                        synthesis_params["speaker_embedding"] = speaker_embedding

                    if emotion:
                        synthesis_params["emotion"] = emotion

                    try:
                        if output_path:
                            # Save to file
                            if hasattr(self.tts, "synthesize_to_file"):
                                self.tts.synthesize_to_file(
                                    output_path=str(output_path), **synthesis_params
                                )
                                audio = None
                            else:
                                # Fallback: synthesize then save
                                audio = self.tts.synthesize(**synthesis_params)
                                import soundfile as sf

                                sample_rate = getattr(self.tts, "output_sample_rate", 22050)
                                sf.write(str(output_path), audio, sample_rate)
                                audio = None
                        else:
                            # Return audio array
                            audio = self.tts.synthesize(**synthesis_params)
                            audio = np.array(audio) if isinstance(audio, (list, tuple)) else audio

                        batch_results.append(audio)
                    except Exception as e:
                        logger.error(f"Batch synthesis failed for text {batch_start + i}: {e}")
                        batch_results.append(None)

            results.extend(batch_results)

            # Clear GPU cache periodically
            if torch.cuda.is_available() and (batch_start + batch_size) % (batch_size * 2) == 0:
                torch.cuda.empty_cache()

        return results

    def enable_caching(self, enable: bool = True) -> None:
        """Enable or disable caching."""
        self._caching_enabled = enable
        logger.info(f"Model caching {'enabled' if enable else 'disabled'}")

    def set_batch_size(self, batch_size: int):
        """Set batch size for batch operations."""
        self.batch_size = max(1, batch_size)
        logger.info(f"Batch size set to {self.batch_size}")

    def _get_memory_usage(self) -> dict[str, float]:
        """Get GPU memory usage in MB."""
        if not torch.cuda.is_available():
            return {"gpu_memory_mb": 0.0, "gpu_memory_allocated_mb": 0.0}

        return {
            "gpu_memory_mb": torch.cuda.get_device_properties(0).total_memory / 1024**2,
            "gpu_memory_allocated_mb": torch.cuda.memory_allocated(0) / 1024**2,
        }

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported language codes.

        Returns:
            List of language codes (23 languages)
        """
        return self.SUPPORTED_LANGUAGES.copy()

    def get_supported_emotions(self) -> list[str]:
        """
        Get list of supported emotions.

        Returns:
            List of emotion names
        """
        return self.SUPPORTED_EMOTIONS.copy()

    def cleanup(self):
        """Clean up resources."""
        if self.tts is not None:
            del self.tts
            self.tts = None
            self._initialized = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Chatterbox Engine cleaned up")


# Factory function for easy instantiation
def create_chatterbox_engine(
    model_name: str = "chatterbox-tts/base",
    device: str | None = None,
    gpu: bool = True,
) -> ChatterboxEngine:
    """
    Create and initialize Chatterbox TTS engine.

    Args:
        model_name: Chatterbox model identifier
        device: Device to use
        gpu: Whether to use GPU

    Returns:
        Initialized ChatterboxEngine instance
    """
    engine = ChatterboxEngine(model_name=model_name, device=device, gpu=gpu)
    engine.initialize()
    return engine


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = create_chatterbox_engine()

    # Example: Clone voice and synthesize
    reference_audio = "path/to/reference.wav"
    text = "Hello, this is a test of voice cloning with Chatterbox TTS."

    audio = engine.clone_voice(
        reference_audio=reference_audio, text=text, language="en", emotion="happy"
    )

    if audio is not None and isinstance(audio, np.ndarray):
        print(f"Generated audio shape: {audio.shape}")

    # Cleanup
    engine.cleanup()
