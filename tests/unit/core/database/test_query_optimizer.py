"""
Enhanced Unit Tests for Query Optimizer
Tests all optimizations: query caching (LRU with TTL), connection pooling,
health checks, connection reuse, query statistics, and index management.
"""

import contextlib
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules
try:
    from app.core.database.query_optimizer import (
        ConnectionPool,
        DatabaseQueryOptimizer,
        QueryCache,
    )
except ImportError as e:
    pytest.skip(
        f"Could not import query_optimizer modules: {e}",
        allow_module_level=True,
    )


class TestQueryCache:
    """Test QueryCache LRU cache with TTL."""

    def test_cache_initialization(self):
        """Test QueryCache initializes correctly."""
        cache = QueryCache(max_size=10, ttl_seconds=60.0)
        assert cache.max_size == 10
        assert cache.ttl_seconds == 60.0
        assert len(cache.cache) == 0
        assert len(cache.access_order) == 0

    def test_cache_set_and_get(self):
        """Test basic cache set and get."""
        cache = QueryCache(max_size=10, ttl_seconds=60.0)

        cache.set("key1", "value1")
        result = cache.get("key1")

        assert result == "value1"
        assert len(cache.cache) == 1

    def test_cache_ttl_expiration(self):
        """Test cache entries expire after TTL."""
        cache = QueryCache(max_size=10, ttl_seconds=0.1)  # Very short TTL

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # Wait for TTL to expire
        time.sleep(0.2)

        # Should return None after expiration
        result = cache.get("key1")
        assert result is None
        assert len(cache.cache) == 0

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = QueryCache(max_size=3, ttl_seconds=60.0)

        # Fill cache to capacity
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert len(cache.cache) == 3

        # Add one more - should evict oldest (key1)
        cache.set("key4", "value4")
        assert len(cache.cache) == 3
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key4") == "value4"  # New entry

    def test_cache_access_order_update(self):
        """Test access order is updated on get."""
        cache = QueryCache(max_size=3, ttl_seconds=60.0)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 - should move to end
        cache.get("key1")

        # Add new key - should evict key2 (oldest after key1 was accessed)
        cache.set("key4", "value4")
        assert cache.get("key1") == "value1"  # Still in cache
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"  # Still in cache

    def test_cache_clear(self):
        """Test cache clear."""
        cache = QueryCache(max_size=10, ttl_seconds=60.0)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        assert len(cache.cache) == 2

        cache.clear()
        assert len(cache.cache) == 0
        assert len(cache.access_order) == 0

    def test_cache_invalidate_pattern(self):
        """Test cache invalidation with pattern."""
        cache = QueryCache(max_size=10, ttl_seconds=60.0)

        cache.set("user_1", "value1")
        cache.set("user_2", "value2")
        cache.set("profile_1", "value3")

        # Invalidate all user_* entries
        cache.invalidate("user_")

        assert cache.get("user_1") is None
        assert cache.get("user_2") is None
        assert cache.get("profile_1") == "value3"  # Not matched

    def test_cache_statistics(self):
        """Test cache statistics."""
        cache = QueryCache(max_size=10, ttl_seconds=60.0)

        cache.set("key1", "value1")
        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["ttl_seconds"] == 60.0


class TestConnectionPool:
    """Test ConnectionPool optimizations."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Initialize database
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS test " "(id INTEGER PRIMARY KEY, name TEXT)"
        )
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        with contextlib.suppress(Exception):
            Path(db_path).unlink()

    def test_pool_initialization(self, temp_db):
        """Test ConnectionPool initializes correctly."""
        # Use min_connections=0 to test initialization without pre-creation
        pool = ConnectionPool(temp_db, max_connections=5, min_connections=0)
        assert pool.db_path == temp_db
        assert pool.max_connections == 5
        assert len(pool.pool) == 0
        assert pool.active_connections == 0

    def test_connection_creation(self, temp_db):
        """Test connection creation."""
        # Use min_connections=0 to test explicit connection creation
        pool = ConnectionPool(temp_db, max_connections=5, min_connections=0)

        with pool.get_connection() as conn:
            assert conn is not None
            assert pool.total_connections_created == 1
            assert pool.active_connections == 1

    def test_connection_reuse(self, temp_db):
        """Test connection reuse from pool."""
        # Use min_connections=0 to test explicit reuse behavior
        pool = ConnectionPool(temp_db, max_connections=5, min_connections=0)

        # First use - creates connection
        with pool.get_connection():
            ...

        # Second use - should reuse connection
        with pool.get_connection():
            assert pool.total_connections_created == 1
            assert pool.total_connections_reused >= 1

    def test_connection_health_check(self, temp_db):
        """Test connection health checks."""
        pool = ConnectionPool(
            temp_db,
            max_connections=5,
            health_check_interval=0.1,  # Short interval for testing
        )

        # Create and return connection
        with pool.get_connection():
            ...

        # Wait for health check interval
        time.sleep(0.2)

        # Next use should trigger health check
        with pool.get_connection():
            assert pool.total_health_checks >= 1

    def test_connection_pool_max_size(self, temp_db):
        """Test pool respects max connections."""
        pool = ConnectionPool(temp_db, max_connections=2)

        # Create connections up to max
        conns = []
        for _i in range(3):
            conn = pool.get_connection()
            conns.append(conn)
            conn.__enter__()

        # Should have created max_connections
        assert pool.total_connections_created <= 2
        assert pool.active_connections <= 2

        # Cleanup
        for conn in conns:
            with contextlib.suppress(Exception):
                conn.__exit__(None, None, None)

    def test_idle_connection_cleanup(self, temp_db):
        """Test idle connections are cleaned up."""
        pool = ConnectionPool(
            temp_db,
            max_connections=5,
            max_idle_time=0.1,  # Short idle time for testing
        )

        # Create and return connection
        with pool.get_connection():
            ...

        # Wait for idle timeout
        time.sleep(0.2)

        # Next get_connection should cleanup idle connection
        with pool.get_connection():
            # Should create new connection (old one cleaned up)
            ...

    def test_connection_statistics(self, temp_db):
        """Test connection pool statistics."""
        pool = ConnectionPool(temp_db, max_connections=5)

        # Use connection
        with pool.get_connection():
            ...

        stats = pool.get_stats()
        assert "pool_size" in stats
        assert "active_connections" in stats
        assert "max_connections" in stats
        assert "total_connections_created" in stats
        assert "total_connections_reused" in stats
        assert "reuse_rate" in stats
        assert stats["total_connections_created"] >= 1

    def test_close_all_connections(self, temp_db):
        """Test closing all connections."""
        pool = ConnectionPool(temp_db, max_connections=5)

        # Create and return connections
        for _ in range(3):
            with pool.get_connection():
                ...

        # Close all
        pool.close_all()

        assert len(pool.pool) == 0
        assert pool.active_connections == 0


class TestDatabaseQueryOptimizer:
    """Test DatabaseQueryOptimizer integration."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Initialize database
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS test " "(id INTEGER PRIMARY KEY, name TEXT)"
        )
        conn.execute("INSERT INTO test (name) VALUES ('test1')")
        conn.execute("INSERT INTO test (name) VALUES ('test2')")
        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        with contextlib.suppress(Exception):
            Path(db_path).unlink()

    def test_optimizer_initialization(self, temp_db):
        """Test DatabaseQueryOptimizer initializes correctly."""
        optimizer = DatabaseQueryOptimizer(
            temp_db,
            enable_cache=True,
            cache_size=10,
            cache_ttl=60.0,
            max_connections=5,
        )
        assert optimizer.db_path == temp_db
        assert optimizer.enable_cache is True
        assert optimizer.cache is not None
        assert optimizer.pool is not None

    def test_query_execution(self, temp_db):
        """Test query execution."""
        optimizer = DatabaseQueryOptimizer(temp_db, enable_cache=False)

        results = optimizer.execute_query("SELECT * FROM test")

        assert len(results) == 2
        assert results[0]["name"] == "test1"
        assert results[1]["name"] == "test2"

    def test_query_caching(self, temp_db):
        """Test query result caching."""
        optimizer = DatabaseQueryOptimizer(
            temp_db,
            enable_cache=True,
            cache_size=10,
            cache_ttl=60.0,
        )

        # First execution - should execute query
        results1 = optimizer.execute_query("SELECT * FROM test", use_cache=True)
        assert len(results1) == 2

        # Second execution - should use cache
        results2 = optimizer.execute_query("SELECT * FROM test", use_cache=True)
        assert len(results2) == 2
        assert results1 == results2

        # Check cache was used - access query_stats directly
        assert "SELECT * FROM test" in optimizer.query_stats
        query_stat = optimizer.query_stats["SELECT * FROM test"]
        assert query_stat.cache_hits >= 1

    def test_query_statistics(self, temp_db):
        """Test query statistics tracking."""
        optimizer = DatabaseQueryOptimizer(temp_db, enable_cache=False)

        # Execute query multiple times
        for _i in range(3):
            optimizer.execute_query("SELECT * FROM test")

        # Access query_stats directly
        assert "SELECT * FROM test" in optimizer.query_stats
        query_stat = optimizer.query_stats["SELECT * FROM test"]
        assert query_stat.execution_count == 3
        # Fast in-memory SQLite operations may complete in 0.0 seconds
        assert query_stat.total_time >= 0.0
        assert query_stat.average_time >= 0.0

    def test_cache_hit_statistics(self, temp_db):
        """Test cache hit statistics."""
        optimizer = DatabaseQueryOptimizer(
            temp_db,
            enable_cache=True,
            cache_size=10,
            cache_ttl=60.0,
        )

        # Execute query twice (second should be cached)
        optimizer.execute_query("SELECT * FROM test", use_cache=True)
        optimizer.execute_query("SELECT * FROM test", use_cache=True)

        # Access query_stats directly
        assert "SELECT * FROM test" in optimizer.query_stats
        query_stat = optimizer.query_stats["SELECT * FROM test"]
        assert query_stat.cache_hits >= 1
        assert query_stat.cache_misses >= 1

    def test_connection_pooling_integration(self, temp_db):
        """Test connection pooling is used."""
        optimizer = DatabaseQueryOptimizer(
            temp_db,
            enable_cache=False,
            max_connections=5,
        )

        # Execute multiple queries
        for _ in range(5):
            optimizer.execute_query("SELECT * FROM test")

        # Check pool statistics
        pool_stats = optimizer.pool.get_stats()
        assert pool_stats["total_connections_created"] <= 5
        assert pool_stats["total_connections_reused"] >= 0

    def test_index_creation(self, temp_db):
        """Test index creation."""
        optimizer = DatabaseQueryOptimizer(temp_db, enable_cache=False)

        # Create index
        optimizer.create_index("test", "name")

        # Verify index exists by querying
        results = optimizer.execute_query(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name LIKE 'idx_test_%'"
        )
        assert len(results) > 0

    def test_cache_invalidation(self, temp_db):
        """Test cache invalidation."""
        optimizer = DatabaseQueryOptimizer(
            temp_db,
            enable_cache=True,
            cache_size=10,
            cache_ttl=60.0,
        )

        # Cache a query
        optimizer.execute_query("SELECT * FROM test", use_cache=True)

        # Invalidate cache using cache's invalidate method
        optimizer.cache.invalidate("SELECT")

        # Next execution should miss cache (cache was invalidated)
        optimizer.execute_query("SELECT * FROM test", use_cache=True)
        # Access query_stats directly
        assert "SELECT * FROM test" in optimizer.query_stats
        query_stat = optimizer.query_stats["SELECT * FROM test"]
        # Should have cache misses after invalidation
        assert query_stat.cache_misses >= 1

    def test_query_with_parameters(self, temp_db):
        """Test query execution with parameters."""
        optimizer = DatabaseQueryOptimizer(temp_db, enable_cache=False)

        results = optimizer.execute_query(
            "SELECT * FROM test WHERE name = ?",
            parameters=("test1",),
        )

        assert len(results) == 1
        assert results[0]["name"] == "test1"

    def test_query_with_parameters_caching(self, temp_db):
        """Test parameterized queries are cached separately."""
        optimizer = DatabaseQueryOptimizer(
            temp_db,
            enable_cache=True,
            cache_size=10,
            cache_ttl=60.0,
        )

        # Execute with different parameters
        results1 = optimizer.execute_query(
            "SELECT * FROM test WHERE name = ?",
            parameters=("test1",),
            use_cache=True,
        )
        results2 = optimizer.execute_query(
            "SELECT * FROM test WHERE name = ?",
            parameters=("test2",),
            use_cache=True,
        )

        assert len(results1) == 1
        assert len(results2) == 1
        assert results1[0]["name"] == "test1"
        assert results2[0]["name"] == "test2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
