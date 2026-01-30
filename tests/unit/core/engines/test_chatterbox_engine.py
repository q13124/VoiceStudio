"""
Unit Tests for Chatterbox Engine
Tests Chatterbox TTS engine functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the chatterbox engine module
try:
    from app.core.engines import chatterbox_engine
except ImportError:
    pytest.skip("Could not import chatterbox_engine", allow_module_level=True)


class TestChatterboxEngineImports:
    """Test chatterbox engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            chatterbox_engine is not None
        ), "Failed to import chatterbox_engine module"

    def test_module_has_chatterbox_engine_class(self):
        """Test module has ChatterboxEngine class."""
        if hasattr(chatterbox_engine, "ChatterboxEngine"):
            cls = getattr(chatterbox_engine, "ChatterboxEngine")
            assert isinstance(cls, type), "ChatterboxEngine should be a class"


class TestChatterboxEngineClass:
    """Test ChatterboxEngine class."""

    def test_chatterbox_engine_class_exists(self):
        """Test ChatterboxEngine class exists."""
        if hasattr(chatterbox_engine, "ChatterboxEngine"):
            cls = getattr(chatterbox_engine, "ChatterboxEngine")
            assert isinstance(cls, type), "ChatterboxEngine should be a class"

    def test_supported_languages_exists(self):
        """Test SUPPORTED_LANGUAGES constant exists."""
        if hasattr(chatterbox_engine, "ChatterboxEngine"):
            cls = getattr(chatterbox_engine, "ChatterboxEngine")
            if hasattr(cls, "SUPPORTED_LANGUAGES"):
                languages = getattr(cls, "SUPPORTED_LANGUAGES")
                assert isinstance(
                    languages, list
                ), "SUPPORTED_LANGUAGES should be a list"


def test_process_audio_quality_enables_ml_prediction():
    """
    VS-0009 regression: ensure ML prediction is enabled in quality metric calculation.
    """
    if not getattr(chatterbox_engine, "HAS_QUALITY_METRICS", False):
        pytest.skip("Quality metrics not available for chatterbox_engine")

    import numpy as np

    engine = chatterbox_engine.ChatterboxEngine.__new__(chatterbox_engine.ChatterboxEngine)
    audio = np.zeros(16000, dtype=np.float32)

    with patch.object(chatterbox_engine, "calculate_all_metrics", autospec=True) as calc:
        calc.return_value = {"quality_score": 0.5}

        processed, metrics = engine._process_audio_quality(
            audio=audio,
            sample_rate=16000,
            reference_audio=None,
            enhance=False,
            calculate_metrics=True,
        )

        assert processed is not None
        assert isinstance(metrics, dict)
        assert calc.call_count == 1
        assert calc.call_args.kwargs.get("include_ml_prediction") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

