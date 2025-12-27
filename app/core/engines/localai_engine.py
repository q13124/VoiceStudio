"""
LocalAI Engine for VoiceStudio
Local inference server for AI models integration

LocalAI is a local inference server that provides OpenAI-compatible
APIs for various AI models including Stable Diffusion.

Compatible with:
- Python 3.10+
- LocalAI server (requires separate installation)
- HTTP API compatible with OpenAI format
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


class LocalAIEngine(EngineProtocol):
    """
    LocalAI Engine for local inference server image generation.
    
    Supports:
    - Text-to-image generation
    - Image-to-image transformation
    - Multiple model support
    - OpenAI-compatible API
    - Local inference
    """
    
    SUPPORTED_FORMATS = ["png", "jpg", "webp"]
    
    def __init__(
        self,
        server_url: str = "http://127.0.0.1:8080",
        model_name: str = "stable-diffusion",
        device: Optional[str] = None,
        gpu: bool = True
    ):
        """Initialize LocalAI engine."""
        super().__init__(device=device, gpu=gpu)
        
        self.server_url = server_url.rstrip('/')
        self.model_name = model_name
        self.api_url = f"{self.server_url}/v1"
        self.session = requests.Session()
        self.session.timeout = 300
    
    def initialize(self) -> bool:
        """Initialize the LocalAI engine by connecting to server."""
        try:
            if self._initialized:
                return True
            
            logger.info(f"Connecting to LocalAI server: {self.server_url}")
            
            try:
                # Check if server is running
                response = self.session.get(f"{self.server_url}/ready", timeout=5)
                if response.status_code == 200:
                    logger.info("LocalAI server connection successful")
                    self._initialized = True
                    return True
                else:
                    logger.error(f"LocalAI server returned status {response.status_code}")
                    self._initialized = False
                    return False
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to connect to LocalAI server: {e}")
                logger.error(f"Make sure LocalAI server is running at {self.server_url}")
                logger.error("Install from: https://github.com/go-skynet/LocalAI")
                self._initialized = False
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize LocalAI engine: {e}")
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
        **kwargs
    ) -> Union[Optional[Image.Image], Tuple[Optional[Image.Image], Dict]]:
        """Generate image using LocalAI (OpenAI-compatible API)."""
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            # LocalAI uses OpenAI-compatible format
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "num_images": 1
            }
            
            if seed is not None:
                payload["seed"] = seed
            
            endpoint = f"{self.api_url}/images/generations"
            response = self.session.post(endpoint, json=payload, timeout=300)
            
            if response.status_code != 200:
                logger.error(f"LocalAI generation failed: {response.text}")
                return None
            
            result = response.json()
            
            # Extract image from OpenAI-compatible response
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0].get("url") or result["data"][0].get("b64_json")
                if image_data:
                    if image_data.startswith("data:image"):
                        image_data = image_data.split(",")[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    
                    if output_path:
                        image.save(output_path)
                        logger.info(f"Image saved to: {output_path}")
                        return image
                    
                    return image
            
            logger.error("No images in response")
            return None
            
        except Exception as e:
            logger.error(f"LocalAI generation failed: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if hasattr(self, 'session'):
                self.session.close()
            self._initialized = False
            logger.info("LocalAI engine cleaned up")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    def get_info(self) -> Dict:
        """Get engine information."""
        info = super().get_info()
        info.update({
            "server_url": self.server_url,
            "model_name": self.model_name,
            "supported_formats": self.SUPPORTED_FORMATS
        })
        return info


def create_localai_engine(
    server_url: str = "http://127.0.0.1:8080",
    model_name: str = "stable-diffusion",
    device: Optional[str] = None,
    gpu: bool = True
) -> LocalAIEngine:
    """Factory function to create a LocalAI engine instance."""
    return LocalAIEngine(
        server_url=server_url,
        model_name=model_name,
        device=device,
        gpu=gpu
    )

