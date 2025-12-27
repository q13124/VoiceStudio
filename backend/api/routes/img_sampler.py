"""
Image Sampler Routes

Endpoints for image sampling/rendering with different samplers
for diffusion models (DDIM, Euler, etc.).
"""

import base64
import logging
import os
import tempfile
import uuid
from io import BytesIO
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from PIL import Image

from ..models_additional import ImgSamplerRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/img/sampler", tags=["img", "sampler"])

# In-memory storage for sampled images
_image_storage: Dict[str, str] = {}  # image_id -> file_path

# Supported samplers
SUPPORTED_SAMPLERS = [
    "ddim",
    "ddpm",
    "euler",
    "euler_a",
    "heun",
    "dpm_2",
    "dpm_2_a",
    "lms",
    "plms",
    "dpm_fast",
    "dpm_adaptive",
    "dpmpp_2s_a",
    "dpmpp_2m",
    "dpmpp_sde",
    "uni_pc",
]


@router.post("/render")
async def render(req: ImgSamplerRequest) -> dict:
    """
    Render/sample an image using a diffusion model sampler.

    This endpoint uses image generation engines to create images
    with different sampling methods (DDIM, Euler, etc.).

    Args:
        req: Request with prompt and sampler type

    Returns:
        Dictionary with generated image as base64 data URL
    """
    try:
        prompt = req.prompt
        sampler = req.sampler.lower()

        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400, detail="prompt is required"
            )

        # Validate sampler
        if sampler not in SUPPORTED_SAMPLERS:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported sampler '{sampler}'. "
                    f"Supported: {', '.join(SUPPORTED_SAMPLERS)}"
                ),
            )

        # Try to use image generation engine
        try:
            # Import image generation route
            from ..models_additional import ImageGenerateRequest
            from .image_gen import generate_image

            # Create image generation request
            gen_req = ImageGenerateRequest(
                prompt=prompt,
                engine="sdxl_comfy",  # Default to SDXL ComfyUI
                width=512,
                height=512,
                num_inference_steps=20,
                guidance_scale=7.5,
                sampler=sampler,  # Pass sampler to generation
            )

            # Generate image
            gen_result = await generate_image(gen_req)

            # Get image path from result
            image_id = gen_result.image_id
            image_path = gen_result.image_path

            if image_path and os.path.exists(image_path):
                # Read image and convert to base64
                with open(image_path, "rb") as f:
                    image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode("utf-8")
                    mime_type = "image/png"
                    if image_path.lower().endswith(".jpg") or image_path.lower().endswith(
                        ".jpeg"
                    ):
                        mime_type = "image/jpeg"
                    elif image_path.lower().endswith(".webp"):
                        mime_type = "image/webp"

                    data_url = f"data:{mime_type};base64,{image_base64}"

                    logger.info(
                        f"Image sampled: prompt='{prompt[:50]}...', "
                        f"sampler={sampler}, image_id={image_id}"
                    )

                    return {
                        "image": data_url,
                        "image_id": image_id,
                        "sampler": sampler,
                        "prompt": prompt,
                    }
            else:
                # Fallback: create fallback image when generation unavailable
                logger.warning(
                    f"Image generation returned no path, "
                    f"creating fallback image for sampler={sampler}"
                )
                return _create_placeholder_image(prompt, sampler)

        except ImportError:
            # Image generation not available, create fallback image
            logger.warning(
                "Image generation engine not available, "
                "creating fallback image"
            )
            return _create_placeholder_image(prompt, sampler)
        except Exception as e:
            logger.error(
                f"Image generation failed: {e}, creating fallback image",
                exc_info=True,
            )
            # Fallback to fallback image on error
            return _create_placeholder_image(prompt, sampler)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image sampling failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Image sampling failed: {str(e)}"
        ) from e


def _create_placeholder_image(prompt: str, sampler: str) -> dict:
    """
    Create a fallback image when generation is not available.
    Generates a deterministic gradient image with text overlay.

    Args:
        prompt: Image prompt
        sampler: Sampler name

    Returns:
        Dictionary with fallback image as base64 data URL
    """
    try:
        import numpy as np

        # Create a simple placeholder image
        width, height = 512, 512
        # Create gradient background
        img_array = np.zeros((height, width, 3), dtype=np.uint8)

        # Create a simple gradient
        for y in range(height):
            for x in range(width):
                img_array[y, x] = [
                    int(255 * (x / width)),
                    int(255 * (y / height)),
                    int(255 * 0.5),
                ]

        # Convert to PIL Image
        img = Image.fromarray(img_array)

        # Add text overlay (if PIL supports it)
        try:
            from PIL import ImageDraw, ImageFont

            draw = ImageDraw.Draw(img)
            # Try to use default font
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except Exception:
                font = ImageFont.load_default()

            # Draw prompt text (truncated)
            text = f"Sampler: {sampler}\n{prompt[:40]}..."
            draw.text(
                (10, 10),
                text,
                fill=(255, 255, 255),
                font=font,
            )
        except Exception:
            # If text rendering fails, just use gradient
            pass

        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        data_url = f"data:image/png;base64,{image_base64}"

        # Generate image ID
        image_id = f"sampled_{uuid.uuid4().hex[:8]}"

        logger.info(
            f"Created fallback image: sampler={sampler}, "
            f"image_id={image_id}"
        )

        return {
            "image": data_url,
            "image_id": image_id,
            "sampler": sampler,
            "prompt": prompt,
            "generated": False,
        }

    except Exception as e:
        logger.error(f"Failed to create fallback image: {e}")
        # Ultimate fallback: return empty base64 image
        # 1x1 transparent PNG
        empty_png = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        return {
            "image": f"data:image/png;base64,{empty_png}",
            "image_id": f"sampled_{uuid.uuid4().hex[:8]}",
            "sampler": sampler,
            "prompt": prompt,
            "generated": False,
        }


@router.get("/samplers")
async def list_samplers() -> dict:
    """List all supported image samplers."""
    return {
        "samplers": SUPPORTED_SAMPLERS,
        "count": len(SUPPORTED_SAMPLERS),
        "default": "ddim",
    }


@router.get("/samplers/{sampler_name}")
async def get_sampler_info(sampler_name: str) -> dict:
    """Get information about a specific sampler."""
    sampler = sampler_name.lower()

    if sampler not in SUPPORTED_SAMPLERS:
        raise HTTPException(
            status_code=404,
            detail=f"Sampler '{sampler_name}' not found",
        )

    # Sampler descriptions
    descriptions = {
        "ddim": "Denoising Diffusion Implicit Models - Fast, deterministic",
        "ddpm": "Denoising Diffusion Probabilistic Models - Original method",
        "euler": "Euler method - Fast, good quality",
        "euler_a": "Euler Ancestral - Stochastic variant",
        "heun": "Heun's method - More accurate than Euler",
        "dpm_2": "DPM-Solver-2 - Fast and accurate",
        "dpm_2_a": "DPM-Solver-2 Ancestral - Stochastic variant",
        "lms": "Linear Multi-Step - Stable, good quality",
        "plms": "Pseudo Linear Multi-Step - Fast variant",
        "dpm_fast": "DPM Fast - Very fast, lower quality",
        "dpm_adaptive": "DPM Adaptive - Adaptive step size",
        "dpmpp_2s_a": "DPM++ 2S Ancestral - High quality",
        "dpmpp_2m": "DPM++ 2M - Fast and high quality",
        "dpmpp_sde": "DPM++ SDE - Stochastic Differential Equation",
        "uni_pc": "UniPC - Unified Predictor-Corrector",
    }

    return {
        "name": sampler,
        "description": descriptions.get(sampler, "No description available"),
        "type": "deterministic" if "a" not in sampler else "stochastic",
    }
