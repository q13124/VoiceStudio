#!/usr/bin/env python3
"""
Test VoiceStudio Router Uploads
Tests the reference WAV upload functionality
"""

import requests
import tempfile
import os
from pathlib import Path
import numpy as np
import soundfile as sf


def create_test_wav():
    """Create a test WAV file for uploading"""
    # Generate a simple sine wave test audio
    sample_rate = 22050
    duration = 2.0  # seconds
    frequency = 440  # Hz (A4 note)

    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.sin(2 * np.pi * frequency * t) * 0.3  # Low volume

    # Create temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(temp_file.name, audio, sample_rate)
    temp_file.close()

    return temp_file.name


def test_upload_ref():
    """Test the /upload_ref endpoint"""
    base_url = "http://127.0.0.1:5090"

    print("=== VoiceStudio Router Uploads Test ===")
    print(f"Testing against: {base_url}")

    # Create test WAV file
    print("\n1. Creating test WAV file...")
    test_wav_path = create_test_wav()
    print(f"   Test WAV created: {test_wav_path}")

    try:
        # Test upload
        print("\n2. Testing /upload_ref endpoint...")

        with open(test_wav_path, "rb") as f:
            files = {"file": ("test_reference.wav", f, "audio/wav")}
            response = requests.post(f"{base_url}/upload_ref", files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Upload ID: {result.get('id')}")
            print(f"   Server path: {result.get('path')}")

            # Verify file exists on server
            server_path = result.get("path")
            if server_path and os.path.exists(server_path):
                file_size = os.path.getsize(server_path)
                print(f"   File size: {file_size} bytes")
                print(f"   ✅ File verified on server")
            else:
                print(f"   ⚠️  File not found on server at: {server_path}")

        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Clean up test file
        try:
            os.unlink(test_wav_path)
            print(f"\n3. Cleaned up test file: {test_wav_path}")
        except:
            pass

    # Test unsupported file type
    print("\n4. Testing unsupported file type...")
    try:
        # Create a fake text file
        fake_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        fake_file.write(b"This is not an audio file")
        fake_file.close()

        with open(fake_file.name, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(f"{base_url}/upload_ref", files=files, timeout=30)

        if response.status_code == 400:
            print("✅ Correctly rejected unsupported file type")
        else:
            print(f"❌ Should have rejected file: {response.status_code}")

        os.unlink(fake_file.name)

    except Exception as e:
        print(f"❌ Error testing unsupported file: {e}")

    # Test different audio formats
    print("\n5. Testing different audio formats...")

    audio_formats = [
        (".wav", "audio/wav"),
        (".flac", "audio/flac"),
        (".mp3", "audio/mpeg"),
        (".m4a", "audio/mp4"),
    ]

    for ext, mime_type in audio_formats:
        print(f"   Testing {ext} format...")
        try:
            # Create test audio file
            test_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)

            # Generate simple audio data
            sample_rate = 22050
            duration = 1.0
            frequency = 440
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio = np.sin(2 * np.pi * frequency * t) * 0.3

            # Write audio file
            if ext == ".wav":
                sf.write(test_file.name, audio, sample_rate)
            elif ext == ".flac":
                sf.write(test_file.name, audio, sample_rate)
            elif ext in [".mp3", ".m4a"]:
                # For MP3/M4A, we'll create a simple WAV and rename it
                # (In real usage, you'd use proper encoders)
                sf.write(test_file.name, audio, sample_rate)

            test_file.close()

            # Upload the file
            with open(test_file.name, "rb") as f:
                files = {"file": (f"test{ext}", f, mime_type)}
                response = requests.post(
                    f"{base_url}/upload_ref", files=files, timeout=30
                )

            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {ext} upload successful (ID: {result.get('id')})")
            else:
                print(f"   ❌ {ext} upload failed: {response.status_code}")

            # Clean up
            os.unlink(test_file.name)

        except Exception as e:
            print(f"   ❌ Error testing {ext}: {e}")

    print("\n=== Router Uploads Test Complete ===")


if __name__ == "__main__":
    test_upload_ref()
