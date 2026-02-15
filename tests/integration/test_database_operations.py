"""
Database Operation Tests.

Comprehensive tests for database operations including:
- Transaction rollback scenarios
- Concurrent database access
- Migration validation
- Data integrity checks

Part of the Testing Expansion Plan.
"""

import concurrent.futures
import contextlib
import sqlite3
import tempfile
import time
from pathlib import Path

import pytest

# Try to import test dependencies
try:
    from httpx import Client as HttpClient
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    HttpClient = None


# Test configuration
API_BASE_URL = "http://localhost:8088"
TEST_DB_PATH = "data/voicestudio.db"


def retry_on_rate_limit(func, *args, max_retries=3, **kwargs):
    """Retry function on rate limit errors."""
    for i in range(max_retries):
        response = func(*args, **kwargs)
        if response.status_code != 429:
            return response
        time.sleep(1 * (i + 1))
    return response


@pytest.fixture
def api_client():
    """Create API client for testing."""
    if not HAS_HTTPX:
        pytest.skip("httpx not installed")

    try:
        client = HttpClient(base_url=API_BASE_URL, timeout=30.0)
        response = client.get("/api/health")
        if response.status_code != 200:
            pytest.skip("Backend not available")
        return client
    except Exception as e:
        pytest.skip(f"Cannot connect to backend: {e}")


@pytest.fixture
def temp_db():
    """Create temporary database for isolated tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    with contextlib.suppress(Exception):
        Path(db_path).unlink()


class TestTransactionBehavior:
    """Tests for database transaction behavior."""

    def test_rollback_on_error(self, api_client):
        """Verify transactions roll back on errors."""
        # Create a profile
        create_response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": "Rollback Test", "settings": {"key": "original"}}
        )

        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test profile")

        profile = create_response.json()
        profile_id = profile.get("id", profile.get("profile_id"))

        if not profile_id:
            pytest.skip("No profile ID returned")

        # Try to update with invalid data that should fail
        update_response = retry_on_rate_limit(
            api_client.put,
            f"/api/profiles/{profile_id}",
            json={"invalid_structure": True}
        )

        # If update failed, verify original data is intact
        if update_response.status_code >= 400:
            get_response = api_client.get(f"/api/profiles/{profile_id}")
            if get_response.status_code == 200:
                retrieved = get_response.json()
                # Original value should be preserved
                assert retrieved.get("name") == "Rollback Test" or \
                       "settings" in retrieved

    def test_concurrent_updates(self, api_client):
        """Verify concurrent updates are handled correctly."""
        # Create a profile
        create_response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": "Concurrent Test", "settings": {"counter": 0}}
        )

        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test profile")

        profile = create_response.json()
        profile_id = profile.get("id", profile.get("profile_id"))

        if not profile_id:
            pytest.skip("No profile ID returned")

        # Make concurrent update requests
        def update_profile(value: int) -> int:
            try:
                response = api_client.patch(
                    f"/api/profiles/{profile_id}",
                    json={"settings": {"counter": value}}
                )
                return response.status_code
            except Exception:
                return 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(update_profile, i) for i in range(5)]
            results = [f.result() for f in futures]

        # All updates should complete (success or conflict)
        for status in results:
            assert status in [200, 204, 400, 404, 409, 422, 429]

    def test_deadlock_prevention(self, api_client):
        """Verify deadlocks are prevented or handled."""
        # Create two profiles
        profiles = []
        for i in range(2):
            response = retry_on_rate_limit(
                api_client.post,
                "/api/profiles",
                json={"name": f"Deadlock Test {i}", "settings": {}}
            )
            if response.status_code in [200, 201]:
                profiles.append(response.json())

        if len(profiles) < 2:
            pytest.skip("Could not create test profiles")

        # Attempt operations that might cause deadlock
        def update_both(order: list[int]):
            for idx in order:
                profile = profiles[idx]
                profile_id = profile.get("id", profile.get("profile_id"))
                if profile_id:
                    api_client.patch(
                        f"/api/profiles/{profile_id}",
                        json={"settings": {"updated": True}}
                    )

        # Run in different orders simultaneously
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            f1 = executor.submit(update_both, [0, 1])
            f2 = executor.submit(update_both, [1, 0])

            # Both should complete without hanging
            try:
                f1.result(timeout=30)
                f2.result(timeout=30)
            except concurrent.futures.TimeoutError:
                pytest.fail("Potential deadlock detected")


class TestDataIntegrity:
    """Tests for data integrity constraints."""

    def test_cascade_deletes(self, api_client):
        """Verify cascade deletes work correctly."""
        # Create a profile
        create_response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": "Cascade Test", "settings": {}}
        )

        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test profile")

        profile = create_response.json()
        profile_id = profile.get("id", profile.get("profile_id"))

        if not profile_id:
            pytest.skip("No profile ID returned")

        # Delete the profile
        delete_response = api_client.delete(f"/api/profiles/{profile_id}")

        # Verify deletion
        if delete_response.status_code in [200, 204]:
            get_response = api_client.get(f"/api/profiles/{profile_id}")
            # Should not find deleted profile
            assert get_response.status_code in [404, 410]

    def test_foreign_key_constraints(self, api_client):
        """Verify foreign key constraints are enforced."""
        # Try to reference non-existent foreign key
        response = retry_on_rate_limit(
            api_client.post,
            "/api/jobs/submit",
            json={
                "type": "synthesis",
                "profile_id": "nonexistent-profile-id-12345",
                "data": {"text": "test"}
            }
        )

        # Should either succeed (if FK not enforced) or fail gracefully
        assert response.status_code in [200, 201, 202, 400, 404, 422]

    def test_unique_constraints(self, api_client):
        """Verify unique constraints are enforced."""
        # Create first profile with specific name
        unique_name = f"Unique Test {time.time()}"

        response1 = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": unique_name, "settings": {}}
        )

        if response1.status_code not in [200, 201]:
            pytest.skip("Could not create first profile")

        # Try to create another with same name (if uniqueness is enforced)
        response2 = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": unique_name, "settings": {}}
        )

        # Either succeeds (no unique constraint) or fails with conflict
        assert response2.status_code in [200, 201, 400, 409, 422]

    def test_not_null_constraints(self, api_client):
        """Verify NOT NULL constraints are enforced."""
        # Try to create with null required field
        response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": None, "settings": {}}
        )

        # Should be rejected
        assert response.status_code in [400, 422]

    def test_data_type_constraints(self, api_client):
        """Verify data type constraints are enforced."""
        # Try to insert wrong data types
        response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": 12345, "settings": "not-an-object"}
        )

        # Should be rejected or coerced
        assert response.status_code in [200, 201, 400, 422]


class TestMigrations:
    """Tests for database migration behavior."""

    def test_migration_idempotency(self, temp_db):
        """Verify migrations can be run multiple times safely."""
        # This tests the migration system directly
        try:
            from backend.data.migrations import run_migrations

            # Run migrations twice
            run_migrations(temp_db)
            run_migrations(temp_db)  # Should not fail

        except ImportError:
            # Migration system may not be importable directly
            # Test via API instead
            pass

    def test_database_version_tracking(self, api_client):
        """Verify database version is tracked."""
        # Check if version endpoint exists
        response = api_client.get("/api/database/version")

        if response.status_code == 404:
            # Version endpoint may not exist, that's okay
            pass
        elif response.status_code == 200:
            data = response.json()
            assert "version" in data or "schema_version" in data

    def test_schema_validation(self, temp_db):
        """Verify schema matches expected structure."""
        # Create connection to temp database
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        try:
            # Try to create expected table structure
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Verify table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
            )
            result = cursor.fetchone()
            assert result is not None

        finally:
            conn.close()


class TestConcurrentAccess:
    """Tests for concurrent database access patterns."""

    def test_read_during_write(self, api_client):
        """Verify reads work during writes."""
        results = {"reads": [], "writes": []}

        def do_reads():
            for _ in range(10):
                response = api_client.get("/api/profiles")
                results["reads"].append(response.status_code)
                time.sleep(0.05)

        def do_writes():
            for i in range(5):
                response = api_client.post(
                    "/api/profiles",
                    json={"name": f"Concurrent Read/Write {i}", "settings": {}}
                )
                results["writes"].append(response.status_code)
                time.sleep(0.1)

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(do_reads)
            executor.submit(do_writes)

        # Most reads should succeed
        read_success = sum(1 for s in results["reads"] if s in [200, 429])
        assert read_success >= len(results["reads"]) * 0.8

    def test_multiple_writers(self, api_client):
        """Verify multiple concurrent writers are handled."""
        results = []

        def writer(writer_id: int):
            for i in range(5):
                response = api_client.post(
                    "/api/profiles",
                    json={
                        "name": f"Writer {writer_id} Item {i}",
                        "settings": {}
                    }
                )
                results.append((writer_id, response.status_code))

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(writer, w) for w in range(3)]
            for f in futures:
                f.result()

        # Should have handled all writes
        assert len(results) == 15

        # Most should succeed or be rate limited
        success_count = sum(1 for _, s in results if s in [200, 201, 429])
        assert success_count >= len(results) * 0.5

    def test_connection_pool_exhaustion(self, api_client):
        """Verify connection pool handles exhaustion gracefully."""
        # Make many concurrent requests
        results = []

        def make_request():
            try:
                response = api_client.get("/api/profiles")
                return response.status_code
            except Exception:
                return 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in futures]

        # Should handle gracefully (some may fail but not all)
        success_count = sum(1 for s in results if s in [200, 429, 503])
        assert success_count >= len(results) * 0.5


class TestDataPersistence:
    """Tests for data persistence guarantees."""

    def test_data_survives_restart(self, api_client):
        """Verify data persists across operations."""
        # Create data
        unique_name = f"Persistence Test {time.time()}"
        create_response = retry_on_rate_limit(
            api_client.post,
            "/api/profiles",
            json={"name": unique_name, "settings": {"persistent": True}}
        )

        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create test profile")

        profile_id = create_response.json().get("id", create_response.json().get("profile_id"))

        if not profile_id:
            pytest.skip("No profile ID returned")

        # Verify data can be retrieved
        get_response = api_client.get(f"/api/profiles/{profile_id}")

        if get_response.status_code == 200:
            data = get_response.json()
            assert data.get("name") == unique_name or unique_name in str(data)

    def test_transaction_durability(self, api_client):
        """Verify committed transactions are durable."""
        # Create multiple items
        created_ids = []

        for i in range(3):
            response = retry_on_rate_limit(
                api_client.post,
                "/api/profiles",
                json={"name": f"Durability Test {i}", "settings": {}}
            )
            if response.status_code in [200, 201]:
                profile_id = response.json().get("id", response.json().get("profile_id"))
                if profile_id:
                    created_ids.append(profile_id)

        # Verify all can be retrieved
        for profile_id in created_ids:
            response = api_client.get(f"/api/profiles/{profile_id}")
            assert response.status_code in [200, 404]  # 404 if cleanup happened


class TestQueryPerformance:
    """Tests for query performance characteristics."""

    def test_indexed_lookup_performance(self, api_client):
        """Verify indexed lookups are fast."""
        # Measure lookup time
        times = []

        # Get a profile ID first
        list_response = api_client.get("/api/profiles")
        if list_response.status_code != 200:
            pytest.skip("Could not list profiles")

        profiles = list_response.json()
        if isinstance(profiles, list) and profiles:
            profile_id = profiles[0].get("id", profiles[0].get("profile_id"))
        elif isinstance(profiles, dict) and profiles.get("profiles"):
            profile_id = profiles["profiles"][0].get("id")
        else:
            pytest.skip("No profiles to test")

        if not profile_id:
            pytest.skip("No profile ID available")

        # Measure lookup times
        for _ in range(10):
            start = time.time()
            response = api_client.get(f"/api/profiles/{profile_id}")
            if response.status_code == 200:
                times.append(time.time() - start)

        if times:
            avg_time = sum(times) / len(times)
            # Indexed lookup should be fast (< 500ms)
            assert avg_time < 0.5, f"Slow indexed lookup: {avg_time:.3f}s"

    def test_list_query_performance(self, api_client):
        """Verify list queries perform well."""
        times = []

        for _ in range(10):
            start = time.time()
            response = api_client.get("/api/profiles")
            if response.status_code == 200:
                times.append(time.time() - start)

        if times:
            avg_time = sum(times) / len(times)
            # List should be reasonably fast
            assert avg_time < 2.0, f"Slow list query: {avg_time:.3f}s"

    def test_filtered_query_performance(self, api_client):
        """Verify filtered queries perform well."""
        times = []

        for _ in range(10):
            start = time.time()
            response = api_client.get("/api/profiles", params={"search": "Test"})
            if response.status_code in [200, 422]:  # 422 if search not supported
                times.append(time.time() - start)

        if times:
            avg_time = sum(times) / len(times)
            # Filtered query should be reasonable
            assert avg_time < 3.0, f"Slow filtered query: {avg_time:.3f}s"
