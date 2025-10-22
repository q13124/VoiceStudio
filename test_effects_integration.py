#!/usr/bin/env python3
"""
Test VoiceStudio Effects Integration
Tests the enhanced TTS endpoints with post-processing effects
"""

import requests
import json
import base64
import tempfile
from pathlib import Path


def test_effects_integration():
    """Test the enhanced TTS endpoints with effects"""
    base_url = "http://127.0.0.1:5090"

    print("=== VoiceStudio Effects Integration Test ===")
    print(f"Testing against: {base_url}")

    # Test data
    test_text = "Hello from VoiceStudio with effects processing!"
    test_params = {"post_chain": ["lufs", "de_ess", "noise_gate"], "sample_rate": 22050}

    # Test sync enhanced endpoint
    print("\n1. Testing /tts_enhanced (sync)...")
    try:
        response = requests.post(
            f"{base_url}/tts_enhanced",
            json={
                "text": test_text,
                "language": "en",
                "quality": "balanced",
                "voice_profile": {},
                "params": test_params,
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Engine: {result.get('engine')}")
            print(f"   Tried order: {result.get('tried_order')}")

            # Save the enhanced audio
            if result.get("result_b64_wav"):
                audio_data = base64.b64decode(result["result_b64_wav"])
                output_file = (
                    Path(tempfile.gettempdir()) / "voicestudio_enhanced_test.wav"
                )
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                print(f"   Enhanced audio saved: {output_file}")
            else:
                print("   ⚠️  No audio data returned")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test async enhanced endpoint
    print("\n2. Testing /tts_async_enhanced (async)...")
    try:
        response = requests.post(
            f"{base_url}/tts_async_enhanced",
            json={
                "text": test_text,
                "language": "en",
                "quality": "balanced",
                "voice_profile": {},
                "params": test_params,
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ Job submitted: {job_id}")

            # Poll for completion
            import time

            max_attempts = 60  # 30 seconds max
            for attempt in range(max_attempts):
                time.sleep(0.5)

                status_response = requests.get(f"{base_url}/jobs/{job_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    job_status = status.get("status")

                    if job_status == "done":
                        print(f"✅ Job completed! Engine: {status.get('engine')}")

                        # Save the enhanced audio
                        if status.get("result_b64_wav"):
                            audio_data = base64.b64decode(status["result_b64_wav"])
                            output_file = (
                                Path(tempfile.gettempdir())
                                / "voicestudio_async_enhanced_test.wav"
                            )
                            with open(output_file, "wb") as f:
                                f.write(audio_data)
                            print(f"   Enhanced async audio saved: {output_file}")
                        break
                    elif job_status == "error":
                        print(f"❌ Job failed: {status.get('error')}")
                        break
                    else:
                        progress = status.get("progress", 0)
                        print(f"   Job {job_status}: {int(progress * 100)}%")
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break
            else:
                print("❌ Job timed out")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

    # Test different effect combinations
    print("\n3. Testing different effect combinations...")

    effect_combinations = [
        ["lufs"],
        ["de_ess"],
        ["noise_gate"],
        ["lufs", "de_ess"],
        ["de_ess", "noise_gate"],
        ["lufs", "noise_gate"],
        ["lufs", "de_ess", "noise_gate"],
    ]

    for i, effects in enumerate(effect_combinations):
        print(f"   Testing combination {i+1}: {effects}")
        try:
            response = requests.post(
                f"{base_url}/tts_enhanced",
                json={
                    "text": f"Test {i+1} with effects: {', '.join(effects)}",
                    "language": "en",
                    "quality": "fast",
                    "voice_profile": {},
                    "params": {"post_chain": effects, "sample_rate": 22050},
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success with {result.get('engine')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n=== Effects Integration Test Complete ===")


if __name__ == "__main__":
    test_effects_integration()
