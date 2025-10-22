"""
Test script for VoiceStudio Voice Engine Router
"""
import requests
import json
import time

def test_router_endpoints():
    base_url = "http://127.0.0.1:5090"
    
    print("Testing VoiceStudio Voice Engine Router...")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing /health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Health check passed: {data['ok']}")
            print(f"   ✓ Available engines: {list(data['engines'].keys())}")
        else:
            print(f"   ✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Health check error: {e}")
        return False
    
    # Test engines endpoint
    print("\n2. Testing /engines endpoint...")
    try:
        response = requests.get(f"{base_url}/engines", timeout=5)
        if response.status_code == 200:
            engines = response.json()
            print(f"   ✓ Engines endpoint working")
            for engine_id, engine_data in engines.items():
                status = "Healthy" if engine_data.get("healthy") else "Unhealthy"
                load = engine_data.get("load", 0)
                print(f"   - {engine_id}: {status} (Load: {load:.1%})")
        else:
            print(f"   ✗ Engines endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Engines endpoint error: {e}")
    
    # Test TTS endpoint
    print("\n3. Testing /tts endpoint...")
    try:
        tts_request = {
            "text": "Hello, this is a test of the VoiceStudio router!",
            "language": "en",
            "quality": "balanced",
            "voice_profile": {},
            "params": {"sample_rate": 22050},
            "mode": "sync"
        }
        
        response = requests.post(f"{base_url}/tts", json=tts_request, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ TTS request successful")
            print(f"   ✓ Selected engine: {data['engine']}")
            print(f"   ✓ Engine order: {' → '.join(data['tried_order'])}")
            if data.get('result_b64_wav'):
                print(f"   ✓ Audio generated: {len(data['result_b64_wav'])} characters")
            else:
                print(f"   ✓ Job ID: {data.get('job_id')}")
        else:
            print(f"   ✗ TTS request failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ TTS request error: {e}")
    
    # Test A/B testing endpoint
    print("\n4. Testing /abtest endpoint...")
    try:
        abtest_request = {
            "text": "A/B test sample",
            "language": "en",
            "quality": "balanced"
        }
        
        response = requests.post(f"{base_url}/abtest", json=abtest_request, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ A/B test successful")
            print(f"   ✓ Tested engines: {data['candidates']}")
            print(f"   ✓ Results: {len(data['results'])} engines tested")
        else:
            print(f"   ✗ A/B test failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ A/B test error: {e}")
    
    print("\n" + "=" * 50)
    print("Router testing completed!")
    return True

if __name__ == "__main__":
    test_router_endpoints()
