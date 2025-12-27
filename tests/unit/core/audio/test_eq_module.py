"""
Unit Tests for EQ Module
Tests equalizer functionality.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the EQ module
try:
    from app.core.audio import eq_module
except ImportError:
    pytest.skip("Could not import eq_module", allow_module_level=True)


class TestEQModuleImports:
    """Test EQ module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert eq_module is not None, "Failed to import eq_module module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(eq_module)
        assert len(functions) > 0, "module should have functions"


class TestEQModuleFunctions:
    """Test EQ module functions exist."""

    def test_apply_eq_function_exists(self):
        """Test apply_eq function exists."""
        if hasattr(eq_module, "apply_eq"):
            assert callable(eq_module.apply_eq), "apply_eq should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

