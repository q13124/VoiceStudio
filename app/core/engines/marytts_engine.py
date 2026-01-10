"""
MaryTTS Engine for VoiceStudio
Classic open-source multilingual TTS integration

MaryTTS is a modular open-source multilingual text-to-speech synthesis platform.
It supports multiple languages and voices through a server-based architecture.

Compatible with:
- Python 3.10+
- MaryTTS server (requires separate installation)
- HTTP requests for synthesis
"""

import hashlib
import logging
import os
import tempfile
from collections import OrderedDict
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import requests
import soundfile as sf

# Try importing requests for connection pooling
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    HAS_REQUESTS_ADAPTERS = True
except ImportError:
    HAS_REQUESTS_ADAPTERS = False

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

# Import base protocol
try:
    from .protocols import EngineProtocol
except ImportError:
    # Fallback if protocols not available
    try:
        from .base import EngineProtocol
    except ImportError:
        # Final fallback
        from abc import ABC, abstractmethod

        class EngineProtocol(ABC):
            def __init__(self, device=None, gpu=True):
                self.device = device or ("cuda" if gpu else "cpu")
                self._initialized = False

            @abstractmethod
            def initialize(self):
                ...

            @abstractmethod
            def cleanup(self):
                ...

            def is_initialized(self):
                return self._initialized

            def get_device(self):
                return self.device


class MaryTTSEngine(EngineProtocol):
    """
    MaryTTS Engine for multilingual text-to-speech synthesis.

    Supports:
    - Multiple languages (depends on installed voices)
    - Multiple voices per language
    - SSML markup for prosody control
    - Server-based architecture
    """

    # Common supported languages (may vary based on installed voices)
    SUPPORTED_LANGUAGES = ["en", "de", "fr", "it", "es", "ru", "tr", "te", "hi", "zh"]

    # Default sample rate for MaryTTS (typically 16000 or 22050)
    DEFAULT_SAMPLE_RATE = 16000

    def __init__(
        self,
        server_url: str = "http://localhost:59125",
        device: Optional[str] = None,
        gpu: bool = False,  # MaryTTS server handles GPU internally
    ):
        """
        Initialize MaryTTS engine.

        Args:
            server_url: URL of MaryTTS server (default: http://localhost:59125)
            device: Device parameter (not used for MaryTTS, kept for protocol compatibility)
            gpu: GPU parameter (not used for MaryTTS, kept for protocol compatibility)
        """
        # Initialize base protocol
        super().__init__(device=device, gpu=gpu)

        self.server_url = server_url.rstrip("/")
        self.voices = []
        self.available_languages = []
        self.session = requests.Session()
        self.session.timeout = 30
        self._synthesis_cache = OrderedDict()  # LRU cache for synthesis results
        self._cache_max_size = 100  # Maximum number of cached synthesis results
        self.enable_cache = True

    def initialize(self) -> bool:
        """
        Initialize the MaryTTS engine by connecting to server.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if self._initialized:
                return True

            logger.info(f"Connecting to MaryTTS server: {self.server_url}")

            # Set up connection pooling with retry strategy
            if HAS_REQUESTS_ADAPTERS:
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                )
                adapter = HTTPAdapter(
                    max_retries=retry_strategy,
                    pool_connections=10,
                    pool_maxsize=20,
                )
                self.session.mount("http://", adapter)
                self.session.mount("https://", adapter)
                logger.debug("Connection pooling enabled for MaryTTS API")

            # Test server connection and get available voices
            try:
                voices_url = f"{self.server_url}/voices"
                response = self.session.get(voices_url, timeout=5)

                if response.status_code == 200:
                    # Parse voices list (format: "voice_name (language)")
                    voices_text = response.text.strip()
                    if voices_text:
                        self.voices = [
                            v.strip() for v in voices_text.split("\n") if v.strip()
                        ]
                        # Extract languages from voices
                        self.available_languages = list(
                            set(
                                [
                                    v.split("(")[1].split(")")[0].strip()
                                    for v in self.voices
                                    if "(" in v and ")" in v
                                ]
                            )
                        )
                        logger.info(
                            f"Found {len(self.voices)} voices in {len(self.available_languages)} languages"
                        )
                    else:
                        logger.warning("MaryTTS server returned empty voices list")
                        self.voices = []
                        self.available_languages = []
                else:
                    logger.warning(
                        f"MaryTTS server returned status {response.status_code}"
                    )
                    # Continue anyway - voices might be available via synthesis endpoint
                    self.voices = []
                    self.available_languages = []

                # Test synthesis endpoint
                test_url = f"{self.server_url}/process"
                test_response = self.session.get(
                    test_url,
                    params={
                        "INPUT_TEXT": "test",
                        "INPUT_TYPE": "TEXT",
                        "OUTPUT_TYPE": "AUDIO",
                        "LOCALE": "en",
                    },
                    timeout=5,
                )

                if test_response.status_code == 200:
                    self._initialized = True
                    logger.info("MaryTTS engine initialized successfully")
                    return True
                else:
                    logger.error(
                        f"MaryTTS synthesis test failed with status {test_response.status_code}"
                    )
                    self._initialized = False
                    return False

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to connect to MaryTTS server: {e}")
                logger.error(
                    f"Make sure MaryTTS server is running at {self.server_url}"
                )
                logger.error(
                    "Install MaryTTS server from: https://github.com/marytts/marytts"
                )
                self._initialized = False
                return False

        except Exception as e:
            logger.error(f"Failed to initialize MaryTTS engine: {e}")
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
        Synthesize speech from text using MaryTTS.

        Args:
            text: Text to synthesize
            language: Language code (e.g., 'en', 'de', 'fr')
            voice: Voice name (optional, uses default for language if not specified)
            output_path: Optional path to save output audio
            enhance_quality: If True, apply quality enhancement pipeline
            calculate_quality: If True, return quality metrics along with audio
            **kwargs: Additional synthesis parameters
                - ssml: If True, treat text as SSML markup
                - audio_format: Output format ('WAV', 'MP3', etc.)

        Returns:
            Audio array (numpy) or None if synthesis failed,
            or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        if not self._initialized:
            if not self.initialize():
                return None

        try:
            # Check synthesis cache (LRU)
            if self.enable_cache:
                cache_key = hashlib.md5(
                    f"{text}_{language}_{voice}_{kwargs.get('audio_format', 'WAV')}".encode()
                ).hexdigest()
                if cache_key in self._synthesis_cache:
                    logger.debug("Using cached MaryTTS synthesis result")
                    self._synthesis_cache.move_to_end(cache_key)  # LRU update
                    cached_result = self._synthesis_cache[cache_key]
                    # Return cached audio
                    if output_path:
                        sf.write(
                            output_path,
                            cached_result["audio"],
                            cached_result["sample_rate"],
                        )
                        return None
                    if calculate_quality:
                        return cached_result["audio"], cached_result.get(
                            "quality_metrics", {}
                        )
                    return cached_result["audio"]

            # Build synthesis URL
            synthesis_url = f"{self.server_url}/process"

            # Prepare parameters
            params = {
                "INPUT_TEXT": text,
                "INPUT_TYPE": "SSML" if kwargs.get("ssml", False) else "TEXT",
                "OUTPUT_TYPE": "AUDIO",
                "LOCALE": language,
                "AUDIO": kwargs.get("audio_format", "WAV"),
            }

            # Add voice if specified
            if voice:
                params["VOICE"] = voice

            # Request synthesis
            response = self.session.get(synthesis_url, params=params, timeout=60)

            if response.status_code != 200:
                logger.error(
                    f"MaryTTS synthesis failed with status {response.status_code}: {response.text}"
                )
                return None

            # Read audio from response
            audio_bytes = BytesIO(response.content)
            audio, sample_rate = sf.read(audio_bytes)

            # Convert to mono if stereo
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            # Convert to float32 if needed
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95

            # Cache result if successful (LRU)
            quality_metrics_result = {}
            if self.enable_cache:
                # Process quality if needed for caching
                if calculate_quality:
                    quality_metrics_result = self._calculate_quality_metrics(
                        audio, sample_rate
                    )

                # Manage cache size - remove oldest entries if cache is full
                if len(self._synthesis_cache) >= self._cache_max_size:
                    oldest_key = next(iter(self._synthesis_cache))
                    del self._synthesis_cache[oldest_key]

                cache_key = hashlib.md5(
                    f"{text}_{language}_{voice}_{kwargs.get('audio_format', 'WAV')}".encode()
                ).hexdigest()
                self._synthesis_cache[cache_key] = {
                    "audio": audio.copy(),
                    "sample_rate": sample_rate,
                    "quality_metrics": (
                        quality_metrics_result if calculate_quality else {}
                    ),
                }
                self._synthesis_cache.move_to_end(cache_key)  # LRU update

            # Apply quality processing if requested
            if enhance_quality or calculate_quality:
                audio = self._process_audio_quality(
                    audio, sample_rate, None, enhance_quality, calculate_quality
                )
                if isinstance(audio, tuple):
                    # Quality metrics returned
                    enhanced_audio, quality_metrics = audio
                    if output_path:
                        sf.write(output_path, enhanced_audio, sample_rate)
                        return None, quality_metrics
                    return enhanced_audio, quality_metrics
                else:
                    if output_path:
                        sf.write(output_path, audio, sample_rate)
                        return None
                    return audio

            # Save to file if requested
            if output_path:
                sf.write(output_path, audio, sample_rate)
                logger.info(f"Audio saved to: {output_path}")
                return None

            return audio

        except Exception as e:
            logger.error(f"MaryTTS synthesis failed: {e}")
            return None

    def _calculate_quality_metrics(
        self,
        audio: np.ndarray,
        sample_rate: int,
        reference_audio: Optional[Union[str, Path]] = None,
    ) -> Dict:
        """Calculate quality metrics for audio."""
        quality_metrics = {}

        if HAS_QUALITY_METRICS:
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

        return quality_metrics

    def _process_audio_quality(
        self,
        audio: np.ndarray,
        sample_rate: int,
        reference_audio: Optional[Union[str, Path]] = None,
        enhance: bool = False,
        calculate: bool = False,
    ) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
        """
        Process audio for quality enhancement and/or metrics calculation.

        Args:
            audio: Audio array
            sample_rate: Sample rate
            reference_audio: Optional reference audio for similarity calculation
            enhance: If True, enhance audio quality
            calculate: If True, calculate quality metrics

        Returns:
            Enhanced audio or tuple of (audio, metrics) if calculate=True
        """
        quality_metrics = {}

        # Enhance audio if requested
        if enhance and HAS_AUDIO_UTILS:
            try:
                audio = enhance_voice_quality(audio, sample_rate)
                audio = normalize_lufs(audio, sample_rate, target_lufs=-23.0)
                audio = remove_artifacts(audio, sample_rate)
            except Exception as e:
                logger.warning(f"Quality enhancement failed: {e}")

        # Calculate metrics if requested
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
        """
        Get available voices.

        Args:
            language: Optional language filter

        Returns:
            List of voice names
        """
        if not self._initialized:
            if not self.initialize():
                return []

        if language:
            return [v for v in self.voices if f"({language})" in v]
        return self.voices

    def get_languages(self) -> List[str]:
        """
        Get available languages.

        Returns:
            List of language codes
        """
        if not self._initialized:
            if not self.initialize():
                return []

        return (
            self.available_languages
            if self.available_languages
            else self.SUPPORTED_LANGUAGES
        )

    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, "session"):
                self.session.close()
            self._synthesis_cache.clear()
            self._initialized = False
            logger.info("MaryTTS engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during MaryTTS cleanup: {e}")

    def clear_cache(self):
        """Clear synthesis cache."""
        self._synthesis_cache.clear()
        logger.info("Synthesis cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._synthesis_cache),
            "max_cache_size": self._cache_max_size,
            "cache_enabled": self.enable_cache,
        }

    def get_info(self) -> Dict:
        """Get engine information."""
        info = super().get_info()
        info.update(
            {
                "server_url": self.server_url,
                "voices_count": len(self.voices),
                "languages": self.available_languages,
                "sample_rate": self.DEFAULT_SAMPLE_RATE,
            }
        )
        return info


def create_marytts_engine(
    server_url: str = "http://localhost:59125",
    device: Optional[str] = None,
    gpu: bool = False,
) -> MaryTTSEngine:
    """
    Factory function to create a MaryTTS engine instance.

    Args:
        server_url: URL of MaryTTS server
        device: Device parameter (not used)
        gpu: GPU parameter (not used)

    Returns:
        MaryTTSEngine instance
    """
    return MaryTTSEngine(server_url=server_url, device=device, gpu=gpu)
