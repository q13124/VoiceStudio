"""
Integration tests for TTS utility libraries (gTTS, pyttsx3).
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.tts.tts_utilities import (
    GTTSWrapper,
    Pyttsx3Wrapper,
    get_gtts,
    get_pyttsx3,
    synthesize_with_utility,
)


class TestGTTSWrapper:
    """Tests for gTTS wrapper."""

    def test_gtts_initialization(self):
        """Test gTTS wrapper initialization."""
        pytest.importorskip("gtts")

        wrapper = GTTSWrapper()
        assert wrapper.available is True

    def test_gtts_synthesize(self):
        """Test gTTS synthesis."""
        pytest.importorskip("gtts")

        wrapper = GTTSWrapper()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = wrapper.synthesize(
                "Hello, this is a test.", language="en", output_path=str(temp_path)
            )
            assert result == str(temp_path)
            assert temp_path.exists()
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_gtts_get_languages(self):
        """Test getting available languages."""
        pytest.importorskip("gtts")

        wrapper = GTTSWrapper()
        languages = wrapper.get_available_languages()
        assert isinstance(languages, list)
        assert "en" in languages

    def test_gtts_language_support(self):
        """Test language support check."""
        pytest.importorskip("gtts")

        wrapper = GTTSWrapper()
        assert wrapper.is_language_supported("en") is True
        assert wrapper.is_language_supported("es") is True


class TestPyttsx3Wrapper:
    """Tests for pyttsx3 wrapper."""

    def test_pyttsx3_initialization(self):
        """Test pyttsx3 wrapper initialization."""
        pytest.importorskip("pyttsx3")

        wrapper = Pyttsx3Wrapper()
        assert wrapper.available is True
        assert wrapper.engine is not None

    def test_pyttsx3_synthesize(self):
        """Test pyttsx3 synthesis."""
        pytest.importorskip("pyttsx3")

        wrapper = Pyttsx3Wrapper()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = wrapper.synthesize("Hello, this is a test.", output_path=str(temp_path))
            assert result == str(temp_path)
            assert temp_path.exists()
        finally:
            if temp_path.exists():
                temp_path.unlink()
            wrapper.cleanup()

    def test_pyttsx3_get_voices(self):
        """Test getting available voices."""
        pytest.importorskip("pyttsx3")

        wrapper = Pyttsx3Wrapper()
        voices = wrapper.get_available_voices()
        assert isinstance(voices, list)
        wrapper.cleanup()

    def test_pyttsx3_get_properties(self):
        """Test getting TTS properties."""
        pytest.importorskip("pyttsx3")

        wrapper = Pyttsx3Wrapper()
        properties = wrapper.get_properties()
        assert isinstance(properties, dict)
        assert "rate" in properties
        assert "volume" in properties
        wrapper.cleanup()

    def test_pyttsx3_cleanup(self):
        """Test pyttsx3 cleanup."""
        pytest.importorskip("pyttsx3")

        wrapper = Pyttsx3Wrapper()
        wrapper.cleanup()
        assert wrapper.available is False
        assert wrapper.engine is None


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_gtts(self):
        """Test getting gTTS instance."""
        pytest.importorskip("gtts")

        wrapper = get_gtts()
        assert wrapper is not None
        assert isinstance(wrapper, GTTSWrapper)

    def test_get_pyttsx3(self):
        """Test getting pyttsx3 instance."""
        pytest.importorskip("pyttsx3")

        wrapper = get_pyttsx3()
        assert wrapper is not None
        assert isinstance(wrapper, Pyttsx3Wrapper)
        wrapper.cleanup()

    def test_synthesize_with_utility_gtts(self):
        """Test synthesize_with_utility using gTTS."""
        pytest.importorskip("gtts")

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = synthesize_with_utility(
                "Test text", utility="gtts", language="en", output_path=str(temp_path)
            )
            assert result == str(temp_path)
            assert temp_path.exists()
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_synthesize_with_utility_pyttsx3(self):
        """Test synthesize_with_utility using pyttsx3."""
        pytest.importorskip("pyttsx3")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = synthesize_with_utility(
                "Test text", utility="pyttsx3", output_path=str(temp_path)
            )
            assert result == str(temp_path)
            assert temp_path.exists()
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_synthesize_with_utility_invalid(self):
        """Test synthesize_with_utility with invalid utility."""
        with pytest.raises(ValueError):
            synthesize_with_utility("Test", utility="invalid")
