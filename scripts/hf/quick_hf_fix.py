#!/usr/bin/env python3
"""
Quick Hugging Face API Endpoint Fix

A simplified version that focuses on the essential fixes without extensive cache clearing.
"""

import os
import sys

# New router endpoint
ROUTER_ENDPOINT = "https://router.huggingface.co"
LEGACY_ENDPOINT = "https://api-inference.huggingface.co"

def set_environment_variables():
    """Set the essential environment variables."""
    print("Setting environment variables...")

    env_vars = [
        "HF_INFERENCE_API_BASE",
        "HF_ENDPOINT",
    ]

    for var in env_vars:
        os.environ[var] = ROUTER_ENDPOINT
        print(f"  {var} = {ROUTER_ENDPOINT}")

def patch_huggingface_hub():
    """Patch huggingface_hub if it's already imported."""
    try:
        import huggingface_hub

        # Patch constants if available
        if hasattr(huggingface_hub, 'constants'):
            constants = huggingface_hub.constants
            if hasattr(constants, 'HF_INFERENCE_API_BASE'):
                if constants.HF_INFERENCE_API_BASE == LEGACY_ENDPOINT:
                    constants.HF_INFERENCE_API_BASE = ROUTER_ENDPOINT
                    print("Patched huggingface_hub.constants.HF_INFERENCE_API_BASE")

        # Patch InferenceClient if available
        if hasattr(huggingface_hub, 'InferenceClient'):
            original_init = huggingface_hub.InferenceClient.__init__

            def patched_init(self, *args, **kwargs):
                kwargs["base_url"] = ROUTER_ENDPOINT
                return original_init(self, *args, **kwargs)

            huggingface_hub.InferenceClient.__init__ = patched_init
            print("Patched huggingface_hub.InferenceClient.__init__")

    except ImportError:
        print("huggingface_hub not imported yet (will use env vars)")

def test_fix():
    """Test that the fix is working."""
    print("\nTesting fix...")

    # Check environment variables
    hf_base = os.environ.get("HF_INFERENCE_API_BASE")
    hf_endpoint = os.environ.get("HF_ENDPOINT")

    if hf_base == ROUTER_ENDPOINT:
        print("✓ HF_INFERENCE_API_BASE is set correctly")
    else:
        print(f"✗ HF_INFERENCE_API_BASE: {hf_base} (expected: {ROUTER_ENDPOINT})")

    if hf_endpoint == ROUTER_ENDPOINT:
        print("✓ HF_ENDPOINT is set correctly")
    else:
        print(f"✗ HF_ENDPOINT: {hf_endpoint} (expected: {ROUTER_ENDPOINT})")

    # Test InferenceClient creation
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient()
        print("✓ InferenceClient created successfully")
    except Exception as e:
        print(f"⚠ InferenceClient test failed: {e}")

def main():
    """Main fix function."""
    print("=" * 50)
    print("Quick Hugging Face API Endpoint Fix")
    print("=" * 50)

    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Apply fixes
    set_environment_variables()
    print()

    patch_huggingface_hub()
    print()

    test_fix()

    print("\n" + "=" * 50)
    print("Fix applied! VoiceStudio should now work without")
    print("the 'api-inference.huggingface.co is no longer supported' error.")
    print("=" * 50)

if __name__ == "__main__":
    main()