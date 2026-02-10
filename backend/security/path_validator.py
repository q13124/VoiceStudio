"""
Path Traversal Prevention.

Task 2.2.3: Comprehensive path validation.
Prevents path traversal attacks and validates file paths.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


class PathValidationError(Exception):
    """Raised when path validation fails."""
    
    def __init__(self, message: str, path: str, violation: str):
        super().__init__(message)
        self.path = path
        self.violation = violation


@dataclass
class PathValidatorConfig:
    """Configuration for path validator."""
    # Allowed base directories
    allowed_bases: List[str] = field(default_factory=lambda: [
        "data",
        "uploads",
        "projects",
        "exports",
    ])
    
    # Blocked patterns
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r"\.\.",           # Parent directory
        r"~",              # Home directory
        r"^\s*\|",         # Pipe commands
        r";\s*",           # Command chaining
        r"\$\(",           # Command substitution
        r"`",              # Backtick execution
        r"\x00",           # Null bytes
    ])
    
    # Blocked file names
    blocked_names: Set[str] = field(default_factory=lambda: {
        "con", "prn", "aux", "nul",  # Windows reserved
        "com1", "com2", "com3", "com4",
        "lpt1", "lpt2", "lpt3", "lpt4",
        ".htaccess", ".htpasswd",
        "web.config",
        ".git", ".svn",
    })
    
    # Maximum path length
    max_path_length: int = 260
    
    # Maximum filename length
    max_filename_length: int = 255


class PathValidator:
    """
    Validates and sanitizes file paths.
    
    Features:
    - Path traversal prevention
    - Base directory enforcement
    - Reserved name checking
    - Path length limits
    - Dangerous pattern detection
    """
    
    def __init__(self, config: Optional[PathValidatorConfig] = None):
        self.config = config or PathValidatorConfig()
        
        self._blocked_patterns = [
            re.compile(p) for p in self.config.blocked_patterns
        ]
    
    def validate(
        self,
        path: str,
        base_dir: Optional[str] = None,
    ) -> str:
        """
        Validate and normalize a path.
        
        Args:
            path: Path to validate
            base_dir: Required base directory
            
        Returns:
            Normalized safe path
            
        Raises:
            PathValidationError: If path is invalid
        """
        if not path:
            raise PathValidationError(
                "Empty path",
                path="",
                violation="empty",
            )
        
        # Check length
        if len(path) > self.config.max_path_length:
            raise PathValidationError(
                f"Path too long: {len(path)} > {self.config.max_path_length}",
                path=path,
                violation="length",
            )
        
        # Check for blocked patterns
        for pattern in self._blocked_patterns:
            if pattern.search(path):
                raise PathValidationError(
                    f"Blocked pattern detected in path",
                    path=path,
                    violation="pattern",
                )
        
        # Normalize path
        try:
            normalized = os.path.normpath(path)
        except Exception as e:
            raise PathValidationError(
                f"Path normalization failed: {e}",
                path=path,
                violation="normalization",
            )
        
        # Check for path traversal after normalization
        if ".." in normalized:
            raise PathValidationError(
                "Path traversal detected",
                path=path,
                violation="traversal",
            )
        
        # Check filename
        filename = os.path.basename(normalized)
        self._validate_filename(filename)
        
        # Check base directory
        if base_dir:
            self._validate_base(normalized, base_dir)
        else:
            # Check against allowed bases
            self._validate_allowed_base(normalized)
        
        return normalized
    
    def _validate_filename(self, filename: str) -> None:
        """Validate a filename."""
        if not filename:
            return
        
        # Check length
        if len(filename) > self.config.max_filename_length:
            raise PathValidationError(
                f"Filename too long: {len(filename)}",
                path=filename,
                violation="filename_length",
            )
        
        # Check blocked names
        name_lower = filename.lower().split(".")[0]
        if name_lower in self.config.blocked_names:
            raise PathValidationError(
                f"Blocked filename: {filename}",
                path=filename,
                violation="blocked_name",
            )
        
        # Check for hidden files (starting with .)
        if filename.startswith(".") and filename not in {".", ".."}:
            # Allow some hidden files but log
            logger.debug(f"Hidden file accessed: {filename}")
    
    def _validate_base(self, path: str, base_dir: str) -> None:
        """Ensure path is within base directory."""
        try:
            # Resolve to absolute paths
            base_resolved = os.path.realpath(base_dir)
            path_resolved = os.path.realpath(
                os.path.join(base_dir, path) if not os.path.isabs(path) else path
            )
            
            # Check if path is under base
            common = os.path.commonpath([base_resolved, path_resolved])
            if common != base_resolved:
                raise PathValidationError(
                    "Path escapes base directory",
                    path=path,
                    violation="base_escape",
                )
                
        except ValueError:
            raise PathValidationError(
                "Path validation failed",
                path=path,
                violation="base_check",
            )
    
    def _validate_allowed_base(self, path: str) -> None:
        """Check path starts with an allowed base."""
        if os.path.isabs(path):
            # Absolute paths need explicit base_dir
            return
        
        path_parts = Path(path).parts
        if not path_parts:
            return
        
        first_part = path_parts[0].lower()
        allowed = [b.lower() for b in self.config.allowed_bases]
        
        if first_part not in allowed:
            raise PathValidationError(
                f"Path must start with allowed base: {self.config.allowed_bases}",
                path=path,
                violation="base_not_allowed",
            )
    
    def sanitize(self, path: str) -> str:
        """
        Sanitize a path by removing dangerous characters.
        
        Note: Validation should still be performed after sanitization.
        """
        # Remove null bytes
        sanitized = path.replace("\x00", "")
        
        # Remove control characters
        sanitized = "".join(c for c in sanitized if ord(c) >= 32)
        
        # Normalize slashes
        sanitized = sanitized.replace("\\", "/")
        
        # Remove multiple slashes
        while "//" in sanitized:
            sanitized = sanitized.replace("//", "/")
        
        # Remove leading slashes for relative paths
        sanitized = sanitized.lstrip("/")
        
        return sanitized
    
    def join_safe(self, base: str, *parts: str) -> str:
        """
        Safely join path components.
        
        Each part is validated before joining.
        """
        result = base
        
        for part in parts:
            # Sanitize part
            clean_part = self.sanitize(part)
            
            # Validate part
            self.validate(clean_part, base_dir=base)
            
            result = os.path.join(result, clean_part)
        
        return result
    
    def is_safe(self, path: str, base_dir: Optional[str] = None) -> bool:
        """Check if path is safe (returns bool instead of raising)."""
        try:
            self.validate(path, base_dir)
            return True
        except PathValidationError:
            return False


# Global validator
_validator: Optional[PathValidator] = None


def get_path_validator() -> PathValidator:
    """Get or create the global path validator."""
    global _validator
    if _validator is None:
        _validator = PathValidator()
    return _validator
