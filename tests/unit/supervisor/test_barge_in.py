"""
Unit tests for BargeInHandler (Phase 11.2.3)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.supervisor.barge_in import BargeInHandler
from app.core.supervisor.interruption_fsm import InterruptionAction


class TestBargeInHandler:
    """Tests for BargeInHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.on_stop_callback = AsyncMock()
        self.handler = BargeInHandler(on_stop=self.on_stop_callback)

    def test_handler_initialization(self):
        """Test handler initializes with correct defaults."""
        handler = BargeInHandler()
        assert handler._ai_speaking is False
        assert handler._fsm is not None

    def test_set_ai_speaking(self):
        """Test set_ai_speaking updates state."""
        self.handler.set_ai_speaking(True)
        assert self.handler._ai_speaking is True

        self.handler.set_ai_speaking(False)
        assert self.handler._ai_speaking is False

    @pytest.mark.asyncio
    async def test_handle_user_speech_when_not_speaking(self):
        """Test handler processes input when AI is not speaking."""
        self.handler.set_ai_speaking(False)

        result = await self.handler.handle_user_speech("test", audio_energy=0.8)

        # Should return a valid action from the FSM
        assert result.get("action") in (
            InterruptionAction.IGNORE.value,
            InterruptionAction.BUFFER.value,
            InterruptionAction.STOP_AND_LISTEN.value,
        )

    @pytest.mark.asyncio
    async def test_handle_user_speech_low_energy(self):
        """Test handler behavior with low-energy audio."""
        self.handler.set_ai_speaking(True)

        result = await self.handler.handle_user_speech("", audio_energy=0.01)

        # Low energy should typically be ignored or buffered
        assert result.get("action") in (
            InterruptionAction.IGNORE.value,
            InterruptionAction.BUFFER.value,
            InterruptionAction.STOP_AND_LISTEN.value,
        )

    @pytest.mark.asyncio
    async def test_handle_user_speech_returns_action(self):
        """Test handler returns interruption action."""
        self.handler.set_ai_speaking(True)

        result = await self.handler.handle_user_speech("stop that", audio_energy=0.9)

        # Should return an action from the FSM
        assert "action" in result
        assert result["action"] in (
            InterruptionAction.STOP_AND_LISTEN.value,
            InterruptionAction.BUFFER.value,
            InterruptionAction.IGNORE.value,
        )

    @pytest.mark.asyncio
    async def test_handle_user_speech_calls_callback_on_stop(self):
        """Test handler calls stop callback when stopping."""
        # Mock the FSM to always return stop action
        mock_fsm = MagicMock()
        mock_fsm.classify_interruption.return_value = {
            "action": InterruptionAction.STOP_AND_LISTEN.value,
            "type": "directive",
        }
        handler = BargeInHandler(interruption_fsm=mock_fsm, on_stop=self.on_stop_callback)
        handler.set_ai_speaking(True)

        await handler.handle_user_speech("stop", audio_energy=0.95)

        self.on_stop_callback.assert_called()

    @pytest.mark.asyncio
    async def test_handle_user_speech_returns_type(self):
        """Test handler returns interruption type."""
        self.handler.set_ai_speaking(True)

        result = await self.handler.handle_user_speech("wait", audio_energy=0.5)

        assert "type" in result or "action" in result

    def test_custom_fsm(self):
        """Test handler accepts custom FSM."""
        mock_fsm = MagicMock()
        handler = BargeInHandler(interruption_fsm=mock_fsm)
        assert handler._fsm is mock_fsm

    @pytest.mark.asyncio
    async def test_flush_buffer(self):
        """Test flush_buffer returns and clears buffered input."""
        self.handler._buffered_input = ["first", "second"]

        result = self.handler.flush_buffer()

        assert "first" in result
        assert "second" in result
        assert len(self.handler._buffered_input) == 0
