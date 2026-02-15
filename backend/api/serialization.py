"""
Serialization Consistency Module.

Provides standardized serialization patterns for the VoiceStudio API:
- Consistent JSON encoding/decoding
- Standardized Pydantic model configurations
- Response formatting utilities
- Date/time handling

Usage:
    from backend.api.serialization import (
        api_json_encoder,
        serialize_response,
        BaseApiModel,
        StandardResponse,
    )
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# JSON Encoding Standards
# =============================================================================


class ApiJsonEncoder(json.JSONEncoder):
    """
    Standard JSON encoder for API responses.

    Handles:
    - datetime/date/timedelta
    - UUID
    - Decimal
    - Enum
    - Path
    - Pydantic models
    - Dataclasses
    - Sets
    - Bytes
    """

    def default(self, obj: Any) -> Any:
        # Datetime handling
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return obj.total_seconds()

        # UUID handling
        if isinstance(obj, UUID):
            return str(obj)

        # Decimal handling (preserve precision)
        if isinstance(obj, Decimal):
            return float(obj)

        # Enum handling
        if isinstance(obj, Enum):
            return obj.value

        # Path handling
        if isinstance(obj, Path):
            return str(obj)

        # Pydantic model handling
        if isinstance(obj, BaseModel):
            return obj.model_dump()

        # Set handling
        if isinstance(obj, (set, frozenset)):
            return list(obj)

        # Bytes handling
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")

        # Dataclass handling
        if hasattr(obj, "__dataclass_fields__"):
            return {k: getattr(obj, k) for k in obj.__dataclass_fields__}

        return super().default(obj)


def api_json_dumps(
    obj: Any,
    *,
    indent: int | None = None,
    sort_keys: bool = False,
) -> str:
    """
    Serialize object to JSON string using standard encoding.

    Args:
        obj: Object to serialize
        indent: Indentation level (None for compact)
        sort_keys: Whether to sort dictionary keys

    Returns:
        JSON string
    """
    return json.dumps(
        obj,
        cls=ApiJsonEncoder,
        indent=indent,
        sort_keys=sort_keys,
        ensure_ascii=False,
    )


def api_json_loads(s: str | bytes) -> Any:
    """
    Deserialize JSON string to object.

    Args:
        s: JSON string or bytes

    Returns:
        Deserialized object
    """
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    return json.loads(s)


# =============================================================================
# Standard Pydantic Configuration
# =============================================================================


# Standard config for API request models
REQUEST_MODEL_CONFIG = ConfigDict(
    # Performance optimizations
    validate_assignment=False,
    validate_default=False,
    use_enum_values=True,
    # String handling
    str_strip_whitespace=True,
    # Extra field handling
    extra="forbid",
    # Serialization
    populate_by_name=True,
)

# Standard config for API response models
RESPONSE_MODEL_CONFIG = ConfigDict(
    # Optimized for serialization
    validate_assignment=False,
    validate_default=False,
    use_enum_values=True,
    # Allow extra fields in responses for forward compatibility
    extra="ignore",
    # Serialization options
    populate_by_name=True,
    ser_json_timedelta="float",
    ser_json_bytes="base64",
)

# Standard config for strict models (full validation)
STRICT_MODEL_CONFIG = ConfigDict(
    validate_assignment=True,
    validate_default=True,
    use_enum_values=True,
    str_strip_whitespace=True,
    extra="forbid",
    strict=True,
)


# =============================================================================
# Base Model Classes
# =============================================================================


class BaseApiModel(BaseModel):
    """
    Base model for all API models with standard configuration.

    Features:
    - Consistent serialization
    - Performance optimizations
    - Standard field aliases
    """

    model_config = RESPONSE_MODEL_CONFIG

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return api_json_dumps(self.model_dump())

    @classmethod
    def from_json(cls, s: str | bytes) -> BaseApiModel:
        """Deserialize from JSON string."""
        data = api_json_loads(s)
        return cls.model_validate(data)


class BaseRequestModel(BaseModel):
    """Base model for API request payloads."""

    model_config = REQUEST_MODEL_CONFIG

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return api_json_dumps(self.model_dump())


class BaseResponseModel(BaseModel):
    """Base model for API response payloads."""

    model_config = RESPONSE_MODEL_CONFIG

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return api_json_dumps(self.model_dump())


# =============================================================================
# Standard Response Types
# =============================================================================


class SuccessResponse(BaseResponseModel):
    """Standard success response."""

    ok: bool = True
    message: str | None = None


class ErrorResponse(BaseResponseModel):
    """Standard error response."""

    ok: bool = False
    error: str
    error_code: str | None = None
    details: dict[str, Any] | None = None
    request_id: str | None = None


class PaginatedResponse(BaseResponseModel, Generic[T]):
    """Standard paginated response."""

    items: list[Any] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False

    @classmethod
    def create(
        cls,
        items: list[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse:
        """Create paginated response from items."""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=(page * page_size) < total,
        )


class StandardResponse(BaseResponseModel, Generic[T]):
    """
    Standard wrapper for API responses.

    Provides consistent structure across all endpoints.
    """

    ok: bool = True
    data: Any | None = None
    message: str | None = None
    warnings: list[str] = Field(default_factory=list)
    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str | None = None,
        request_id: str | None = None,
    ) -> StandardResponse:
        """Create success response."""
        return cls(
            ok=True,
            data=data,
            message=message,
            request_id=request_id,
        )

    @classmethod
    def error(
        cls,
        message: str,
        data: Any = None,
        request_id: str | None = None,
    ) -> StandardResponse:
        """Create error response."""
        return cls(
            ok=False,
            data=data,
            message=message,
            request_id=request_id,
        )


# =============================================================================
# Response Serialization Utilities
# =============================================================================


def serialize_response(
    data: Any,
    *,
    exclude_none: bool = True,
    exclude_unset: bool = False,
) -> dict[str, Any]:
    """
    Serialize response data to dictionary.

    Args:
        data: Data to serialize
        exclude_none: Exclude None values
        exclude_unset: Exclude unset fields

    Returns:
        Serialized dictionary
    """
    if isinstance(data, BaseModel):
        return data.model_dump(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
        )

    if hasattr(data, "__dataclass_fields__"):
        result = {}
        for field_name in data.__dataclass_fields__:
            value = getattr(data, field_name)
            if exclude_none and value is None:
                continue
            result[field_name] = value
        return result

    if isinstance(data, dict):
        if exclude_none:
            return {k: v for k, v in data.items() if v is not None}
        return data

    return {"value": data}


def format_datetime(
    dt: datetime | None,
    *,
    format_str: str | None = None,
) -> str | None:
    """
    Format datetime for API response.

    Args:
        dt: Datetime to format
        format_str: Custom format string (default: ISO 8601)

    Returns:
        Formatted string or None
    """
    if dt is None:
        return None
    if format_str:
        return dt.strftime(format_str)
    return dt.isoformat()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1h 23m 45s")
    """
    if seconds < 0:
        return "0s"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_file_size(bytes_size: int) -> str:
    """
    Format file size in bytes to human-readable string.

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if bytes_size < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_size)

    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} PB"


# =============================================================================
# Validation Helpers
# =============================================================================


def validate_json_string(s: str) -> bool:
    """
    Check if string is valid JSON.

    Args:
        s: String to validate

    Returns:
        True if valid JSON
    """
    try:
        json.loads(s)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def safe_parse_json(
    s: str | bytes,
    default: Any = None,
) -> Any:
    """
    Safely parse JSON string, returning default on failure.

    Args:
        s: JSON string or bytes
        default: Default value on parse failure

    Returns:
        Parsed value or default
    """
    try:
        return api_json_loads(s)
    except (json.JSONDecodeError, TypeError) as e:
        logger.debug("JSON parse failed: %s", e)
        return default


# =============================================================================
# Field Conversion Helpers
# =============================================================================


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_keys(
    data: dict[str, Any],
    converter: Callable[[str], str],
) -> dict[str, Any]:
    """
    Convert all dictionary keys using converter function.

    Args:
        data: Dictionary to convert
        converter: Key conversion function

    Returns:
        Dictionary with converted keys
    """
    result: dict[str, Any] = {}
    for key, value in data.items():
        new_key = converter(key)
        if isinstance(value, dict):
            result[new_key] = convert_keys(value, converter)
        elif isinstance(value, list):
            converted_list: list[Any] = []
            for item in value:
                if isinstance(item, dict):
                    converted_list.append(convert_keys(item, converter))
                else:
                    converted_list.append(item)
            result[new_key] = converted_list
        else:
            result[new_key] = value
    return result
