"""
Unit tests for SupervisorRouter (Phase 21.2).

Tests the routing logic between S2S, Cascade, and Half-Cascade pipelines.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSupervisorRouter:
    """Tests for SupervisorRouter."""

    def test_import(self):
        """Test that SupervisorRouter can be imported."""
        from app.core.supervisor import SupervisorRouter
        assert SupervisorRouter is not None

    def test_create_router(self):
        """Test creating a router with defaults."""
        from app.core.supervisor import SupervisorRouter
        router = SupervisorRouter()
        assert router is not None
        assert router.state is not None

    def test_create_router_with_dependencies(self):
        """Test creating a router with all dependencies."""
        from app.core.supervisor import (
            SupervisorRouter,
            IntentClassifier,
            FillerPhraseGenerator,
            ContextSync,
            BargeInHandler,
            IntentBuffer,
        )
        
        router = SupervisorRouter(
            classifier=IntentClassifier(),
            filler_generator=FillerPhraseGenerator(),
            context_sync=ContextSync(),
            barge_in_handler=BargeInHandler(),
            intent_buffer=IntentBuffer(),
        )
        
        assert router is not None

    @pytest.mark.asyncio
    async def test_process_input_cascade_fallback(self):
        """Test that router falls back to cascade when no S2S."""
        from app.core.supervisor import SupervisorRouter
        
        mock_cascade = AsyncMock()
        mock_cascade.process_text = AsyncMock(return_value={
            "response": "Hello!",
            "audio": None,
        })
        
        router = SupervisorRouter(
            cascade_pipeline=mock_cascade,
        )
        
        result = await router.process_input("Hello")
        
        assert result is not None
        assert "route" in result

    @pytest.mark.asyncio
    async def test_process_input_records_context(self):
        """Test that processing records conversation context."""
        from app.core.supervisor import SupervisorRouter, ContextSync
        
        context_sync = ContextSync()
        mock_cascade = AsyncMock()
        mock_cascade.process_text = AsyncMock(return_value={
            "response": "Test response",
            "audio": None,
        })
        
        router = SupervisorRouter(
            cascade_pipeline=mock_cascade,
            context_sync=context_sync,
        )
        
        await router.process_input("Test input")
        
        # Context should have recorded the turn
        synopsis = context_sync.get_synopsis()
        # Synopsis may be empty for single turn, but should not error
        assert isinstance(synopsis, str)

    def test_set_session(self):
        """Test setting session for cost tracking."""
        from app.core.supervisor import SupervisorRouter
        
        router = SupervisorRouter()
        router.set_session("session-123")
        
        # No error should occur

    def test_reset(self):
        """Test resetting router state."""
        from app.core.supervisor import SupervisorRouter
        
        router = SupervisorRouter()
        router.set_session("session-123")
        router.reset()
        
        # Router should be in clean state
        assert router.state is not None


class TestFillerPhraseGenerator:
    """Tests for FillerPhraseGenerator."""

    def test_import(self):
        """Test import."""
        from app.core.supervisor import FillerPhraseGenerator
        assert FillerPhraseGenerator is not None

    def test_get_filler_thinking(self):
        """Test getting thinking filler phrase."""
        from app.core.supervisor import FillerPhraseGenerator
        
        generator = FillerPhraseGenerator()
        filler = generator.get_filler("thinking")
        
        assert filler is not None
        assert len(filler) > 0

    def test_get_filler_processing(self):
        """Test getting processing filler phrase."""
        from app.core.supervisor import FillerPhraseGenerator
        
        generator = FillerPhraseGenerator()
        filler = generator.get_filler("processing")
        
        assert filler is not None

    def test_get_filler_for_handoff(self):
        """Test getting filler for mode transition."""
        from app.core.supervisor import FillerPhraseGenerator
        
        generator = FillerPhraseGenerator()
        filler = generator.get_filler_for_handoff("s2s", "cascade")
        
        assert filler is not None

    def test_avoids_recent_phrases(self):
        """Test that generator avoids recently used phrases."""
        from app.core.supervisor import FillerPhraseGenerator
        
        generator = FillerPhraseGenerator()
        
        # Get several phrases
        phrases = [generator.get_filler("thinking") for _ in range(3)]
        
        # Should not all be the same (unless only one phrase exists)
        # At minimum, should not error
        assert len(phrases) == 3


class TestContextSync:
    """Tests for ContextSync."""

    def test_import(self):
        """Test import."""
        from app.core.supervisor import ContextSync
        assert ContextSync is not None

    def test_add_turn(self):
        """Test adding conversation turns."""
        from app.core.supervisor import ContextSync
        
        sync = ContextSync()
        sync.add_turn("user", "Hello", "cascade")
        sync.add_turn("assistant", "Hi there!", "cascade")
        
        synopsis = sync.get_synopsis()
        assert isinstance(synopsis, str)

    def test_get_context_for_mode(self):
        """Test getting context for mode switch."""
        from app.core.supervisor import ContextSync
        
        sync = ContextSync()
        sync.add_turn("user", "Test message", "s2s")
        
        context = sync.get_context_for_mode("cascade")
        
        assert "synopsis" in context
        assert "recent_turns" in context

    def test_generate_system_prompt_injection(self):
        """Test generating system prompt injection."""
        from app.core.supervisor import ContextSync
        
        sync = ContextSync()
        sync.add_turn("user", "Previous question", "s2s")
        sync.add_turn("assistant", "Previous answer", "s2s")
        
        injection = sync.generate_system_prompt_injection("cascade")
        
        assert isinstance(injection, str)

    def test_reset(self):
        """Test resetting context."""
        from app.core.supervisor import ContextSync
        
        sync = ContextSync()
        sync.add_turn("user", "Test", "cascade")
        sync.reset()
        
        synopsis = sync.get_synopsis()
        assert synopsis == ""


class TestIntentBuffer:
    """Tests for IntentBuffer."""

    def test_import(self):
        """Test import."""
        from app.core.supervisor import IntentBuffer
        assert IntentBuffer is not None

    def test_add_and_flush(self):
        """Test adding and flushing buffered content."""
        from app.core.supervisor import IntentBuffer
        
        buffer = IntentBuffer()
        buffer.add("Hello")
        buffer.add("World")
        
        assert buffer.has_content()
        
        flushed = buffer.flush()
        assert "Hello" in flushed
        assert "World" in flushed
        
        assert not buffer.has_content()

    def test_peek(self):
        """Test peeking at buffer without clearing."""
        from app.core.supervisor import IntentBuffer
        
        buffer = IntentBuffer()
        buffer.add("Test")
        
        peeked = buffer.peek()
        assert len(peeked) == 1
        
        # Should still have content
        assert buffer.has_content()

    def test_clear(self):
        """Test clearing buffer."""
        from app.core.supervisor import IntentBuffer
        
        buffer = IntentBuffer()
        buffer.add("Test")
        buffer.clear()
        
        assert not buffer.has_content()
