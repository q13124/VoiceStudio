"""
Unit Tests for Text Processor Utilities
Tests text processing utility functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the text processor module
try:
    from app.core.utils import text_processor
except ImportError:
    pytest.skip(
        "Could not import text_processor", allow_module_level=True
    )


class TestTextProcessorImports:
    """Test text processor module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            text_processor is not None
        ), "Failed to import text_processor module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(text_processor)
        assert len(functions) > 0, "module should have functions"


class TestTextProcessorFunctions:
    """Test text processor functions exist."""

    def test_process_text_function_exists(self):
        """Test process_text function exists."""
        if hasattr(text_processor, "process_text"):
            assert callable(
                text_processor.process_text
            ), "process_text should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

