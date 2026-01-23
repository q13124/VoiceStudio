#!/usr/bin/env python3
"""
Test HuggingFace token authentication
"""

import os
import sys


def main():
    print("Testing HuggingFace Token Authentication")
    print("=" * 50)

    # Check environment variables
    hf_token = os.getenv("HF_TOKEN")
    hf_hub_token = os.getenv("HUGGINGFACE_HUB_TOKEN")

    print(f"HF_TOKEN: {'SET' if hf_token else 'NOT SET'}")
    print(f"HUGGINGFACE_HUB_TOKEN: {'SET' if hf_hub_token else 'NOT SET'}")

    if hf_token:
        print(f"Token starts with: {hf_token[:10]}...")
    if hf_hub_token:
        print(f"Hub token starts with: {hf_hub_token[:10]}...")

    print()

    # Test authentication
    try:
        from huggingface_hub import HfApi

        print("Testing authentication...")

        api = HfApi()
        user = api.whoami()

        print("[SUCCESS] Authentication works!")
        print(f"   Username: {user['name']}")
        print(f"   User ID: {user.get('id', 'unknown')}")
        print(f"   Type: {user.get('type', 'unknown')}")

        return True

    except Exception as e:
        print("[FAILED] Authentication error")
        print(f"   Error: {e}")

        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("   -> Token is invalid or expired")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("   -> Token doesn't have required permissions")

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
