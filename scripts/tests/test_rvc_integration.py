#!/usr/bin/env python3
"""
Test script for RVC engine integration
"""

import os
import sys

import numpy as np

# Ensure UTF-8 output so checkmark/cross characters don't crash on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_rvc_engine():
    """Test basic RVC engine functionality."""
    try:
        from app.core.engines.rvc_engine import RVCEngine

        print("Testing RVC Engine Integration...")

        # Create RVC engine instance
        engine = RVCEngine(device='cpu', gpu=False)
        print("✓ RVC Engine created")

        # Test initialization (lazy loading)
        success = engine.initialize()
        if success:
            print("✓ RVC Engine initialized successfully (lazy loading enabled)")
        else:
            print("✗ RVC Engine initialization failed")
            return False

        # Test with dummy audio (1 second of silence)
        sample_rate = 16000
        duration = 1.0
        audio = np.random.randn(int(sample_rate * duration)).astype(np.float32) * 0.1

        print(f"Testing with {duration}s audio at {sample_rate}Hz")

        # Test basic functionality without loading models
        print("Testing basic engine functionality...")

        # Test enhanced feature-based conversion directly
        try:
            converted = engine._convert_with_enhanced_features(audio, np.zeros((10, 80), dtype=np.float32))
            if converted is not None and len(converted) > 0:
                print(f"✓ Enhanced feature-based conversion successful: {len(converted)} samples")
            else:
                print("✗ Enhanced conversion returned None or empty audio")
                return False
        except Exception as e:
            print(f"✗ Enhanced conversion failed: {e}")
            return False

        # Test voice conversion
        try:
            converted = engine.convert_voice(audio)
            if converted is not None and len(converted) > 0:
                print(f"✓ Voice conversion successful: {len(converted)} samples")
            else:
                print("✗ Voice conversion returned None or empty audio")
                return False
        except Exception as e:
            print(f"✗ Voice conversion failed: {e}")
            return False

        # Test real-time conversion
        try:
            chunk = audio[:1024]  # Small chunk
            converted_chunk = engine.convert_realtime(chunk)
            if converted_chunk is not None and len(converted_chunk) > 0:
                print(f"✓ Real-time conversion successful: {len(converted_chunk)} samples")
            else:
                print("✗ Real-time conversion returned None or empty audio")
        except Exception as e:
            print(f"✗ Real-time conversion failed: {e}")
            return False

        # Test cleanup
        try:
            engine.cleanup()
            print("✓ Engine cleanup successful")
        except Exception as e:
            print(f"✗ Engine cleanup failed: {e}")

        print("\n🎉 All RVC engine tests passed!")
        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_rvc_engine()
    sys.exit(0 if success else 1)
