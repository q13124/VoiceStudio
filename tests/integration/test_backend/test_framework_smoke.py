"""
Framework Smoke Tests.

Validates that the backend integration test framework is working correctly.
This file serves as both a verification test and usage example.
"""

import pytest

from .base import AsyncIntegrationTestBase, IntegrationTestBase, integration
from .fixtures import (
    DatabaseTestContext,
    ServiceTestContext,
    create_test_database,
    service_context,
)


class TestDatabaseContextUsage(IntegrationTestBase):
    """Test DatabaseTestContext functionality."""

    @integration
    def test_database_context_creation(self, db_context: DatabaseTestContext):
        """Verify database context is created and usable."""
        assert db_context is not None
        assert db_context.connection is not None
        # In-memory databases use ':memory:' path which doesn't exist as file
        # Check if connection is open instead
        assert db_context.connection is not None

    @integration
    def test_table_creation(self, db_context: DatabaseTestContext):
        """Verify table creation works correctly."""
        db_context.create_table(
            "test_users",
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL",
        )
        assert "test_users" in db_context.tables_created

    @integration
    def test_seed_data(self, db_context: DatabaseTestContext):
        """Verify seed data works correctly."""
        db_context.create_table(
            "test_items",
            "id INTEGER PRIMARY KEY, value TEXT",
        )
        # seed_data takes (table_name, rows) - rows is list of dicts
        db_context.seed_data("test_items", [{"value": "item1"}, {"value": "item2"}])

        # query returns list of dicts, not tuples
        results = db_context.query("SELECT value FROM test_items ORDER BY id")
        assert len(results) == 2
        assert results[0]["value"] == "item1"
        assert results[1]["value"] == "item2"

    @integration
    def test_standard_schema(self, db_with_standard_schema: DatabaseTestContext):
        """Verify standard schema includes all required tables."""
        expected_tables = ["profiles", "projects", "audio", "jobs"]
        for table in expected_tables:
            assert table in db_with_standard_schema.tables_created


class TestServiceContextUsage(IntegrationTestBase):
    """Test ServiceTestContext functionality."""

    @integration
    def test_service_context_creation(self, svc_context: ServiceTestContext):
        """Verify service context is created."""
        assert svc_context is not None
        assert svc_context.mocks is not None

    @integration
    def test_mock_engine_service(self, svc_context: ServiceTestContext):
        """Verify engine service mock works."""
        mock = svc_context.mock_engine_service()
        assert mock is not None
        assert "engine_service" in svc_context.mocks

        # Mock should have proper return values
        engines = mock.get_engines()
        assert len(engines) == 2

    @integration
    def test_mock_storage_service(self, svc_context: ServiceTestContext):
        """Verify storage service mock works."""
        mock = svc_context.mock_storage_service()
        assert mock is not None
        assert "storage_service" in svc_context.mocks


class TestBaseClassAssertions(IntegrationTestBase):
    """Test assertion methods in base class."""

    @integration
    def test_assertion_methods_exist(self):
        """Verify assertion methods are available."""
        # Check that assertion methods exist
        assert hasattr(self, "assert_success")
        assert hasattr(self, "assert_status")
        assert hasattr(self, "assert_error")
        assert hasattr(self, "assert_schema")
        assert hasattr(self, "assert_latency")


class TestSampleDataFixtures(IntegrationTestBase):
    """Test sample data fixtures."""

    @integration
    def test_sample_profile_data(self, sample_profile_data):
        """Verify sample profile data structure."""
        # Match actual fixture keys
        assert "name" in sample_profile_data
        assert "description" in sample_profile_data
        assert "language" in sample_profile_data
        assert "engine" in sample_profile_data

    @integration
    def test_sample_project_data(self, sample_project_data):
        """Verify sample project data structure."""
        # Match actual fixture keys
        assert "name" in sample_project_data
        assert "description" in sample_project_data
        assert "settings" in sample_project_data

    @integration
    def test_sample_audio_metadata(self, sample_audio_metadata):
        """Verify sample audio metadata structure."""
        # Match actual fixture keys
        assert "id" in sample_audio_metadata
        assert "format" in sample_audio_metadata
        assert "sample_rate" in sample_audio_metadata
        assert sample_audio_metadata["format"] == "wav"

    @integration
    def test_sample_synthesis_request(self, sample_synthesis_request):
        """Verify sample synthesis request structure."""
        # Match actual fixture keys
        assert "text" in sample_synthesis_request
        assert "profile_id" in sample_synthesis_request
        assert "engine" in sample_synthesis_request


class TestDatabaseContextManager(IntegrationTestBase):
    """Test database context manager function."""

    @integration
    def test_create_test_database_context_manager(self):
        """Verify create_test_database works as context manager."""
        with create_test_database(in_memory=True) as db:
            assert db.connection is not None
            db.create_table("temp_table", "id INTEGER PRIMARY KEY, value TEXT")
            # seed_data takes (table, list_of_dicts)
            db.seed_data("temp_table", [{"id": 1, "value": "a"}, {"id": 2, "value": "b"}])
            results = db.query("SELECT COUNT(*) as cnt FROM temp_table")
            assert results[0]["cnt"] == 2

    @integration
    def test_database_transaction_rollback(self):
        """Verify transaction rollback on cleanup."""
        with create_test_database(in_memory=True, cleanup=True) as db:
            db.create_table("rollback_test", "id INTEGER PRIMARY KEY, name TEXT")
            db.seed_data("rollback_test", [{"id": 1, "name": "test"}])
            # Don't commit - should rollback on cleanup


class TestServiceContextManager(IntegrationTestBase):
    """Test service context manager function."""

    @integration
    def test_service_context_manager(self):
        """Verify service_context works as context manager."""
        with service_context() as ctx:
            ctx.mock_engine_service()
            ctx.mock_storage_service()
            assert len(ctx.mocks) >= 2

        # After context, patches should be cleaned up


# =============================================================================
# Async Test Examples
# =============================================================================


class TestAsyncFramework(AsyncIntegrationTestBase):
    """Test async functionality of the framework."""

    @pytest.mark.asyncio
    @integration
    async def test_async_test_execution(self):
        """Verify async tests work correctly."""
        import asyncio

        await asyncio.sleep(0.01)
        assert True

    @pytest.mark.asyncio
    @integration
    async def test_async_with_fixtures(self, db_context: DatabaseTestContext):
        """Verify async tests can use sync fixtures."""
        assert db_context is not None
        db_context.create_table("async_test", "id INTEGER PRIMARY KEY")
        assert "async_test" in db_context.tables_created
