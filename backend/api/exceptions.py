"""
Custom Exceptions for VoiceStudio Backend API

Domain-specific exceptions that provide better error context and user-friendly messages.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class VoiceStudioException(HTTPException):
    """Base exception for all VoiceStudio-specific errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        recovery_suggestion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.recovery_suggestion = recovery_suggestion
        self.context = context or {}


# Resource Not Found Exceptions


class ProfileNotFoundException(VoiceStudioException):
    """Raised when a voice profile is not found."""

    def __init__(self, profile_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{profile_id}' not found.",
            error_code="PROFILE_NOT_FOUND",
            recovery_suggestion="Please verify the profile ID exists or create a new profile.",
            context={"profile_id": profile_id},
        )


class ProjectNotFoundException(VoiceStudioException):
    """Raised when a project is not found."""

    def __init__(self, project_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
            error_code="PROJECT_NOT_FOUND",
            recovery_suggestion="Please verify the project ID exists or create a new project.",
            context={"project_id": project_id},
        )


class EffectChainNotFoundException(VoiceStudioException):
    """Raised when an effect chain is not found."""

    def __init__(self, chain_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Effect chain '{chain_id}' not found.",
            error_code="EFFECT_CHAIN_NOT_FOUND",
            recovery_suggestion="Please verify the effect chain ID exists or create a new effect chain.",
            context={"chain_id": chain_id},
        )


class AudioFileNotFoundException(VoiceStudioException):
    """Raised when an audio file is not found."""

    def __init__(self, audio_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file '{audio_id}' not found.",
            error_code="AUDIO_FILE_NOT_FOUND",
            recovery_suggestion="Please verify the audio ID exists or upload a new audio file.",
            context={"audio_id": audio_id},
        )


# Validation Exceptions


class InvalidInputException(VoiceStudioException):
    """Raised when input validation fails."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            error_code="INVALID_INPUT",
            recovery_suggestion="Please check your input and try again.",
            context={"field": field, "value": value},
        )


class InvalidEngineException(VoiceStudioException):
    """Raised when an invalid or unavailable engine is specified."""

    def __init__(self, engine: str, available_engines: Optional[list[str]] = None):
        engines_str = ", ".join(available_engines) if available_engines else "none"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid engine '{engine}'. Available engines: {engines_str}",
            error_code="INVALID_ENGINE",
            recovery_suggestion=f"Please select one of the available engines: {engines_str}",
            context={"engine": engine, "available_engines": available_engines or []},
        )


# Resource Conflict Exceptions


class ResourceAlreadyExistsException(VoiceStudioException):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource_type} '{resource_id}' already exists.",
            error_code="RESOURCE_ALREADY_EXISTS",
            recovery_suggestion=f"Use a different {resource_type.lower()} ID or update the existing one.",
            context={"resource_type": resource_type, "resource_id": resource_id},
        )


# Engine and Processing Exceptions


class EngineUnavailableException(VoiceStudioException):
    """Raised when an engine is unavailable or failed to initialize."""

    def __init__(self, engine: str, reason: Optional[str] = None):
        detail = f"Engine '{engine}' is not available"
        if reason:
            detail += f": {reason}"
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="ENGINE_UNAVAILABLE",
            recovery_suggestion="Please try again later or use a different engine.",
            context={"engine": engine, "reason": reason},
        )


class EngineProcessingException(VoiceStudioException):
    """Raised when an engine fails during processing."""

    def __init__(self, engine: str, operation: str, error_message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Engine '{engine}' failed during {operation}: {error_message}",
            error_code="ENGINE_PROCESSING_ERROR",
            recovery_suggestion="Please try again or contact support if the issue persists.",
            context={
                "engine": engine,
                "operation": operation,
                "error_message": error_message,
            },
        )


class AudioProcessingException(VoiceStudioException):
    """Raised when audio processing fails."""

    def __init__(self, operation: str, error_message: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing failed during {operation}: {error_message}",
            error_code="AUDIO_PROCESSING_ERROR",
            recovery_suggestion="Please check the audio file format and try again.",
            context={"operation": operation, "error_message": error_message},
        )


# File and Storage Exceptions


class FileNotFoundException(VoiceStudioException):
    """Raised when a file is not found on disk."""

    def __init__(self, file_path: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            recovery_suggestion="Please verify the file path exists or upload the file again.",
            context={"file_path": file_path},
        )


class StorageLimitExceededException(VoiceStudioException):
    """Raised when storage limit is exceeded."""

    def __init__(self, resource_type: str, limit: int):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Storage limit exceeded for {resource_type}. Maximum allowed: {limit}",
            error_code="STORAGE_LIMIT_EXCEEDED",
            recovery_suggestion=f"Please delete some {resource_type.lower()}s or contact support to increase your limit.",
            context={"resource_type": resource_type, "limit": limit},
        )


# Rate Limiting Exceptions


class RateLimitExceededException(VoiceStudioException):
    """Raised when rate limit is exceeded."""

    def __init__(self, operation: str, retry_after: Optional[int] = None):
        detail = f"Rate limit exceeded for {operation}"
        recovery = "Please wait a moment before trying again."
        if retry_after:
            detail += f". Retry after {retry_after} seconds"
            recovery = f"Please wait {retry_after} seconds before trying again."

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
            recovery_suggestion=recovery,
            context={"operation": operation, "retry_after": retry_after},
        )


# Configuration Exceptions


class ConfigurationException(VoiceStudioException):
    """Raised when there's a configuration error."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {message}",
            error_code="CONFIGURATION_ERROR",
            recovery_suggestion="Please check your configuration or contact support.",
            context={"config_key": config_key},
        )


# Operation Cancellation Exception


class OperationCancelledException(VoiceStudioException):
    """Raised when an operation is cancelled by the user."""

    def __init__(self, operation: str):
        # Using 499 (Client Closed Request) - commonly used for cancelled requests
        # Not a standard HTTP status but widely recognized (Nginx convention)
        super().__init__(
            status_code=499,
            detail=f"Operation '{operation}' was cancelled.",
            error_code="OPERATION_CANCELLED",
            recovery_suggestion="You can restart the operation if needed.",
            context={"operation": operation},
        )
