"""
Realistic Vision Engine for VoiceStudio
High-quality photorealistic Stable Diffusion model integration

Realistic Vision is a Stable Diffusion model optimized for
photorealistic image generation.

Compatible with:
- Python 3.10+
- diffusers library
- PyTorch 2.0+
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

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


class RealisticVisionEngine(EngineProtocol):
    """Realistic Vision Engine for photorealistic image generation."""

    SUPPORTED_FORMATS = ["png", "jpg", "webp"]

    def __init__(
        self,
        model_id: str = "SG161222/Realistic_Vision_V5.1_noVAE",
        vae: Optional[str] = None,
        device: Optional[str] = None,
        gpu: bool = True,
    ):
        """Initialize Realistic Vision engine."""
        super().__init__(device=device, gpu=gpu)

        if not HAS_DIFFUSERS:
            raise ImportError("diffusers library not installed")

        if gpu and torch.cuda.is_available() and self.device == "cpu":
            self.device = "cuda"

        self.model_id = model_id
        self.vae = vae
        self.pipe = None

    def initialize(self) -> bool:
        """Initialize the Realistic Vision model."""
        try:
            if self._initialized:
                return True

            logger.info(
                f"Loading Realistic Vision model: {self.model_id} (device: {self.device})"
            )

            model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
            if not model_cache_dir:
                model_cache_dir = os.path.join(
                    os.getenv("PROGRAMDATA", "C:\\ProgramData"),
                    "VoiceStudio",
                    "models",
                    "realistic_vision",
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
                if self.vae:
                    from diffusers import AutoencoderKL

                    vae_model = AutoencoderKL.from_pretrained(
                        self.vae, cache_dir=model_cache_dir
                    )
                    self.pipe.vae = vae_model
                self.pipe = self.pipe.to(self.device)
                self._initialized = True
                logger.info("Realistic Vision engine initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to load Realistic Vision model: {e}")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Realistic Vision engine: {e}")
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
        sampler: Optional[str] = None,
        seed: Optional[int] = None,
        output_path: Optional[Union[str, Path]] = None,
        **kwargs,
    ) -> Union[Optional[Image.Image], Tuple[Optional[Image.Image], Dict]]:
        """Generate photorealistic image."""
        if not self._initialized:
            if not self.initialize():
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
            logger.error(f"Realistic Vision generation failed: {e}")
            return None

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.pipe is not None:
                del self.pipe
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self._initialized = False
            logger.info("Realistic Vision engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def get_info(self) -> Dict:
        """Get engine information."""
        info = super().get_info()
        info.update(
            {
                "model_id": self.model_id,
                "vae": self.vae,
                "supported_formats": self.SUPPORTED_FORMATS,
            }
        )
        return info


def create_realistic_vision_engine(
    model_id: str = "SG161222/Realistic_Vision_V5.1_noVAE",
    vae: Optional[str] = None,
    device: Optional[str] = None,
    gpu: bool = True,
) -> RealisticVisionEngine:
    """Factory function to create a Realistic Vision engine instance."""
    return RealisticVisionEngine(model_id=model_id, vae=vae, device=device, gpu=gpu)
