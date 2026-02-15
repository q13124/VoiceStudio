"""
Tacotron 2 TTS Engine for VoiceStudio.

Implements Tacotron 2 speech synthesis via Coqui TTS.
Provides fast, high-quality TTS with multi-language support.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from app.core.engines.base import EngineProtocol, traced

logger = logging.getLogger(__name__)

# Available Tacotron 2 models via Coqui TTS
AVAILABLE_MODELS = {
    "en": "tts_models/en/ljspeech/tacotron2-DDC",
    "en_vctk": "tts_models/en/vctk/tacotron2-DDC",
    "de": "tts_models/de/thorsten/tacotron2-DDC",
    "fr": "tts_models/fr/mai/tacotron2-DDC",
    "es": "tts_models/es/mai/tacotron2-DDC",
    "it": "tts_models/it/mai_female/tacotron2-DDC",
    "pt": "tts_models/pt/cv/tacotron2-DDC",
    "pl": "tts_models/pl/mai_female/tacotron2-DDC",
    "tr": "tts_models/tr/common-voice/tacotron2-DDC",
    "ru": "tts_models/ru/ruslan/tacotron2-DDC",
}

# Supported languages
SUPPORTED_LANGUAGES = list(AVAILABLE_MODELS.keys())


class Tacotron2Engine(EngineProtocol):
    """
    Tacotron 2 TTS engine via Coqui TTS.

    Provides fast, high-quality text-to-speech synthesis with support
    for multiple languages using pre-trained Tacotron 2 models.

    Features:
    - Multi-language support (en, de, fr, es, it, pt, pl, tr, ru)
    - Fast inference on both CPU and GPU
    - High-quality synthesis with DDC vocoder
    - Consistent interface via EngineProtocol
    """

    ENGINE_ID = "tacotron2"
    SUPPORTED_LANGUAGES = SUPPORTED_LANGUAGES

    def __init__(
        self,
        device: str | None = None,
        gpu: bool = True,
        model_name: str | None = None,
    ):
        """
        Initialize Tacotron 2 engine.

        Args:
            device: Device to use ('cuda', 'cpu', or None for auto).
            gpu: Whether to use GPU if available.
            model_name: Coqui TTS model identifier (default: English LJSpeech).
        """
        super().__init__(device=device, gpu=gpu)
        self._tts = None
        self._model_name = model_name or AVAILABLE_MODELS["en"]
        self._current_language = "en"
        self._sample_rate = 22050  # Tacotron 2 default

    @traced(operation_name="tacotron2_initialize")
    def initialize(self) -> bool:
        """
        Initialize the Tacotron 2 model via Coqui TTS.

        Returns:
            True if initialization successful, False otherwise.
        """
        if self._initialized:
            logger.info("Tacotron2Engine already initialized")
            return True

        try:
            from TTS.api import TTS

            use_gpu = self.device == "cuda"
            logger.info(
                "Initializing Tacotron 2 with model=%s, gpu=%s",
                self._model_name,
                use_gpu,
            )

            self._tts = TTS(model_name=self._model_name, gpu=use_gpu)
            self._sample_rate = getattr(
                self._tts.synthesizer.output_sample_rate,
                "item",
                lambda: self._tts.synthesizer.output_sample_rate
            )() if hasattr(self._tts, "synthesizer") else 22050

            self._initialized = True
            logger.info(
                "Tacotron2Engine initialized successfully (sample_rate=%d)",
                self._sample_rate,
            )
            return True

        except ImportError as e:
            logger.error("Coqui TTS not installed: %s", e)
            return False
        except Exception as e:
            logger.error("Failed to initialize Tacotron 2: %s", e)
            return False

    @traced(operation_name="tacotron2_synthesize")
    def synthesize(
        self,
        text: str,
        output_path: str | None = None,
        language: str = "en",
        speaker_idx: int | None = None,
        **kwargs: Any,
    ) -> np.ndarray:
        """
        Synthesize speech from text.

        Args:
            text: Input text to synthesize.
            output_path: Optional path to save WAV file.
            language: Language code (en, de, fr, es, it, pt, pl, tr, ru).
            speaker_idx: Speaker index for multi-speaker models.
            **kwargs: Additional synthesis parameters.

        Returns:
            Audio data as numpy array (float32, mono).

        Raises:
            RuntimeError: If engine not initialized.
            ValueError: If language not supported.
        """
        if not self._initialized or self._tts is None:
            raise RuntimeError("Tacotron2Engine not initialized. Call initialize() first.")

        # Check cancellation
        token = kwargs.get("cancellation_token")
        if token:
            self._current_cancellation_token = token
            token.raise_if_cancelled()

        # Switch model if language changed
        if language != self._current_language:
            if language not in AVAILABLE_MODELS:
                raise ValueError(
                    f"Language '{language}' not supported. "
                    f"Available: {', '.join(SUPPORTED_LANGUAGES)}"
                )
            self._switch_language(language)

        logger.debug(
            "Synthesizing text (length=%d, language=%s)",
            len(text),
            language,
        )

        try:
            # Perform synthesis
            if output_path:
                # Synthesize directly to file
                self._tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker=speaker_idx,
                )
                # Also return the audio data
                audio = self._tts.tts(text=text, speaker=speaker_idx)
            else:
                audio = self._tts.tts(text=text, speaker=speaker_idx)

            # Convert to numpy array if needed
            if not isinstance(audio, np.ndarray):
                audio = np.array(audio, dtype=np.float32)

            # Check cancellation after synthesis
            if token:
                token.raise_if_cancelled()

            logger.debug("Synthesis complete (samples=%d)", len(audio))
            return audio

        except Exception as e:
            logger.error("Synthesis failed: %s", e)
            raise

    def _switch_language(self, language: str) -> None:
        """
        Switch to a different language model.

        Args:
            language: Language code to switch to.
        """
        from TTS.api import TTS

        model_name = AVAILABLE_MODELS[language]
        logger.info("Switching Tacotron 2 model to %s", model_name)

        use_gpu = self.device == "cuda"
        self._tts = TTS(model_name=model_name, gpu=use_gpu)
        self._model_name = model_name
        self._current_language = language

    @traced(operation_name="tacotron2_cleanup")
    def cleanup(self) -> None:
        """Clean up resources and free memory."""
        if self._tts is not None:
            logger.info("Cleaning up Tacotron2Engine resources")
            self._tts = None
            self._initialized = False
            self.cleanup_gpu_memory()
            logger.info("Tacotron2Engine cleanup complete")

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        return SUPPORTED_LANGUAGES.copy()

    def get_available_models(self) -> dict[str, str]:
        """Get dictionary of available models by language."""
        return AVAILABLE_MODELS.copy()

    def get_sample_rate(self) -> int:
        """Get output sample rate in Hz."""
        return self._sample_rate

    def synthesize_stream(
        self,
        text: str,
        language: str = "en",
        chunk_size: int = 4800,
        **kwargs: Any,
    ):
        """
        Stream synthesized audio in chunks.

        D.3 Enhancement: Streaming synthesis support for Tacotron 2.

        Args:
            text: Input text to synthesize.
            language: Language code.
            chunk_size: Size of each audio chunk in samples.
            **kwargs: Additional parameters.

        Yields:
            Audio chunks as numpy arrays.
        """
        if not self._initialized or self._tts is None:
            raise RuntimeError("Tacotron2Engine not initialized. Call initialize() first.")

        # Switch model if language changed
        if language != self._current_language:
            if language not in AVAILABLE_MODELS:
                raise ValueError(
                    f"Language '{language}' not supported. "
                    f"Available: {', '.join(SUPPORTED_LANGUAGES)}"
                )
            self._switch_language(language)

        logger.debug("Starting streaming synthesis (length=%d)", len(text))

        try:
            # Synthesize full audio first, then stream in chunks
            # (Tacotron 2 doesn't support true streaming, so we simulate it)
            audio = self._tts.tts(text=text)

            if not isinstance(audio, np.ndarray):
                audio = np.array(audio, dtype=np.float32)

            # Yield audio in chunks
            for i in range(0, len(audio), chunk_size):
                yield audio[i:i + chunk_size]

        except Exception as e:
            logger.error("Streaming synthesis failed: %s", e)
            raise

    def get_info(self) -> dict[str, Any]:
        """Get engine information."""
        base_info = super().get_info()
        base_info.update({
            "engine_id": self.ENGINE_ID,
            "model_name": self._model_name,
            "current_language": self._current_language,
            "supported_languages": self.get_supported_languages(),
            "sample_rate": self._sample_rate,
            "capabilities": [
                "tts",
                "multi_language",
                "fast_inference",
            ],
        })
        return base_info

    def health_check(self) -> bool:
        """
        Check if engine is healthy and ready for synthesis.

        Returns:
            True if engine is ready, False otherwise.
        """
        return not (not self._initialized or self._tts is None)

    def get_health_details(self) -> dict[str, Any]:
        """
        Get detailed health status.

        Returns:
            Dictionary with health status details.
        """
        return {
            "healthy": self.health_check(),
            "initialized": self._initialized,
            "model_loaded": self._tts is not None,
            "device": self.device,
            "model_name": self._model_name,
            "current_language": self._current_language,
        }
