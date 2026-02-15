"""
Unit tests for IntentBuffer (Phase 11.2.4)
"""


from app.core.supervisor.intent_buffer import BufferedUtterance, IntentBuffer


class TestIntentBuffer:
    """Tests for IntentBuffer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.buffer = IntentBuffer()

    def test_initialization(self):
        """Test buffer initializes empty."""
        buffer = IntentBuffer()
        assert len(buffer._utterances) == 0

    def test_add_utterance(self):
        """Test adding an utterance to the buffer."""
        self.buffer.add(
            text="Hello",
            audio_energy=0.5,
            interruption_type="cooperative",
        )

        assert len(self.buffer._utterances) == 1

    def test_add_multiple_utterances(self):
        """Test adding multiple utterances."""
        self.buffer.add(text="First", audio_energy=0.4)
        self.buffer.add(text="Second", audio_energy=0.6)
        self.buffer.add(text="Third", audio_energy=0.5)

        assert len(self.buffer._utterances) == 3

    def test_flush_returns_combined_text(self):
        """Test flush returns combined text from all utterances."""
        self.buffer.add(text="Hello", audio_energy=0.5)
        self.buffer.add(text="world", audio_energy=0.5)

        result = self.buffer.flush()

        assert "Hello" in result
        assert "world" in result

    def test_flush_clears_buffer(self):
        """Test flush clears the buffer."""
        self.buffer.add(text="Test", audio_energy=0.5)
        self.buffer.flush()

        assert len(self.buffer._utterances) == 0

    def test_flush_empty_buffer_returns_empty(self):
        """Test flush on empty buffer returns empty string."""
        result = self.buffer.flush()

        assert result == ""

    def test_clear(self):
        """Test clear empties the buffer."""
        self.buffer.add(text="Test", audio_energy=0.5)
        self.buffer.clear()

        assert len(self.buffer._utterances) == 0

    def test_is_empty(self):
        """Test is_empty property."""
        assert self.buffer.is_empty()

        self.buffer.add(text="Test", audio_energy=0.5)
        assert not self.buffer.is_empty()

    def test_max_buffer_size(self):
        """Test buffer respects max size limit."""
        buffer = IntentBuffer(max_size=3)

        for i in range(10):
            buffer.add(text=f"Message {i}", audio_energy=0.5)

        # Should be limited to max_size
        assert len(buffer._utterances) <= 3

    def test_buffered_utterance_dataclass(self):
        """Test BufferedUtterance dataclass."""
        utterance = BufferedUtterance(
            text="Test",
            audio_energy=0.75,
            interruption_type="directive",
            timestamp=1000.0,
        )

        assert utterance.text == "Test"
        assert utterance.audio_energy == 0.75
        assert utterance.interruption_type == "directive"
        assert utterance.timestamp == 1000.0

    def test_get_last_utterance(self):
        """Test getting the last utterance."""
        self.buffer.add(text="First", audio_energy=0.4)
        self.buffer.add(text="Last", audio_energy=0.6)

        last = self.buffer.get_last()

        assert last is not None
        assert last.text == "Last"

    def test_get_last_empty_buffer(self):
        """Test getting last from empty buffer returns None."""
        last = self.buffer.get_last()

        assert last is None

    def test_utterances_ordered_by_time(self):
        """Test utterances maintain order."""
        self.buffer.add(text="First", audio_energy=0.5)
        self.buffer.add(text="Second", audio_energy=0.5)
        self.buffer.add(text="Third", audio_energy=0.5)

        # Flush should preserve order
        result = self.buffer.flush()

        first_idx = result.find("First")
        second_idx = result.find("Second")
        third_idx = result.find("Third")

        # Should be in order (if all found)
        if first_idx >= 0 and second_idx >= 0:
            assert first_idx < second_idx
        if second_idx >= 0 and third_idx >= 0:
            assert second_idx < third_idx
