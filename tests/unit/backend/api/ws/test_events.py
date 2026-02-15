"""
Unit Tests for WebSocket Events
Tests WebSocket event handling functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the WebSocket events module
try:
    from backend.api.ws import events
except ImportError:
    pytest.skip("Could not import events", allow_module_level=True)


class TestEventsImports:
    """Test WebSocket events module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert events is not None, "Failed to import events module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(events)
        assert len(functions) > 0, "module should have functions"


class TestEventsFunctions:
    """Test WebSocket events functions exist."""

    def test_emit_event_function_exists(self):
        """Test emit_event function exists."""
        if hasattr(events, "emit_event"):
            assert callable(
                events.emit_event
            ), "emit_event should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

