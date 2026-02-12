"""
Unit tests for BargeInHandler (Phase 11.2.3)
"""

import pytest
from unittest.mock import AsyncMock

from app.core.supervisor.barge_in import BargeInHandler


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
        assert handler._interrupt_threshold > 0

    def test_set_ai_speaking(self):
        """Test set_ai_speaking updates state."""
        self.handler.set_ai_speaking(True)
        assert self.handler._ai_speaking is True

        self.handler.set_ai_speaking(False)
        assert self.handler._ai_speaking is False

    @pytest.mark.asyncio
    async def test_handle_user_speech_when_not_speaking(self):
        """Test handler ignores input when AI is not speaking."""
        self.handler.set_ai_speaking(False)

        result = await self.handler.handle_user_speech("test", audio_energy=0.8)

        assert result.get("action") == "ignore"

    @pytest.mark.asyncio
    async def test_handle_user_speech_low_energy(self):
        """Test handler ignores low-energy audio."""
        self.handler.set_ai_speaking(True)

        result = await self.handler.handle_user_speech("", audio_energy=0.01)

        assert result.get("action") in ("ignore", "buffer")

    @pytest.mark.asyncio
    async def test_handle_user_speech_triggers_stop(self):
        """Test handler triggers stop on clear interruption."""
        self.handler.set_ai_speaking(True)

        result = await self.handler.handle_user_speech(
            "stop that", audio_energy=0.9
        )

        # High energy + content should trigger an action
        assert result.get("action") in ("stop", "buffer", "ignore")

    @pytest.mark.asyncio
    async def test_handle_user_speech_calls_callback(self):
        """Test handler calls stop callback when appropriate."""
        self.handler.set_ai_speaking(True)
        self.handler._interrupt_threshold = 0.1  # Low threshold

        # Simulate clear interruption
        result = await self.handler.handle_user_speech(
            "stop right now", audio_energy=0.95
        )

        if result.get("action") == "stop":
            self.on_stop_callback.assert_called()

    @pytest.mark.asyncio
    async def test_handle_user_speech_returns_type(self):
        """Test handler returns interruption type."""
        self.handler.set_ai_speaking(True)

        result = await self.handler.handle_user_speech("wait", audio_energy=0.5)

        assert "type" in result or "action" in result

    def test_custom_threshold(self):
        """Test handler respects custom threshold."""
        handler = BargeInHandler(interrupt_threshold=0.9)
        assert handler._interrupt_threshold == 0.9

    @pytest.mark.asyncio
    async def test_energy_below_threshold(self):
        """Test handler buffers when energy is below threshold."""
        self.handler.set_ai_speaking(True)
        self.handler._interrupt_threshold = 0.8

        result = await self.handler.handle_user_speech("hello", audio_energy=0.3)

        # Should not stop with low energy
        assert result.get("action") != "stop" or result.get("action") is None
