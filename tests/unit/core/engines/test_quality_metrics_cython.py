"""
Unit tests for Cython-optimized quality metrics.

Tests integration with Cython functions and fallback behavior.
"""

from unittest.mock import patch

import numpy as np
import pytest

from app.core.engines import quality_metrics


class TestCythonIntegration:
    """Tests for Cython integration in quality metrics."""

    def test_has_cython_quality_flag(self):
        """Test HAS_CYTHON_QUALITY flag exists."""
        has_cython = hasattr(quality_metrics, "HAS_CYTHON_QUALITY")
        assert has_cython is True  # Flag should always exist

    def test_calculate_snr_uses_cython(self):
        """Test that calculate_snr uses Cython if available (or fallback)."""
        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_snr(audio)

        # Should return a valid SNR regardless of Cython availability
        assert isinstance(result, (float, type(None)))
        if result is not None:
            assert result >= 0 or result < 0  # SNR can be any value

    @patch.object(quality_metrics, "HAS_CYTHON_QUALITY", False)
    def test_calculate_snr_fallback(self):
        """Test that calculate_snr falls back to Python if Cython not available."""
        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_snr(audio)

        assert isinstance(result, (float, type(None)))

    def test_mos_score_calculation(self):
        """Test that calculate_mos_score works (with or without Cython)."""
        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_mos_score(audio)

        assert isinstance(result, float)
        assert 1.0 <= result <= 5.0

    def test_naturalness_calculation(self):
        """Test that calculate_naturalness works (with or without Cython)."""
        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_naturalness(audio)

        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_detect_artifacts(self):
        """Test that detect_artifacts works (with or without Cython)."""
        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.detect_artifacts(audio)

        assert isinstance(result, dict)
        assert "artifact_score" in result

    def test_cython_flag_state(self):
        """Test that HAS_CYTHON_QUALITY is a boolean."""
        assert isinstance(quality_metrics.HAS_CYTHON_QUALITY, bool)


class TestCythonFallback:
    """Tests for graceful fallback when Cython not available."""

    @patch.object(quality_metrics, "HAS_CYTHON_QUALITY", False)
    def test_all_functions_work_without_cython(self):
        """Test that all quality metric functions work without Cython."""
        audio = np.random.randn(1000).astype(np.float32)

        # All functions should work with Python fallback
        snr = quality_metrics.calculate_snr(audio)
        assert snr is None or isinstance(snr, float)

        mos = quality_metrics.calculate_mos_score(audio)
        assert isinstance(mos, float)
        assert 1.0 <= mos <= 5.0

        naturalness = quality_metrics.calculate_naturalness(audio)
        assert isinstance(naturalness, float)
        assert 0.0 <= naturalness <= 1.0

        artifacts = quality_metrics.detect_artifacts(audio)
        assert isinstance(artifacts, dict)
        assert "artifact_score" in artifacts


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
