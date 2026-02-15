"""
Base Tool

Abstract base class for all governed tools.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    """
    Result of a tool execution.

    Attributes:
        success: Whether the tool executed successfully
        output: Output data from the tool
        error: Error message if failed
        metadata: Additional metadata about the execution
    """

    success: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, output: Any = None, **metadata) -> "ToolResult":
        """Create a successful result."""
        return cls(success=True, output=output, metadata=metadata)

    @classmethod
    def fail(cls, error: str, **metadata) -> "ToolResult":
        """Create a failed result."""
        return cls(success=False, error=error, metadata=metadata)


class BaseTool(ABC):
    """
    Abstract base class for governed tools.

    All tools must inherit from this class and implement the execute method.
    Tools should NOT perform actions directly - they are invoked through
    the ToolGateway which handles policy enforcement and auditing.
    """

    # Tool name (override in subclass)
    name: str = "BaseTool"

    # Human-readable description
    description: str = "Base tool class"

    # Required parameters
    required_params: tuple = ()

    # Optional parameters with defaults
    optional_params: dict[str, Any] = {}

    @abstractmethod
    def execute(self, **params) -> ToolResult:
        """
        Execute the tool with given parameters.

        This method should only be called through the ToolGateway.

        Args:
            **params: Tool-specific parameters

        Returns:
            ToolResult with success/failure and output
        """
        pass

    def validate_params(self, params: dict[str, Any]) -> str | None:
        """
        Validate parameters before execution.

        Args:
            params: Parameters to validate

        Returns:
            Error message if validation fails, None if valid
        """
        # Check required parameters
        for param in self.required_params:
            if param not in params:
                return f"Missing required parameter: {param}"

        return None

    def get_param(
        self,
        params: dict[str, Any],
        name: str,
        default: Any = None,
    ) -> Any:
        """Get a parameter with default fallback."""
        if name in params:
            return params[name]
        if name in self.optional_params:
            return self.optional_params[name]
        return default
