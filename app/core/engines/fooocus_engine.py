"""
Fooocus Engine for VoiceStudio
Simplified quality-focused Stable Diffusion interface integration

Fooocus is a simplified, quality-focused interface for Stable Diffusion
that prioritizes ease of use and high-quality results.

Compatible with:
- Python 3.10+
- Fooocus server (requires separate installation)
- HTTP API for image generation
"""

import os
import requests
import base64
from typing import Optional, Dict, List, Tuple, Union
from pathlib import Path
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

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
            def initialize(self): pass
            @abstractmethod
            def cleanup(self): pass
            def is_initialized(self): return self._initialized
            def get_device(self): return self.device


class FooocusEngine(EngineProtocol):
    """
    Fooocus Engine for simplified, quality-focused image generation.
    
    Supports:
    - Text-to-image generation
    - High-quality defaults
    - Simplified API
    - Automatic quality optimization
    """
    
    SUPPORTED_FORMATS = ["png", "jpg", "webp"]
    
    def __init__(
        self,
        server_url: str = "http://127.0.0.1:7860",
        device: Optional[str] = None,
        gpu: bool = True
    ):
        """Initialize Fooocus engine."""
        super().__init__(device=device, gpu=gpu)
        
        self.server_url = server_url.rstrip('/')
        self.api_url = f"{self.server_url}/v1"
        self.session = requests.Session()
        self.session.timeout = 300
    
    def initialize(self) -> bool:
        """Initialize the Fooocus engine by connecting to server."""
        try:
            if self._initialized:
                return True
            
            logger.info(f"Connecting to Fooocus server: {self.server_url}")
            
            try:
                # Fooocus typically uses /v1/engines endpoint
                response = self.session.get(f"{self.api_url}/engines", timeout=5)
                if response.status_code == 200:
                    logger.info("Fooocus server connection successful")
                    self._initialized = True
                    return True
                else:
                    # Try alternative endpoint
                    response = self.session.get(f"{self.server_url}/", timeout=5)
                    if response.status_code == 200:
                        logger.info("Fooocus server connection successful (via root)")
                        self._initialized = True
                        return True
                    else:
                        logger.error(f"Fooocus server returned status {response.status_code}")
                        self._initialized = False
                        return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to connect to Fooocus server: {e}")
                logger.error(f"Make sure Fooocus server is running at {self.server_url}")
                logger.error("Install from: https://github.com/lllyasviel/Fooocus")
                self._initialized = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Fooocus engine: {e}")
            self._initialized = False
            return False
    
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        sampler: Optional[str] = None,
        seed: Optional[int] = None,
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Union[Optional[Image.Image], Tuple[Optional[Image.Image], Dict]]:
        """Generate image using Fooocus."""
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            # Fooocus uses a simplified API
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_images": 1
            }
            
            if steps is not None:
                payload["steps"] = steps
            if cfg_scale is not None:
                payload["cfg_scale"] = cfg_scale
            if seed is not None:
                payload["seed"] = seed
            
            # Try /v1/images/generations endpoint (OpenAI-compatible)
            endpoint = f"{self.api_url}/images/generations"
            response = self.session.post(endpoint, json=payload, timeout=300)
            
            if response.status_code != 200:
                # Try alternative endpoint
                endpoint = f"{self.server_url}/api/v1/txt2img"
                response = self.session.post(endpoint, json=payload, timeout=300)
            
            if response.status_code != 200:
                logger.error(f"Fooocus generation failed: {response.text}")
                return None
            
            result = response.json()
            
            # Extract image from response (format may vary)
            image = None
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0].get("url") or result["data"][0].get("b64_json")
                if image_data:
                    if image_data.startswith("data:image"):
                        image_data = image_data.split(",")[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
            elif "images" in result and len(result["images"]) > 0:
                image_data = result["images"][0]
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                else:
                    image = Image.open(BytesIO(image_data))
            
            if image:
                if output_path:
                    image.save(output_path)
                    logger.info(f"Image saved to: {output_path}")
                    return image
                return image
            else:
                logger.error("No images in response")
                return None
            
        except Exception as e:
            logger.error(f"Fooocus generation failed: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'session'):
                self.session.close()
            self._initialized = False
            logger.info("Fooocus engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def get_info(self) -> Dict:
        """Get engine information."""
        info = super().get_info()
        info.update({
            "server_url": self.server_url,
            "supported_formats": self.SUPPORTED_FORMATS
        })
        return info


def create_fooocus_engine(
    server_url: str = "http://127.0.0.1:7860",
    device: Optional[str] = None,
    gpu: bool = True
) -> FooocusEngine:
    """Factory function to create a Fooocus engine instance."""
    return FooocusEngine(server_url=server_url, device=device, gpu=gpu)

