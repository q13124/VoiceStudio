"""
Parler-TTS Engine Integration.

Task 4.4.3: High-quality expressive TTS.
Natural prosody and expression through text descriptions.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.core.engines.base import EngineProtocol

logger = logging.getLogger(__name__)


@dataclass
class ParlerTTSConfig:
    """Configuration for Parler-TTS."""

    model_name: str = "parler-tts/parler-tts-mini-v1"
    use_gpu: bool = True
    sample_rate: int = 44100
    max_length: int = 2048


class ParlerTTSEngine(EngineProtocol):
    """
    Parler-TTS expressive text-to-speech.

    Features:
    - Text-described voice control
    - Natural prosody
    - High-quality 44.1kHz output
    - Controllable style via descriptions

    Reference: https://github.com/huggingface/parler-tts
    """

    ENGINE_ID = "parler_tts"
    ENGINE_NAME = "Parler-TTS"
    SUPPORTED_LANGUAGES = ["en"]

    def __init__(self, config: ParlerTTSConfig | None = None):
        super().__init__()
        self.config = config or ParlerTTSConfig()
        self._model = None
        self._tokenizer = None
        self._loaded = False

    def initialize(self) -> bool:
        """Sync wrapper for EngineProtocol compliance."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self._async_initialize())
        finally:
            loop.close()

    def cleanup(self) -> None:
        """Sync wrapper for EngineProtocol compliance."""
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.shutdown())
        finally:
            loop.close()

    async def _async_initialize(self) -> bool:
        """Initialize Parler-TTS."""
        try:
            logger.info("Loading Parler-TTS engine...")

            try:
                import torch
                from parler_tts import ParlerTTSForConditionalGeneration
                from transformers import AutoTokenizer

                device = "cuda" if self.config.use_gpu and torch.cuda.is_available() else "cpu"

                self._model = ParlerTTSForConditionalGeneration.from_pretrained(
                    self.config.model_name
                ).to(device)

                self._tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
                self._device = device

                logger.info(f"Parler-TTS loaded on {device}")

            except ImportError:
                logger.warning("parler-tts not installed, using placeholder")
                self._model = None

            self._loaded = True
            return True

        except Exception as e:
            logger.error(f"Failed to load Parler-TTS: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown and cleanup."""
        self._model = None
        self._tokenizer = None
        self._loaded = False

        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            logger.debug("torch not available for CUDA cache cleanup")

    async def synthesize(
        self,
        text: str,
        description: str = "A female speaker with a clear and natural voice.",
    ) -> np.ndarray:
        """
        Synthesize speech with style description.

        Args:
            text: Text to synthesize
            description: Voice style description

        Returns:
            Synthesized audio at 44.1kHz
        """
        if not self._loaded:
            await self.initialize()

        if self._model is not None and self._tokenizer is not None:
            return await self._synthesize_real(text, description)

        # Graceful degradation: Generate silence when parler-tts library is not installed.
        # To enable full functionality, install parler-tts: pip install parler-tts
        # See: https://github.com/huggingface/parler-tts for installation instructions.
        logger.warning(
            "Parler-TTS model not loaded - returning silence. Install parler-tts for actual synthesis."
        )
        duration = len(text) * 0.06
        samples = int(duration * self.config.sample_rate)
        return np.zeros(samples, dtype=np.float32)

    async def _synthesize_real(self, text: str, description: str) -> np.ndarray:
        """Real synthesis using Parler-TTS."""
        import torch

        # Tokenize
        input_ids = self._tokenizer(description, return_tensors="pt").input_ids.to(self._device)
        prompt_input_ids = self._tokenizer(text, return_tensors="pt").input_ids.to(self._device)

        # Generate
        with torch.no_grad():
            generation = self._model.generate(
                input_ids=input_ids,
                prompt_input_ids=prompt_input_ids,
                max_new_tokens=self.config.max_length,
            )

        audio = generation.cpu().numpy().squeeze()
        return audio.astype(np.float32)

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "description_control": True,
            "languages": self.SUPPORTED_LANGUAGES,
            "sample_rate": self.config.sample_rate,
            "expressive": True,
        }


# Example descriptions for different styles
VOICE_DESCRIPTIONS = {
    "professional_female": "A professional female speaker with a clear, confident, and warm voice.",
    "professional_male": "A professional male speaker with a deep, authoritative, and calm voice.",
    "young_female": "A young woman with an energetic, friendly, and cheerful voice.",
    "young_male": "A young man with a casual, upbeat, and engaging voice.",
    "narrator": "A narrator with a smooth, expressive voice perfect for storytelling.",
    "news_anchor": "A news anchor with a neutral, clear, and steady voice.",
    "excited": "An excited speaker with high energy, fast pace, and enthusiasm.",
    "calm": "A calm speaker with a slow, soothing, and peaceful voice.",
}
