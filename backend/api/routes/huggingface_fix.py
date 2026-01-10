"""
Hugging Face API Endpoint Fix
Ensures the new router endpoint is used throughout the application

This module should be imported early in the application startup to set
environment variables before huggingface_hub is imported.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Set Hugging Face inference API base to new router endpoint
HF_INFERENCE_API_BASE = "https://router.huggingface.co"
HF_INFERENCE_API_LEGACY = "https://api-inference.huggingface.co"  # DEPRECATED

def _ensure_router_env(var_name: str) -> None:
    """Guarantee env vars point to router.huggingface.co (override legacy)."""

    current = os.environ.get(var_name)
    desired = HF_INFERENCE_API_BASE

    if not current:
        os.environ[var_name] = desired
        logger.info("✅ Set %s=%s", var_name, desired)
        return

    normalized = current.rstrip("/")
    if normalized == HF_INFERENCE_API_LEGACY:
        os.environ[var_name] = desired
        logger.warning(
            "%s pointed at deprecated Hugging Face endpoint. Overriding with %s.",
            var_name,
            desired,
        )
    else:
        logger.debug("%s already set to %s", var_name, current)


# Set environment variables before any huggingface_hub imports
_ensure_router_env("HF_INFERENCE_API_BASE")

# Also set HF_ENDPOINT for InferenceClient compatibility
_ensure_router_env("HF_ENDPOINT")

# Log current configuration
logger.info(
    f"Hugging Face API Configuration: "
    f"HF_INFERENCE_API_BASE={os.environ.get('HF_INFERENCE_API_BASE', 'not set')}"
)

