"""
SD.Next Engine for VoiceStudio
Advanced AUTOMATIC1111 fork integration

SD.Next is an advanced fork of AUTOMATIC1111 WebUI with additional
features, optimizations, and improvements.

Compatible with:
- Python 3.10+
- SD.Next server (requires separate installation)
- HTTP API for image generation
"""

from __future__ import annotations

import base64
import logging
import os
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

logger = logging.getLogger(__name__)

# Import base protocol from canonical source
from .base import EngineProtocol


class SDNextEngine(EngineProtocol):
    """
    SD.Next Engine for advanced Stable Diffusion image generation.

    Supports:
    - All AUTOMATIC1111 features
    - Additional optimizations
    - Enhanced performance
    - Extended API features
    """

    SUPPORTED_FORMATS = ["png", "jpg", "webp"]

    def __init__(
        self,
        webui_url: str = "http://127.0.0.1:7860",
        api_endpoint: str = "/sdapi/v1",
        sampler: str = "Euler a",
        steps: int = 20,
        cfg_scale: float = 7.0,
        device: str | None = None,
        gpu: bool = True,
    ):
        """Initialize SD.Next engine."""
        super().__init__(device=device, gpu=gpu)

        self.webui_url = webui_url.rstrip("/")
        self.api_endpoint = api_endpoint.rstrip("/")
        self.api_url = f"{self.webui_url}{self.api_endpoint}"
        self.default_sampler = sampler
        self.default_steps = steps
        self.default_cfg_scale = cfg_scale
        self.session = requests.Session()
        self.session.timeout = 300

    def initialize(self) -> bool:
        """Initialize the SD.Next engine by connecting to server."""
        try:
            if self._initialized:
                return True

            logger.info(f"Connecting to SD.Next server: {self.webui_url}")

            try:
                response = self.session.get(f"{self.api_url}/options", timeout=5)
                if response.status_code == 200:
                    logger.info("SD.Next server connection successful")
                    self._initialized = True
                    return True
                else:
                    logger.error(f"SD.Next server returned status {response.status_code}")
                    self._initialized = False
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to connect to SD.Next server: {e}")
                logger.error(f"Make sure SD.Next server is running at {self.webui_url}")
                logger.error("Install from: https://github.com/vladmandic/automatic")
                self._initialized = False
                return False

        except Exception as e:
            logger.error(f"Failed to initialize SD.Next engine: {e}")
            self._initialized = False
            return False

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int | None = None,
        cfg_scale: float | None = None,
        sampler: str | None = None,
        seed: int | None = None,
        output_path: str | Path | None = None,
        **kwargs,
    ) -> Image.Image | None | tuple[Image.Image | None, dict]:
        """Generate image using SD.Next (same API as AUTOMATIC1111)."""
        if not self._initialized and not self.initialize():
            return None

        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps if steps is not None else self.default_steps,
                "cfg_scale": (cfg_scale if cfg_scale is not None else self.default_cfg_scale),
                "sampler_name": sampler if sampler else self.default_sampler,
                "seed": seed if seed is not None else -1,
                "batch_size": 1,
                "n_iter": 1,
            }

            if "image" in kwargs:
                image_input = kwargs["image"]
                if isinstance(image_input, str):
                    if os.path.exists(image_input):
                        with open(image_input, "rb") as f:
                            image_data = base64.b64encode(f.read()).decode("utf-8")
                    else:
                        image_data = image_input
                elif isinstance(image_input, Image.Image):
                    buffer = BytesIO()
                    image_input.save(buffer, format="PNG")
                    image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
                else:
                    image_data = str(image_input)

                payload["init_images"] = [image_data]
                payload["denoising_strength"] = kwargs.get("denoising_strength", 0.7)
                endpoint = f"{self.api_url}/img2img"
            else:
                endpoint = f"{self.api_url}/txt2img"

            if "mask" in kwargs:
                mask_input = kwargs["mask"]
                if isinstance(mask_input, str):
                    if os.path.exists(mask_input):
                        with open(mask_input, "rb") as f:
                            mask_data = base64.b64encode(f.read()).decode("utf-8")
                    else:
                        mask_data = mask_input
                elif isinstance(mask_input, Image.Image):
                    buffer = BytesIO()
                    mask_input.save(buffer, format="PNG")
                    mask_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
                else:
                    mask_data = str(mask_input)

                payload["mask"] = mask_data
                payload["inpainting_fill"] = kwargs.get("inpainting_fill", 1)
                payload["inpaint_full_res"] = kwargs.get("inpaint_full_res", False)

            if "controlnet" in kwargs:
                payload["alwayson_scripts"] = {"controlnet": {"args": [kwargs["controlnet"]]}}

            response = self.session.post(endpoint, json=payload, timeout=300)

            if response.status_code != 200:
                logger.error(f"SD.Next generation failed: {response.text}")
                return None

            result = response.json()

            if "images" in result and len(result["images"]) > 0:
                image_data = result["images"][0]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))

                if output_path:
                    image.save(output_path)
                    logger.info(f"Image saved to: {output_path}")
                    return image

                return image
            else:
                logger.error("No images in response")
                return None

        except Exception as e:
            logger.error(f"SD.Next generation failed: {e}")
            return None

    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, "session"):
                self.session.close()
            self._initialized = False
            logger.info("SD.Next engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def get_info(self) -> dict:
        """Get engine information."""
        info = super().get_info()
        info.update(
            {
                "webui_url": self.webui_url,
                "api_endpoint": self.api_endpoint,
                "default_sampler": self.default_sampler,
                "default_steps": self.default_steps,
                "default_cfg_scale": self.default_cfg_scale,
                "supported_formats": self.SUPPORTED_FORMATS,
            }
        )
        return info


def create_sdnext_engine(
    webui_url: str = "http://127.0.0.1:7860",
    api_endpoint: str = "/sdapi/v1",
    sampler: str = "Euler a",
    steps: int = 20,
    cfg_scale: float = 7.0,
    device: str | None = None,
    gpu: bool = True,
) -> SDNextEngine:
    """Factory function to create an SD.Next engine instance."""
    return SDNextEngine(
        webui_url=webui_url,
        api_endpoint=api_endpoint,
        sampler=sampler,
        steps=steps,
        cfg_scale=cfg_scale,
        device=device,
        gpu=gpu,
    )
