"""
XTTS Engine for VoiceStudio
Coqui TTS XTTS v2 integration for voice cloning and synthesis

Compatible with:
- Python 3.10.15
- Coqui TTS 0.27.2
- Transformers 4.55.4
- PyTorch 2.2.2+cu121
"""

import logging
import os
import sys
import time
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch

# Optional quality metrics import
try:
    from .quality_metrics import (calculate_all_metrics, calculate_mos_score,
                                  calculate_naturalness, calculate_similarity)

    HAS_QUALITY_METRICS = True
except ImportError:
    HAS_QUALITY_METRICS = False

# Optional audio utilities import for quality enhancement
try:
    from ..audio.audio_utils import (enhance_voice_cloning_quality,
                                     enhance_voice_quality,
                                     match_voice_profile, normalize_lufs,
                                     remove_artifacts)

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    enhance_voice_cloning_quality = None

try:
    from TTS.api import TTS
    from TTS.utils.manage import ModelManager
except ImportError:
    TTS = None
    ModelManager = None
    logging.warning(
        "Coqui TTS not installed. Install with: pip install coqui-tts==0.27.2"
    )

logger = logging.getLogger(__name__)

# Optional librosa import for prosody control
try:
    import librosa

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    librosa = None
    logger.warning("librosa not available. Prosody control will be limited.")

# Coqui TTS expects model IDs like: tts_models/<language>/<dataset>/<model_name>.
# Older configs/docs may use the HuggingFace-style repo id (e.g. "coqui/XTTS-v2").
XTTS_DEFAULT_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
_XTTS_MODEL_NAME_ALIASES = {
    "coqui/xtts-v2": XTTS_DEFAULT_MODEL_NAME,
}


def _normalize_xtts_model_name(model_name: Optional[str]) -> str:
    """
    Normalize XTTS model identifiers to a Coqui-TTS-compatible model id.

    Accepts legacy HuggingFace-style repo ids and maps them to the canonical Coqui ID.
    """
    if not model_name:
        return XTTS_DEFAULT_MODEL_NAME

    name = str(model_name).strip()
    if not name:
        return XTTS_DEFAULT_MODEL_NAME

    return _XTTS_MODEL_NAME_ALIASES.get(name.lower(), name)


# Try importing general model cache
try:
    from ..models.cache import get_model_cache

    _model_cache = get_model_cache(max_models=5, max_memory_mb=2048.0)  # 2GB max
    HAS_MODEL_CACHE = True
except ImportError:
    HAS_MODEL_CACHE = False
    _model_cache = None
    logger.debug("General model cache not available, using XTTS-specific cache")

# Fallback: XTTS-specific cache (for backward compatibility)
_MODEL_CACHE: OrderedDict = OrderedDict()
_MAX_CACHE_SIZE = 2  # Maximum number of models to cache in memory


def _get_cache_key(model_name: str, device: str) -> str:
    """Generate cache key for model."""
    return f"{model_name}::{device}"


def _get_cached_model(model_name: str, device: str):
    """Get cached model if available."""
    # Try general model cache first
    if HAS_MODEL_CACHE and _model_cache is not None:
        cached = _model_cache.get("xtts", model_name, device=device)
        if cached is not None:
            return cached

    # Fallback to XTTS-specific cache
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
            _model_cache.set("xtts", model_name, model, device=device)
            return
        except Exception as e:
            logger.warning(f"Failed to cache in general cache: {e}, using fallback")

    # Fallback to XTTS-specific cache
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
            def initialize(self): ...

            @abstractmethod
            def cleanup(self): ...

            def is_initialized(self):
                return self._initialized

            def get_device(self):
                return self.device


class XTTSEngine(EngineProtocol):
    """
    XTTS v2 Engine for voice cloning and text-to-speech synthesis.

    Supports:
    - Voice cloning from reference audio
    - Multi-language synthesis
    - Emotion and style control
    - Real-time and batch processing
    """

    def __init__(
        self,
        model_name: str = XTTS_DEFAULT_MODEL_NAME,
        device: Optional[str] = None,
        gpu: bool = True,
    ):
        """
        Initialize XTTS engine.

        Args:
            model_name: XTTS model identifier
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
        """
        if TTS is None:
            raise ImportError(
                "Coqui TTS not installed. Install with: pip install coqui-tts==0.27.2"
            )

        # Initialize base protocol
        super().__init__(device=device, gpu=gpu)

        requested_model_name = model_name
        self.model_name = _normalize_xtts_model_name(model_name)
        if requested_model_name != self.model_name:
            logger.info(
                f"Normalized XTTS model_name '{requested_model_name}' -> '{self.model_name}'"
            )
        # Override device if GPU requested and available
        if gpu and torch.cuda.is_available() and self.device == "cpu":
            self.device = "cuda"

        # Guardrail: some GPUs (e.g. RTX 50-series / sm_120) are newer than the pinned
        # PyTorch build and will crash at runtime with:
        #   "CUDA error: no kernel image is available for execution on the device"
        # Detect unsupported compute capability and fall back to CPU automatically so
        # voice cloning remains functional (albeit slower).
        if self.device == "cuda" and torch.cuda.is_available():
            try:
                cap = torch.cuda.get_device_capability(0)
                arch = f"sm_{cap[0]}{cap[1]}"
                supported_arches = list(torch.cuda.get_arch_list())
                if supported_arches and arch not in supported_arches:
                    gpu_name = torch.cuda.get_device_name(0)
                    logger.warning(
                        "CUDA device '%s' (capability %s) is not supported by this PyTorch build (%s). "
                        "Supported arches: %s. Falling back to CPU for XTTS.",
                        gpu_name,
                        arch,
                        torch.__version__,
                        " ".join(supported_arches),
                    )
                    self.device = "cpu"
            except Exception as e:
                logger.warning(
                    f"Failed to verify CUDA arch compatibility for XTTS: {e}"
                )
        self.tts = None
        self._use_cache = True  # Enable model caching by default
        self._lazy_load = False  # Lazy loading flag
        self._batch_size = 1  # Default batch size for batch processing

    def initialize(self, lazy: bool = False) -> bool:
        """
        Initialize the TTS model with caching and optimization.

        Args:
            lazy: If True, delay actual model loading until first use

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if self._initialized:
                return True

            # Check cache first if enabled
            if self._use_cache:
                cached_model = _get_cached_model(self.model_name, self.device)
                if cached_model is not None:
                    logger.info(
                        f"Using cached XTTS model: {self.model_name} "
                        f"(device: {self.device})"
                    )
                    self.tts = cached_model
                    self._initialized = True
                    return True

            # Lazy loading: just mark as ready, load on first use
            if lazy:
                self._lazy_load = True
                self._initialized = True
                logger.info(
                    f"XTTS engine initialized with lazy loading "
                    f"(model: {self.model_name})"
                )
                return True

            # Load model immediately
            return self._load_model()

        except Exception as e:
            logger.error(f"Failed to initialize XTTS model: {e}")
            self._initialized = False
            return False

    def _load_model(self) -> bool:
        """
        Actually load the TTS model from disk or cache.

        Returns:
            True if loading successful, False otherwise
        """
        try:
            logger.info(f"Loading XTTS model: {self.model_name}")

            # Coqui XTTS-v2 downloads can require interactive CPML acceptance (input prompt).
            # In non-interactive backend runs, this can hang the server. Fail fast with a clear
            # instruction to set COQUI_TOS_AGREED=1 (or use start_backend.ps1 -CoquiTosAgreed).
            if os.environ.get("COQUI_TOS_AGREED") != "1":
                try:
                    stdin_is_tty = bool(getattr(sys.stdin, "isatty", lambda: False)())
                except Exception:
                    stdin_is_tty = False
                if not stdin_is_tty:
                    raise RuntimeError(
                        "XTTS-v2 model download requires CPML/commercial license acceptance. "
                        "For non-interactive runs, set COQUI_TOS_AGREED=1 "
                        "(e.g. start_backend.ps1 -CoquiTosAgreed)."
                    )

            # Use VOICESTUDIO_MODELS_PATH for model cache if available (default: E:\VoiceStudio\models)
            model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
            if not model_cache_dir:
                model_cache_dir = os.path.join(
                    os.getenv("VOICESTUDIO_REPO_ROOT", r"E:\VoiceStudio"),
                    "models",
                )

            # Ensure model cache directory exists
            os.makedirs(model_cache_dir, exist_ok=True)

            # Load model with progress bar disabled for faster loading
            start_time = time.time()
            self.tts = TTS(model_name=self.model_name, progress_bar=False)

            # Move to device
            self.tts.to(self.device)

            # Optimize for inference (disable gradient computation)
            if hasattr(self.tts, "model"):
                if hasattr(self.tts.model, "eval"):
                    self.tts.model.eval()
                # Enable inference mode for better performance
                if hasattr(torch, "inference_mode"):
                    # Will use inference_mode context in synthesize
                    ...

            load_time = time.time() - start_time
            logger.info(
                f"XTTS model loaded in {load_time:.2f}s "
                f"(cache: {model_cache_dir}, device: {self.device})"
            )

            # Cache model if enabled
            if self._use_cache:
                _cache_model(self.model_name, self.device, self.tts)

            self._initialized = True
            self._lazy_load = False
            return True

        except Exception as e:
            logger.error(f"Failed to load XTTS model: {e}")
            self._initialized = False
            return False

    def synthesize(
        self,
        text: str,
        speaker_wav: Union[str, Path, List[Union[str, Path]]],
        language: str = "en",
        output_path: Optional[Union[str, Path]] = None,
        enhance_quality: bool = False,
        calculate_quality: bool = False,
        **kwargs,
    ) -> Union[Optional[np.ndarray], Tuple[Optional[np.ndarray], Dict]]:
        """
        Synthesize speech from text using voice cloning.

        Args:
            text: Text to synthesize
            speaker_wav: Path to reference speaker audio file(s)
            language: Language code (e.g., 'en', 'es', 'fr', 'de', 'it', 'pt', 'pl')
            output_path: Optional path to save output audio
            enhance_quality: If True, apply quality enhancement pipeline
            calculate_quality: If True, return quality metrics along with audio
            **kwargs: Additional synthesis parameters

        Returns:
            Audio array (numpy) or None if synthesis failed,
            or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        # Handle lazy loading
        if self._lazy_load or not self._initialized:
            if not self._load_model():
                return None

        try:
            # Convert speaker_wav to list if single path
            if isinstance(speaker_wav, (str, Path)):
                speaker_wav = [speaker_wav]

            # Ensure all paths are strings
            speaker_wav = [str(path) for path in speaker_wav]

            # Get sample rate from TTS model (typically 22050 for XTTS)
            sample_rate = getattr(self.tts, "output_sample_rate", 22050)

            # Synthesize
            if output_path:
                output_path = str(output_path)
                self.tts.tts_to_file(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    file_path=output_path,
                    **kwargs,
                )
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
                # Use inference mode for better performance
                with torch.inference_mode():
                    wav = self.tts.tts(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language,
                        **kwargs,
                    )
                audio = np.array(wav)

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
        if enhance:
            try:
                # Use advanced voice cloning quality enhancement (if available)
                if HAS_AUDIO_UTILS and enhance_voice_cloning_quality is not None:
                    processed_audio = enhance_voice_cloning_quality(
                        processed_audio,
                        sample_rate,
                        enhancement_level="standard",
                        preserve_prosody=True,
                        target_lufs=-23.0,
                    )
                    logger.debug(
                        "Applied advanced voice cloning quality enhancement to synthesized audio"
                    )
                elif HAS_AUDIO_UTILS:
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
        reference_audio: Union[str, Path, List[Union[str, Path]]],
        text: str,
        language: str = "en",
        output_path: Optional[Union[str, Path]] = None,
        emotion: Optional[str] = None,
        speed: float = 1.0,
        calculate_quality: bool = False,
        enhance_quality: bool = False,
        quality_preset: Optional[str] = None,
        prosody_params: Optional[Dict[str, float]] = None,
        use_multi_reference: bool = False,
    ) -> Union[Optional[np.ndarray], Tuple[Optional[np.ndarray], Dict]]:
        """
        Clone voice from reference audio and synthesize text with advanced quality features.

        Args:
            reference_audio: Path to reference speaker audio or list of paths for multi-reference
            text: Text to synthesize
            language: Language code
            output_path: Optional output file path
            emotion: Optional emotion/style (if supported)
            speed: Speech speed multiplier
            calculate_quality: If True, return quality metrics along with audio
            enhance_quality: If True, apply advanced quality enhancement pipeline
            quality_preset: Quality preset override ('fast', 'standard', 'high', 'ultra')
            prosody_params: Advanced prosody control (pitch, tempo, formant_shift, energy)
            use_multi_reference: If True and multiple references provided, use ensemble approach

        Returns:
            Audio array or None, or tuple of (audio, quality_metrics) if calculate_quality=True
        """
        # Support multi-reference voice cloning
        if isinstance(reference_audio, list) and len(reference_audio) > 1:
            if use_multi_reference:
                # Use ensemble approach with multiple references
                logger.info(
                    f"Using multi-reference voice cloning with {len(reference_audio)} references"
                )
                return self._clone_voice_multi_reference(
                    reference_audio,
                    text,
                    language,
                    output_path,
                    emotion,
                    speed,
                    calculate_quality,
                    enhance_quality,
                    quality_preset,
                    prosody_params,
                )
            else:
                # Use first reference
                reference_audio = reference_audio[0]

        kwargs = {}
        if speed != 1.0:
            kwargs["speed"] = speed

        # Apply quality preset if specified
        if quality_preset:
            # Map quality presets to XTTS parameters
            quality_params = {
                "fast": {"temperature": 0.7, "length_penalty": 0.8},
                "standard": {"temperature": 0.75, "length_penalty": 1.0},
                "high": {"temperature": 0.8, "length_penalty": 1.2},
                "ultra": {"temperature": 0.85, "length_penalty": 1.5},
            }
            if quality_preset in quality_params:
                kwargs.update(quality_params[quality_preset])

        audio = self.synthesize(
            text=text,
            speaker_wav=reference_audio,
            language=language,
            output_path=output_path,
            enhance_quality=enhance_quality,
            calculate_quality=calculate_quality,
            **kwargs,
        )

        # `synthesize()` may return:
        # - ndarray (audio) when output_path is None
        # - (audio, metrics) when calculate_quality=True and output_path is None
        # - None when output_path is provided (file written to disk)
        # - (None, metrics) when calculate_quality=True and output_path is provided
        # In the output_path case, the file is already written and quality metrics are already
        # computed inside `synthesize()`. Avoid re-processing here.
        if isinstance(audio, tuple):
            audio_arr, quality_metrics = audio
            # If audio was written to disk, propagate metrics and return early.
            if audio_arr is None:
                return None, quality_metrics
            # If we already have metrics and no extra post-processing is requested,
            # return early to avoid double-processing.
            if not prosody_params:
                return audio_arr, quality_metrics
            audio = audio_arr

        # Apply advanced prosody control if specified
        if audio is not None and prosody_params:
            audio = self._apply_prosody_control(
                audio, getattr(self.tts, "output_sample_rate", 22050), prosody_params
            )

        # Process audio quality (enhancement + metrics)
        if audio is not None:
            audio = self._process_audio_quality(
                audio,
                getattr(self.tts, "output_sample_rate", 22050),
                (
                    reference_audio
                    if not isinstance(reference_audio, list)
                    else reference_audio[0]
                ),
                enhance=enhance_quality,
                calculate_metrics=calculate_quality,
            )
            if isinstance(audio, tuple):
                return audio  # (audio, quality_metrics)

        return audio

    def _clone_voice_multi_reference(
        self,
        reference_audios: List[Union[str, Path]],
        text: str,
        language: str,
        output_path: Optional[Union[str, Path]],
        emotion: Optional[str],
        speed: float,
        calculate_quality: bool,
        enhance_quality: bool,
        quality_preset: Optional[str],
        prosody_params: Optional[Dict[str, float]],
    ) -> Union[Optional[np.ndarray], Tuple[Optional[np.ndarray], Dict]]:
        """
        Clone voice using multiple reference audios for improved quality and stability.

        Uses ensemble approach: synthesizes with each reference and combines results.
        """
        logger.info(f"Multi-reference cloning with {len(reference_audios)} references")

        # Synthesize with each reference
        audio_results = []
        for i, ref_audio in enumerate(reference_audios):
            try:
                audio = self.synthesize(
                    text=text,
                    speaker_wav=ref_audio,
                    language=language,
                    enhance_quality=False,  # Apply enhancement after ensemble
                    calculate_quality=False,
                    speed=speed,
                )
                if audio is not None:
                    audio_results.append(audio)
            except Exception as e:
                logger.warning(f"Failed to synthesize with reference {i+1}: {e}")

        if not audio_results:
            logger.error("All reference audios failed to synthesize")
            return None

        # Ensemble: average the audio results for stability
        if len(audio_results) > 1:
            # Ensure all have same length
            min_length = min(len(a) for a in audio_results)
            audio_results = [a[:min_length] for a in audio_results]
            # Weighted average (first reference has more weight)
            weights = np.linspace(
                0.6, 0.4 / (len(audio_results) - 1), len(audio_results)
            )
            weights = weights / weights.sum()  # Normalize
            audio = np.average(audio_results, axis=0, weights=weights)
        else:
            audio = audio_results[0]

        # Apply prosody control if specified
        if prosody_params:
            audio = self._apply_prosody_control(
                audio, getattr(self.tts, "output_sample_rate", 22050), prosody_params
            )

        # Apply quality processing
        audio = self._process_audio_quality(
            audio,
            getattr(self.tts, "output_sample_rate", 22050),
            reference_audios[0],  # Use first reference for metrics
            enhance=enhance_quality,
            calculate_metrics=calculate_quality,
        )

        if isinstance(audio, tuple):
            return audio

        # Save if output path specified
        if output_path:
            import soundfile as sf

            sf.write(
                str(output_path), audio, getattr(self.tts, "output_sample_rate", 22050)
            )

        return audio

    def _apply_prosody_control(
        self,
        audio: np.ndarray,
        sample_rate: int,
        prosody_params: Dict[str, float],
    ) -> np.ndarray:
        """
        Apply advanced prosody control to audio.

        Args:
            audio: Audio array
            sample_rate: Sample rate
            prosody_params: Prosody parameters:
                - pitch: Pitch shift in semitones (-12 to +12)
                - tempo: Tempo multiplier (0.5 to 2.0)
                - formant_shift: Formant shift factor (0.5 to 2.0)
                - energy: Energy boost (0.5 to 2.0)

        Returns:
            Modified audio array
        """
        if not HAS_LIBROSA:
            logger.warning("librosa required for prosody control, skipping")
            return audio

        try:
            modified_audio = audio.copy()

            # Pitch shifting
            if "pitch" in prosody_params:
                pitch_shift = prosody_params["pitch"]
                if abs(pitch_shift) > 0.01:  # Only if significant shift
                    modified_audio = librosa.effects.pitch_shift(
                        modified_audio, sr=sample_rate, n_steps=pitch_shift
                    )

            # Tempo modification
            if "tempo" in prosody_params:
                tempo = prosody_params["tempo"]
                if abs(tempo - 1.0) > 0.01:  # Only if significant change
                    modified_audio = librosa.effects.time_stretch(
                        modified_audio, rate=tempo
                    )

            # Formant shifting (spectral envelope modification)
            if "formant_shift" in prosody_params:
                formant_shift = prosody_params["formant_shift"]
                if abs(formant_shift - 1.0) > 0.01:
                    # Use phase vocoder for formant shifting
                    stft = librosa.stft(modified_audio)
                    # Shift formants by modifying spectral envelope
                    magnitude = np.abs(stft)
                    phase = np.angle(stft)

                    # Apply formant shift (simplified approach)
                    freqs = librosa.fft_frequencies(sr=sample_rate)
                    formant_region = (freqs > 500) & (freqs < 4000)
                    magnitude[formant_region, :] *= formant_shift

                    modified_audio = librosa.istft(magnitude * np.exp(1j * phase))

            # Energy adjustment
            if "energy" in prosody_params:
                energy = prosody_params["energy"]
                modified_audio = modified_audio * energy

            # Normalize to prevent clipping
            if np.max(np.abs(modified_audio)) > 0:
                modified_audio = modified_audio / np.max(np.abs(modified_audio)) * 0.95

            return modified_audio

        except Exception as e:
            logger.warning(f"Prosody control failed: {e}, returning original audio")
            return audio

    def batch_synthesize(
        self,
        texts: List[str],
        speaker_wav: Union[str, Path],
        language: str = "en",
        output_dir: Optional[Union[str, Path]] = None,
        batch_size: Optional[int] = None,
        parallel: bool = False,
        **kwargs,
    ) -> List[Optional[np.ndarray]]:
        """
        Synthesize multiple texts in batch with optimizations.

        Args:
            texts: List of texts to synthesize
            speaker_wav: Path to reference speaker audio
            language: Language code
            output_dir: Optional directory to save outputs
            batch_size: Batch size for processing (default: self._batch_size)
            parallel: If True, use parallel processing (experimental)
            **kwargs: Additional synthesis parameters

        Returns:
            List of audio arrays
        """
        if not texts:
            return []

        # Ensure initialized
        if not self._initialized:
            if not self._load_model():
                return [None] * len(texts)

        batch_size = batch_size or self._batch_size
        results = []

        # Optimize: Pre-process speaker_wav once
        if isinstance(speaker_wav, (str, Path)):
            speaker_wav = [str(speaker_wav)]
        speaker_wav = [str(path) for path in speaker_wav]

        # Process in batches for better memory management
        if batch_size > 1 and len(texts) > batch_size:
            logger.info(f"Processing {len(texts)} texts in batches of {batch_size}")

            for batch_start in range(0, len(texts), batch_size):
                batch_end = min(batch_start + batch_size, len(texts))
                batch_texts = texts[batch_start:batch_end]

                batch_results = []
                for i, text in enumerate(batch_texts):
                    output_path = None
                    if output_dir:
                        output_path = (
                            Path(output_dir) / f"output_{batch_start + i:04d}.wav"
                        )

                    # Use inference mode for batch processing
                    try:
                        with torch.inference_mode():
                            audio = self.synthesize(
                                text=text,
                                speaker_wav=speaker_wav,
                                language=language,
                                output_path=output_path,
                                **kwargs,
                            )
                        batch_results.append(audio)
                    except Exception as e:
                        logger.error(
                            f"Batch synthesis failed for text {batch_start + i}: {e}"
                        )
                        batch_results.append(None)

                results.extend(batch_results)

                # Clear GPU cache between batches if using GPU
                if self.device == "cuda" and torch.cuda.is_available():
                    torch.cuda.empty_cache()
        else:
            # Process sequentially (original behavior)
            for i, text in enumerate(texts):
                output_path = None
                if output_dir:
                    output_path = Path(output_dir) / f"output_{i:04d}.wav"

                audio = self.synthesize(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    output_path=output_path,
                    **kwargs,
                )
                results.append(audio)

        logger.info(f"Batch synthesis complete: {len(results)} results")
        return results

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported language codes.

        Returns:
            List of language codes
        """
        return [
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
        ]

    def cleanup(self, clear_cache: bool = False):
        """
        Clean up resources.

        Args:
            clear_cache: If True, also clear the global model cache
        """
        # Only delete model if not cached (cached models are shared)
        if self.tts is not None:
            cache_key = _get_cache_key(self.model_name, self.device)
            if cache_key not in _MODEL_CACHE:
                # Not cached, safe to delete
                del self.tts
            else:
                # Cached, just remove reference
                logger.debug("Model is cached, not deleting")
            self.tts = None
            self._initialized = False

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        if clear_cache:
            _MODEL_CACHE.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("XTTS model cache cleared")

        logger.info("XTTS Engine cleaned up")

    def set_batch_size(self, batch_size: int):
        """
        Set batch size for batch processing.

        Args:
            batch_size: Batch size (1 = sequential, >1 = batched)
        """
        self._batch_size = max(1, batch_size)
        logger.debug(f"Batch size set to {self._batch_size}")

    def enable_caching(self, enable: bool = True):
        """
        Enable or disable model caching.

        Args:
            enable: If True, enable caching; if False, disable
        """
        self._use_cache = enable
        logger.debug(f"Model caching {'enabled' if enable else 'disabled'}")

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current GPU memory usage if using CUDA.

        Returns:
            Dictionary with memory usage stats in MB
        """
        if not torch.cuda.is_available() or self.device != "cuda":
            return {"gpu_available": False}

        try:
            allocated = torch.cuda.memory_allocated() / 1024**2  # MB
            reserved = torch.cuda.memory_reserved() / 1024**2  # MB
            max_allocated = torch.cuda.max_memory_allocated() / 1024**2  # MB

            return {
                "gpu_available": True,
                "allocated_mb": allocated,
                "reserved_mb": reserved,
                "max_allocated_mb": max_allocated,
            }
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return {"gpu_available": True, "error": str(e)}


# Factory function for easy instantiation
def create_xtts_engine(
    model_name: str = XTTS_DEFAULT_MODEL_NAME,
    device: Optional[str] = None,
    gpu: bool = True,
) -> XTTSEngine:
    """
    Create and initialize XTTS engine.

    Args:
        model_name: XTTS model identifier
        device: Device to use
        gpu: Whether to use GPU

    Returns:
        Initialized XTTSEngine instance
    """
    engine = XTTSEngine(model_name=model_name, device=device, gpu=gpu)
    engine.initialize()
    return engine


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = create_xtts_engine()

    # Example: Clone voice and synthesize
    reference_audio = "path/to/reference.wav"
    text = "Hello, this is a test of voice cloning."

    audio = engine.clone_voice(
        reference_audio=reference_audio, text=text, language="en"
    )

    if audio is not None:
        print(f"Generated audio shape: {audio.shape}")

    # Cleanup
    engine.cleanup()
