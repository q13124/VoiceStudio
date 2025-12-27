"""
Hugging Face API Utilities
Handles Hugging Face API endpoints and ensures compatibility with latest API
changes

Compatible with:
- transformers>=4.20.0
- huggingface_hub>=0.20.0
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Hugging Face API endpoints
# Updated to use new router endpoint (2025)
HF_INFERENCE_API_BASE = "https://router.huggingface.co"
HF_API_BASE = "https://huggingface.co"
HF_HUB_API_BASE = "https://huggingface.co/api"

# Legacy endpoints (deprecated)
HF_INFERENCE_API_LEGACY = "https://api-inference.huggingface.co"  # DEPRECATED

# Set environment variable to ensure huggingface_hub uses new endpoint
# This must be set before importing huggingface_hub
if "HF_INFERENCE_API_BASE" not in os.environ:
    os.environ["HF_INFERENCE_API_BASE"] = HF_INFERENCE_API_BASE
    logger.info(f"Set HF_INFERENCE_API_BASE to {HF_INFERENCE_API_BASE}")

# Also set for InferenceClient compatibility
if "HF_ENDPOINT" not in os.environ:
    os.environ["HF_ENDPOINT"] = HF_INFERENCE_API_BASE
    logger.debug(f"Set HF_ENDPOINT to {HF_INFERENCE_API_BASE}")


def get_inference_api_url(model_id: str, endpoint: str = "") -> str:
    """
    Get Hugging Face inference API URL using the new router endpoint.

    Args:
        model_id: Hugging Face model ID (e.g., "microsoft/speecht5_tts")
        endpoint: Optional endpoint path (e.g., "/generate")

    Returns:
        Full URL for inference API
    """
    # Use new router endpoint
    base_url = HF_INFERENCE_API_BASE

    # Construct URL
    if endpoint:
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        url = f"{base_url}/{model_id}/{endpoint}"
    else:
        url = f"{base_url}/{model_id}"

    return url


def get_hub_api_url(endpoint: str) -> str:
    """
    Get Hugging Face Hub API URL.

    Args:
        endpoint: API endpoint path (e.g., "/models")

    Returns:
        Full URL for Hub API
    """
    endpoint = endpoint.lstrip("/")
    return f"{HF_HUB_API_BASE}/{endpoint}"


def get_model_url(model_id: str) -> str:
    """
    Get Hugging Face model page URL.

    Args:
        model_id: Hugging Face model ID

    Returns:
        Full URL to model page
    """
    return f"{HF_API_BASE}/{model_id}"


def get_api_headers(token: Optional[str] = None) -> Dict[str, str]:
    """
    Get headers for Hugging Face API requests.

    Args:
        token: Optional Hugging Face API token

    Returns:
        Dictionary of headers
    """
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "VoiceStudio/1.0",
    }

    # Add token if provided
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        # Try to get from environment
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"

    return headers


def check_api_compatibility() -> Dict[str, Any]:
    """
    Check Hugging Face API compatibility and endpoint status.

    Returns:
        Dictionary with compatibility information
    """
    import requests

    info = {
        "inference_api_base": HF_INFERENCE_API_BASE,
        "legacy_endpoint_deprecated": True,
        "legacy_endpoint": HF_INFERENCE_API_LEGACY,
        "status": "unknown",
    }

    try:
        # Test new router endpoint
        response = requests.get(
            f"{HF_INFERENCE_API_BASE}/health", timeout=5, headers=get_api_headers()
        )
        info["status"] = "available" if response.status_code == 200 else "unavailable"
        info["router_endpoint_working"] = response.status_code == 200
    except Exception as e:
        logger.warning(f"Could not verify Hugging Face API: {e}")
        info["status"] = "error"
        info["error"] = str(e)

    return info


# Environment variable for overriding API base (for testing)
def get_inference_api_base() -> str:
    """
    Get inference API base URL, with support for environment override.

    Returns:
        Base URL for inference API
    """
    # Allow override via environment variable
    override = os.getenv("HF_INFERENCE_API_BASE")
    if override:
        logger.info(f"Using custom HF inference API base: {override}")
        return override.rstrip("/")

    return HF_INFERENCE_API_BASE


# Update transformers and huggingface_hub library configuration
def configure_transformers_for_new_api():
    """
    Configure transformers and huggingface_hub libraries to use new API
    endpoints.

    This sets environment variables that these libraries check for the API
    base URL.
    """
    try:
        # Set environment variables for huggingface_hub
        os.environ["HF_INFERENCE_API_BASE"] = HF_INFERENCE_API_BASE

        # Try to configure huggingface_hub if available
        try:
            import huggingface_hub

            # Check version
            hf_hub_version = huggingface_hub.__version__
            logger.debug(f"huggingface_hub version: {hf_hub_version}")

            # For huggingface_hub >= 0.20.0, InferenceClient should use new
            # endpoint. The environment variable should be sufficient
            if hasattr(huggingface_hub, "InferenceClient"):
                logger.debug("huggingface_hub.InferenceClient available")

        except ImportError:
            logger.debug("huggingface_hub not installed")

        # Try to configure transformers if available
        # Transformers uses huggingface_hub under the hood
        # Setting the environment variable should be sufficient
        try:
            import importlib.util

            if importlib.util.find_spec("transformers") is not None:
                logger.debug("transformers library available")
        except Exception:
            logger.debug("transformers not installed")

    except Exception as e:
        logger.warning(f"Could not configure Hugging Face libraries: {e}")


# Initialize on import - set environment variables before any imports
configure_transformers_for_new_api()
