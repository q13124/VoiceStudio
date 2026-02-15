"""
Backend Integration Test Framework.

Provides base classes, fixtures, and utilities for backend integration testing.

This module includes:
- IntegrationTestBase: Base class for all backend integration tests
- Database fixtures with transaction rollback
- API client with response tracking
- Test isolation and cleanup utilities
"""

from .base import IntegrationTestBase
from .fixtures import (
    DatabaseTestContext,
    ServiceTestContext,
    create_test_client,
    create_test_database,
)

__all__ = [
    "DatabaseTestContext",
    "IntegrationTestBase",
    "ServiceTestContext",
    "create_test_client",
    "create_test_database",
]
