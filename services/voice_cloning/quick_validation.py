#!/usr/bin/env python3
"""
VoiceStudio Voice Cloning Quick Validation
Quick validation script to check if the voice cloning system is working.
"""

import requests
import time
import tempfile
import numpy as np
import soundfile as sf
import os
import sys

def create_test_audio(duration=1.0, sample_rate=22050):
    """Create a simple test audio file"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # A4 note
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    sf.write(temp_file.name, audio, sample_rate)
    return temp_file.name

def test_service_health(base_url="http://localhost:5083"):
    """Test if the voice cloning service is running"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data.get('service', 'unknown')}")
            return True
        else:
            print(f"❌ Service health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Service health check error: {e}")
        return False

def test_voice_cloning(base_url="http://localhost:5083"):
    """Test basic voice cloning functionality"""
    try:
        print("Testing voice cloning...")
        
        # Create test audio
        audio_file = create_test_audio()
        
        # Test voice cloning
        with open(audio_file, 'rb') as f:
            files = {'reference_audio': f}
            data = {
                'target_text': 'Hello, this is a test of the voice cloning system.',
                'speaker_id': 'test_speaker',
                'model_type': 'gpt_sovits'
            }
            response = requests.post(f"{base_url}/clone-voice", files=files, data=data, timeout=30)
        
        # Cleanup
        os.unlink(audio_file)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice cloning successful!")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   Model used: {result.get('model_type', 'unknown')}")
            return True
        else:
            print(f"❌ Voice cloning failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Voice cloning test error: {e}")
        return False

def test_web_interface(web_url="http://localhost:8080"):
    """Test web interface availability"""
    try:
        response = requests.get(f"{web_url}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "VoiceStudio" in content:
                print("✅ Web interface is accessible")
                return True
            else:
                print("❌ Web interface content validation failed")
                return False
        else:
            print(f"❌ Web interface test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web interface test error: {e}")
        return False

def main():
    """Run quick validation tests"""
    print("🚀 VoiceStudio Voice Cloning Quick Validation")
    print("=" * 50)
    
    # Test service health
    if not test_service_health():
        print("\n❌ Voice cloning service is not running!")
        print("   Please start the service with: python start-voice-cloning-services.py")
        sys.exit(1)
    
    # Test voice cloning
    if not test_voice_cloning():
        print("\n❌ Voice cloning functionality failed!")
        sys.exit(1)
    
    # Test web interface
    if not test_web_interface():
        print("\n⚠️  Web interface is not accessible")
        print("   You can still use the API directly")
    
    print("\n🎉 All tests passed! Voice cloning system is working correctly.")
    print("\n📋 Next steps:")
    print("   1. Open web interface: http://localhost:8080")
    print("   2. Use API directly: http://localhost:5083")
    print("   3. Check documentation: services/voice_cloning/README.md")

if __name__ == "__main__":
    main()
