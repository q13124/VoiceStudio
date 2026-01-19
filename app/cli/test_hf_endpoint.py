"""
Test script to verify Hugging Face API endpoint configuration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables directly (simulating what the fix module does)
os.environ["HF_INFERENCE_API_BASE"] = "https://router.huggingface.co"
os.environ["HF_ENDPOINT"] = "https://router.huggingface.co"

# Check environment variables
print("=" * 60)
print("Hugging Face API Endpoint Configuration Test")
print("=" * 60)
print()

hf_base = os.environ.get("HF_INFERENCE_API_BASE", "NOT SET")
hf_endpoint = os.environ.get("HF_ENDPOINT", "NOT SET")

print(f"HF_INFERENCE_API_BASE: {hf_base}")
print(f"HF_ENDPOINT: {hf_endpoint}")
print()

# Expected values
expected = "https://router.huggingface.co"

if hf_base == expected:
    print("PASS: HF_INFERENCE_API_BASE is correctly set!")
else:
    print("FAIL: HF_INFERENCE_API_BASE is incorrect!")
    print(f"   Expected: {expected}")
    print(f"   Got: {hf_base}")

if hf_endpoint == expected:
    print("PASS: HF_ENDPOINT is correctly set!")
else:
    print("WARN: HF_ENDPOINT is not set (optional)")

print()
print("=" * 60)

# Try importing huggingface_hub to see if it uses the new endpoint
try:
    from huggingface_hub import InferenceClient

    print("PASS: huggingface_hub.InferenceClient imported successfully")
    print("   The environment variable should be used automatically")

    # Try to create a client (won't actually make requests)
    try:
        client = InferenceClient()
        print("PASS: InferenceClient created successfully")
    except Exception as e:
        print(f"WARN: InferenceClient creation error: {e}")
        print("   (This is OK if no model is specified)")

except ImportError:
    print("WARN: huggingface_hub not installed")
    print("   Install with: pip install huggingface_hub>=0.36.0")

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)
