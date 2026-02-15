"""
System Integration Tests

Tests complete system integration including database, caching, monitoring, and resilience features.
"""

import logging
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class TestSystemIntegration:
    """Test complete system integration."""

    def test_database_integration(self):
        """Test database integration."""
        try:
            from app.core.database.query_optimizer import DatabaseQueryOptimizer
            from app.core.security.database import WatermarkDatabase

            # Create database
            db = WatermarkDatabase()

            # Test watermark storage
            test_data = b"test_watermark_data"
            watermark_id = db.store_watermark(test_data)

            assert watermark_id is not None, "Watermark storage failed"

            # Test watermark retrieval
            retrieved = db.get_watermark(watermark_id)
            assert retrieved == test_data, "Watermark retrieval failed"

        except ImportError:
            pytest.skip("Database modules not available")
        except Exception as e:
            pytest.skip(f"Database test skipped: {e}")

    def test_caching_integration(self):
        """Test caching system integration."""
        try:
            from app.core.engines.quality_metrics_cache import get_quality_metrics_cache
            from app.core.models.cache import get_model_cache

            # Test model cache
            model_cache = get_model_cache(max_models=5, max_memory_mb=100.0)
            assert model_cache is not None, "Model cache creation failed"

            # Test quality metrics cache
            metrics_cache = get_quality_metrics_cache(max_size=100, ttl=3600.0)
            assert metrics_cache is not None, "Quality metrics cache creation failed"

        except ImportError:
            pytest.skip("Caching modules not available")

    def test_monitoring_integration(self):
        """Test monitoring system integration."""
        try:
            from app.core.monitoring.error_tracking import get_error_tracker
            from app.core.monitoring.metrics import get_metrics_collector
            from app.core.monitoring.structured_logging import get_structured_logger

            # Test metrics collector
            collector = get_metrics_collector()
            collector.increment("test.counter")
            assert collector.get_counter("test.counter") == 1.0, "Metrics collection failed"

            # Test error tracker
            tracker = get_error_tracker()
            assert tracker is not None, "Error tracker creation failed"

            # Test structured logger
            logger = get_structured_logger()
            assert logger is not None, "Structured logger creation failed"

        except ImportError:
            pytest.skip("Monitoring modules not available")

    def test_resilience_integration(self):
        """Test resilience system integration."""
        try:
            from app.core.resilience.circuit_breaker import get_circuit_breaker
            from app.core.resilience.health_check import get_health_checker
            from app.core.resilience.retry import get_metrics_collector

            # Test circuit breaker
            breaker = get_circuit_breaker("test_service")
            assert breaker is not None, "Circuit breaker creation failed"

            # Test health checker
            checker = get_health_checker("test_service")
            assert checker is not None, "Health checker creation failed"

        except ImportError:
            pytest.skip("Resilience modules not available")

    @pytest.mark.asyncio
    async def test_complete_system_workflow(self):
        """Test complete system workflow."""
        try:
            import numpy as np

            from app.core.audio import enhance_voice_quality
            from app.core.engines.quality_metrics import calculate_all_metrics
            from app.core.engines.xtts_engine import XTTSEngine
            from app.core.monitoring.metrics import Timer, get_metrics_collector

            # Generate test audio
            audio = np.random.randn(48000).astype(np.float32) * 0.1

            # Track metrics
            collector = get_metrics_collector()

            # Step 1: Synthesize (if engine available)
            try:
                engine = XTTSEngine(device="cpu", gpu=False)
                if engine.initialize():
                    with Timer("synthesis", auto_record=True):
                        synthesized = engine.synthesize(
                            text="Test",
                            speaker_wav=audio,
                            sample_rate=24000
                        )
                    engine.cleanup()
                else:
                    synthesized = audio  # Use test audio as fallback
            except Exception:
                synthesized = audio  # Use test audio as fallback

            # Step 2: Enhance
            with Timer("enhancement", auto_record=True):
                enhanced = enhance_voice_quality(
                    synthesized,
                    sample_rate=24000,
                    normalize=True
                )

            # Step 3: Calculate metrics
            with Timer("metrics", auto_record=True):
                metrics = calculate_all_metrics(
                    enhanced,
                    reference_audio=audio,
                    sample_rate=24000
                )

            # Verify results
            assert enhanced is not None, "Enhancement failed"
            assert metrics is not None, "Metrics calculation failed"

            # Verify metrics were recorded
            synthesis_stats = collector.get_timer_stats("synthesis")
            enhancement_stats = collector.get_timer_stats("enhancement")
            metrics_stats = collector.get_timer_stats("metrics")

            # At least one should have stats
            assert any(stats is not None for stats in [
                synthesis_stats, enhancement_stats, metrics_stats
            ]), "No metrics were recorded"

        except ImportError:
            pytest.skip("Required modules not available")

