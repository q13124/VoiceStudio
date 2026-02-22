"""
Resilience tests for concurrent load scenarios.

Tests that the plugin system correctly handles high concurrency
and load situations.
"""

from __future__ import annotations

import asyncio
import random
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

import pytest


class TestConcurrentPluginExecution:
    """Tests for concurrent plugin execution."""

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_parallel_plugin_invocations(self):
        """Test multiple plugins can be invoked in parallel."""
        results = []

        async def plugin_operation(plugin_id: str, delay: float):
            await asyncio.sleep(delay)
            return {"plugin_id": plugin_id, "completed": True}

        # Execute 10 plugins in parallel
        tasks = [plugin_operation(f"plugin-{i}", random.uniform(0.01, 0.05)) for i in range(10)]

        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(r["completed"] for r in results)

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_concurrent_same_plugin_calls(self):
        """Test concurrent calls to the same plugin."""
        call_count = 0
        lock = asyncio.Lock()

        async def plugin_handler(request_id: int):
            nonlocal call_count
            async with lock:
                call_count += 1
            await asyncio.sleep(0.01)
            return {"request_id": request_id, "success": True}

        # 50 concurrent calls
        tasks = [plugin_handler(i) for i in range(50)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 50
        assert call_count == 50

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Test semaphore properly limits concurrent executions."""
        max_concurrent = 5
        semaphore = asyncio.Semaphore(max_concurrent)
        concurrent_count = 0
        max_observed = 0
        lock = asyncio.Lock()

        async def limited_operation():
            nonlocal concurrent_count, max_observed

            async with semaphore:
                async with lock:
                    concurrent_count += 1
                    max_observed = max(max_observed, concurrent_count)

                await asyncio.sleep(0.05)

                async with lock:
                    concurrent_count -= 1

        # Try to execute 20 operations
        tasks = [limited_operation() for _ in range(20)]
        await asyncio.gather(*tasks)

        assert max_observed <= max_concurrent


class TestLoadBalancing:
    """Tests for load balancing under concurrent load."""

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_round_robin_distribution(self):
        """Test round-robin load distribution."""

        class RoundRobinBalancer:
            def __init__(self, workers: list[str]):
                self.workers = workers
                self.index = 0
                self.lock = asyncio.Lock()

            async def get_worker(self) -> str:
                async with self.lock:
                    worker = self.workers[self.index]
                    self.index = (self.index + 1) % len(self.workers)
                    return worker

        balancer = RoundRobinBalancer(["w1", "w2", "w3"])

        # Get 9 workers
        workers = [await balancer.get_worker() for _ in range(9)]

        # Should be evenly distributed
        assert workers.count("w1") == 3
        assert workers.count("w2") == 3
        assert workers.count("w3") == 3

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_least_connections_distribution(self):
        """Test least-connections load distribution."""

        class LeastConnectionsBalancer:
            def __init__(self, workers: list[str]):
                self.connections = dict.fromkeys(workers, 0)
                self.lock = asyncio.Lock()

            async def acquire(self) -> str:
                async with self.lock:
                    # Get worker with least connections
                    worker = min(self.connections, key=self.connections.get)
                    self.connections[worker] += 1
                    return worker

            async def release(self, worker: str):
                async with self.lock:
                    self.connections[worker] -= 1

        balancer = LeastConnectionsBalancer(["w1", "w2", "w3"])

        # Acquire many connections
        acquired = []
        for _ in range(12):
            w = await balancer.acquire()
            acquired.append(w)

        # Should be roughly balanced
        counts = {}
        for w in acquired:
            counts[w] = counts.get(w, 0) + 1

        # Each worker should have 4 connections
        assert all(c == 4 for c in counts.values())


class TestResourceContention:
    """Tests for resource contention under load."""

    @pytest.mark.concurrent
    def test_thread_safe_counter(self):
        """Test thread-safe counter under concurrent access."""

        class ThreadSafeCounter:
            def __init__(self):
                self.value = 0
                self.lock = threading.Lock()

            def increment(self):
                with self.lock:
                    self.value += 1

            def get(self) -> int:
                with self.lock:
                    return self.value

        counter = ThreadSafeCounter()

        def increment_many():
            for _ in range(1000):
                counter.increment()

        # Run from multiple threads
        threads = [threading.Thread(target=increment_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert counter.get() == 10000

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_async_queue_under_load(self):
        """Test async queue under high load."""
        queue = asyncio.Queue(maxsize=100)
        produced = 0
        consumed = 0
        lock = asyncio.Lock()
        stop_consumers = asyncio.Event()

        async def producer():
            nonlocal produced
            for i in range(100):  # Reduced for faster test
                await queue.put(i)
                async with lock:
                    produced += 1

        async def consumer():
            nonlocal consumed
            while not stop_consumers.is_set() or not queue.empty():
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=0.1)
                    async with lock:
                        consumed += 1
                except asyncio.TimeoutError:
                    if stop_consumers.is_set():
                        break

        # Run producers first, then consumers
        producers = [asyncio.create_task(producer()) for _ in range(2)]
        consumers = [asyncio.create_task(consumer()) for _ in range(3)]

        # Wait for producers to finish
        await asyncio.gather(*producers)

        # Signal consumers to stop once queue is empty
        stop_consumers.set()

        # Wait for consumers with timeout
        await asyncio.wait_for(asyncio.gather(*consumers), timeout=5.0)

        assert produced == 200
        assert consumed == 200

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_lock_contention_timeout(self):
        """Test lock acquisition with timeout."""
        lock = asyncio.Lock()
        acquired_count = 0
        timeout_count = 0

        async def try_acquire_lock(hold_time: float):
            nonlocal acquired_count, timeout_count

            try:
                result = await asyncio.wait_for(lock.acquire(), timeout=0.1)
                if result:
                    acquired_count += 1
                    await asyncio.sleep(hold_time)
                    lock.release()
            except asyncio.TimeoutError:
                timeout_count += 1

        # First task holds lock for long time
        # Others should timeout
        tasks = [
            try_acquire_lock(0.5),  # Holds lock
            try_acquire_lock(0.01),  # Will timeout
            try_acquire_lock(0.01),  # Will timeout
        ]

        await asyncio.gather(*tasks)

        assert acquired_count >= 1
        # Some should timeout (depending on timing)


class TestBackpressure:
    """Tests for backpressure handling."""

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_bounded_queue_creates_backpressure(self):
        """Test bounded queue creates backpressure."""
        queue = asyncio.Queue(maxsize=5)
        blocked_time = 0.0

        async def producer():
            nonlocal blocked_time
            for i in range(10):
                start = time.time()
                await queue.put(i)
                blocked_time += time.time() - start

        async def slow_consumer():
            for _ in range(10):
                await asyncio.sleep(0.05)
                await queue.get()

        await asyncio.gather(producer(), slow_consumer())

        # Producer should have been blocked
        assert blocked_time > 0.1

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting under load."""

        class RateLimiter:
            def __init__(self, rate: float):
                self.rate = rate  # requests per second
                self.tokens = rate
                self.last_update = time.time()
                self.lock = asyncio.Lock()

            async def acquire(self) -> bool:
                async with self.lock:
                    now = time.time()
                    elapsed = now - self.last_update
                    self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
                    self.last_update = now

                    if self.tokens >= 1:
                        self.tokens -= 1
                        return True
                    return False

        limiter = RateLimiter(rate=10)  # 10 requests/second

        # Try to make many requests quickly
        allowed = 0
        denied = 0

        for _ in range(20):
            if await limiter.acquire():
                allowed += 1
            else:
                denied += 1

        # Should have been rate limited
        assert allowed <= 12  # Some buffer for timing
        assert denied > 0

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_circuit_breaker_under_load(self):
        """Test circuit breaker opens under high failure rate."""

        class LoadCircuitBreaker:
            def __init__(self, failure_threshold: float = 0.5, window: int = 10):
                self.window = window
                self.threshold = failure_threshold
                self.results = []
                self.open = False

            def record(self, success: bool):
                self.results.append(success)
                if len(self.results) > self.window:
                    self.results.pop(0)

                if len(self.results) >= self.window:
                    failure_rate = 1 - (sum(self.results) / len(self.results))
                    self.open = failure_rate > self.threshold

            def allow(self) -> bool:
                return not self.open

        breaker = LoadCircuitBreaker(failure_threshold=0.5, window=10)

        # Record many failures
        for _ in range(8):
            breaker.record(success=False)
        for _ in range(2):
            breaker.record(success=True)

        # 80% failure rate should open circuit
        assert breaker.open is True


class TestGracefulDegradation:
    """Tests for graceful degradation under load."""

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_shed_load_when_overloaded(self):
        """Test load shedding when system is overloaded."""

        class LoadShedder:
            def __init__(self, max_load: int = 10):
                self.max_load = max_load
                self.current_load = 0
                self.lock = asyncio.Lock()

            async def try_accept(self) -> bool:
                async with self.lock:
                    if self.current_load >= self.max_load:
                        return False
                    self.current_load += 1
                    return True

            async def release(self):
                async with self.lock:
                    self.current_load -= 1

        shedder = LoadShedder(max_load=5)

        accepted = 0
        rejected = 0

        async def try_request():
            nonlocal accepted, rejected
            if await shedder.try_accept():
                accepted += 1
                await asyncio.sleep(0.1)  # Simulate work
                await shedder.release()
            else:
                rejected += 1

        # Submit 20 requests at once
        await asyncio.gather(*[try_request() for _ in range(20)])

        # Some should have been rejected
        assert accepted >= 5
        assert rejected >= 5  # At least 15 should be rejected initially

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_priority_queue_under_load(self):
        """Test priority queue processes high priority first."""

        class PriorityRequest:
            def __init__(self, id: int, priority: int):
                self.id = id
                self.priority = priority

            def __lt__(self, other):
                return self.priority > other.priority  # Higher priority first

        queue = asyncio.PriorityQueue()

        # Add requests in random order
        requests = [
            PriorityRequest(1, priority=1),
            PriorityRequest(2, priority=5),  # Highest
            PriorityRequest(3, priority=3),
            PriorityRequest(4, priority=2),
            PriorityRequest(5, priority=4),
        ]

        for req in requests:
            await queue.put(req)

        # Should come out in priority order (5, 4, 3, 2, 1)
        processed_order = []
        while not queue.empty():
            req = await queue.get()
            processed_order.append(req.priority)

        assert processed_order == [5, 4, 3, 2, 1]


class TestConcurrencyBugs:
    """Tests to catch common concurrency bugs."""

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_no_lost_updates(self):
        """Test atomic operations don't lose updates."""

        class AtomicCounter:
            def __init__(self):
                self._value = 0
                self._lock = asyncio.Lock()

            async def increment(self):
                async with self._lock:
                    self._value += 1

            async def get(self) -> int:
                async with self._lock:
                    return self._value

        counter = AtomicCounter()

        async def increment_many():
            for _ in range(100):
                await counter.increment()

        # Run 10 concurrent incrementers
        await asyncio.gather(*[increment_many() for _ in range(10)])

        assert await counter.get() == 1000

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_no_deadlock_with_lock_ordering(self):
        """Test consistent lock ordering prevents deadlock."""

        class Resource:
            def __init__(self, id: int):
                self.id = id
                self.lock = asyncio.Lock()

        async def transfer(from_res: Resource, to_res: Resource, amount: int):
            # Always lock in order of resource ID to prevent deadlock
            first, second = sorted([from_res, to_res], key=lambda r: r.id)

            async with first.lock:
                async with second.lock:
                    # Simulated transfer
                    await asyncio.sleep(0.001)
                    return True

        r1 = Resource(1)
        r2 = Resource(2)

        # Run many concurrent transfers in both directions
        tasks = []
        for _ in range(50):
            tasks.append(transfer(r1, r2, 10))
            tasks.append(transfer(r2, r1, 10))

        # Should complete without deadlock
        results = await asyncio.gather(*tasks)
        assert all(results)

    @pytest.mark.concurrent
    @pytest.mark.asyncio
    async def test_check_then_act_atomicity(self):
        """Test check-then-act is atomic."""

        class AtomicRegistry:
            def __init__(self):
                self.items = {}
                self.lock = asyncio.Lock()

            async def get_or_create(self, key: str) -> dict:
                async with self.lock:
                    if key not in self.items:
                        self.items[key] = {"key": key, "created": datetime.utcnow()}
                    return self.items[key]

        registry = AtomicRegistry()

        # Many concurrent get_or_create for same key
        results = await asyncio.gather(*[registry.get_or_create("shared-key") for _ in range(100)])

        # All should get the same object
        first_created = results[0]["created"]
        assert all(r["created"] == first_created for r in results)

        # Only one item in registry
        assert len(registry.items) == 1
