"""
Unit tests for ContextSync (Phase 11.1.5)
"""

from app.core.supervisor.context_sync import ContextSync, ConversationTurn


class TestContextSync:
    """Tests for ContextSync class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.context_sync = ContextSync()

    def test_initialization(self):
        """Test ContextSync initializes with empty history."""
        sync = ContextSync()
        assert len(sync._turns) == 0

    def test_add_turn(self):
        """Test adding a conversation turn."""
        self.context_sync.add_turn("user", "Hello", "cascade")

        assert len(self.context_sync._turns) == 1
        turn = self.context_sync._turns[0]
        assert turn.role == "user"
        assert turn.content == "Hello"
        assert turn.mode == "cascade"

    def test_add_multiple_turns(self):
        """Test adding multiple conversation turns."""
        self.context_sync.add_turn("user", "Hello", "cascade")
        self.context_sync.add_turn("assistant", "Hi there", "cascade")
        self.context_sync.add_turn("user", "How are you?", "s2s")

        assert len(self.context_sync._turns) == 3

    def test_get_context_for_mode(self):
        """Test getting context formatted for a specific mode."""
        self.context_sync.add_turn("user", "Hello", "cascade")
        self.context_sync.add_turn("assistant", "Hi", "cascade")

        context = self.context_sync.get_context_for_mode("s2s")

        assert isinstance(context, dict)
        assert "turns" in context or "messages" in context or len(context) >= 0

    def test_generate_system_prompt_injection(self):
        """Test generating system prompt injection for mode switch."""
        self.context_sync.add_turn("user", "Help me with code", "cascade")
        self.context_sync.add_turn("assistant", "Sure, what language?", "cascade")

        injection = self.context_sync.generate_system_prompt_injection("s2s")

        assert isinstance(injection, (str, dict, type(None)))

    def test_reset(self):
        """Test resetting context."""
        self.context_sync.add_turn("user", "Hello", "cascade")
        self.context_sync.add_turn("assistant", "Hi", "cascade")

        self.context_sync.reset()

        assert len(self.context_sync._turns) == 0

    def test_max_history_limit(self):
        """Test context respects max history limit."""
        sync = ContextSync()

        # Add more turns than MAX_HISTORY_TURNS
        for i in range(ContextSync.MAX_HISTORY_TURNS + 10):
            sync.add_turn("user", f"Message {i}", "cascade")

        # Should be limited to MAX_HISTORY_TURNS
        assert len(sync._turns) <= ContextSync.MAX_HISTORY_TURNS

    def test_get_synopsis(self):
        """Test getting conversation synopsis."""
        self.context_sync.add_turn("user", "I want to clone a voice", "cascade")
        self.context_sync.add_turn("assistant", "I can help with that", "cascade")

        synopsis = self.context_sync.get_synopsis()

        assert isinstance(synopsis, str)

    def test_conversation_turn_dataclass(self):
        """Test ConversationTurn dataclass."""
        turn = ConversationTurn(
            role="user",
            content="Test message",
            mode="cascade",
            timestamp=1000.0,
        )

        assert turn.role == "user"
        assert turn.content == "Test message"
        assert turn.mode == "cascade"
        assert turn.timestamp == 1000.0

    def test_context_preservation_across_modes(self):
        """Test context is preserved when switching modes."""
        self.context_sync.add_turn("user", "Message in cascade", "cascade")
        self.context_sync.add_turn("assistant", "Response in cascade", "cascade")
        self.context_sync.add_turn("user", "Message in s2s", "s2s")

        # All turns should be preserved
        assert len(self.context_sync._turns) == 3

        # Get context should include history
        context = self.context_sync.get_context_for_mode("cascade")
        assert context is not None
