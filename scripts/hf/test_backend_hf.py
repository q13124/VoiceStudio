#!/usr/bin/env python3
"""
Test backend HuggingFace integration
"""

import os
import sys


def main():
    print("Testing Backend HuggingFace Integration")
    print("=" * 50)

    # Check environment variables
    print("Environment Variables:")
    print(f"  HF_TOKEN: {os.getenv('HF_TOKEN', 'NOT SET')}")
    print(f"  HF_ENDPOINT: {os.getenv('HF_ENDPOINT', 'NOT SET')}")
    print(f"  HUGGINGFACE_HUB_TOKEN: {os.getenv('HUGGINGFACE_HUB_TOKEN', 'NOT SET')}")
    print()

    try:
        # Import backend HF utilities
        from app.core.utils.huggingface_api import check_api_compatibility, get_api_headers

        print("Testing API compatibility...")
        info = check_api_compatibility()
        print(f"  Router endpoint: {info.get('inference_api_base', 'unknown')}")
        print(f"  Status: {info.get('status', 'unknown')}")
        print()

        headers = get_api_headers()
        print("Headers configuration:")
        print(f"  Has Authorization: {'Authorization' in headers}")
        if 'Authorization' in headers:
            auth_parts = headers['Authorization'].split()
            if len(auth_parts) >= 1:
                print(f"  Auth type: {auth_parts[0]}")
            if len(auth_parts) >= 2:
                token_start = auth_parts[1][:10] + "..."
                print(f"  Token starts with: {token_start}")
        print()

        # Test a simple API call
        print("Testing API endpoint...")
        import requests

        from app.core.utils.huggingface_api import get_inference_api_url

        test_url = get_inference_api_url("microsoft/speecht5_tts")
        print(f"  Test URL: {test_url}")

        # Just test connectivity, don't download model
        response = requests.head(test_url, headers=headers, timeout=10)
        print(f"  Response status: {response.status_code}")

        if response.status_code == 200:
            print("  [SUCCESS] API endpoint accessible")
        elif response.status_code == 401:
            print("  [ERROR] Authentication failed - token invalid")
        elif response.status_code == 403:
            print("  [ERROR] Access forbidden - check token permissions")
        elif response.status_code == 429:
            print("  [WARNING] Rate limited - but should have token")
        else:
            print(f"  [INFO] Status {response.status_code} - {response.reason}")

        return response.status_code in [200, 404]  # 404 is OK for HEAD request

    except Exception as e:
        print(f"[ERROR] Failed to test backend: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print()
    if success:
        print("[SUCCESS] Backend HuggingFace integration appears to be working")
    else:
        print("[FAILED] Backend HuggingFace integration has issues")
    sys.exit(0 if success else 1)
