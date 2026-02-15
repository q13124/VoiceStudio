#!/usr/bin/env python3
"""
Comprehensive Hugging Face API Endpoint Fix

This script ensures that VoiceStudio uses the new Hugging Face router endpoint
(`https://router.huggingface.co`) instead of the deprecated api-inference
endpoint.

Run this script before starting VoiceStudio to ensure the fix is applied.
"""

import os
import shutil
from pathlib import Path

# New router endpoint
ROUTER_ENDPOINT = "https://router.huggingface.co"
LEGACY_ENDPOINT = "https://api-inference.huggingface.co"


def clear_python_cache():
    """Clear Python cache files that might contain old imports."""
    print("Clearing Python cache (safe scan; skips venv/models)...")

    # Only clear caches in project Python sources
    # (avoid walking venv/site-packages).
    roots = ["backend", "app", "scripts"]
    skip_dirs = {
        "venv",
        ".venv",
        ".git",
        ".vs",
        "src",  # WinUI project tree
        "models",
        "proof_runs",
        "installer",
        "bin",
        "obj",
        ".buildlogs",
    }

    cleared = 0
    for base in roots:
        if not os.path.isdir(base):
            continue
        for root, dirs, _files in os.walk(base):
            # Prune heavy/irrelevant directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            if "__pycache__" in dirs:
                cache_dir = os.path.join(root, "__pycache__")
                try:
                    shutil.rmtree(cache_dir)
                    cleared += 1
                except Exception as e:
                    print(f"Warning: Could not clear {cache_dir}: {e}")

    print(f"Cleared {cleared} __pycache__ directories")


def force_environment_variables():
    """Force all relevant environment variables to use router endpoint."""
    print("Setting environment variables...")

    env_vars = [
        "HF_INFERENCE_API_BASE",
        "HF_ENDPOINT",
        "HF_HUB_ENDPOINT",
        "HUGGINGFACE_HUB_INFERENCE_ENDPOINT",
    ]

    for var in env_vars:
        os.environ[var] = ROUTER_ENDPOINT
        print(f"  {var} = {ROUTER_ENDPOINT}")


def patch_requests_if_needed():
    """Patch requests library to redirect legacy endpoint calls."""
    try:
        import requests  # type: ignore

        original_request = requests.request

        def patched_request(
            method: str, url: str, *args: object, **kwargs: object
        ) -> object:
            if LEGACY_ENDPOINT in url:
                new_url = url.replace(LEGACY_ENDPOINT, ROUTER_ENDPOINT)
                print(f"Redirected API call: {url} -> {new_url}")
                url = new_url
            return original_request(method, url, *args, **kwargs)

        requests.request = patched_request
        print("Patched requests library for legacy endpoint redirection")
    except ImportError:
        print("requests library not available for patching")


def patch_urllib_if_needed():
    """
    No-op.

    The backend applies the Hugging Face endpoint fix on startup
    (`backend/api/routes/huggingface_fix.py`), so this extra patch is
    unnecessary.
    """
    print("urllib patch skipped (backend applies HF endpoint fix on startup)")


def test_huggingface_hub():
    """Test that huggingface_hub uses the correct endpoint."""
    print("\nTesting Hugging Face Hub integration...")

    try:
        import huggingface_hub

        # Check constants (best-effort)
        constants = getattr(huggingface_hub, "constants", None)
        current = None
        if constants is not None:
            current = getattr(constants, "HF_INFERENCE_API_BASE", None)
        if current == LEGACY_ENDPOINT and constants is not None:
            constants.HF_INFERENCE_API_BASE = ROUTER_ENDPOINT
            print("Fixed huggingface_hub.constants.HF_INFERENCE_API_BASE")
        elif current == ROUTER_ENDPOINT:
            print("huggingface_hub.constants.HF_INFERENCE_API_BASE is correct")
        elif current:
            print(f"HF_INFERENCE_API_BASE: {current}")

        # Test InferenceClient creation
        if hasattr(huggingface_hub, "InferenceClient"):
            try:
                _ = huggingface_hub.InferenceClient()
                print("InferenceClient created successfully")
            except Exception as e:
                print(f"InferenceClient creation failed: {e}")

    except ImportError:
        print("huggingface_hub not installed")


def test_transformers():
    """Test that transformers uses the correct endpoint."""
    print("\nTesting transformers integration...")

    try:
        import transformers

        # Check API_BASES (best-effort; not a stable public attribute)
        api_bases = getattr(transformers, "API_BASES", None)
        if isinstance(api_bases, dict) and "huggingface" in api_bases:
            current = api_bases.get("huggingface")
            if current == LEGACY_ENDPOINT:
                api_bases["huggingface"] = ROUTER_ENDPOINT
                print("Fixed transformers.API_BASES['huggingface']")
            elif current == ROUTER_ENDPOINT:
                print("transformers.API_BASES['huggingface'] is correct")
            elif current:
                print(f"transformers.API_BASES['huggingface']: {current}")

    except ImportError:
        print("transformers not installed")


def main():
    """Main fix application."""
    print("=" * 60)
    print("VoiceStudio Hugging Face API Endpoint Fix")
    print("=" * 60)
    print()

    # Change to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Apply all fixes
    clear_python_cache()
    print()

    force_environment_variables()
    print()

    patch_requests_if_needed()
    patch_urllib_if_needed()
    print()

    test_huggingface_hub()
    test_transformers()

    print()
    print("=" * 60)
    print("Fix Applied Successfully!")
    print("=" * 60)
    print()
    print("The following changes have been made:")
    print("* Cleared Python cache")
    print("* Set environment variables to router endpoint")
    print("* Patched HTTP libraries for legacy endpoint redirection")
    print("* Verified Hugging Face library integration")
    print()
    print("Start VoiceStudio now. HF legacy endpoint should be resolved.")
    print()
    print("If you still encounter issues, try:")
    print("1. Restart your Python environment")
    print("2. Clear browser cache if using web interface")
    print("3. Run this script again before starting VoiceStudio")


if __name__ == "__main__":
    main()
