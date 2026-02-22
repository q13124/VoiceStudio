"""
Text Processing Utilities for VoiceStudio
NLP processing for text-to-speech engines

Compatible with:
- Python 3.10+
- spacy>=3.8.7 (optional, for advanced NLP)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Try importing spacy for advanced NLP
from typing import Any

HAS_SPACY = False
_spacy_module: Any = None
_japanese_cls: Any = None
try:
    import spacy as _spacy_module
    from spacy.lang.ja import Japanese as _japanese_cls

    HAS_SPACY = True
except ImportError:
    logger.debug(
        "spacy not installed. Advanced NLP processing will be limited. "
        "Install with: pip install spacy[ja]>=3.8.7"
    )

spacy = _spacy_module
Japanese = _japanese_cls

_spacy_models: dict[str, Any] = {}


def load_spacy_model(language: str = "en") -> Any:
    """
    Load spacy model for a specific language.

    Args:
        language: Language code (e.g., "en", "ja", "zh")

    Returns:
        Loaded spacy model or None if not available
    """
    if not HAS_SPACY:
        return None

    # Check cache
    if language in _spacy_models:
        return _spacy_models[language]

    try:
        # Map language codes to spacy model names
        model_map = {
            "en": "en_core_web_sm",
            "ja": "ja_core_news_sm",
            "zh": "zh_core_web_sm",
            "de": "de_core_news_sm",
            "es": "es_core_news_sm",
            "fr": "fr_core_news_sm",
            "it": "it_core_news_sm",
            "pt": "pt_core_news_sm",
            "ru": "ru_core_news_sm",
            "nl": "nl_core_news_sm",
        }

        model_name = model_map.get(language, "en_core_web_sm")

        # Try to load model
        try:
            nlp = spacy.load(model_name)
            _spacy_models[language] = nlp
            logger.info(f"Loaded spacy model: {model_name}")
            return nlp
        except OSError:
            # Model not installed, try to use base language
            if language != "en":
                logger.warning(f"spacy model {model_name} not found, " "falling back to English")
                return load_spacy_model("en")
            else:
                logger.warning(
                    f"spacy model {model_name} not found. "
                    "Install with: python -m spacy download {model_name}"
                )
                return None
    except Exception as e:
        logger.warning(f"Failed to load spacy model for {language}: {e}")
        return None


def preprocess_text(
    text: str,
    language: str = "en",
    normalize: bool = True,
    remove_punctuation: bool = False,
    lowercase: bool = False,
) -> str:
    """
    Preprocess text for TTS synthesis.

    Args:
        text: Input text
        language: Language code
        normalize: Normalize unicode characters
        remove_punctuation: Remove punctuation marks
        lowercase: Convert to lowercase

    Returns:
        Preprocessed text
    """
    processed = text

    # Load spacy model if available
    nlp = load_spacy_model(language) if HAS_SPACY else None

    if nlp is not None:
        try:
            doc = nlp(processed)

            # Extract tokens
            if remove_punctuation:
                tokens = [token.text for token in doc if not token.is_punct and not token.is_space]
            else:
                tokens = [token.text for token in doc if not token.is_space]

            processed = " ".join(tokens)

            # Normalize unicode if requested
            if normalize:
                # spacy handles normalization, but we can add extra steps
                processed = processed.strip()
        except Exception as e:
            logger.warning(f"spacy preprocessing failed: {e}, using basic preprocessing")

    # Basic preprocessing fallback
    if normalize:
        # Basic unicode normalization
        import unicodedata

        processed = unicodedata.normalize("NFKC", processed)

    if lowercase:
        processed = processed.lower()

    return processed.strip()


def extract_phonemes(text: str, language: str = "en") -> list[dict[str, str | float]] | None:
    """
    Extract phonemes from text using spacy (if available).

    Args:
        text: Input text
        language: Language code

    Returns:
        List of phoneme dictionaries with text and position, or None if unavailable
    """
    if not HAS_SPACY:
        return None

    nlp = load_spacy_model(language)
    if nlp is None:
        return None

    try:
        doc = nlp(text)
        phonemes = []

        for token in doc:
            if not token.is_punct and not token.is_space:
                phonemes.append(
                    {
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "start": token.idx,
                        "end": token.idx + len(token.text),
                    }
                )

        return phonemes
    except Exception as e:
        logger.warning(f"Phoneme extraction failed: {e}")
        return None


def segment_text(text: str, language: str = "en", max_length: int = 200) -> list[str]:
    """
    Segment text into sentences or chunks for TTS.

    Args:
        text: Input text
        language: Language code
        max_length: Maximum length per segment

    Returns:
        List of text segments
    """
    nlp = load_spacy_model(language) if HAS_SPACY else None

    if nlp is not None:
        try:
            doc = nlp(text)
            segments = []

            current_segment = ""
            for sent in doc.sents:
                sent_text = sent.text.strip()
                if len(current_segment) + len(sent_text) + 1 <= max_length:
                    if current_segment:
                        current_segment += " " + sent_text
                    else:
                        current_segment = sent_text
                else:
                    if current_segment:
                        segments.append(current_segment)
                    current_segment = sent_text

            if current_segment:
                segments.append(current_segment)

            return segments if segments else [text]
        except Exception as e:
            logger.warning(f"spacy segmentation failed: {e}, using basic segmentation")

    # Basic segmentation fallback
    segments = []
    sentences = text.split(".")
    current_segment = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current_segment) + len(sentence) + 1 <= max_length:
            if current_segment:
                current_segment += ". " + sentence
            else:
                current_segment = sentence
        else:
            if current_segment:
                segments.append(current_segment + ".")
            current_segment = sentence

    if current_segment:
        segments.append(current_segment + ".")

    return segments if segments else [text]


def analyze_text_quality(text: str, language: str = "en") -> dict[str, Any]:
    """
    Analyze text quality and characteristics.

    Args:
        text: Input text
        language: Language code

    Returns:
        Dictionary with text analysis results
    """
    nlp = load_spacy_model(language) if HAS_SPACY else None

    analysis = {
        "length": len(text),
        "word_count": 0,
        "sentence_count": 0,
        "avg_word_length": 0.0,
        "punctuation_count": 0,
        "numbers_count": 0,
        "entities": [],
    }

    if nlp is not None:
        try:
            doc = nlp(text)

            # Word count (excluding punctuation and spaces)
            words = [token for token in doc if not token.is_punct and not token.is_space]
            analysis["word_count"] = len(words)

            # Sentence count
            analysis["sentence_count"] = len(list(doc.sents))

            # Average word length
            if words:
                analysis["avg_word_length"] = sum(len(word.text) for word in words) / len(words)

            # Punctuation count
            analysis["punctuation_count"] = sum(1 for token in doc if token.is_punct)

            # Numbers count
            analysis["numbers_count"] = sum(1 for token in doc if token.like_num)

            # Named entities
            if doc.ents:
                analysis["entities"] = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        except Exception as e:
            logger.warning(f"spacy text analysis failed: {e}, using basic analysis")

    # Basic analysis fallback
    if analysis["word_count"] == 0:
        words = text.split()
        analysis["word_count"] = len(words)
        if words:
            analysis["avg_word_length"] = sum(len(word) for word in words) / len(words)

    if analysis["sentence_count"] == 0:
        analysis["sentence_count"] = text.count(".") + text.count("!") + text.count("?")

    analysis["punctuation_count"] = sum(1 for c in text if c in ".,!?;:()[]{}")
    analysis["numbers_count"] = sum(1 for c in text if c.isdigit())

    return analysis


def cleanup_spacy_models():
    """Clean up loaded spacy models from memory."""
    global _spacy_models
    _spacy_models.clear()
    logger.debug("Cleaned up spacy models from memory")
