"""
CLI test harness for Chatterbox TTS Engine
Tests voice cloning and synthesis functionality with quality metrics
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

from app.core.engines.chatterbox_engine import create_chatterbox_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_engine_initialization():
    """Test engine initialization."""
    logger.info("Testing Chatterbox TTS Engine initialization...")

    try:
        engine = create_chatterbox_engine()
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
        engine = create_chatterbox_engine()
        languages = engine.get_supported_languages()
        assert len(languages) > 0, "Should have supported languages"
        assert "en" in languages, "English should be supported"
        assert len(languages) == 23, "Should support 23 languages"
        logger.info(f"✓ Supported languages: {len(languages)}")
        logger.info(f"  Sample languages: {', '.join(languages[:5])}...")

        engine.cleanup()
        return True

    except Exception as e:
        logger.error(f"✗ Supported languages test failed: {e}")
        return False


def test_supported_emotions():
    """Test supported emotions list."""
    logger.info("Testing supported emotions...")

    try:
        engine = create_chatterbox_engine()
        emotions = engine.get_supported_emotions()
        assert len(emotions) > 0, "Should have supported emotions"
        assert "neutral" in emotions, "Neutral emotion should be supported"
        logger.info(f"✓ Supported emotions: {len(emotions)}")
        logger.info(f"  Emotions: {', '.join(emotions)}")

        engine.cleanup()
        return True

    except Exception as e:
        logger.error(f"✗ Supported emotions test failed: {e}")
        return False


def test_synthesis(reference_audio: str | None = None):
    """Test voice synthesis (requires reference audio)."""
    if not reference_audio:
        logger.warning("Skipping synthesis test - no reference audio provided")
        logger.info("  Usage: python chatterbox_test.py --synthesize <path_to_reference.wav>")
        return True

    logger.info(f"Testing synthesis with reference: {reference_audio}")

    if not os.path.exists(reference_audio):
        logger.error(f"✗ Reference audio not found: {reference_audio}")
        return False

    try:
        engine = create_chatterbox_engine()
        text = "Hello, this is a test of voice cloning with Chatterbox TTS."

        # Test with quality metrics
        result = engine.clone_voice(
            reference_audio=reference_audio,
            text=text,
            language="en",
            emotion="happy",
            calculate_quality=True
        )

        if isinstance(result, tuple):
            audio, metrics = result
            logger.info("✓ Synthesis successful with quality metrics")
            logger.info(f"  Audio shape: {audio.shape}")
            logger.info(f"  MOS Score: {metrics.get('mos_score', 'N/A'):.2f}/5.0")
            logger.info(f"  Naturalness: {metrics.get('naturalness', 'N/A'):.2f}/1.0")
            if 'similarity' in metrics:
                logger.info(f"  Similarity: {metrics['similarity']:.2f}/1.0")
            return True
        elif result is not None:
            logger.info(f"✓ Synthesis successful - audio shape: {result.shape}")
            return True
        else:
            logger.error("✗ Synthesis returned None")
            return False

    except Exception as e:
        logger.error(f"✗ Synthesis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'engine' in locals():
            engine.cleanup()


def main():
    """Run all tests."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Chatterbox TTS Engine")
    parser.add_argument("--synthesize", type=str, help="Path to reference audio for synthesis test")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Chatterbox TTS Engine Test Harness")
    logger.info("=" * 60)

    results = []

    # Test 1: Initialization
    results.append(("Initialization", test_engine_initialization()))

    # Test 2: Supported Languages
    results.append(("Supported Languages", test_supported_languages()))

    # Test 3: Supported Emotions
    results.append(("Supported Emotions", test_supported_emotions()))

    # Test 4: Synthesis (if reference provided)
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

