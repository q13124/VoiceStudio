"""
DateTime utilities for consistent ISO 8601 formatting throughout the API.

This module provides:
- UTC timestamp generation with proper timezone info
- ISO 8601 formatting with Z suffix (recommended for JSON APIs)
- Timezone-aware datetime operations
"""
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """
    Get current UTC time as a timezone-aware datetime.
    
    Returns:
        datetime: Current UTC time with timezone info.
    """
    return datetime.now(timezone.utc)


def to_iso8601(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to ISO 8601 string with UTC timezone.
    
    Args:
        dt: datetime to convert (can be naive or aware)
        
    Returns:
        ISO 8601 formatted string (e.g., "2024-01-15T10:30:00Z")
        or None if input is None.
    
    Note:
        - Naive datetimes are assumed to be UTC
        - Non-UTC timezones are converted to UTC
        - The output always uses Z suffix (not +00:00)
    """
    if dt is None:
        return None
    
    # Ensure timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        dt = dt.astimezone(timezone.utc)
    
    # Format with Z suffix (more compact than +00:00)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def to_iso8601_with_micros(dt: Optional[datetime]) -> Optional[str]:
    """
    Convert datetime to ISO 8601 string with microseconds.
    
    Args:
        dt: datetime to convert
        
    Returns:
        ISO 8601 formatted string with microseconds
        (e.g., "2024-01-15T10:30:00.123456Z")
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    # Format with microseconds and Z suffix
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def from_iso8601(s: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO 8601 string to timezone-aware datetime.
    
    Args:
        s: ISO 8601 formatted string
        
    Returns:
        Timezone-aware datetime in UTC, or None if input is None.
        
    Raises:
        ValueError: If the string is not a valid ISO 8601 format.
    """
    if s is None:
        return None
    
    # Handle Z suffix (replace with +00:00 for fromisoformat)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    
    return datetime.fromisoformat(s)


def timestamp_now() -> str:
    """
    Get current UTC timestamp in ISO 8601 format.
    
    Returns:
        ISO 8601 formatted UTC timestamp string.
        
    Example:
        >>> timestamp_now()
        "2024-01-15T10:30:00Z"
    """
    return to_iso8601(utc_now())  # type: ignore


def timestamp_now_with_micros() -> str:
    """
    Get current UTC timestamp in ISO 8601 format with microseconds.
    
    Returns:
        ISO 8601 formatted UTC timestamp string with microseconds.
    """
    return to_iso8601_with_micros(utc_now())  # type: ignore
