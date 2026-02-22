"""
Text analysis utilities for adaptive quality optimization.
Analyzes text content to recommend optimal quality settings.
"""

from __future__ import annotations

import re
from enum import Enum


class TextComplexity(Enum):
    """Text complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ContentType(Enum):
    """Content type classification."""

    DIALOGUE = "dialogue"
    NARRATION = "narration"
    TECHNICAL = "technical"
    MIXED = "mixed"


class TextAnalysisResult:
    """Result of text analysis."""

    def __init__(
        self,
        text: str,
        complexity: TextComplexity,
        content_type: ContentType,
        word_count: int,
        sentence_count: int,
        character_count: int,
        avg_words_per_sentence: float,
        has_dialogue: bool,
        has_technical_terms: bool,
        detected_emotions: list[str],
        language: str = "en",
    ):
        self.text = text
        self.complexity = complexity
        self.content_type = content_type
        self.word_count = word_count
        self.sentence_count = sentence_count
        self.character_count = character_count
        self.avg_words_per_sentence = avg_words_per_sentence
        self.has_dialogue = has_dialogue
        self.has_technical_terms = has_technical_terms
        self.detected_emotions = detected_emotions
        self.language = language

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "complexity": self.complexity.value,
            "content_type": self.content_type.value,
            "word_count": self.word_count,
            "sentence_count": self.sentence_count,
            "character_count": self.character_count,
            "avg_words_per_sentence": round(self.avg_words_per_sentence, 2),
            "has_dialogue": self.has_dialogue,
            "has_technical_terms": self.has_technical_terms,
            "detected_emotions": self.detected_emotions,
            "language": self.language,
        }


def analyze_text_complexity(text: str) -> TextComplexity:
    """
    Analyze text complexity based on vocabulary and sentence structure.

    Args:
        text: Input text to analyze

    Returns:
        TextComplexity level
    """
    words = text.split()
    if not words:
        return TextComplexity.SIMPLE

    # Count sentences (basic heuristic)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences) if sentences else 1

    # Calculate average words per sentence
    avg_words_per_sentence = len(words) / sentence_count if sentence_count > 0 else len(words)

    # Count long words (4+ characters)
    long_words = sum(1 for w in words if len(w) >= 4)
    long_word_ratio = long_words / len(words) if words else 0

    # Count complex punctuation (colons, semicolons, dashes)
    complex_punct = len(re.findall(r"[:;—]", text))

    # Determine complexity
    if avg_words_per_sentence > 25 or long_word_ratio > 0.5 or complex_punct > 5:
        return TextComplexity.VERY_COMPLEX
    elif avg_words_per_sentence > 15 or long_word_ratio > 0.3 or complex_punct > 2:
        return TextComplexity.COMPLEX
    elif avg_words_per_sentence > 10 or long_word_ratio > 0.2:
        return TextComplexity.MODERATE
    else:
        return TextComplexity.SIMPLE


def detect_content_type(text: str) -> ContentType:
    """
    Detect content type (dialogue, narration, technical, mixed).

    Args:
        text: Input text to analyze

    Returns:
        ContentType classification
    """
    # Check for dialogue (quotes, dialogue markers)
    dialogue_indicators = [
        r'["\']',  # Quotes
        r"said|says|asked|replied|responded",  # Dialogue verbs
        r':\s*["\']',  # Colon followed by quote
    ]
    has_dialogue = any(re.search(pattern, text, re.IGNORECASE) for pattern in dialogue_indicators)

    # Check for technical terms (capitalized acronyms, numbers with units, technical keywords)
    technical_indicators = [
        r"\b[A-Z]{2,}\b",  # Acronyms (2+ uppercase letters)
        r"\d+\s*(?:Hz|kHz|MHz|GHz|GB|MB|KB|%|dB|ms|s|min|hr)",  # Technical units
        r"\b(?:API|CPU|GPU|RAM|HTTP|HTTPS|JSON|XML|SQL|HTML|CSS|JS)\b",  # Tech terms
        r"\b(?:function|method|parameter|variable|class|interface|protocol)\b",  # Programming terms
    ]
    has_technical = any(re.search(pattern, text, re.IGNORECASE) for pattern in technical_indicators)

    # Determine content type
    if has_dialogue and has_technical:
        return ContentType.MIXED
    elif has_dialogue:
        return ContentType.DIALOGUE
    elif has_technical:
        return ContentType.TECHNICAL
    else:
        return ContentType.NARRATION


def detect_emotions(text: str) -> list[str]:
    """
    Detect emotions in text based on keywords.

    Args:
        text: Input text to analyze

    Returns:
        List of detected emotions
    """
    emotion_keywords = {
        "happy": [
            "happy",
            "joy",
            "glad",
            "excited",
            "cheerful",
            "delighted",
            "pleased",
            "smile",
            "laugh",
        ],
        "sad": ["sad", "unhappy", "disappointed", "depressed", "sorrow", "tears", "cry"],
        "angry": ["angry", "mad", "furious", "annoyed", "irritated", "rage"],
        "neutral": ["okay", "fine", "alright", "normal"],
        "surprised": ["surprised", "shocked", "amazed", "astonished", "wow"],
    }

    text_lower = text.lower()
    detected = []

    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected.append(emotion)

    return detected if detected else ["neutral"]


def analyze_text(text: str, language: str = "en") -> TextAnalysisResult:
    """
    Perform comprehensive text analysis.

    Args:
        text: Input text to analyze
        language: Language code (default: "en")

    Returns:
        TextAnalysisResult with all analysis data
    """
    if not text or not text.strip():
        # Return minimal result for empty text
        return TextAnalysisResult(
            text=text,
            complexity=TextComplexity.SIMPLE,
            content_type=ContentType.NARRATION,
            word_count=0,
            sentence_count=0,
            character_count=0,
            avg_words_per_sentence=0.0,
            has_dialogue=False,
            has_technical_terms=False,
            detected_emotions=["neutral"],
            language=language,
        )

    # Basic statistics
    words = text.split()
    word_count = len(words)
    character_count = len(text)

    # Count sentences
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences) if sentences else 1

    avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0.0

    # Analyze complexity
    complexity = analyze_text_complexity(text)

    # Detect content type
    content_type = detect_content_type(text)

    # Check for dialogue
    has_dialogue = bool(re.search(r'["\']', text))

    # Check for technical terms
    has_technical = bool(
        re.search(r"\b[A-Z]{2,}\b|\d+\s*(?:Hz|kHz|MHz|GHz|GB|MB|KB|%|dB|ms|s|min|hr)", text)
    )

    # Detect emotions
    emotions = detect_emotions(text)

    return TextAnalysisResult(
        text=text,
        complexity=complexity,
        content_type=content_type,
        word_count=word_count,
        sentence_count=sentence_count,
        character_count=character_count,
        avg_words_per_sentence=avg_words_per_sentence,
        has_dialogue=has_dialogue,
        has_technical_terms=has_technical,
        detected_emotions=emotions,
        language=language,
    )


def get_text_length_category(text: str) -> str:
    """
    Categorize text by length.

    Args:
        text: Input text

    Returns:
        Length category: "short", "medium", "long", "very_long"
    """
    word_count = len(text.split())

    if word_count < 10:
        return "short"
    elif word_count < 50:
        return "medium"
    elif word_count < 200:
        return "long"
    else:
        return "very_long"
