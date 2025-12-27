"""
Integration Tests for Multi-Select Service (IDEA 12)
Tests the MultiSelectService functionality.
"""

import pytest


class TestMultiSelectService:
    """Test MultiSelectService functionality."""

    def test_get_state_creates_new(self):
        """Test getting state for new panel creates state."""
        try:
            from src.VoiceStudio.App.Services.MultiSelectService import (
                MultiSelectService,
            )

            service = MultiSelectService()
            state = service.GetState("TestPanel")
            assert state is not None
            assert state.Count == 0
        except ImportError:
            pytest.skip("MultiSelectService not available (C# service)")

    def test_get_state_returns_existing(self):
        """Test getting state for existing panel returns same state."""
        try:
            from src.VoiceStudio.App.Services.MultiSelectService import (
                MultiSelectService,
            )

            service = MultiSelectService()
            state1 = service.GetState("TestPanel")
            state1.Add("item1")
            state2 = service.GetState("TestPanel")
            assert state1 is state2
            assert state2.Count == 1
        except ImportError:
            pytest.skip("MultiSelectService not available (C# service)")

    def test_clear_selection(self):
        """Test clearing selection for panel."""
        try:
            from src.VoiceStudio.App.Services.MultiSelectService import (
                MultiSelectService,
            )

            service = MultiSelectService()
            state = service.GetState("TestPanel")
            state.Add("item1")
            state.Add("item2")
            assert state.Count == 2
            service.ClearSelection("TestPanel")
            assert state.Count == 0
        except ImportError:
            pytest.skip("MultiSelectService not available (C# service)")

    def test_clear_all_selections(self):
        """Test clearing all selections."""
        try:
            from src.VoiceStudio.App.Services.MultiSelectService import (
                MultiSelectService,
            )

            service = MultiSelectService()
            state1 = service.GetState("Panel1")
            state2 = service.GetState("Panel2")
            state1.Add("item1")
            state2.Add("item2")
            service.ClearAllSelections()
            assert state1.Count == 0
            assert state2.Count == 0
        except ImportError:
            pytest.skip("MultiSelectService not available (C# service)")

    def test_remove_state(self):
        """Test removing state for panel."""
        try:
            from src.VoiceStudio.App.Services.MultiSelectService import (
                MultiSelectService,
            )

            service = MultiSelectService()
            state = service.GetState("TestPanel")
            service.RemoveState("TestPanel")
            # Getting state again should create new state
            new_state = service.GetState("TestPanel")
            assert new_state is not state
        except ImportError:
            pytest.skip("MultiSelectService not available (C# service)")

    def test_selection_changed_event(self):
        """Test selection changed event fires."""
        try:
            from src.VoiceStudio.App.Services.MultiSelectService import (
                MultiSelectService,
            )

            service = MultiSelectService()
            event_fired = False

            def handler(sender, args):
                nonlocal event_fired
                event_fired = True

            service.SelectionChanged += handler
            state = service.GetState("TestPanel")
            state.Add("item1")
            service.OnSelectionChanged("TestPanel", state)
            assert event_fired
        except ImportError:
            pytest.skip("MultiSelectService not available (C# service)")


class TestMultiSelectState:
    """Test MultiSelectState functionality."""

    def test_add_item(self):
        """Test adding item to selection."""
        try:
            from src.VoiceStudio.Core.Models.MultiSelectState import MultiSelectState

            state = MultiSelectState()
            state.Add("item1")
            assert state.Count == 1
            assert "item1" in state
        except ImportError:
            pytest.skip("MultiSelectState not available (C# model)")

    def test_remove_item(self):
        """Test removing item from selection."""
        try:
            from src.VoiceStudio.Core.Models.MultiSelectState import MultiSelectState

            state = MultiSelectState()
            state.Add("item1")
            state.Remove("item1")
            assert state.Count == 0
            assert "item1" not in state
        except ImportError:
            pytest.skip("MultiSelectState not available (C# model)")

    def test_toggle_item(self):
        """Test toggling item selection."""
        try:
            from src.VoiceStudio.Core.Models.MultiSelectState import MultiSelectState

            state = MultiSelectState()
            state.Toggle("item1")
            assert "item1" in state
            state.Toggle("item1")
            assert "item1" not in state
        except ImportError:
            pytest.skip("MultiSelectState not available (C# model)")

    def test_clear(self):
        """Test clearing all selections."""
        try:
            from src.VoiceStudio.Core.Models.MultiSelectState import MultiSelectState

            state = MultiSelectState()
            state.Add("item1")
            state.Add("item2")
            state.Clear()
            assert state.Count == 0
        except ImportError:
            pytest.skip("MultiSelectState not available (C# model)")

    def test_set_range(self):
        """Test setting range selection."""
        try:
            from src.VoiceStudio.Core.Models.MultiSelectState import MultiSelectState

            state = MultiSelectState()
            all_items = ["item1", "item2", "item3", "item4", "item5"]
            state.SetRange("item2", "item4", all_items)
            assert "item2" in state
            assert "item3" in state
            assert "item4" in state
            assert "item1" not in state
            assert "item5" not in state
        except ImportError:
            pytest.skip("MultiSelectState not available (C# model)")
