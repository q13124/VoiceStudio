"""
Backend Core Security Module

Provides security utilities for file validation, input sanitization,
expression evaluation, and other security-related functionality.
"""

from .expression_evaluator import (
    ExpressionError,
    SafeExpressionEvaluator,
    evaluate_condition,
    get_evaluator,
    parse_frame_rate,
)
from .file_validation import (
    FileCategory,
    FileTypeValidator,
    FileValidationError,
    get_file_type_from_content,
    validate_audio_file,
    validate_file_type,
    validate_image_file,
    validate_media_for_audio_extraction,
    validate_video_file,
)

__all__ = [
    # Expression evaluation
    "ExpressionError",
    # File validation
    "FileCategory",
    "FileTypeValidator",
    "FileValidationError",
    "SafeExpressionEvaluator",
    "evaluate_condition",
    "get_evaluator",
    "get_file_type_from_content",
    "parse_frame_rate",
    "validate_audio_file",
    "validate_file_type",
    "validate_image_file",
    "validate_media_for_audio_extraction",
    "validate_video_file",
]
