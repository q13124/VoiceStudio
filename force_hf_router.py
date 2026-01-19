#!/usr/bin/env python3
"""
Force HuggingFace to use router endpoint.

This is a developer helper script to ensure Hugging Face libraries prefer
https://router.huggingface.co over the deprecated api-inference endpoint.
"""

import os
import sys

ROUTER_ENDPOINT = "https://router.huggingface.co"
LEGACY_ENDPOINT = "https://api-inference.huggingface.co"


def force_hf_router() -> bool:
    """Force Hugging Face libs to use the router endpoint."""

    os.environ["HF_INFERENCE_API_BASE"] = ROUTER_ENDPOINT
    os.environ["HF_ENDPOINT"] = ROUTER_ENDPOINT
    os.environ["HF_HUB_ENDPOINT"] = ROUTER_ENDPOINT

    print("Environment variables set:")
    print(f"  HF_INFERENCE_API_BASE: {os.environ.get('HF_INFERENCE_API_BASE')}")
    print(f"  HF_ENDPOINT: {os.environ.get('HF_ENDPOINT')}")
    print(f"  HF_HUB_ENDPOINT: {os.environ.get('HF_HUB_ENDPOINT')}")

    # Patch urllib to redirect legacy endpoint → router endpoint.
    try:
        import urllib.request

        original_urlopen = urllib.request.urlopen

        def patched_urlopen(url, *args, **kwargs):
            if isinstance(url, str) and LEGACY_ENDPOINT in url:
                url = url.replace(LEGACY_ENDPOINT, ROUTER_ENDPOINT)
            return original_urlopen(url, *args, **kwargs)

        urllib.request.urlopen = patched_urlopen
        print("urllib patched")
    except Exception as ex:
        print(f"urllib patch skipped: {ex}", file=sys.stderr)

    # Patch requests to redirect legacy endpoint → router endpoint.
    try:
        import requests

        original_request = requests.request

        def patched_request(method, url, *args, **kwargs):
            if isinstance(url, str) and LEGACY_ENDPOINT in url:
                url = url.replace(LEGACY_ENDPOINT, ROUTER_ENDPOINT)
            return original_request(method, url, *args, **kwargs)

        requests.request = patched_request
        print("requests patched")
    except Exception as ex:
        print(f"requests patch skipped: {ex}", file=sys.stderr)

    # Patch already-imported libraries (best effort).
    for module_name in ("huggingface_hub", "transformers"):
        module = sys.modules.get(module_name)
        if module is None:
            continue

        print(f"Patching already imported {module_name}")

        try:
            constants = getattr(module, "constants", None)
            if constants is not None and hasattr(constants, "HF_INFERENCE_API_BASE"):
                constants.HF_INFERENCE_API_BASE = ROUTER_ENDPOINT
        except Exception as ex:
            print(f"{module_name}.constants patch skipped: {ex}", file=sys.stderr)

        try:
            api_bases = getattr(module, "API_BASES", None)
            if isinstance(api_bases, dict):
                api_bases["huggingface"] = ROUTER_ENDPOINT
        except Exception as ex:
            print(f"{module_name}.API_BASES patch skipped: {ex}", file=sys.stderr)

    print("HuggingFace router endpoint enforcement active!")
    return True


if __name__ == "__main__":
    ok = force_hf_router()
    if ok:
        print("\nNow start VoiceStudio - the legacy endpoint error should be gone.")
        raise SystemExit(0)
    raise SystemExit(1)
