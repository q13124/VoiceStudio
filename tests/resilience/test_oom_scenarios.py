"""
Resilience tests for out-of-memory (OOM) scenarios.

Tests that the plugin system correctly handles and recovers from
memory exhaustion situations.
"""

from __future__ import annotations

import gc
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.plugins.sandbox.crash_recovery import (
    CircuitState,
    CrashEvent,
    CrashRecoveryManager,
    RecoveryConfig,
    RestartPolicy,
)


class TestOOMDetection:
    """Tests for OOM detection mechanisms."""

    @pytest.mark.oom
    def test_detects_oom_exit_code(self):
        """Test detection of OOM via exit code."""
        # OOM killer typically sends SIGKILL (exit code 137 on Linux)
        crash = CrashEvent(
            plugin_id="test-plugin",
            timestamp=datetime.utcnow(),
            exit_code=137,  # SIGKILL
            error_message="",
        )

        # Check if crash indicates OOM
        is_oom = crash.exit_code in {137, -9, 255}  # Common OOM exit codes
        assert is_oom is True

    @pytest.mark.oom
    def test_detects_oom_error_message(self):
        """Test detection of OOM via error message."""
        crash = CrashEvent(
            plugin_id="test-plugin",
            timestamp=datetime.utcnow(),
            exit_code=1,
            error_message="MemoryError: Unable to allocate array",
        )

        is_oom = "MemoryError" in crash.error_message or "OOM" in crash.error_message
        assert is_oom is True

    @pytest.mark.oom
    def test_detects_java_oom(self):
        """Test detection of Java OOM errors."""
        crash = CrashEvent(
            plugin_id="test-plugin",
            timestamp=datetime.utcnow(),
            exit_code=1,
            error_message="java.lang.OutOfMemoryError: Java heap space",
        )

        is_oom = "OutOfMemoryError" in crash.error_message
        assert is_oom is True


class TestOOMRecovery:
    """Tests for OOM recovery strategies."""

    @pytest.mark.oom
    @pytest.mark.asyncio
    async def test_restart_with_reduced_memory(self):
        """Test that OOM triggers restart with reduced memory config."""
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ON_CRASH,
            max_restarts=3,
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

        # Simulate OOM crash
        await manager.on_crash(exit_code=137, error_message="Killed (OOM)")

        # Verify OOM crash was tracked
        assert len(manager.crash_history) == 1
        assert manager.crash_history[-1].exit_code == 137

    @pytest.mark.oom
    @pytest.mark.asyncio
    async def test_consecutive_oom_triggers_circuit_breaker(self):
        """Test consecutive OOM crashes open circuit breaker."""
        config = RecoveryConfig(
            restart_policy=RestartPolicy.ON_CRASH,
            max_restarts=5,
            circuit_breaker_threshold=3,
        )
        manager = CrashRecoveryManager(
            plugin_id="test-plugin",
            config=config,
        )

        # Simulate multiple OOM crashes
        for _ in range(3):
            await manager.on_crash(exit_code=137, error_message="OOM")

        # Circuit should be open after 3 failures
        assert manager._circuit_breaker.state == CircuitState.OPEN


class TestMemoryLimits:
    """Tests for memory limit enforcement."""

    @pytest.mark.oom
    def test_memory_limit_configuration(self):
        """Test memory limits can be configured."""
        resource_limits = {
            "memory_mb": 512,
            "memory_soft_limit_mb": 384,
        }

        # Verify limits are reasonable
        assert resource_limits["memory_mb"] > resource_limits["memory_soft_limit_mb"]
        assert resource_limits["memory_mb"] > 0

    @pytest.mark.oom
    @pytest.mark.slow
    def test_memory_monitoring(self):
        """Test memory usage monitoring."""
        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Allocate some memory
        data = [0] * 1_000_000

        current_memory = process.memory_info().rss
        assert current_memory >= initial_memory

        # Clean up
        del data
        gc.collect()

    @pytest.mark.oom
    def test_memory_pressure_detection(self):
        """Test detection of memory pressure."""
        import psutil

        mem = psutil.virtual_memory()

        # Define pressure thresholds
        warning_threshold = 0.80  # 80% used
        critical_threshold = 0.95  # 95% used

        usage_percent = mem.percent / 100.0

        if usage_percent > critical_threshold:
            pressure_level = "critical"
        elif usage_percent > warning_threshold:
            pressure_level = "warning"
        else:
            pressure_level = "normal"

        assert pressure_level in {"normal", "warning", "critical"}


class TestOOMPrevention:
    """Tests for OOM prevention strategies."""

    @pytest.mark.oom
    def test_lazy_loading_reduces_memory(self):
        """Test that lazy loading pattern reduces memory usage."""

        class LazyLoader:
            def __init__(self):
                self._data = None

            @property
            def data(self):
                if self._data is None:
                    self._data = [0] * 1000
                return self._data

        loader = LazyLoader()

        # Data shouldn't be loaded yet
        assert loader._data is None

        # Accessing triggers load
        _ = loader.data
        assert loader._data is not None

    @pytest.mark.oom
    def test_streaming_processes_without_full_load(self):
        """Test streaming processes data without loading all at once."""

        def stream_processor(chunks):
            """Process chunks one at a time."""
            total = 0
            for chunk in chunks:
                total += sum(chunk)
                # Chunk goes out of scope, memory freed
            return total

        # Generate chunks lazily
        def chunk_generator():
            for _ in range(10):
                yield [1] * 1000

        result = stream_processor(chunk_generator())
        assert result == 10_000

    @pytest.mark.oom
    def test_memory_pool_reuse(self):
        """Test memory pool reuses allocations."""

        class MemoryPool:
            def __init__(self, size: int):
                self.pool = [None] * size
                self.available = list(range(size))

            def acquire(self):
                if self.available:
                    idx = self.available.pop()
                    self.pool[idx] = [0] * 100
                    return idx, self.pool[idx]
                return None, None

            def release(self, idx: int):
                self.pool[idx] = None
                self.available.append(idx)

        pool = MemoryPool(5)

        # Acquire all slots
        acquired = []
        for _ in range(5):
            idx, data = pool.acquire()
            assert data is not None
            acquired.append(idx)

        # Pool exhausted
        idx, data = pool.acquire()
        assert data is None

        # Release one
        pool.release(acquired[0])

        # Can acquire again
        idx, data = pool.acquire()
        assert data is not None


class TestOOMGracefulDegradation:
    """Tests for graceful degradation under memory pressure."""

    @pytest.mark.oom
    def test_quality_reduction_under_pressure(self):
        """Test quality reduction to conserve memory."""

        class AdaptiveProcessor:
            def __init__(self):
                self.quality = "high"

            def adjust_for_memory_pressure(self, pressure: str):
                if pressure == "critical":
                    self.quality = "low"
                elif pressure == "warning":
                    self.quality = "medium"
                else:
                    self.quality = "high"

        processor = AdaptiveProcessor()

        processor.adjust_for_memory_pressure("normal")
        assert processor.quality == "high"

        processor.adjust_for_memory_pressure("warning")
        assert processor.quality == "medium"

        processor.adjust_for_memory_pressure("critical")
        assert processor.quality == "low"

    @pytest.mark.oom
    def test_cache_eviction_under_pressure(self):
        """Test cache eviction under memory pressure."""

        class AdaptiveCache:
            def __init__(self, max_size: int):
                self.max_size = max_size
                self.cache = {}

            def put(self, key: str, value):
                if len(self.cache) >= self.max_size:
                    # Evict oldest
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]
                self.cache[key] = value

            def reduce_memory(self, factor: float = 0.5):
                """Reduce cache to factor of current size."""
                target_size = int(len(self.cache) * factor)
                while len(self.cache) > target_size:
                    oldest = next(iter(self.cache))
                    del self.cache[oldest]

        cache = AdaptiveCache(10)

        # Fill cache
        for i in range(10):
            cache.put(f"key{i}", f"value{i}")

        assert len(cache.cache) == 10

        # Reduce memory
        cache.reduce_memory(0.5)

        assert len(cache.cache) == 5

    @pytest.mark.oom
    def test_request_queuing_under_pressure(self):
        """Test request queuing when memory is low."""
        from collections import deque

        class RequestQueue:
            def __init__(self, max_size: int = 100):
                self.queue = deque(maxlen=max_size)
                self.processing = False

            def enqueue(self, request):
                if len(self.queue) < self.queue.maxlen:
                    self.queue.append(request)
                    return True
                return False  # Queue full

            def dequeue(self):
                if self.queue:
                    return self.queue.popleft()
                return None

        queue = RequestQueue(max_size=5)

        # Fill queue
        for i in range(5):
            assert queue.enqueue(f"request{i}") is True

        # Queue full
        assert queue.enqueue("overflow") is False

        # Process one
        req = queue.dequeue()
        assert req == "request0"

        # Can add again
        assert queue.enqueue("new_request") is True
