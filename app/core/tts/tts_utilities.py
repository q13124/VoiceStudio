"""
Text-to-Speech Utility Libraries
Integrates gTTS and pyttsx3 as fallback/utility TTS engines.
Part of FREE_LIBRARIES_INTEGRATION - Worker 3.
"""

from __future__ import annotations

import contextlib
import logging
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Try importing TTS utility libraries
try:
    from gtts import gTTS

    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    logger.warning("gTTS not installed, Google TTS utility unavailable")

try:
    import pyttsx3

    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    logger.warning("pyttsx3 not installed, system TTS utility unavailable")


class GTTSWrapper:
    """
    Wrapper for Google Text-to-Speech (gTTS).
    Provides simple TTS synthesis using Google's TTS service.
    """

    def __init__(self):
        """Initialize gTTS wrapper."""
        if not HAS_GTTS:
            raise ImportError("gTTS not installed. Install with: pip install gtts")
        self.available = True

    def synthesize(
        self,
        text: str,
        language: str = "en",
        slow: bool = False,
        output_path: str | Path | None = None,
        **kwargs,
    ) -> np.ndarray | str | tuple[Any, Any] | None:
        """
        Synthesize speech using Google TTS.

        Args:
            text: Text to synthesize
            language: Language code (ISO 639-1)
            slow: Whether to speak slowly
            output_path: Optional output file path
            **kwargs: Additional parameters

        Returns:
            Audio array, (audio, sample_rate) tuple, or output path string
        """
        if not self.available:
            raise RuntimeError("gTTS not available")

        try:
            # Create gTTS instance
            tts = gTTS(text=text, lang=language, slow=slow)

            # Save to file
            if output_path is None:
                output_path = tempfile.mktemp(suffix=".mp3")

            output_path = Path(output_path)
            tts.save(str(output_path))

            logger.info(f"gTTS synthesized text to {output_path}")

            # If output_path provided, return path; otherwise load and return audio
            if kwargs.get("return_audio"):
                try:
                    import soundfile as sf

                    audio, sr = sf.read(str(output_path))
                    return audio, sr
                except ImportError:
                    logger.warning("soundfile not available, returning file path")
                    return str(output_path)

            return str(output_path)

        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            raise

    def get_available_languages(self) -> list:
        """Get list of available languages."""
        if not HAS_GTTS:
            return []

        try:
            from gtts.lang import tts_langs

            return list(tts_langs().keys())
        except Exception as e:
            logger.warning(f"Failed to get gTTS languages: {e}")
            return ["en"]  # Default to English

    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported."""
        return language in self.get_available_languages()


class Pyttsx3Wrapper:
    """
    Wrapper for pyttsx3 (offline TTS using system voices).
    Provides offline TTS synthesis using system TTS engines.
    """

    def __init__(self):
        """Initialize pyttsx3 wrapper."""
        if not HAS_PYTTSX3:
            raise ImportError("pyttsx3 not installed. Install with: pip install pyttsx3")

        try:
            self.engine = pyttsx3.init()
            self.available = True
            logger.info("pyttsx3 initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.engine = None
            self.available = False

    def synthesize(
        self,
        text: str,
        output_path: str | Path | None = None,
        rate: int | None = None,
        volume: float | None = None,
        voice_id: str | None = None,
        **kwargs,
    ) -> np.ndarray | str | tuple[Any, Any] | None:
        """
        Synthesize speech using system TTS.

        Args:
            text: Text to synthesize
            output_path: Optional output file path
            rate: Speech rate (words per minute)
            volume: Volume (0.0 to 1.0)
            voice_id: Optional voice ID
            **kwargs: Additional parameters

        Returns:
            Audio array, (audio, sample_rate) tuple, or output path string
        """
        if not self.available or self.engine is None:
            raise RuntimeError("pyttsx3 not available")

        try:
            # Set properties
            if rate is not None:
                self.engine.setProperty("rate", rate)

            if volume is not None:
                self.engine.setProperty("volume", min(max(volume, 0.0), 1.0))

            if voice_id is not None:
                voices = self.engine.getProperty("voices")
                for voice in voices:
                    if voice.id == voice_id:
                        self.engine.setProperty("voice", voice.id)
                        break

            # Save to file if output_path provided
            if output_path is not None:
                output_path = Path(output_path)
                self.engine.save_to_file(text, str(output_path))
                self.engine.runAndWait()
                logger.info(f"pyttsx3 synthesized text to {output_path}")

                # If return_audio requested, load and return
                if kwargs.get("return_audio"):
                    try:
                        import soundfile as sf

                        audio, sr = sf.read(str(output_path))
                        return audio, sr
                    except ImportError:
                        logger.warning("soundfile not available, returning file path")
                        return str(output_path)

                return str(output_path)
            else:
                # Speak directly (no file output)
                self.engine.say(text)
                self.engine.runAndWait()
                return None

        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            raise

    def get_available_voices(self) -> list:
        """Get list of available system voices."""
        if not self.available or self.engine is None:
            return []

        try:
            voices = self.engine.getProperty("voices")
            return [
                {"id": voice.id, "name": voice.name, "languages": getattr(voice, "languages", [])}
                for voice in voices
            ]
        except Exception as e:
            logger.warning(f"Failed to get pyttsx3 voices: {e}")
            return []

    def get_properties(self) -> dict[str, Any]:
        """Get current TTS properties."""
        if not self.available or self.engine is None:
            return {}

        try:
            return {
                "rate": self.engine.getProperty("rate"),
                "volume": self.engine.getProperty("volume"),
                "voice": self.engine.getProperty("voice"),
            }
        except Exception as e:
            logger.warning(f"Failed to get pyttsx3 properties: {e}")
            return {}

    def cleanup(self):
        """Clean up pyttsx3 engine."""
        if self.engine is not None:
            with contextlib.suppress(Exception):
                self.engine.stop()
            self.engine = None
            self.available = False


# Global instances
_gtts_instance: GTTSWrapper | None = None
_pyttsx3_instance: Pyttsx3Wrapper | None = None


def get_gtts() -> GTTSWrapper | None:
    """Get global gTTS wrapper instance."""
    global _gtts_instance
    if _gtts_instance is None and HAS_GTTS:
        try:
            _gtts_instance = GTTSWrapper()
        except Exception as e:
            logger.warning(f"Failed to create gTTS wrapper: {e}")
            return None
    return _gtts_instance


def get_pyttsx3() -> Pyttsx3Wrapper | None:
    """Get global pyttsx3 wrapper instance."""
    global _pyttsx3_instance
    if _pyttsx3_instance is None and HAS_PYTTSX3:
        try:
            _pyttsx3_instance = Pyttsx3Wrapper()
        except Exception as e:
            logger.warning(f"Failed to create pyttsx3 wrapper: {e}")
            return None
    return _pyttsx3_instance


def synthesize_with_utility(
    text: str,
    utility: str = "gtts",
    language: str = "en",
    output_path: str | Path | None = None,
    **kwargs,
) -> np.ndarray | str | tuple[Any, Any] | None:
    """
    Synthesize text using a TTS utility library.

    Args:
        text: Text to synthesize
        utility: Utility to use ('gtts' or 'pyttsx3')
        language: Language code (for gTTS)
        output_path: Optional output file path
        **kwargs: Additional parameters

    Returns:
        Audio array or output path
    """
    if utility == "gtts":
        gtts_wrapper = get_gtts()
        if gtts_wrapper is None:
            raise RuntimeError("gTTS not available")
        return gtts_wrapper.synthesize(text, language=language, output_path=output_path, **kwargs)
    elif utility == "pyttsx3":
        pyttsx3_wrapper = get_pyttsx3()
        if pyttsx3_wrapper is None:
            raise RuntimeError("pyttsx3 not available")
        return pyttsx3_wrapper.synthesize(text, output_path=output_path, **kwargs)
    else:
        raise ValueError(f"Unknown utility: {utility}. Use 'gtts' or 'pyttsx3'")
