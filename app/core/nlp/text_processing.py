"""
Natural Language Processing for Text Preprocessing
Integrates NLTK and TextBlob for SSML and TTS text preprocessing.
Part of FREE_LIBRARIES_INTEGRATION - Worker 3.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)

# Try importing NLP libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    from nltk.tag import pos_tag
    from nltk.tokenize import sent_tokenize, word_tokenize

    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logger.warning("NLTK not installed, NLP features limited")

try:
    from textblob import TextBlob

    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    logger.warning("TextBlob not installed, sentiment analysis unavailable")

# Try importing phonemizer for phoneme conversion
try:
    from phonemizer import phonemize
    from phonemizer.backend import EspeakBackend, FestivalBackend

    HAS_PHONEMIZER = True
except ImportError:
    HAS_PHONEMIZER = False
    phonemize = None
    EspeakBackend = None
    FestivalBackend = None
    logger.debug("phonemizer not installed. Phoneme conversion will be limited.")

# Check availability of gruut for phoneme conversion
HAS_GRUUT: bool
try:
    import gruut

    HAS_GRUUT = True
except ImportError:
    HAS_GRUUT = False
    logger.debug("gruut not installed. Phoneme conversion will be limited.")


class TextPreprocessor:
    """
    Text preprocessing for TTS and SSML using NLP libraries.
    """

    def __init__(self):
        """Initialize text preprocessor."""
        self._nltk_downloaded = False
        if HAS_NLTK:
            self._ensure_nltk_data()
        if HAS_TEXTBLOB:
            self.lemmatizer = WordNetLemmatizer() if HAS_NLTK else None
            self.stemmer = PorterStemmer() if HAS_NLTK else None

    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded."""
        if self._nltk_downloaded:
            return

        try:
            nltk.download("punkt", quiet=True)
            nltk.download("stopwords", quiet=True)
            nltk.download("wordnet", quiet=True)
            nltk.download("averaged_perceptron_tagger", quiet=True)
            self._nltk_downloaded = True
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for TTS processing.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        # Normalize unicode
        text = unicodedata.normalize("NFKD", text)

        return text

    def sentence_segmentation(self, text: str, language: str = "en") -> list[str]:
        """
        Segment text into sentences.

        Args:
            text: Input text
            language: Language code

        Returns:
            List of sentences
        """
        if HAS_NLTK:
            try:
                result: list[str] = sent_tokenize(text, language=language)
                return result
            except LookupError:
                logger.warning(f"NLTK data for language {language} not available")
                # Fallback to simple segmentation
                return self._simple_sentence_split(text)
        else:
            return self._simple_sentence_split(text)

    def _simple_sentence_split(self, text: str) -> list[str]:
        """Simple sentence splitting fallback."""
        sentences = re.split(r"[.!?]+\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def word_tokenization(self, text: str, language: str = "en") -> list[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text
            language: Language code

        Returns:
            List of words
        """
        if HAS_NLTK:
            try:
                tokens: list[str] = word_tokenize(text, language=language)
                return tokens
            except LookupError:
                logger.warning(f"NLTK data for language {language} not available")
                return text.split()
        else:
            return text.split()

    def remove_stopwords(self, words: list[str], language: str = "en") -> list[str]:
        """
        Remove stopwords from word list.

        Args:
            words: List of words
            language: Language code

        Returns:
            List of words without stopwords
        """
        if HAS_NLTK:
            try:
                stop_words = set(stopwords.words(language))
                return [w for w in words if w.lower() not in stop_words]
            except LookupError:
                logger.warning(f"Stopwords for language {language} not available")
                return words
        else:
            return words

    def lemmatize_words(self, words: list[str]) -> list[str]:
        """
        Lemmatize words (reduce to base form).

        Args:
            words: List of words

        Returns:
            List of lemmatized words
        """
        if HAS_NLTK and self.lemmatizer:
            try:
                return [self.lemmatizer.lemmatize(word) for word in words]
            except Exception as e:
                logger.warning(f"Lemmatization failed: {e}")
                return words
        else:
            return words

    def stem_words(self, words: list[str]) -> list[str]:
        """
        Stem words (reduce to root form).

        Args:
            words: List of words

        Returns:
            List of stemmed words
        """
        if HAS_NLTK and self.stemmer:
            try:
                return [self.stemmer.stem(word) for word in words]
            except Exception as e:
                logger.warning(f"Stemming failed: {e}")
                return words
        else:
            return words

    def pos_tagging(self, words: list[str]) -> list[tuple[str, str]]:
        """
        Part-of-speech tagging.

        Args:
            words: List of words

        Returns:
            List of (word, tag) tuples
        """
        if HAS_NLTK:
            try:
                tagged: list[tuple[str, str]] = pos_tag(words)
                return tagged
            except Exception as e:
                logger.warning(f"POS tagging failed: {e}")
                return [(w, "UNKNOWN") for w in words]
        else:
            return [(w, "UNKNOWN") for w in words]

    def sentiment_analysis(self, text: str) -> dict[str, float]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text

        Returns:
            Dictionary with 'polarity' and 'subjectivity' scores
        """
        if HAS_TEXTBLOB:
            try:
                blob = TextBlob(text)
                return {
                    "polarity": blob.sentiment.polarity,  # -1 to 1
                    "subjectivity": blob.sentiment.subjectivity,  # 0 to 1
                }
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
                return {"polarity": 0.0, "subjectivity": 0.5}
        else:
            return {"polarity": 0.0, "subjectivity": 0.5}

    def detect_language(self, text: str) -> str | None:
        """
        Detect language of text.

        Args:
            text: Input text

        Returns:
            Language code or None
        """
        if HAS_TEXTBLOB:
            try:
                TextBlob(text)
                # TextBlob doesn't have direct language detection, but we can try
                # For now, return None (can be enhanced with langdetect library)
                return None
            except Exception as e:
                logger.warning(f"Language detection failed: {e}")
                return None
        else:
            return None

    def preprocess_for_tts(
        self,
        text: str,
        language: str = "en",
        normalize: bool = True,
        segment_sentences: bool = True,
    ) -> dict[str, Any]:
        """
        Preprocess text for TTS synthesis.

        Args:
            text: Input text
            language: Language code
            normalize: Whether to normalize text
            segment_sentences: Whether to segment into sentences

        Returns:
            Dictionary with preprocessed text and metadata
        """
        normalized_text = text
        # Normalize
        if normalize:
            normalized_text = self.normalize_text(text)

        result: dict[str, Any] = {
            "original": text,
            "normalized": normalized_text,
            "sentences": [],
            "word_count": 0,
            "sentiment": None,
        }

        # Sentence segmentation
        if segment_sentences:
            result["sentences"] = self.sentence_segmentation(normalized_text, language)

        # Word count
        words = self.word_tokenization(normalized_text, language)
        result["word_count"] = len(words)

        # Sentiment analysis
        if HAS_TEXTBLOB:
            result["sentiment"] = self.sentiment_analysis(normalized_text)

        return result

    def preprocess_for_ssml(
        self, text: str, language: str = "en", add_prosody_hints: bool = True
    ) -> str:
        """
        Preprocess text for SSML generation.

        Args:
            text: Input text
            language: Language code
            add_prosody_hints: Whether to add prosody hints based on NLP analysis

        Returns:
            Preprocessed text ready for SSML
        """
        # Normalize text
        normalized = self.normalize_text(text)

        # Segment sentences
        sentences = self.sentence_segmentation(normalized, language)

        # If prosody hints requested, analyze sentiment for each sentence
        if add_prosody_hints and HAS_TEXTBLOB:
            processed_sentences = []
            for sentence in sentences:
                self.sentiment_analysis(sentence)
                # Could add SSML prosody tags based on sentiment
                # For now, just return normalized sentences
                processed_sentences.append(sentence)
            return " ".join(processed_sentences)

        return " ".join(sentences)

    def phonemize_text(self, text: str, language: str = "en", backend: str = "espeak") -> str:
        """
        Convert text to phonemes using phonemizer or gruut.

        Args:
            text: Input text
            language: Language code
            backend: Backend to use ('espeak', 'festival', or 'gruut')

        Returns:
            Phoneme string
        """
        if backend == "gruut" and HAS_GRUUT:
            try:
                import gruut as _gruut

                phonemes = []
                for sentence in _gruut.sentences(text, lang=language):
                    for word in sentence:
                        if hasattr(word, "phonemes") and word.phonemes:
                            phonemes.extend(word.phonemes)
                return " ".join(phonemes)
            except Exception as e:
                logger.warning(f"Gruut phonemization failed: {e}. Falling back to phonemizer.")
                backend = "espeak"

        if HAS_PHONEMIZER:
            try:
                if backend == "espeak":
                    backend_obj = EspeakBackend(language)
                elif backend == "festival":
                    backend_obj = FestivalBackend(language)
                else:
                    backend_obj = EspeakBackend(language)

                result_phonemes: str = phonemize(
                    text,
                    backend=backend_obj,
                    language=language,
                    separator=" ",
                    strip=True,
                )
                return result_phonemes
            except Exception as e:
                logger.warning(f"Phonemizer conversion failed: {e}")
                return text

        logger.warning("No phonemization backend available")
        return text


# Global preprocessor instance
_preprocessor_instance: TextPreprocessor | None = None


def get_text_preprocessor() -> TextPreprocessor:
    """Get global text preprocessor instance."""
    global _preprocessor_instance
    if _preprocessor_instance is None:
        _preprocessor_instance = TextPreprocessor()
    return _preprocessor_instance
