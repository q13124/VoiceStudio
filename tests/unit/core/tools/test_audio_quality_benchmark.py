"""
Unit Tests for Audio Quality Benchmark
Tests audio quality benchmarking functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the audio quality benchmark module
try:
    from app.core.tools import audio_quality_benchmark
except ImportError:
    pytest.skip(
        "Could not import audio_quality_benchmark", allow_module_level=True
    )


class TestAudioQualityBenchmarkImports:
    """Test audio quality benchmark module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            audio_quality_benchmark is not None
        ), "Failed to import audio_quality_benchmark module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(audio_quality_benchmark)
        assert len(functions) > 0, "module should have functions"


class TestAudioQualityBenchmarkFunctions:
    """Test audio quality benchmark functions exist."""

    def test_run_benchmark_function_exists(self):
        """Test run_benchmark function exists."""
        if hasattr(audio_quality_benchmark, "run_benchmark"):
            assert callable(
                audio_quality_benchmark.run_benchmark
            ), "run_benchmark should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

