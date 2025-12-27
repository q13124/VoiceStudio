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

# Set environment variables before any huggingface_hub imports
if "HF_INFERENCE_API_BASE" not in os.environ:
    os.environ["HF_INFERENCE_API_BASE"] = HF_INFERENCE_API_BASE
    logger.info(f"✅ Set HF_INFERENCE_API_BASE={HF_INFERENCE_API_BASE}")

# Also set HF_ENDPOINT for InferenceClient compatibility
if "HF_ENDPOINT" not in os.environ:
    os.environ["HF_ENDPOINT"] = HF_INFERENCE_API_BASE
    logger.debug(f"Set HF_ENDPOINT={HF_INFERENCE_API_BASE}")

# Log current configuration
logger.info(
    f"Hugging Face API Configuration: "
    f"HF_INFERENCE_API_BASE={os.environ.get('HF_INFERENCE_API_BASE', 'not set')}"
)

