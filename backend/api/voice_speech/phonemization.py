"""
Phonemization Integration
Integrates phonemizer and gruut libraries for text-to-phoneme conversion.
"""

import logging

logger = logging.getLogger(__name__)

# Try importing phonemizer
HAS_PHONEMIZER = False
try:
    from phonemizer import phonemize
    from phonemizer.backend import EspeakBackend, FestivalBackend

    HAS_PHONEMIZER = True
except ImportError:
    logger.warning("phonemizer not available.")

# Try importing gruut
HAS_GRUUT = False
try:
    import gruut

    HAS_GRUUT = True
except ImportError:
    logger.warning("gruut not available.")


class Phonemizer:
    """
    Phonemization using phonemizer and gruut libraries.
    """

    def __init__(self):
        """Initialize phonemizer."""
        self.phonemizer_available = HAS_PHONEMIZER
        self.gruut_available = HAS_GRUUT

    def phonemize_with_phonemizer(
        self,
        text: str,
        language: str = "en-us",
        backend: str = "espeak",
        separator: str = " ",
        strip: bool = True,
    ) -> str:
        """
        Convert text to phonemes using phonemizer library.

        Args:
            text: Input text
            language: Language code (e.g., "en-us", "fr-fr")
            backend: Backend ("espeak" or "festival")
            separator: Separator between phonemes
            strip: Strip whitespace

        Returns:
            Phoneme string
        """
        if not self.phonemizer_available:
            raise ImportError("phonemizer library not available")

        try:
            if backend == "espeak":
                backend_obj = EspeakBackend(language)
            elif backend == "festival":
                backend_obj = FestivalBackend(language)
            else:
                backend_obj = EspeakBackend(language)

            phonemes = phonemize(
                text,
                language=language,
                backend=backend_obj,
                separator=separator,
                strip=strip,
            )

            return phonemes
        except Exception as e:
            logger.error(f"Error in phonemization: {e}", exc_info=True)
            raise

    def phonemize_with_gruut(
        self,
        text: str,
        language: str = "en-us",
    ) -> list[dict]:
        """
        Convert text to phonemes using gruut library.

        Args:
            text: Input text
            language: Language code

        Returns:
            List of word dictionaries with phonemes
        """
        if not self.gruut_available:
            raise ImportError("gruut library not available")

        try:
            lang_code = language.split("-")[0] if "-" in language else language
            lang = gruut.get_lang(lang_code)

            sentences = gruut.sentences(text, lang=lang)
            result = []

            for sentence in sentences:
                for word in sentence:
                    word_data = {
                        "text": word.text,
                        "phonemes": word.phonemes if hasattr(word, "phonemes") else [],
                        "phonemes_str": " ".join(word.phonemes) if hasattr(word, "phonemes") else "",
                    }
                    result.append(word_data)

            return result
        except Exception as e:
            logger.error(f"Error in gruut phonemization: {e}", exc_info=True)
            raise

    def get_available_backends(self) -> list[str]:
        """
        Get list of available phonemization backends.

        Returns:
            List of backend names
        """
        backends = []
        if self.phonemizer_available:
            backends.extend(["espeak", "festival"])
        if self.gruut_available:
            backends.append("gruut")
        return backends

