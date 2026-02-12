"""
Security module for VoiceStudio API.

Provides route security configuration and authentication utilities.
"""

from .route_security import (
    SecurityLevel,
    ROUTE_SECURITY_MATRIX,
    SENSITIVE_OPERATIONS,
    get_security_level,
    is_sensitive_operation,
    get_route_security_matrix_report,
)

__all__ = [
    "SecurityLevel",
    "ROUTE_SECURITY_MATRIX",
    "SENSITIVE_OPERATIONS",
    "get_security_level",
    "is_sensitive_operation",
    "get_route_security_matrix_report",
]
