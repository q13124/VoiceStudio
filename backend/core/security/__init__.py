"""
Backend Core Security Module

Provides security utilities for file validation, input sanitization,
expression evaluation, and other security-related functionality.
"""

from .file_validation import (
    FileValidationError,
    FileTypeValidator,
    validate_audio_file,
    validate_image_file,
    validate_video_file,
    validate_file_type,
    get_file_type_from_content,
)
from .expression_evaluator import (
    ExpressionError,
    SafeExpressionEvaluator,
    parse_frame_rate,
    evaluate_condition,
    get_evaluator,
)

__all__ = [
    # File validation
    "FileValidationError",
    "FileTypeValidator",
    "validate_audio_file",
    "validate_image_file",
    "validate_video_file",
    "validate_file_type",
    "get_file_type_from_content",
    # Expression evaluation
    "ExpressionError",
    "SafeExpressionEvaluator",
    "parse_frame_rate",
    "evaluate_condition",
    "get_evaluator",
]
