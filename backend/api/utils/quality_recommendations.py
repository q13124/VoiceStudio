"""
Quality recommendation system for adaptive quality optimization.
Uses text analysis to recommend optimal quality settings.
"""

from typing import Dict, Optional

from api.utils.text_analysis import ContentType, TextAnalysisResult, TextComplexity


class QualityRecommendation:
    """Quality settings recommendation based on text analysis."""

    def __init__(
        self,
        recommended_engine: str,
        recommended_quality_mode: str,
        recommended_enhance_quality: bool,
        predicted_quality_score: float,
        reasoning: str,
        confidence: float,
    ):
        self.recommended_engine = recommended_engine
        self.recommended_quality_mode = recommended_quality_mode
        self.recommended_enhance_quality = recommended_enhance_quality
        self.predicted_quality_score = predicted_quality_score
        self.reasoning = reasoning
        self.confidence = confidence

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "recommended_engine": self.recommended_engine,
            "recommended_quality_mode": self.recommended_quality_mode,
            "recommended_enhance_quality": self.recommended_enhance_quality,
            "predicted_quality_score": round(self.predicted_quality_score, 3),
            "reasoning": self.reasoning,
            "confidence": round(self.confidence, 2),
        }


def recommend_quality_settings(
    text_analysis: TextAnalysisResult,
    available_engines: Optional[list] = None,
    target_quality: Optional[float] = None,
) -> QualityRecommendation:
    """
    Recommend optimal quality settings based on text analysis.

    Args:
        text_analysis: TextAnalysisResult from text analysis
        available_engines: List of available engines (default: ["xtts", "chatterbox", "tortoise"])
        target_quality: Target quality score (0.0-1.0), None for auto

    Returns:
        QualityRecommendation with recommended settings
    """
    if available_engines is None:
        available_engines = ["xtts", "chatterbox", "tortoise"]

    # Determine recommended engine based on content type and complexity
    recommended_engine = _select_engine(
        text_analysis.content_type,
        text_analysis.complexity,
        text_analysis.word_count,
        available_engines,
    )

    # Determine quality mode based on complexity and content type
    quality_mode = _select_quality_mode(
        text_analysis.complexity, text_analysis.content_type, text_analysis.word_count
    )

    # Determine if quality enhancement should be enabled
    enhance_quality = _should_enhance_quality(
        text_analysis.complexity, text_analysis.content_type, target_quality
    )

    # Predict quality score
    predicted_quality = _predict_quality_score(
        recommended_engine,
        quality_mode,
        enhance_quality,
        text_analysis.complexity,
        text_analysis.content_type,
    )

    # Generate reasoning
    reasoning = _generate_reasoning(
        text_analysis, recommended_engine, quality_mode, enhance_quality
    )

    # Calculate confidence (based on how clear the recommendations are)
    confidence = _calculate_confidence(text_analysis, target_quality)

    return QualityRecommendation(
        recommended_engine=recommended_engine,
        recommended_quality_mode=quality_mode,
        recommended_enhance_quality=enhance_quality,
        predicted_quality_score=predicted_quality,
        reasoning=reasoning,
        confidence=confidence,
    )


def _select_engine(
    content_type: ContentType,
    complexity: TextComplexity,
    word_count: int,
    available_engines: list,
) -> str:
    """
    Select the best engine for the text characteristics.

    Rules:
    - Simple dialogue: XTTS (fast)
    - Complex narration: Tortoise (high quality)
    - Technical content: Chatterbox (balanced)
    - Very long text: XTTS or Chatterbox (speed matters)
    """
    # Very long text needs speed
    if word_count > 500:
        if "xtts" in available_engines:
            return "xtts"
        elif "chatterbox" in available_engines:
            return "chatterbox"

    # Complex content needs high quality
    if complexity in [TextComplexity.COMPLEX, TextComplexity.VERY_COMPLEX]:
        if content_type == ContentType.NARRATION and "tortoise" in available_engines:
            return "tortoise"
        elif "chatterbox" in available_engines:
            return "chatterbox"

    # Dialogue benefits from balanced engines
    if content_type == ContentType.DIALOGUE:
        if "chatterbox" in available_engines:
            return "chatterbox"

    # Technical content needs clarity
    if content_type == ContentType.TECHNICAL:
        if "chatterbox" in available_engines:
            return "chatterbox"

    # Default to first available engine
    return available_engines[0] if available_engines else "xtts"


def _select_quality_mode(
    complexity: TextComplexity, content_type: ContentType, word_count: int
) -> str:
    """
    Select quality mode (fast, standard, high, ultra).

    Rules:
    - Simple/short text: fast or standard
    - Complex text: high or ultra
    - Technical content: high (clarity important)
    - Very long text: standard (speed matters)
    """
    # Very long text prioritizes speed
    if word_count > 500:
        return "standard"

    # Complex content needs high quality
    if complexity == TextComplexity.VERY_COMPLEX:
        return "ultra"
    elif complexity == TextComplexity.COMPLEX:
        return "high"

    # Technical content needs clarity
    if content_type == ContentType.TECHNICAL:
        return "high"

    # Dialogue can use standard (naturalness more important than perfection)
    if content_type == ContentType.DIALOGUE:
        if complexity == TextComplexity.SIMPLE:
            return "fast"
        else:
            return "standard"

    # Narration benefits from higher quality
    if content_type == ContentType.NARRATION:
        if complexity in [TextComplexity.COMPLEX, TextComplexity.VERY_COMPLEX]:
            return "ultra"
        elif complexity == TextComplexity.MODERATE:
            return "high"
        else:
            return "standard"

    # Default
    return "standard"


def _should_enhance_quality(
    complexity: TextComplexity,
    content_type: ContentType,
    target_quality: Optional[float],
) -> bool:
    """
    Determine if quality enhancement should be enabled.

    Rules:
    - Enable for complex content
    - Enable for technical content (clarity)
    - Enable if target quality is high (>0.85)
    - Disable for simple/short dialogue (speed)
    """
    # High target quality requires enhancement
    if target_quality and target_quality > 0.85:
        return True

    # Complex content benefits from enhancement
    if complexity in [TextComplexity.COMPLEX, TextComplexity.VERY_COMPLEX]:
        return True

    # Technical content needs clarity
    if content_type == ContentType.TECHNICAL:
        return True

    # Narration benefits from enhancement
    if content_type == ContentType.NARRATION and complexity != TextComplexity.SIMPLE:
        return True

    # Simple dialogue doesn't need enhancement (speed priority)
    if content_type == ContentType.DIALOGUE and complexity == TextComplexity.SIMPLE:
        return False

    return False


def _predict_quality_score(
    engine: str,
    quality_mode: str,
    enhance_quality: bool,
    complexity: TextComplexity,
    content_type: ContentType,
) -> float:
    """
    Predict expected quality score based on settings and text characteristics.

    Returns:
        Predicted quality score (0.0-1.0)
    """
    # Base quality by engine
    engine_quality = {"xtts": 0.75, "chatterbox": 0.85, "tortoise": 0.90}
    base_quality = engine_quality.get(engine, 0.80)

    # Quality mode multipliers
    mode_multipliers = {"fast": 0.90, "standard": 1.00, "high": 1.05, "ultra": 1.10}
    quality = base_quality * mode_multipliers.get(quality_mode, 1.0)

    # Enhancement bonus
    if enhance_quality:
        quality *= 1.05

    # Complexity penalty (complex text is harder to synthesize well)
    complexity_penalties = {
        TextComplexity.SIMPLE: 1.00,
        TextComplexity.MODERATE: 0.98,
        TextComplexity.COMPLEX: 0.95,
        TextComplexity.VERY_COMPLEX: 0.92,
    }
    quality *= complexity_penalties.get(complexity, 1.0)

    # Content type adjustments
    if content_type == ContentType.DIALOGUE:
        quality *= 0.98  # Dialogue is slightly easier
    elif content_type == ContentType.TECHNICAL:
        quality *= 0.97  # Technical terms can be challenging

    # Clamp to valid range
    return max(0.0, min(1.0, quality))


def _generate_reasoning(
    text_analysis: TextAnalysisResult,
    engine: str,
    quality_mode: str,
    enhance_quality: bool,
) -> str:
    """Generate human-readable reasoning for the recommendations."""
    reasons = []

    # Engine reasoning
    if engine == "tortoise":
        reasons.append(
            "Tortoise engine selected for maximum quality on complex content"
        )
    elif engine == "chatterbox":
        reasons.append("Chatterbox engine selected for balanced quality and speed")
    else:
        reasons.append("XTTS engine selected for fast synthesis")

    # Quality mode reasoning
    if quality_mode == "ultra":
        reasons.append("Ultra quality mode for complex content")
    elif quality_mode == "high":
        reasons.append("High quality mode for better clarity")
    elif quality_mode == "fast":
        reasons.append("Fast mode for simple, short content")

    # Content type reasoning
    if text_analysis.content_type == ContentType.DIALOGUE:
        reasons.append("Dialogue content optimized for naturalness")
    elif text_analysis.content_type == ContentType.TECHNICAL:
        reasons.append("Technical content optimized for clarity")

    # Enhancement reasoning
    if enhance_quality:
        reasons.append("Quality enhancement enabled for improved output")

    # Complexity reasoning
    if text_analysis.complexity in [
        TextComplexity.COMPLEX,
        TextComplexity.VERY_COMPLEX,
    ]:
        reasons.append(
            f"Higher quality settings for {text_analysis.complexity.value} text"
        )

    return ". ".join(reasons) + "."


def _calculate_confidence(
    text_analysis: TextAnalysisResult, target_quality: Optional[float]
) -> float:
    """
    Calculate confidence in recommendations (0.0-1.0).

    Higher confidence when:
    - Clear content type
    - Clear complexity level
    - Target quality specified
    """
    confidence = 0.7  # Base confidence

    # Clear content type increases confidence
    if text_analysis.content_type != ContentType.MIXED:
        confidence += 0.1

    # Clear complexity increases confidence
    if text_analysis.complexity in [TextComplexity.SIMPLE, TextComplexity.VERY_COMPLEX]:
        confidence += 0.1

    # Target quality specified increases confidence
    if target_quality is not None:
        confidence += 0.1

    return min(1.0, confidence)
