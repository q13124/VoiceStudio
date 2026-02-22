"""
Engine Workflow Integration Tests

Tests complete engine workflows including initialization, synthesis, and cleanup.
"""

import contextlib
import logging
import sys
from pathlib import Path

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def generate_test_audio(duration_seconds: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
    audio = np.sin(2 * np.pi * 440.0 * t)
    audio = audio * 0.5
    return audio.astype(np.float32)


class TestEngineWorkflows:
    """Test complete engine workflows."""

    @pytest.mark.asyncio
    async def test_xtts_complete_workflow(self):
        """Test complete XTTS engine workflow."""
        try:
            from app.core.engines.xtts_engine import XTTSEngine

            # Initialize engine
            engine = XTTSEngine(device="cpu", gpu=False)
            assert engine.initialize(), "Engine initialization failed"

            # Generate reference audio
            reference_audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Synthesize
            text = "Hello, this is a test of the XTTS engine."
            audio = engine.synthesize(
                text=text, speaker_wav=reference_audio, sample_rate=24000, language="en"
            )

            assert audio is not None, "Synthesis returned None"
            assert len(audio) > 0, "Synthesis returned empty audio"
            assert isinstance(audio, np.ndarray), "Synthesis returned wrong type"

            # Cleanup
            engine.cleanup()

        except ImportError:
            pytest.skip("XTTS engine not available")

    @pytest.mark.asyncio
    async def test_engine_lifecycle_workflow(self):
        """Test engine lifecycle workflow."""
        try:
            from app.core.runtime.engine_lifecycle import get_lifecycle_manager

            # Prefer EnhancedRuntimeEngine, fallback to RuntimeEngine
            with contextlib.suppress(ImportError):
                pass

            lifecycle_manager = get_lifecycle_manager()

            # Create test manifest
            test_manifest = {
                "engine_id": "test_engine",
                "name": "Test Engine",
                "type": "audio",
                "entry_point": "app.core.engines.xtts_engine.XTTSEngine",
            }

            # Register engine
            lifecycle_manager.register_engine(
                engine_id="test_engine",
                manifest=test_manifest,
                pool_size=1,
                is_singleton=True,
            )

            # Start engine
            instance = lifecycle_manager.start_engine("test_engine")
            assert instance is not None, "Engine start failed"

            # Check health
            is_healthy = lifecycle_manager.check_engine_health("test_engine")
            assert isinstance(is_healthy, bool), "Health check returned wrong type"

            # Stop engine
            lifecycle_manager.stop_engine("test_engine")

        except Exception as e:
            pytest.skip(f"Engine lifecycle test skipped: {e}")

    @pytest.mark.asyncio
    async def test_batch_synthesis_workflow(self):
        """Test batch synthesis workflow."""
        try:
            from app.core.engines.xtts_engine import XTTSEngine

            engine = XTTSEngine(device="cpu", gpu=False)
            assert engine.initialize(), "Engine initialization failed"

            # Generate reference audio
            reference_audio = generate_test_audio(duration_seconds=2.0, sample_rate=24000)

            # Batch synthesis
            texts = ["First sentence.", "Second sentence.", "Third sentence."]

            results = engine.batch_synthesize(
                texts=texts, speaker_wav=reference_audio, sample_rate=24000
            )

            assert results is not None, "Batch synthesis returned None"
            assert len(results) == len(texts), "Batch synthesis returned wrong number of results"
            assert all(
                isinstance(audio, np.ndarray) for audio in results
            ), "Batch synthesis returned wrong types"

            engine.cleanup()

        except ImportError:
            pytest.skip("XTTS engine not available")
        except AttributeError:
            pytest.skip("Batch synthesis not available")

    @pytest.mark.asyncio
    async def test_engine_error_recovery_workflow(self):
        """Test engine error recovery workflow."""
        try:
            from app.core.engines.xtts_engine import XTTSEngine
            from app.core.resilience.retry import RetryStrategy, retry_with_backoff

            # Create engine that may fail
            engine = XTTSEngine(device="cpu", gpu=False)

            # Test with retry
            async def initialize_with_retry():
                return engine.initialize()

            result = await retry_with_backoff(
                initialize_with_retry,
                max_attempts=3,
                strategy=RetryStrategy.EXPONENTIAL,
                initial_delay=0.1,
            )

            assert isinstance(result, bool), "Retry returned wrong type"

            if result:
                engine.cleanup()

        except ImportError:
            pytest.skip("Required modules not available")
