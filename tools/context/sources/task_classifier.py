"""
Task classifier source adapter.

Provides compatibility layer for inject_context.py to use the
task classifier from tools.context.classifier.

This module wraps the TaskClassifier to provide the expected
`classify_from_prompt` interface.
"""

from __future__ import annotations

from tools.context.classifier.task_classifier import (
    ClassificationResult,
    get_classifier,
)

__all__ = ["ClassificationResult", "classify_from_prompt"]


def classify_from_prompt(
    prompt: str,
    file_hint: str | None = None,
) -> ClassificationResult | None:
    """
    Classify a user prompt into a role profile.

    This is the primary entry point used by inject_context.py.

    Args:
        prompt: The user's task prompt.
        file_hint: Optional file path hint for context.

    Returns:
        ClassificationResult with role and confidence, or None if no match.
    """
    if not prompt or not prompt.strip():
        return None

    classifier = get_classifier()
    result = classifier.classify(prompt, file_hint)

    # Return None if confidence is too low
    if result.confidence < 0.2:
        return None

    return result
