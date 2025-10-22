#!/usr/bin/env python3
"""
Test VoiceStudio Router Diagnostics
Tests the diagnostics bundle generation functionality
"""

import requests
import base64
import tempfile
import zipfile
import json
from pathlib import Path


def test_diagnostics():
    """Test the /diagnostics endpoint"""
    base_url = "http://127.0.0.1:5090"

    print("=== VoiceStudio Router Diagnostics Test ===")
    print(f"Testing against: {base_url}")

    try:
        # Test diagnostics endpoint
        print("\n1. Testing /diagnostics endpoint...")

        response = requests.get(f"{base_url}/diagnostics", timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Diagnostics bundle generated successfully!")
            print(f"   Filename: {result.get('filename')}")

            # Decode and save the ZIP file
            zip_data = base64.b64decode(result.get("b64_zip"))

            # Save to temporary file
            temp_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
            temp_zip.write(zip_data)
            temp_zip.close()

            print(f"   Bundle saved: {temp_zip.name}")

            # Extract and examine contents
            print("\n2. Examining diagnostics bundle contents...")

            with zipfile.ZipFile(temp_zip.name, "r") as z:
                file_list = z.namelist()
                print(f"   Files in bundle: {len(file_list)}")

                for filename in file_list:
                    print(f"   - {filename}")

                    # Read and display content of key files
                    if filename == "system.json":
                        try:
                            content = z.read(filename).decode("utf-8")
                            system_info = json.loads(content)
                            print(
                                f"     Python: {system_info.get('python', 'N/A')[:50]}..."
                            )
                            print(
                                f"     Platform: {system_info.get('platform', 'N/A')}"
                            )
                        except Exception as e:
                            print(f"     Error reading system.json: {e}")

                    elif filename == "torch.json":
                        try:
                            content = z.read(filename).decode("utf-8")
                            torch_info = json.loads(content)
                            print(
                                f"     PyTorch version: {torch_info.get('version', 'N/A')}"
                            )
                            print(
                                f"     CUDA available: {torch_info.get('cuda_available', 'N/A')}"
                            )
                            print(
                                f"     Device count: {torch_info.get('device_count', 'N/A')}"
                            )
                        except Exception as e:
                            print(f"     Error reading torch.json: {e}")

                    elif filename == "tts_version.txt":
                        try:
                            content = z.read(filename).decode("utf-8")
                            print(f"     TTS version: {content.strip()}")
                        except Exception as e:
                            print(f"     Error reading tts_version.txt: {e}")

                    elif filename == "pip_top.txt":
                        try:
                            content = z.read(filename).decode("utf-8")
                            lines = content.strip().split("\n")
                            print(f"     Top packages ({len(lines)} lines):")
                            for line in lines[:5]:  # Show first 5 packages
                                print(f"       {line}")
                            if len(lines) > 5:
                                print(f"       ... and {len(lines) - 5} more")
                        except Exception as e:
                            print(f"     Error reading pip_top.txt: {e}")

                    elif filename == "health.json":
                        try:
                            content = z.read(filename).decode("utf-8")
                            health_info = json.loads(content)
                            print(
                                f"     Health info: {len(health_info)} engines discovered"
                            )
                        except Exception as e:
                            print(f"     Error reading health.json: {e}")

                    elif filename.endswith(".yaml"):
                        try:
                            content = z.read(filename).decode("utf-8")
                            lines = content.strip().split("\n")
                            print(f"     Config file ({len(lines)} lines)")
                        except Exception as e:
                            print(f"     Error reading {filename}: {e}")

            # Clean up
            try:
                Path(temp_zip.name).unlink()
                print(f"\n3. Cleaned up temporary file: {temp_zip.name}")
            except:
                pass

        else:
            print(f"❌ Diagnostics failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test bundle size and content validation
    print("\n4. Validating bundle content...")
    try:
        response = requests.get(f"{base_url}/diagnostics", timeout=30)
        if response.status_code == 200:
            result = response.json()
            zip_data = base64.b64decode(result.get("b64_zip"))

            # Check bundle size
            bundle_size = len(zip_data)
            print(
                f"   Bundle size: {bundle_size:,} bytes ({bundle_size / 1024:.1f} KB)"
            )

            if bundle_size < 1000:
                print("   ⚠️  Bundle seems unusually small")
            elif bundle_size > 1024 * 1024:  # 1MB
                print("   ⚠️  Bundle seems unusually large")
            else:
                print("   ✅ Bundle size looks reasonable")

            # Validate ZIP structure
            try:
                with zipfile.ZipFile(io.BytesIO(zip_data), "r") as z:
                    z.testzip()
                print("   ✅ ZIP file structure is valid")
            except Exception as e:
                print(f"   ❌ ZIP file validation failed: {e}")

    except Exception as e:
        print(f"   ❌ Bundle validation error: {e}")

    print("\n=== Router Diagnostics Test Complete ===")


if __name__ == "__main__":
    import io

    test_diagnostics()
