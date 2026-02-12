"""
Unit tests for FillerPhraseGenerator (Phase 11.1.4)
"""

import pytest

from app.core.supervisor.filler_generator import FillerPhraseGenerator


class TestFillerPhraseGenerator:
    """Tests for FillerPhraseGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = FillerPhraseGenerator()

    def test_initialization(self):
        """Test generator initializes correctly."""
        gen = FillerPhraseGenerator()
        assert gen._max_recent == 5
        assert len(gen._used_recently) == 0

    def test_get_filler_returns_string(self):
        """Test get_filler returns a string."""
        filler = self.generator.get_filler()

        assert isinstance(filler, str)
        assert len(filler) > 0

    def test_get_filler_thinking_category(self):
        """Test get_filler returns thinking phrases."""
        filler = self.generator.get_filler(category="thinking")

        assert filler in self.generator.THINKING_FILLERS

    def test_get_filler_processing_category(self):
        """Test get_filler returns processing phrases."""
        filler = self.generator.get_filler(category="processing")

        assert filler in self.generator.PROCESSING_FILLERS

    def test_get_filler_tool_category(self):
        """Test get_filler returns tool phrases."""
        filler = self.generator.get_filler(category="tool")

        assert filler in self.generator.TOOL_FILLERS

    def test_get_filler_acknowledgment_category(self):
        """Test get_filler returns acknowledgment phrases."""
        filler = self.generator.get_filler(category="acknowledgment")

        assert filler in self.generator.ACKNOWLEDGMENT_FILLERS

    def test_get_filler_unknown_category_defaults_to_thinking(self):
        """Test unknown category defaults to thinking."""
        filler = self.generator.get_filler(category="unknown")

        assert filler in self.generator.THINKING_FILLERS

    def test_get_filler_avoids_recent(self):
        """Test get_filler avoids recently used phrases."""
        used_fillers = set()

        # Get multiple fillers
        for _ in range(5):
            filler = self.generator.get_filler(category="thinking")
            used_fillers.add(filler)

        # Should have used different phrases
        assert len(used_fillers) > 1

    def test_get_filler_for_handoff_cascade(self):
        """Test get_filler_for_handoff to cascade mode."""
        filler = self.generator.get_filler_for_handoff("s2s", "cascade")

        assert filler in self.generator.THINKING_FILLERS

    def test_get_filler_for_handoff_s2s(self):
        """Test get_filler_for_handoff back to S2S."""
        filler = self.generator.get_filler_for_handoff("cascade", "s2s")

        assert filler in self.generator.ACKNOWLEDGMENT_FILLERS

    def test_get_filler_for_handoff_default(self):
        """Test get_filler_for_handoff default case."""
        filler = self.generator.get_filler_for_handoff("unknown", "unknown")

        assert filler in self.generator.PROCESSING_FILLERS

    def test_recent_history_clears_when_exhausted(self):
        """Test recent history clears when all phrases used."""
        gen = FillerPhraseGenerator()
        gen._max_recent = 2  # Small limit

        # Use more than _max_recent phrases
        for _ in range(10):
            gen.get_filler(category="acknowledgment")

        # Should not raise, history resets
        filler = gen.get_filler(category="acknowledgment")
        assert filler is not None

    def test_all_phrase_categories_have_content(self):
        """Test all phrase categories have at least one phrase."""
        assert len(self.generator.THINKING_FILLERS) > 0
        assert len(self.generator.PROCESSING_FILLERS) > 0
        assert len(self.generator.TOOL_FILLERS) > 0
        assert len(self.generator.ACKNOWLEDGMENT_FILLERS) > 0
