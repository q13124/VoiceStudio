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
        """Test HAS_CYTHON_QUALITY flag."""
        # Should be False if Cython not compiled, True if compiled
        has_cython = hasattr(quality_metrics, "HAS_CYTHON_QUALITY")
        assert has_cython is True  # Flag should always exist

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", True)
    @patch("app.core.engines.quality_metrics.calculate_snr_cython_impl")
    def test_calculate_snr_uses_cython(self, mock_cython):
        """Test that calculate_snr uses Cython if available."""
        mock_cython.return_value = 25.5

        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_snr(audio)

        assert result == 25.5
        mock_cython.assert_called_once()

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", False)
    def test_calculate_snr_fallback(self):
        """Test that calculate_snr falls back to Python if Cython not available."""
        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_snr(audio)

        assert isinstance(result, float)
        assert result >= 0  # SNR should be non-negative

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", True)
    @patch("app.core.engines.quality_metrics.calculate_dynamic_range_cython")
    def test_mos_score_uses_cython(self, mock_cython_dr):
        """Test that calculate_mos_score uses Cython for dynamic range."""
        mock_cython_dr.return_value = 0.5

        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_mos_score(audio)

        assert isinstance(result, float)
        assert 1.0 <= result <= 5.0
        mock_cython_dr.assert_called()

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", True)
    @patch("app.core.engines.quality_metrics.calculate_zero_crossing_rate_cython")
    def test_naturalness_uses_cython(self, mock_cython_zcr):
        """Test that calculate_naturalness uses Cython for ZCR."""
        mock_cython_zcr.return_value = 0.05

        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_naturalness(audio)

        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0
        mock_cython_zcr.assert_called()

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", True)
    @patch("app.core.engines.quality_metrics.calculate_artifact_score_cython")
    def test_detect_artifacts_uses_cython(self, mock_cython_artifact):
        """Test that detect_artifacts uses Cython if available."""
        mock_cython_artifact.return_value = 0.3

        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.detect_artifacts(audio)

        assert "artifact_score" in result
        assert result["artifact_score"] == 0.3
        mock_cython_artifact.assert_called_once()

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", True)
    @patch("app.core.engines.quality_metrics.calculate_snr_cython_impl")
    def test_cython_error_fallback(self, mock_cython):
        """Test that errors in Cython functions fall back to Python."""
        mock_cython.side_effect = Exception("Cython error")

        audio = np.random.randn(1000).astype(np.float32)
        result = quality_metrics.calculate_snr(audio)

        # Should fall back to Python implementation
        assert isinstance(result, float)
        assert result >= 0


class TestCythonFallback:
    """Tests for graceful fallback when Cython not available."""

    @patch("app.core.engines.quality_metrics.HAS_CYTHON_QUALITY", False)
    def test_all_functions_work_without_cython(self):
        """Test that all quality metric functions work without Cython."""
        audio = np.random.randn(1000).astype(np.float32)

        # All functions should work with Python fallback
        snr = quality_metrics.calculate_snr(audio)
        assert isinstance(snr, float)

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

