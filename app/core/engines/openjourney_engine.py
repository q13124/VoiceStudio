"""
OpenJourney Engine for VoiceStudio
Midjourney-style Stable Diffusion model integration

OpenJourney is a Stable Diffusion model trained to generate
Midjourney-style artistic images.

Compatible with:
- Python 3.10+
- diffusers library
- PyTorch 2.0+
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import torch
from PIL import Image

logger = logging.getLogger(__name__)

try:
    from diffusers import StableDiffusionPipeline

    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False
    logger.warning(
        "diffusers not installed. Install with: pip install diffusers>=0.21.0"
    )

# Import base protocol from canonical source
from .base import EngineProtocol


class OpenJourneyEngine(EngineProtocol):
    """OpenJourney Engine for Midjourney-style artistic image generation."""

    SUPPORTED_FORMATS = ["png", "jpg", "webp"]
    MODEL_VERSIONS = {
        "v1": "prompthero/openjourney",
        "v2": "prompthero/openjourney-v2",
        "v3": "prompthero/openjourney-v3",
        "v4": "prompthero/openjourney-v4",
    }

    def __init__(
        self,
        model_id: str | None = None,
        version: str = "v4",
        device: str | None = None,
        gpu: bool = True,
    ):
        """Initialize OpenJourney engine."""
        super().__init__(device=device, gpu=gpu)

        if not HAS_DIFFUSERS:
            raise ImportError("diffusers library not installed")

        if gpu and torch.cuda.is_available() and self.device == "cpu":
            self.device = "cuda"

        self.model_id = model_id or self.MODEL_VERSIONS.get(
            version, "prompthero/openjourney-v4"
        )
        self.version = version
        self.pipe = None

    def initialize(self) -> bool:
        """Initialize the OpenJourney model."""
        try:
            if self._initialized:
                return True

            logger.info(
                f"Loading OpenJourney model: {self.model_id} (device: {self.device})"
            )

            model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
            if not model_cache_dir:
                model_cache_dir = os.path.join(
                    os.getenv("PROGRAMDATA", "C:\\ProgramData"),
                    "VoiceStudio",
                    "models",
                    "openjourney",
                )
            os.makedirs(model_cache_dir, exist_ok=True)

            try:
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=(
                        torch.float16 if self.device == "cuda" else torch.float32
                    ),
                    cache_dir=model_cache_dir,
                )
                self.pipe = self.pipe.to(self.device)
                self._initialized = True
                logger.info("OpenJourney engine initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to load OpenJourney model: {e}")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize OpenJourney engine: {e}")
            self._initialized = False
            return False

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        sampler: str | None = None,
        seed: int | None = None,
        output_path: str | Path | None = None,
        **kwargs,
    ) -> Image.Image | None | tuple[Image.Image | None, dict]:
        """Generate Midjourney-style artistic image."""
        if not self._initialized and not self.initialize():
            return None

        try:
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)

            images = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=cfg_scale,
                generator=generator,
                **kwargs,
            ).images

            if not images:
                return None

            image = images[0]

            if output_path:
                image.save(output_path)
                logger.info(f"Image saved to: {output_path}")
                return image

            return image

        except Exception as e:
            logger.error(f"OpenJourney generation failed: {e}")
            return None

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.pipe is not None:
                del self.pipe
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self._initialized = False
            logger.info("OpenJourney engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def get_info(self) -> dict:
        """Get engine information."""
        info = super().get_info()
        info.update(
            {
                "model_id": self.model_id,
                "version": self.version,
                "supported_formats": self.SUPPORTED_FORMATS,
            }
        )
        return info


def create_openjourney_engine(
    model_id: str | None = None,
    version: str = "v4",
    device: str | None = None,
    gpu: bool = True,
) -> OpenJourneyEngine:
    """Factory function to create an OpenJourney engine instance."""
    return OpenJourneyEngine(model_id=model_id, version=version, device=device, gpu=gpu)
