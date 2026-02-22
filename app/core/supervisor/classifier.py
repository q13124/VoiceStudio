"""
Intent Classifier for Hybrid Supervisor (Phase 11.1.1)

Lightweight classifier that determines the optimal processing path
for incoming user input. Must operate under 50ms to maintain
conversation fluidity.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    """Complexity level of user input."""

    LOW = "low"  # Simple greeting, short response expected
    MEDIUM = "medium"  # Regular conversation
    HIGH = "high"  # Complex reasoning, tool calling needed


@dataclass
class ClassificationResult:
    """Result from intent classification."""

    complexity: ComplexityLevel
    confidence: float  # 0.0 to 1.0
    requires_tool_call: bool
    requires_reasoning: bool
    suggested_route: str  # "s2s", "cascade", "half_cascade"
    latency_ms: float
    features: dict[str, Any]


class IntentClassifier:
    """
    Fast intent classifier for routing decisions.

    Uses keyword heuristics and pattern matching for < 50ms classification.
    Optionally delegates to an LLM for higher accuracy when available.
    """

    # Keywords indicating complex reasoning needs
    COMPLEX_KEYWORDS = frozenset(
        {
            "explain",
            "analyze",
            "compare",
            "calculate",
            "debug",
            "optimize",
            "recommend",
            "why",
            "how does",
            "what if",
            "summarize",
            "translate",
            "write",
            "code",
            "implement",
            "review",
            "evaluate",
            "plan",
            "design",
            "research",
        }
    )

    # Keywords indicating tool/action invocation
    TOOL_KEYWORDS = frozenset(
        {
            "generate",
            "synthesize",
            "clone",
            "convert",
            "create",
            "adjust",
            "change",
            "set",
            "apply",
            "export",
            "import",
            "train",
            "process",
            "render",
            "mix",
            "master",
            "record",
            "play",
            "stop",
            "pause",
            "save",
            "load",
            "delete",
        }
    )

    # Keywords indicating casual interaction
    CASUAL_KEYWORDS = frozenset(
        {
            "hi",
            "hello",
            "hey",
            "thanks",
            "thank you",
            "bye",
            "yes",
            "no",
            "ok",
            "sure",
            "maybe",
            "good",
            "great",
            "nice",
            "cool",
            "awesome",
            "fine",
            "right",
        }
    )

    def __init__(self):
        self._classification_count = 0
        self._total_latency_ms = 0.0

    def classify(
        self,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> ClassificationResult:
        """
        Classify user input for routing.

        Must complete in < 50ms for real-time operation.

        Args:
            text: User input text (from STT or direct text).
            context: Optional conversation context.

        Returns:
            ClassificationResult with routing recommendation.
        """
        start_time = time.perf_counter()

        text_lower = text.lower().strip()
        words = set(text_lower.split())
        word_count = len(text_lower.split())

        features: dict[str, Any] = {
            "word_count": word_count,
            "has_question": "?" in text,
            "has_command": any(
                text_lower.startswith(w) for w in ("please", "can you", "could you")
            ),
        }

        # Check for tool keywords
        tool_matches = words & self.TOOL_KEYWORDS
        has_tool_intent = bool(tool_matches)
        features["tool_keywords"] = list(tool_matches)

        # Check for complex reasoning
        complex_matches = words & self.COMPLEX_KEYWORDS
        has_complex_intent = bool(complex_matches) or word_count > 30
        features["complex_keywords"] = list(complex_matches)

        # Check for casual intent
        casual_matches = words & self.CASUAL_KEYWORDS
        is_casual = bool(casual_matches) and not has_tool_intent and not has_complex_intent
        features["casual_keywords"] = list(casual_matches)

        # Determine complexity
        if has_tool_intent:
            complexity = ComplexityLevel.HIGH
            suggested_route = "cascade"
            confidence = 0.8
        elif has_complex_intent:
            complexity = ComplexityLevel.HIGH
            suggested_route = "cascade"
            confidence = 0.75
        elif is_casual and word_count < 10:
            complexity = ComplexityLevel.LOW
            suggested_route = "s2s"
            confidence = 0.85
        elif word_count < 15:
            complexity = ComplexityLevel.MEDIUM
            suggested_route = "s2s"
            confidence = 0.65
        else:
            complexity = ComplexityLevel.MEDIUM
            suggested_route = "half_cascade"
            confidence = 0.55

        # Context adjustments
        if context:
            prev_route = context.get("previous_route")
            if prev_route == "cascade" and complexity == ComplexityLevel.MEDIUM:
                # Stay in cascade if already there for continuity
                suggested_route = "cascade"
                confidence += 0.1

        latency_ms = (time.perf_counter() - start_time) * 1000
        self._classification_count += 1
        self._total_latency_ms += latency_ms

        result = ClassificationResult(
            complexity=complexity,
            confidence=min(confidence, 1.0),
            requires_tool_call=has_tool_intent,
            requires_reasoning=has_complex_intent,
            suggested_route=suggested_route,
            latency_ms=latency_ms,
            features=features,
        )

        logger.debug(
            f"Classified: complexity={complexity.value}, "
            f"route={suggested_route}, "
            f"confidence={confidence:.2f}, "
            f"latency={latency_ms:.1f}ms"
        )

        return result

    def get_stats(self) -> dict[str, Any]:
        """Get classifier performance statistics."""
        avg_latency = (
            self._total_latency_ms / self._classification_count
            if self._classification_count > 0
            else 0.0
        )
        return {
            "total_classifications": self._classification_count,
            "avg_latency_ms": round(avg_latency, 2),
            "meets_target": avg_latency < 50.0,
        }
