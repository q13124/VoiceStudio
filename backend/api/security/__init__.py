"""
Security module for VoiceStudio API.

Provides route security configuration and authentication utilities.
"""

from .route_security import (
    ROUTE_SECURITY_MATRIX,
    SENSITIVE_OPERATIONS,
    SecurityLevel,
    get_route_security_matrix_report,
    get_security_level,
    is_sensitive_operation,
)

__all__ = [
    "ROUTE_SECURITY_MATRIX",
    "SENSITIVE_OPERATIONS",
    "SecurityLevel",
    "get_route_security_matrix_report",
    "get_security_level",
    "is_sensitive_operation",
]
