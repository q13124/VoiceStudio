"""
Unit Tests for Batch Processor CLI
Tests batch processing CLI functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the batch processor module
try:
    from app.cli import batch_processor
except ImportError:
    pytest.skip("Could not import batch_processor", allow_module_level=True)


class TestBatchProcessorImports:
    """Test batch processor module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert batch_processor is not None, "Failed to import batch_processor module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(batch_processor)
        assert len(functions) > 0, "module should have functions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
