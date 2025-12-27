"""
CLI test harness for XTTS Engine
Tests voice cloning and synthesis functionality
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.engines.xtts_engine import create_xtts_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_engine_initialization():
    """Test engine initialization."""
    logger.info("Testing XTTS Engine initialization...")
    
    try:
        engine = create_xtts_engine()
        assert engine.is_initialized(), "Engine should be initialized"
        assert engine.get_device() in ["cuda", "cpu"], "Device should be cuda or cpu"
        logger.info(f"✓ Engine initialized on device: {engine.get_device()}")
        
        info = engine.get_info()
        logger.info(f"✓ Engine info: {info}")
        
        engine.cleanup()
        logger.info("✓ Engine cleanup successful")
        return True
        
    except Exception as e:
        logger.error(f"✗ Engine initialization failed: {e}")
        return False


def test_supported_languages():
    """Test supported languages list."""
    logger.info("Testing supported languages...")
    
    try:
        engine = create_xtts_engine()
        languages = engine.get_supported_languages()
        assert len(languages) > 0, "Should have supported languages"
        assert "en" in languages, "English should be supported"
        logger.info(f"✓ Supported languages: {len(languages)}")
        logger.info(f"  Languages: {', '.join(languages[:5])}...")
        
        engine.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"✗ Supported languages test failed: {e}")
        return False


def test_synthesis(reference_audio: Optional[str] = None):
    """Test voice synthesis (requires reference audio)."""
    if not reference_audio:
        logger.warning("Skipping synthesis test - no reference audio provided")
        logger.info("  Usage: python xtts_test.py --synthesize <path_to_reference.wav>")
        return True
    
    logger.info(f"Testing synthesis with reference: {reference_audio}")
    
    if not os.path.exists(reference_audio):
        logger.error(f"✗ Reference audio not found: {reference_audio}")
        return False
    
    try:
        engine = create_xtts_engine()
        text = "Hello, this is a test of voice cloning."
        
        audio = engine.clone_voice(
            reference_audio=reference_audio,
            text=text,
            language="en"
        )
        
        if audio is not None:
            logger.info(f"✓ Synthesis successful - audio shape: {audio.shape}")
            return True
        else:
            logger.error("✗ Synthesis returned None")
            return False
        
    except Exception as e:
        logger.error(f"✗ Synthesis test failed: {e}")
        return False
    finally:
        if 'engine' in locals():
            engine.cleanup()


def main():
    """Run all tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test XTTS Engine")
    parser.add_argument("--synthesize", type=str, help="Path to reference audio for synthesis test")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("XTTS Engine Test Harness")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: Initialization
    results.append(("Initialization", test_engine_initialization()))
    
    # Test 2: Supported Languages
    results.append(("Supported Languages", test_supported_languages()))
    
    # Test 3: Synthesis (if reference provided)
    if args.synthesize:
        results.append(("Synthesis", test_synthesis(args.synthesize)))
    else:
        test_synthesis()  # Will skip with warning
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"  {status}: {name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

