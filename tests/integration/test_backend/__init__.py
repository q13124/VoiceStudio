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
    create_test_database,
    create_test_client,
    DatabaseTestContext,
    ServiceTestContext,
)

__all__ = [
    "IntegrationTestBase",
    "create_test_database",
    "create_test_client",
    "DatabaseTestContext",
    "ServiceTestContext",
]
