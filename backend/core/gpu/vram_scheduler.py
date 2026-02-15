"""
VRAM Resource Scheduler.

TD-013: VRAM Resource Scheduler implementation.
Phase 9 Gap Resolution (2026-02-10):

This module provides high-level VRAM scheduling for engine requests,
building on top of the GPUMemoryPool for allocation management.

Features:
- Request queuing with priority
- Engine-specific VRAM requirements
- OOM prevention with pre-flight checks
- Automatic model unloading when under pressure
- Multi-GPU support (future)
"""

from __future__ import annotations

import asyncio
import heapq
import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.core.gpu.memory_pool import (
    GPUMemoryPool,
    MemoryAllocation,
    MemoryPriority,
    get_memory_pool,
)

logger = logging.getLogger(__name__)


class SchedulerState(Enum):
    """Scheduler operational state."""
    IDLE = "idle"
    PROCESSING = "processing"
    UNDER_PRESSURE = "under_pressure"
    PAUSED = "paused"


@dataclass
class VRAMRequirement:
    """VRAM requirements for an engine or operation."""
    engine_name: str
    model_vram_mb: int  # Base model size
    working_memory_mb: int = 512  # Additional working memory
    batch_multiplier: float = 1.0  # Per-batch memory multiplier

    @property
    def total_mb(self) -> int:
        """Total required VRAM in MB."""
        return self.model_vram_mb + self.working_memory_mb

    @property
    def total_bytes(self) -> int:
        """Total required VRAM in bytes."""
        return self.total_mb * 1024 * 1024

    def for_batch(self, batch_size: int) -> int:
        """Calculate VRAM for a given batch size."""
        base = self.model_vram_mb + self.working_memory_mb
        batch_overhead = int(self.working_memory_mb * self.batch_multiplier * (batch_size - 1))
        return (base + batch_overhead) * 1024 * 1024


# Known engine VRAM requirements (conservative estimates)
ENGINE_VRAM_REQUIREMENTS: dict[str, VRAMRequirement] = {
    "xtts": VRAMRequirement("xtts", model_vram_mb=2000, working_memory_mb=1000),
    "xtts_v2": VRAMRequirement("xtts_v2", model_vram_mb=2500, working_memory_mb=1000),
    "tortoise": VRAMRequirement("tortoise", model_vram_mb=4000, working_memory_mb=2000),
    "chatterbox": VRAMRequirement("chatterbox", model_vram_mb=2000, working_memory_mb=800),
    "piper": VRAMRequirement("piper", model_vram_mb=200, working_memory_mb=100),
    "whisper_tiny": VRAMRequirement("whisper_tiny", model_vram_mb=500, working_memory_mb=200),
    "whisper_base": VRAMRequirement("whisper_base", model_vram_mb=1000, working_memory_mb=300),
    "whisper_small": VRAMRequirement("whisper_small", model_vram_mb=2000, working_memory_mb=500),
    "whisper_medium": VRAMRequirement("whisper_medium", model_vram_mb=4000, working_memory_mb=1000),
    "whisper_large": VRAMRequirement("whisper_large", model_vram_mb=8000, working_memory_mb=2000),
    "rvc": VRAMRequirement("rvc", model_vram_mb=1500, working_memory_mb=500),
    "emotion": VRAMRequirement("emotion", model_vram_mb=1000, working_memory_mb=300),
    "translation": VRAMRequirement("translation", model_vram_mb=3000, working_memory_mb=1000),
    "lip_sync": VRAMRequirement("lip_sync", model_vram_mb=2000, working_memory_mb=1500),
    "default": VRAMRequirement("default", model_vram_mb=1000, working_memory_mb=500),
}


@dataclass(order=True)
class ScheduledRequest:
    """A request waiting in the scheduler queue."""
    priority: int  # Lower = higher priority (for heapq)
    submitted_at: datetime = field(compare=False)
    request_id: str = field(compare=False)
    engine_name: str = field(compare=False)
    required_vram_bytes: int = field(compare=False)
    callback: Callable[[], Awaitable[Any]] | None = field(compare=False, default=None)
    timeout_seconds: float = field(compare=False, default=300.0)
    metadata: dict[str, Any] = field(compare=False, default_factory=dict)

    # Internal state
    _event: asyncio.Event = field(compare=False, default_factory=asyncio.Event)
    _allocation: MemoryAllocation | None = field(compare=False, default=None)
    _result: Any = field(compare=False, default=None)
    _error: Exception | None = field(compare=False, default=None)


class VRAMScheduler:
    """
    High-level VRAM resource scheduler.

    Manages engine requests with:
    - Priority queue for fair scheduling
    - Pre-flight VRAM checks to prevent OOM
    - Automatic model unloading under pressure
    - Request timeout handling
    """

    def __init__(
        self,
        memory_pool: GPUMemoryPool | None = None,
        max_queue_size: int = 100,
        pressure_threshold: float = 0.85,
    ):
        self._pool = memory_pool or get_memory_pool()
        self._max_queue_size = max_queue_size
        self._pressure_threshold = pressure_threshold

        self._state = SchedulerState.IDLE
        self._queue: list[ScheduledRequest] = []  # heap
        self._active_requests: dict[str, ScheduledRequest] = {}
        self._loaded_engines: dict[str, datetime] = {}  # engine -> last used
        self._unload_callbacks: dict[str, Callable[[], Awaitable[None]]] = {}

        self._lock = asyncio.Lock()
        self._request_counter = 0
        self._processor_task: asyncio.Task | None = None

        logger.info(
            f"VRAM Scheduler initialized: "
            f"pool={self._pool.available_memory / 1e9:.2f}GB, "
            f"pressure_threshold={pressure_threshold}"
        )

    @property
    def state(self) -> SchedulerState:
        """Current scheduler state."""
        return self._state

    @property
    def queue_size(self) -> int:
        """Number of pending requests."""
        return len(self._queue)

    @property
    def active_count(self) -> int:
        """Number of active (processing) requests."""
        return len(self._active_requests)

    def get_requirement(self, engine_name: str) -> VRAMRequirement:
        """Get VRAM requirements for an engine."""
        return ENGINE_VRAM_REQUIREMENTS.get(
            engine_name.lower(),
            ENGINE_VRAM_REQUIREMENTS["default"],
        )

    def register_engine_unload(
        self,
        engine_name: str,
        unload_callback: Callable[[], Awaitable[None]],
    ) -> None:
        """
        Register a callback to unload an engine when under memory pressure.

        Args:
            engine_name: Engine identifier
            unload_callback: Async function to unload the engine
        """
        self._unload_callbacks[engine_name] = unload_callback
        logger.debug(f"Registered unload callback for {engine_name}")

    def mark_engine_loaded(self, engine_name: str) -> None:
        """Mark an engine as currently loaded in VRAM."""
        self._loaded_engines[engine_name] = datetime.now()

    def mark_engine_unloaded(self, engine_name: str) -> None:
        """Mark an engine as unloaded from VRAM."""
        self._loaded_engines.pop(engine_name, None)

    async def can_allocate(
        self,
        engine_name: str,
        batch_size: int = 1,
    ) -> bool:
        """
        Pre-flight check: can we allocate VRAM for this engine?

        Returns True if there's enough free VRAM or we can evict to make space.
        """
        requirement = self.get_requirement(engine_name)
        needed = requirement.for_batch(batch_size)

        # Check if already loaded
        if engine_name in self._loaded_engines:
            return True

        # Check free memory
        if self._pool.free_memory >= needed:
            return True

        # Check if eviction would help
        evictable = await self._get_evictable_memory()
        return self._pool.free_memory + evictable >= needed

    async def _get_evictable_memory(self) -> int:
        """Calculate how much memory can be evicted."""
        # Engines that haven't been used recently
        evictable = 0
        now = datetime.now()

        for engine_name, last_used in self._loaded_engines.items():
            age_seconds = (now - last_used).total_seconds()
            if age_seconds > 60 and engine_name in self._unload_callbacks:
                req = self.get_requirement(engine_name)
                evictable += req.total_bytes

        return evictable

    async def submit(
        self,
        engine_name: str,
        callback: Callable[[], Awaitable[Any]],
        priority: MemoryPriority = MemoryPriority.NORMAL,
        batch_size: int = 1,
        timeout_seconds: float = 300.0,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Submit a request for VRAM allocation and processing.

        This method blocks until the request is processed or times out.

        Args:
            engine_name: Engine requiring VRAM
            callback: Async function to execute when VRAM is allocated
            priority: Request priority
            batch_size: Batch size for VRAM calculation
            timeout_seconds: Maximum wait time
            metadata: Optional request metadata

        Returns:
            Result from the callback function

        Raises:
            TimeoutError: If request times out
            MemoryError: If VRAM allocation fails
        """
        async with self._lock:
            if len(self._queue) >= self._max_queue_size:
                raise RuntimeError("Scheduler queue is full")

            self._request_counter += 1
            request_id = f"req_{self._request_counter}_{engine_name}"

            requirement = self.get_requirement(engine_name)

            request = ScheduledRequest(
                priority=priority.value,
                submitted_at=datetime.now(),
                request_id=request_id,
                engine_name=engine_name,
                required_vram_bytes=requirement.for_batch(batch_size),
                callback=callback,
                timeout_seconds=timeout_seconds,
                metadata=metadata or {},
            )

            heapq.heappush(self._queue, request)
            logger.debug(f"Submitted request {request_id} (queue size: {len(self._queue)})")

        # Start processor if not running
        if self._processor_task is None or self._processor_task.done():
            self._processor_task = asyncio.create_task(self._process_queue())

        # Wait for completion
        try:
            await asyncio.wait_for(request._event.wait(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            # Remove from queue if still there
            async with self._lock:
                if request in self._queue:
                    self._queue.remove(request)
                    heapq.heapify(self._queue)
            raise TimeoutError(f"Request {request_id} timed out after {timeout_seconds}s")

        if request._error:
            raise request._error

        return request._result

    async def _process_queue(self) -> None:
        """Process queued requests."""
        self._state = SchedulerState.PROCESSING

        while True:
            async with self._lock:
                if not self._queue:
                    self._state = SchedulerState.IDLE
                    return

                # Check memory pressure
                if await self._pool.check_pressure():
                    self._state = SchedulerState.UNDER_PRESSURE
                    await self._handle_pressure()

                # Get next request
                request = heapq.heappop(self._queue)

            # Try to allocate and process
            try:
                await self._process_request(request)
            except Exception as e:
                logger.error(f"Request {request.request_id} failed: {e}")
                request._error = e
            finally:
                request._event.set()

            # Small yield to allow other tasks
            await asyncio.sleep(0)

    async def _process_request(self, request: ScheduledRequest) -> None:
        """Process a single request."""
        self._active_requests[request.request_id] = request

        try:
            # Allocate VRAM
            allocation = await self._pool.allocate(
                size_bytes=request.required_vram_bytes,
                owner=request.engine_name,
                priority=MemoryPriority(request.priority),
                metadata={"request_id": request.request_id},
            )

            if allocation is None:
                # Try to free memory
                freed = await self._free_memory_for(request.required_vram_bytes)
                if freed:
                    allocation = await self._pool.allocate(
                        size_bytes=request.required_vram_bytes,
                        owner=request.engine_name,
                        priority=MemoryPriority(request.priority),
                    )

                if allocation is None:
                    raise MemoryError(
                        f"Cannot allocate {request.required_vram_bytes / 1e6:.1f}MB "
                        f"for {request.engine_name}"
                    )

            request._allocation = allocation

            # Mark engine as loaded
            self.mark_engine_loaded(request.engine_name)

            # Execute callback
            if request.callback:
                request._result = await request.callback()

        finally:
            self._active_requests.pop(request.request_id, None)

            # Release allocation (model stays loaded, working memory freed)
            if request._allocation:
                await request._allocation.release()

    async def _handle_pressure(self) -> None:
        """Handle memory pressure by unloading engines."""
        logger.warning("Memory pressure detected, unloading inactive engines")

        now = datetime.now()
        unloaded = []

        # Sort engines by last use (oldest first)
        sorted_engines = sorted(
            self._loaded_engines.items(),
            key=lambda x: x[1],
        )

        for engine_name, last_used in sorted_engines:
            age_seconds = (now - last_used).total_seconds()

            # Only unload if not recently used (>60s) and has callback
            if age_seconds > 60 and engine_name in self._unload_callbacks:
                try:
                    await self._unload_callbacks[engine_name]()
                    self.mark_engine_unloaded(engine_name)
                    unloaded.append(engine_name)
                    logger.info(f"Unloaded {engine_name} to free memory")
                except Exception as e:
                    logger.error(f"Failed to unload {engine_name}: {e}")

            # Stop if pressure is relieved
            if not await self._pool.check_pressure():
                break

        if unloaded:
            logger.info(f"Unloaded {len(unloaded)} engines: {', '.join(unloaded)}")

        self._state = SchedulerState.PROCESSING

    async def _free_memory_for(self, required_bytes: int) -> bool:
        """Try to free memory for a new allocation."""
        if self._pool.free_memory >= required_bytes:
            return True

        # Defragment first
        await self._pool.defragment()

        if self._pool.free_memory >= required_bytes:
            return True

        # Unload engines
        await self._handle_pressure()

        return self._pool.free_memory >= required_bytes

    @asynccontextmanager
    async def allocate_for_engine(
        self,
        engine_name: str,
        batch_size: int = 1,
        priority: MemoryPriority = MemoryPriority.NORMAL,
    ):
        """
        Context manager for temporary engine VRAM allocation.

        Usage:
            async with scheduler.allocate_for_engine("xtts") as allocation:
                # Do work with guaranteed VRAM
                result = await engine.synthesize(text)
        """
        requirement = self.get_requirement(engine_name)
        required_bytes = requirement.for_batch(batch_size)

        allocation = await self._pool.allocate(
            size_bytes=required_bytes,
            owner=engine_name,
            priority=priority,
        )

        if allocation is None:
            await self._free_memory_for(required_bytes)
            allocation = await self._pool.allocate(
                size_bytes=required_bytes,
                owner=engine_name,
                priority=priority,
            )

        if allocation is None:
            raise MemoryError(
                f"Cannot allocate {required_bytes / 1e6:.1f}MB for {engine_name}"
            )

        self.mark_engine_loaded(engine_name)

        try:
            yield allocation
        finally:
            await allocation.release()

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        return {
            "state": self._state.value,
            "queue_size": len(self._queue),
            "active_requests": len(self._active_requests),
            "loaded_engines": list(self._loaded_engines.keys()),
            "total_requests": self._request_counter,
            "memory_pool": self._pool.get_stats(),
        }


# Global scheduler instance
_vram_scheduler: VRAMScheduler | None = None


def get_vram_scheduler() -> VRAMScheduler:
    """Get or create the global VRAM scheduler."""
    global _vram_scheduler
    if _vram_scheduler is None:
        _vram_scheduler = VRAMScheduler()
    return _vram_scheduler
