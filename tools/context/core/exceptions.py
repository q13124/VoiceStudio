from __future__ import annotations


class ConfigValidationError(ValueError):
    """Raised when context configuration fails validation."""

    def __init__(self, errors: list[str]):
        super().__init__("Context config validation failed")
        self.errors = errors


class SourceFetchError(RuntimeError):
    """Raised when a source adapter fails to fetch."""
