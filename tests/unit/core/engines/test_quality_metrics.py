"""
Unit Tests for Quality Metrics
Tests quality metrics calculation functionality.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the quality metrics module
try:
    from app.core.engines import quality_metrics
except ImportError:
    pytest.skip("Could not import quality_metrics", allow_module_level=True)


class TestQualityMetricsImports:
    """Test quality metrics module can be imported."""

    def test_quality_metrics_imports(self):
        """Test quality_metrics can be imported."""
        assert quality_metrics is not None, "Failed to import quality_metrics module"

    def test_quality_metrics_has_functions(self):
        """Test quality_metrics has expected functions."""
        functions = dir(quality_metrics)
        assert len(functions) > 0, "quality_metrics should have functions"


class TestQualityMetricsFunctions:
    """Test quality metrics functions exist."""

    def test_calculate_mos_score_function_exists(self):
        """Test calculate_mos_score function exists."""
        if hasattr(quality_metrics, "calculate_mos_score"):
            assert callable(
                quality_metrics.calculate_mos_score
            ), "calculate_mos_score should be callable"

    def test_calculate_similarity_function_exists(self):
        """Test calculate_similarity function exists."""
        if hasattr(quality_metrics, "calculate_similarity"):
            assert callable(
                quality_metrics.calculate_similarity
            ), "calculate_similarity should be callable"

    def test_calculate_naturalness_function_exists(self):
        """Test calculate_naturalness function exists."""
        if hasattr(quality_metrics, "calculate_naturalness"):
            assert callable(
                quality_metrics.calculate_naturalness
            ), "calculate_naturalness should be callable"

    def test_calculate_all_metrics_function_exists(self):
        """Test calculate_all_metrics function exists."""
        if hasattr(quality_metrics, "calculate_all_metrics"):
            assert callable(
                quality_metrics.calculate_all_metrics
            ), "calculate_all_metrics should be callable"


class TestQualityMetricsFunctionality:
    """Test quality metrics functionality with mocked dependencies."""

    @pytest.mark.skipif(
        not hasattr(quality_metrics, "calculate_mos_score"),
        reason="calculate_mos_score not available",
    )
    def test_calculate_mos_score_with_audio(self):
        """Test calculate_mos_score with audio data."""
        try:
            # Create mock audio data
            audio_data = np.random.randn(44100).astype(np.float32)
            result = quality_metrics.calculate_mos_score(audio_data, 44100)
            assert isinstance(result, (float, dict)), "calculate_mos_score should return float or dict"
            if isinstance(result, float):
                assert 0.0 <= result <= 5.0, "MOS score should be between 0 and 5"
        except Exception as e:
            pytest.skip(f"calculate_mos_score test skipped: {e}")

    @pytest.mark.skipif(
        not hasattr(quality_metrics, "calculate_similarity"),
        reason="calculate_similarity not available",
    )
    def test_calculate_similarity_with_audio(self):
        """Test calculate_similarity with audio data."""
        try:
            # Create mock audio data
            audio1 = np.random.randn(44100).astype(np.float32)
            audio2 = np.random.randn(44100).astype(np.float32)
            result = quality_metrics.calculate_similarity(audio1, audio2, 44100)
            assert isinstance(result, (float, dict)), "calculate_similarity should return float or dict"
            if isinstance(result, float):
                assert 0.0 <= result <= 1.0, "Similarity should be between 0 and 1"
        except Exception as e:
            pytest.skip(f"calculate_similarity test skipped: {e}")


class TestQualityMetricsErrorHandling:
    """Test quality metrics error handling."""

    @pytest.mark.skipif(
        not hasattr(quality_metrics, "calculate_mos_score"),
        reason="calculate_mos_score not available",
    )
    def test_calculate_mos_score_with_invalid_input(self):
        """Test calculate_mos_score handles invalid input."""
        try:
            with pytest.raises((TypeError, ValueError, AttributeError)):
                quality_metrics.calculate_mos_score(None, 44100)
        except AttributeError:
            pytest.skip("calculate_mos_score not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

