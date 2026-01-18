"""
Piper (Rhasspy) Engine for VoiceStudio
Fast, lightweight TTS integration

Piper is a fast, lightweight neural TTS engine that provides
high-quality speech synthesis with minimal resource usage.

Compatible with:
- Python 3.10+
- piper-tts package or compiled binary
- System installation of Piper
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import soundfile as sf

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
try:
    from ..audio.audio_utils import (
        enhance_voice_quality,
        match_voice_profile,
        normalize_lufs,
        remove_artifacts,
    )

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False

logger = logging.getLogger(__name__)

# Piper instance cache (for Python package)
_PIPER_INSTANCE_CACHE: OrderedDict = OrderedDict()
_MAX_PIPER_CACHE_SIZE = 3  # Maximum number of Piper instances to cache

# Temp directory cache (reuse temp directory)
_temp_dir: Optional[tempfile.TemporaryDirectory] = None


def _get_piper_cache_key(voice: Optional[str], model_path: Optional[str]) -> str:
    """Generate cache key for Piper instance."""
    return f"piper::{voice or 'default'}::{model_path or 'default'}"


def _get_cached_piper_instance(voice: Optional[str], model_path: Optional[str]):
    """Get cached Piper instance if available."""
    cache_key = _get_piper_cache_key(voice, model_path)
    if cache_key in _PIPER_INSTANCE_CACHE:
        # Move to end (most recently used)
        _PIPER_INSTANCE_CACHE.move_to_end(cache_key)
        return _PIPER_INSTANCE_CACHE[cache_key]
    return None


def _cache_piper_instance(voice: Optional[str], model_path: Optional[str], instance):
    """Cache Piper instance with LRU eviction."""
    cache_key = _get_piper_cache_key(voice, model_path)

    # Remove if already exists
    if cache_key in _PIPER_INSTANCE_CACHE:
        _PIPER_INSTANCE_CACHE.move_to_end(cache_key)
        return

    # Add new instance
    _PIPER_INSTANCE_CACHE[cache_key] = instance

    # Evict oldest if cache full
    if len(_PIPER_INSTANCE_CACHE) > _MAX_PIPER_CACHE_SIZE:
        oldest_key, oldest_instance = _PIPER_INSTANCE_CACHE.popitem(last=False)
        # Cleanup oldest instance
        try:
            del oldest_instance
            logger.debug(f"Evicted Piper instance from cache: {oldest_key}")
        except Exception as e:
            logger.warning(f"Error evicting Piper instance from cache: {e}")

    logger.debug(
        f"Cached Piper instance: {cache_key} (cache size: {len(_PIPER_INSTANCE_CACHE)})"
    )


def _get_temp_dir() -> str:
    """Get or create reusable temp directory."""
    global _temp_dir
    if _temp_dir is None:
        _temp_dir = tempfile.TemporaryDirectory(prefix="piper_")
        logger.debug(f"Created reusable temp directory: {_temp_dir.name}")
    return _temp_dir.name


# Import base protocol
try:
    from .protocols import EngineProtocol
except ImportError:
    try:
        from .base import EngineProtocol
    except ImportError:
        from abc import ABC, abstractmethod

        class EngineProtocol(ABC):
            def __init__(self, device=None, gpu=True):
                self.device = device or ("cuda" if gpu else "cpu")
                self._initialized = False

            @abstractmethod
            def initialize(self): ...

            @abstractmethod
            def cleanup(self): ...

            def is_initialized(self):
                return self._initialized

            def get_device(self):
                return self.device


class PiperEngine(EngineProtocol):
    """
    Piper Engine for fast, lightweight TTS synthesis.

    Supports:
    - Fast synthesis
    - Multiple languages
    - Multiple voices
    - Low resource usage
    """

    # Supported languages
    SUPPORTED_LANGUAGES = [
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "pl",
        "ru",
        "uk",
        "cs",
        "sk",
        "hr",
        "sr",
        "bg",
        "ro",
        "hu",
        "el",
        "tr",
        "ar",
        "zh",
        "ja",
        "ko",
        "vi",
        "th",
        "hi",
        "nl",
        "sv",
        "da",
        "no",
        "fi",
    ]

    # Default sample rate
    DEFAULT_SAMPLE_RATE = 22050

    def __init__(
        self,
        model_path: Optional[str] = None,
        voice: Optional[str] = None,
        piper_path: Optional[str] = None,
        device: Optional[str] = None,
        gpu: bool = False,
        lazy_load: bool = True,
        batch_size: int = 4,
        enable_caching: bool = True,
    ):
        """
        Initialize Piper engine.

        Args:
            model_path: Path to Piper model file (.onnx)
            voice: Voice name (e.g., 'en_US-lessac-medium')
            piper_path: Path to Piper executable (auto-detect if None)
            device: Device parameter (not used, kept for protocol compatibility)
            gpu: Whether to use GPU (Piper typically uses CPU)
            lazy_load: If True, defer initialization until first use
            batch_size: Batch size for batch synthesis operations
            enable_caching: If True, enable Piper instance caching
        """
        super().__init__(device=device, gpu=gpu)

        self.model_path = model_path
        self.voice = voice
        self.piper_path = piper_path
        self.executable_path = None
        self.sample_rate = self.DEFAULT_SAMPLE_RATE
        self.lazy_load = lazy_load
        self.batch_size = batch_size
        self.enable_caching = enable_caching
        self._piper_instance = None  # Cached Piper instance (Python package)

        # Apply defaults for model/voice using the shared models root
        models_root = os.getenv("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models")
        if self.voice is None:
            self.voice = "en_US-amy-medium"
        if self.model_path is None:
            candidate = os.path.join(models_root, "piper", "en_US-amy-medium.onnx")
            if os.path.exists(candidate):
                self.model_path = candidate
            else:
                logger.warning(
                    "Piper model not found at default path: %s. "
                    "Place en_US-amy-medium.onnx under models\\piper or "
                    "pass a model_path.",
                    candidate,
                )

    def _find_executable(
        self, name: str, custom_path: Optional[str] = None
    ) -> Optional[str]:
        """Find executable in PATH or custom path."""
        if (
            custom_path
            and os.path.isfile(custom_path)
            and os.access(custom_path, os.X_OK)
        ):
            return custom_path

        if custom_path and os.path.isdir(custom_path):
            exe_path = os.path.join(custom_path, name)
            if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                return exe_path

        exe_path = shutil.which(name)
        if exe_path:
            return exe_path

        exe_path = shutil.which(f"{name}.exe")
        if exe_path:
            return exe_path

        return None

    def _initialize_piper_instance(self):
        """Initialize and cache Piper instance (Python package only)."""
        if self._piper_instance is not None:
            return self._piper_instance

        # Check cache first
        if self.enable_caching:
            cached = _get_cached_piper_instance(self.voice, self.model_path)
            if cached is not None:
                logger.debug("Using cached Piper instance")
                self._piper_instance = cached
                return cached

        # Create new instance
        try:
            import piper_tts

            if self.voice:
                piper = piper_tts.Piper(voice=self.voice)
            elif self.model_path:
                piper = piper_tts.Piper(model_path=self.model_path)
            else:
                piper = piper_tts.Piper()

            # Cache instance
            if self.enable_caching:
                _cache_piper_instance(self.voice, self.model_path, piper)

            self._piper_instance = piper
            return piper
        except ImportError:
            return None
        except Exception as e:
            logger.warning(f"Failed to create Piper instance: {e}")
            return None

    def initialize(self) -> bool:
        """
        Initialize the Piper engine.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if self._initialized:
                return True

            # Lazy loading: defer until first use
            if self.lazy_load:
                logger.debug(
                    "Lazy loading enabled, engine will be initialized on first use"
                )
                return True

            logger.info("Initializing Piper engine")

            # Try Python package first
            try:
                import piper_tts

                logger.info("piper-tts Python package found")
                self.executable_path = "python_package"
                self._initialized = True
                return True
            except ImportError:
                logger.info("piper-tts Python package not found, trying binary")

            # Find executable
            self.executable_path = self._find_executable("piper", self.piper_path)
            if not self.executable_path:
                # Try common names
                for exe_name in ["piper-tts", "piper.exe", "piper-tts.exe"]:
                    self.executable_path = self._find_executable(
                        exe_name, self.piper_path
                    )
                    if self.executable_path:
                        break

            if not self.executable_path:
                logger.error(
                    "Piper executable not found. Install from: https://github.com/rhasspy/piper"
                )
                logger.error("Or use Python package: pip install piper-tts")
                self._initialized = False
                return False

            # Test executable
            try:
                if self.executable_path != "python_package":
                    result = subprocess.run(
                        [self.executable_path, "--help"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode != 0:
                        logger.warning("Piper help command returned non-zero")
            except subprocess.TimeoutExpired:
                logger.warning("Piper help check timed out, but continuing")
            except Exception as e:
                logger.warning(f"Piper test failed: {e}, but continuing")

            self._initialized = True
            logger.info(
                f"Piper engine initialized successfully (executable: {self.executable_path})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Piper engine: {e}")
            self._initialized = False
            return False

    def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
        enhance_quality: bool = False,
        calculate_quality: bool = False,
        **kwargs,
    ) -> Union[Optional[np.ndarray], Tuple[Optional[np.ndarray], Dict]]:
        """
        Synthesize speech from text using Piper.

        Args:
            text: Text to synthesize
            language: Language code (e.g., 'en', 'es', 'fr')
            voice: Voice name (optional, uses default if not provided)
            output_path: Optional path to save output audio
            enhance_quality: If True, apply quality enhancement pipeline
            calculate_quality: If True, return quality metrics along with audio
            **kwargs: Additional synthesis parameters
                - speed: Speech speed (0.5-2.0, default 1.0)
                - length_scale: Length scale for prosody (default 1.0)

        Returns:
            Audio array (numpy) or None if synthesis failed,
            or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        if not self._initialized:
            if not self.initialize():
                return None

        try:
            # Get synthesis parameters
            speed = kwargs.get("speed", 1.0)
            length_scale = kwargs.get("length_scale", 1.0)

            # Use provided voice or default
            selected_voice = voice or self.voice

            # Use reusable temp directory for temp files
            if output_path:
                output_file = Path(output_path)
            else:
                temp_dir = _get_temp_dir()
                import uuid

                output_file = Path(temp_dir) / f"{uuid.uuid4().hex}.wav"

            try:
                # Use Python package if available
                if self.executable_path == "python_package":
                    # Use cached instance if available
                    piper = self._initialize_piper_instance()
                    if piper is None:
                        logger.error("Failed to initialize Piper instance")
                        return None

                    # Synthesize
                    audio = piper.synthesize(text)

                    # Get sample rate
                    self.sample_rate = (
                        piper.sample_rate if hasattr(piper, "sample_rate") else 22050
                    )

                    # Convert to numpy if needed
                    if not isinstance(audio, np.ndarray):
                        audio = np.array(audio, dtype=np.float32)
                else:
                    # Use command-line interface
                    cmd = [self.executable_path]

                    # Add model/voice
                    if self.model_path:
                        cmd.extend(["--model", str(self.model_path)])
                    elif selected_voice:
                        cmd.extend(["--voice", selected_voice])

                    # Add output file
                    cmd.extend(["--output-file", str(output_file.absolute())])

                    # Run synthesis
                    result = subprocess.run(
                        cmd,
                        input=text,
                        text=True,
                        capture_output=True,
                        timeout=60,
                    )

                    if result.returncode != 0:
                        logger.error(f"Piper synthesis failed: {result.stderr}")
                        return None

                    # Read generated audio
                    audio, sample_rate = sf.read(output_file)

                    # Update sample rate
                    self.sample_rate = sample_rate

                # Convert to mono if stereo
                if len(audio.shape) > 1:
                    audio = np.mean(audio, axis=1)

                # Convert to float32
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)

                # Normalize
                if np.max(np.abs(audio)) > 0:
                    audio = audio / np.max(np.abs(audio)) * 0.95

                # Apply speed adjustment if needed
                if speed != 1.0:
                    try:
                        import librosa

                        audio = librosa.effects.time_stretch(audio, rate=speed)
                    except ImportError:
                        logger.warning("librosa not available for speed adjustment")

            finally:
                # Cleanup temp file if created (only if not in reusable temp dir)
                if not output_path and os.path.exists(output_file):
                    try:
                        # Only delete if not in reusable temp directory
                        temp_dir = _get_temp_dir()
                        if str(output_file.parent) != temp_dir:
                            os.unlink(output_file)
                    except Exception as e:
                        logger.debug(f"Temp file cleanup: {e}")

            # Apply quality processing if requested
            if enhance_quality or calculate_quality:
                audio = self._process_audio_quality(
                    audio,
                    self.sample_rate,
                    None,
                    enhance_quality,
                    calculate_quality,
                )
                if isinstance(audio, tuple):
                    enhanced_audio, quality_metrics = audio
                    if output_path:
                        sf.write(output_path, enhanced_audio, self.sample_rate)
                        return None, quality_metrics
                    return enhanced_audio, quality_metrics
                else:
                    if output_path:
                        sf.write(output_path, audio, self.sample_rate)
                        return None
                    return audio

            # Save to file if requested
            if output_path:
                sf.write(output_path, audio, self.sample_rate)
                logger.info(f"Audio saved to: {output_path}")
                return None

            return audio

        except Exception as e:
            logger.error(f"Piper synthesis failed: {e}")
            return None

    def _process_audio_quality(
        self,
        audio: np.ndarray,
        sample_rate: int,
        reference_audio: Optional[Union[str, Path]] = None,
        enhance: bool = False,
        calculate: bool = False,
    ) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
        """Process audio for quality enhancement and/or metrics calculation."""
        quality_metrics = {}

        if enhance and HAS_AUDIO_UTILS:
            try:
                audio = enhance_voice_quality(audio, sample_rate)
                audio = normalize_lufs(audio, sample_rate, target_lufs=-23.0)
                audio = remove_artifacts(audio, sample_rate)
            except Exception as e:
                logger.warning(f"Quality enhancement failed: {e}")

        if calculate and HAS_QUALITY_METRICS:
            try:
                quality_metrics = calculate_all_metrics(audio, sample_rate)
                if reference_audio:
                    try:
                        ref_audio, ref_sr = sf.read(reference_audio)
                        similarity = calculate_similarity(
                            audio, sample_rate, ref_audio, ref_sr
                        )
                        quality_metrics["similarity"] = similarity
                    except Exception as e:
                        logger.warning(f"Similarity calculation failed: {e}")
            except Exception as e:
                logger.warning(f"Quality metrics calculation failed: {e}")
                quality_metrics = {}

        if calculate:
            return audio, quality_metrics
        return audio

    def get_voices(self, language: Optional[str] = None) -> List[str]:
        """Get available voices/speakers."""
        if not self._initialized:
            if not self.initialize():
                return []

        # Common Piper voices
        voices = [
            "en_US-lessac-medium",
            "en_US-lessac-low",
            "en_US-amy-medium",
            "en_US-amy-low",
            "en_GB-alba-medium",
            "en_GB-alba-low",
            "es_ES-davefx-medium",
            "es_ES-davefx-low",
            "fr_FR-siwis-medium",
            "fr_FR-siwis-low",
            "de_DE-thorsten-medium",
            "de_DE-thorsten-low",
            "it_IT-riccardo-medium",
            "it_IT-riccardo-low",
            "pt_PT-tugal-medium",
            "pt_PT-tugal-low",
        ]

        if language:
            # Filter by language
            voices = [v for v in voices if v.startswith(language)]

        return voices

    def get_languages(self) -> List[str]:
        """Get available languages."""
        return self.SUPPORTED_LANGUAGES

    def batch_synthesize(
        self,
        texts: List[str],
        language: str = "en",
        voice: Optional[str] = None,
        output_dir: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> List[Optional[np.ndarray]]:
        """
        Synthesize multiple texts in batch with optimized processing.

        Args:
            texts: List of texts to synthesize
            language: Language code
            voice: Voice name (optional)
            output_dir: Optional directory to save outputs
            **kwargs: Additional synthesis parameters

        Returns:
            List of audio arrays
        """
        if not self._initialized:
            if not self.initialize():
                return [None] * len(texts)

        results = []

        # Use Python package if available (faster for batch)
        if self.executable_path == "python_package":
            piper = self._initialize_piper_instance()
            if piper is None:
                return [None] * len(texts)

            # Process in batches
            batch_size = self.batch_size
            for batch_start in range(0, len(texts), batch_size):
                batch_texts = texts[batch_start : batch_start + batch_size]
                batch_results = []

                for i, text in enumerate(batch_texts):
                    try:
                        audio = piper.synthesize(text)

                        # Convert to numpy if needed
                        if not isinstance(audio, np.ndarray):
                            audio = np.array(audio, dtype=np.float32)

                        # Convert to mono if stereo
                        if len(audio.shape) > 1:
                            audio = np.mean(audio, axis=1)

                        # Normalize
                        if np.max(np.abs(audio)) > 0:
                            audio = audio / np.max(np.abs(audio)) * 0.95

                        # Save to file if output_dir provided
                        if output_dir:
                            output_path = (
                                Path(output_dir) / f"output_{batch_start + i:04d}.wav"
                            )
                            sf.write(str(output_path), audio, self.sample_rate)
                            batch_results.append(None)
                        else:
                            batch_results.append(audio)
                    except Exception as e:
                        logger.error(
                            f"Batch synthesis failed for text {batch_start + i}: {e}"
                        )
                        batch_results.append(None)

                results.extend(batch_results)
        else:
            # Use subprocess with parallel processing
            batch_size = self.batch_size

            def synthesize_single(args):
                idx, text = args
                try:
                    result = self.synthesize(
                        text=text, language=language, voice=voice, **kwargs
                    )
                    if output_dir and result is not None:
                        output_path = Path(output_dir) / f"output_{idx:04d}.wav"
                        sf.write(str(output_path), result, self.sample_rate)
                        return None
                    return result
                except Exception as e:
                    logger.error(f"Batch synthesis failed for text {idx}: {e}")
                    return None

            # Process in parallel batches
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                results = list(
                    executor.map(
                        synthesize_single, [(i, text) for i, text in enumerate(texts)]
                    )
                )

        return results

    def enable_caching(self, enable: bool = True):
        """Enable or disable caching."""
        self.enable_caching = enable
        logger.info(f"Piper instance caching {'enabled' if enable else 'disabled'}")

    def set_batch_size(self, batch_size: int):
        """Set batch size for batch operations."""
        self.batch_size = max(1, batch_size)
        logger.info(f"Batch size set to {self.batch_size}")

    def cleanup(self):
        """Clean up resources."""
        try:
            self._piper_instance = None
            self._initialized = False
            logger.info("Piper engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def get_info(self) -> Dict:
        """Get engine information."""
        info = super().get_info()
        info.update(
            {
                "model_path": self.model_path,
                "voice": self.voice,
                "executable_path": (
                    str(self.executable_path) if self.executable_path else None
                ),
                "sample_rate": self.sample_rate,
                "supported_languages": len(self.SUPPORTED_LANGUAGES),
                "lightweight": True,
                "fast": True,
            }
        )
        return info


def create_piper_engine(
    model_path: Optional[str] = None,
    voice: Optional[str] = None,
    piper_path: Optional[str] = None,
    device: Optional[str] = None,
    gpu: bool = False,
) -> PiperEngine:
    """Factory function to create a Piper engine instance."""
    return PiperEngine(
        model_path=model_path,
        voice=voice,
        piper_path=piper_path,
        device=device,
        gpu=gpu,
    )
