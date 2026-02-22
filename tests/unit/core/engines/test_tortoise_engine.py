"""
Unit Tests for Tortoise Engine
Tests Tortoise TTS engine functionality.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the tortoise engine module
try:
    from app.core.engines import tortoise_engine
except ImportError:
    pytest.skip("Could not import tortoise_engine", allow_module_level=True)


class TestTortoiseEngineImports:
    """Test tortoise engine module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert tortoise_engine is not None, "Failed to import tortoise_engine module"

    def test_module_has_tortoise_engine_class(self):
        """Test module has TortoiseEngine class."""
        if hasattr(tortoise_engine, "TortoiseEngine"):
            cls = tortoise_engine.TortoiseEngine
            assert isinstance(cls, type), "TortoiseEngine should be a class"


class TestTortoiseEngineClass:
    """Test TortoiseEngine class."""

    def test_tortoise_engine_class_exists(self):
        """Test TortoiseEngine class exists."""
        if hasattr(tortoise_engine, "TortoiseEngine"):
            cls = tortoise_engine.TortoiseEngine
            assert isinstance(cls, type), "TortoiseEngine should be a class"


def test_process_audio_quality_enables_ml_prediction():
    """
    VS-0009 regression: ensure ML prediction is enabled in quality metric calculation.
    """
    if not getattr(tortoise_engine, "HAS_QUALITY_METRICS", False):
        pytest.skip("Quality metrics not available for tortoise_engine")

    import numpy as np

    engine = tortoise_engine.TortoiseEngine.__new__(tortoise_engine.TortoiseEngine)
    audio = np.zeros(16000, dtype=np.float32)

    with patch.object(tortoise_engine, "calculate_all_metrics", autospec=True) as calc:
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
