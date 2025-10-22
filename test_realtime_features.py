#!/usr/bin/env python3
"""
Test script for VoiceStudio realtime features
Tests WebSocket progress updates and async TTS jobs
"""

import asyncio
import json
import time
import websockets
import requests
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:5090"
WS_URL = "ws://127.0.0.1:5090/ws"


async def test_websocket_connection():
    """Test WebSocket connection and message handling"""
    print("Testing WebSocket connection...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            # Wait for hello message
            hello_msg = await websocket.recv()
            hello_data = json.loads(hello_msg)
            print(f"SUCCESS: Received hello: {hello_data}")

            # Send a ping to keep connection alive
            await websocket.send("ping")
            print("SUCCESS: WebSocket connection established")
            return True

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False


def test_router_health():
    """Test basic router health endpoint"""
    print("🏥 Testing router health...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Router healthy: {health_data.get('ok', False)}")
            print(
                f"   Available engines: {list(health_data.get('engines', {}).keys())}"
            )
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_sync_tts():
    """Test synchronous TTS generation"""
    print("🎤 Testing sync TTS...")

    try:
        payload = {
            "text": "Hello from VoiceStudio test",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {"sample_rate": 22050},
            "mode": "sync",
        }

        response = requests.post(f"{BASE_URL}/tts", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sync TTS successful")
            print(f"   Engine used: {result.get('engine')}")
            print(f"   Audio size: {len(result.get('result_b64_wav', ''))} chars")
            return True
        else:
            print(f"❌ Sync TTS failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sync TTS error: {e}")
        return False


def test_async_tts():
    """Test asynchronous TTS generation"""
    print("⚡ Testing async TTS...")

    try:
        payload = {
            "text": "Async hello from VoiceStudio",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {"sample_rate": 22050},
            "mode": "async",
        }

        response = requests.post(f"{BASE_URL}/tts", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ Async job created: {job_id}")

            # Poll job status
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(1)
                status_response = requests.get(f"{BASE_URL}/jobs/{job_id}")
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(
                        f"   Status: {status.get('status')} ({status.get('progress', 0)*100:.0f}%)"
                    )

                    if status.get("status") == "completed":
                        print(f"✅ Async job completed successfully")
                        return True
                    elif status.get("status") == "failed":
                        print(f"❌ Async job failed: {status.get('error_message')}")
                        return False
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False

            print(f"❌ Async job timed out after {max_attempts} seconds")
            return False
        else:
            print(f"❌ Async TTS failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Async TTS error: {e}")
        return False


def test_abtest():
    """Test A/B testing endpoint"""
    print("🧪 Testing A/B test...")

    try:
        payload = {
            "text": "A/B test this text",
            "language": "en",
            "quality": "balanced",
        }

        response = requests.post(f"{BASE_URL}/abtest", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            candidates = result.get("candidates", [])
            results = result.get("results", {})
            print(f"✅ A/B test successful")
            print(f"   Candidates: {candidates}")
            print(f"   Results: {list(results.keys())}")
            return True
        else:
            print(f"❌ A/B test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ A/B test error: {e}")
        return False


async def test_websocket_with_async_job():
    """Test WebSocket progress updates with async job"""
    print("🔄 Testing WebSocket progress updates...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            # Receive hello message
            hello_msg = await websocket.recv()
            print(f"✅ Connected: {json.loads(hello_msg)}")

            # Create async job
            payload = {
                "text": "WebSocket progress test",
                "language": "en",
                "quality": "balanced",
                "voice_profile": {},
                "params": {"sample_rate": 22050},
                "mode": "async",
            }

            response = requests.post(f"{BASE_URL}/tts", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                job_id = result.get("job_id")
                print(f"✅ Created job: {job_id}")

                # Listen for progress updates
                progress_received = False
                timeout = 30
                start_time = time.time()

                while time.time() - start_time < timeout:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)

                        if (
                            data.get("type") == "job_update"
                            and data.get("job_id") == job_id
                        ):
                            progress_received = True
                            status = data.get("status", "unknown")
                            progress = data.get("progress", 0) * 100
                            print(f"   📊 Progress: {status} ({progress:.0f}%)")

                            if status == "completed":
                                print(f"✅ WebSocket progress test completed")
                                return True
                            elif status == "failed":
                                print(f"❌ Job failed: {data.get('error_message')}")
                                return False
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"❌ WebSocket error: {e}")
                        return False

                if not progress_received:
                    print(f"❌ No progress updates received")
                    return False
                else:
                    print(f"❌ WebSocket test timed out")
                    return False
            else:
                print(f"❌ Failed to create async job: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ WebSocket progress test error: {e}")
        return False


async def main():
    """Run all tests"""
    print("VoiceStudio Realtime Features Test Suite")
    print("=" * 50)

    tests = [
        ("Router Health", test_router_health),
        ("WebSocket Connection", test_websocket_connection),
        ("Sync TTS", test_sync_tts),
        ("Async TTS", test_async_tts),
        ("A/B Test", test_abtest),
        ("WebSocket Progress", test_websocket_with_async_job),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print(
            "🎉 All tests passed! VoiceStudio realtime features are working correctly."
        )
    else:
        print("⚠️  Some tests failed. Check the router logs for details.")


if __name__ == "__main__":
    asyncio.run(main())
