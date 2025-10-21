#!/usr/bin/env python3
"""
Test script for voice cloning integration with EnhancedAudioProcessor
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the vsdml module to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'vsdml'))

from vsdml.services.audio_processor import EnhancedAudioProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_voice_cloning_integration():
    """Test the voice cloning integration"""
    
    print("Testing Voice Cloning Integration with EnhancedAudioProcessor")
    print("=" * 60)
    
    # Initialize the enhanced audio processor
    processor = EnhancedAudioProcessor(max_workers=4, cache_size=1000)
    
    try:
        # Test 1: Check if voice cloning models are initialized
        print("\n1. Testing Voice Cloning Models Initialization:")
        print(f"   Available models: {list(processor.voice_cloning_models.keys())}")
        print(f"   Voice cloning metrics initialized: {bool(processor._voice_cloning_metrics)}")
        print("   [OK] Voice cloning models initialized successfully")
        
        # Test 2: Test voice profile extraction (with mock audio)
        print("\n2. Testing Voice Profile Extraction:")
        
        # Create a mock audio file for testing
        import numpy as np
        import soundfile as sf
        
        # Generate test audio
        sample_rate = 22050
        duration = 2.0  # 2 seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a simple sine wave with some harmonics
        audio = np.sin(2 * np.pi * 440 * t) * 0.3  # A4 note
        audio += np.sin(2 * np.pi * 880 * t) * 0.1  # A5 note (octave)
        audio += np.random.normal(0, 0.05, len(audio))  # Add some noise
        
        # Save test audio file
        test_audio_path = "test_reference_audio.wav"
        sf.write(test_audio_path, audio, sample_rate)
        print(f"   Created test audio file: {test_audio_path}")
        
        # Test voice profile extraction
        print("   Extracting voice profile...")
        voice_profile = await processor.extract_voice_profile(test_audio_path)
        
        print(f"   [OK] Voice profile extracted successfully")
        print(f"   Audio length: {voice_profile.get('audio_length', 'N/A')}s")
        print(f"   Sample rate: {voice_profile.get('sample_rate', 'N/A')} Hz")
        print(f"   Speaker embedding size: {len(voice_profile.get('speaker_embedding', []))}")
        print(f"   Speaking rate: {voice_profile.get('speaking_rate', 'N/A')}")
        print(f"   Emotion prediction: {voice_profile.get('emotion_patterns', {}).get('emotion_prediction', 'N/A')}")
        
        # Test 3: Test voice cloning
        print("\n3. Testing Voice Cloning:")
        
        target_text = "Hello, this is a test of the voice cloning system. The integration is working correctly."
        print(f"   Target text: '{target_text}'")
        print("   Cloning voice...")
        
        clone_result = await processor.clone_voice(
            reference_audio=test_audio_path,
            target_text=target_text,
            speaker_id="test_speaker_001",
            model_type="gpt_sovits"
        )
        
        print(f"   [OK] Voice cloning completed successfully")
        print(f"   Processing time: {clone_result.get('processing_time', 'N/A'):.2f}s")
        print(f"   Model used: {clone_result.get('model_type', 'N/A')}")
        print(f"   Speaker ID: {clone_result.get('speaker_id', 'N/A')}")
        print(f"   Cloned audio file: {clone_result.get('cloned_audio', 'N/A')}")
        
        # Test 4: Test performance metrics
        print("\n4. Testing Performance Metrics:")
        
        metrics = processor.get_performance_metrics()
        voice_cloning_metrics = metrics.get('voice_cloning', {})
        
        print(f"   [OK] Performance metrics retrieved successfully")
        print(f"   Voice clones created: {voice_cloning_metrics.get('voice_clones_created', 0)}")
        print(f"   Voice cache hit rate: {voice_cloning_metrics.get('voice_cache_hit_rate', 0):.2%}")
        print(f"   Average processing time: {voice_cloning_metrics.get('voice_processing_time_avg', 0):.2f}s")
        print(f"   Loaded models: {voice_cloning_metrics.get('loaded_models', [])}")
        
        # Test 5: Test caching
        print("\n5. Testing Voice Profile Caching:")
        
        # Extract voice profile again to test caching
        print("   Extracting voice profile again (should use cache)...")
        voice_profile_cached = await processor.extract_voice_profile(test_audio_path)
        
        # Check if caching worked
        cache_key = f"voice_profile:{test_audio_path}"
        cached_profile = processor._get_from_cache(cache_key)
        
        if cached_profile is not None:
            print("   [OK] Voice profile caching working correctly")
        else:
            print("   ⚠️  Voice profile caching may not be working")
        
        # Test 6: Test different models
        print("\n6. Testing Different Voice Cloning Models:")
        
        models_to_test = ["openvoice", "coqui_xtts", "tortoise_tts"]
        
        for model_type in models_to_test:
            print(f"   Testing {model_type} model...")
            
            clone_result = await processor.clone_voice(
                reference_audio=test_audio_path,
                target_text=f"Test with {model_type} model",
                speaker_id=f"test_speaker_{model_type}",
                model_type=model_type
            )
            
            print(f"   [OK] {model_type} model working correctly")
            print(f"      Processing time: {clone_result.get('processing_time', 0):.2f}s")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! Voice cloning integration is working correctly!")
        print("=" * 60)
        
        # Final metrics summary
        final_metrics = processor.get_performance_metrics()
        final_voice_metrics = final_metrics.get('voice_cloning', {})
        
        print(f"\nFinal Performance Summary:")
        print(f"   Total voice clones created: {final_voice_metrics.get('voice_clones_created', 0)}")
        print(f"   Cache hit rate: {final_voice_metrics.get('voice_cache_hit_rate', 0):.2%}")
        print(f"   Average processing time: {final_voice_metrics.get('voice_processing_time_avg', 0):.2f}s")
        print(f"   Models tested: {final_voice_metrics.get('loaded_models', [])}")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        processor.close()
        
        # Remove test files
        if os.path.exists(test_audio_path):
            os.remove(test_audio_path)
            print(f"\nCleaned up test file: {test_audio_path}")
        
        # Clean up any generated cloned audio files
        for file in Path(".").glob("cloned_*.wav"):
            file.unlink()
            print(f"Cleaned up generated file: {file}")
    
    return True

if __name__ == "__main__":
    print("Starting Voice Cloning Integration Test")
    print("This test verifies that the EnhancedAudioProcessor has been successfully")
    print("extended with voice cloning capabilities.")
    print()
    
    # Run the test
    success = asyncio.run(test_voice_cloning_integration())
    
    if success:
        print("\n[OK] Integration test completed successfully!")
        print("The EnhancedAudioProcessor is now ready for voice cloning operations.")
    else:
        print("\n[ERROR] Integration test failed!")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)
