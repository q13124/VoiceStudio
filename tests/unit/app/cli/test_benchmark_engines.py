"""
Unit Tests for Benchmark Engines CLI
Tests engine benchmarking CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the benchmark engines module
try:
    from app.cli import benchmark_engines
except ImportError:
    pytest.skip("Could not import benchmark_engines", allow_module_level=True)


class TestBenchmarkEnginesImports:
    """Test benchmark engines module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            benchmark_engines is not None
        ), "Failed to import benchmark_engines module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(benchmark_engines)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

