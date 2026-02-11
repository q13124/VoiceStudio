"""
Task Classifier module for MCP auto-selection.

Classifies user prompts into role profiles for context routing.
"""

from tools.context.classifier.task_classifier import (
    ClassificationResult,
    TaskClassifier,
)

__all__ = ["ClassificationResult", "TaskClassifier"]
