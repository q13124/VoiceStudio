"""
GPU Memory Pool Manager.

Task 1.2.1: Unified VRAM allocation across engines.
Manages GPU memory allocation to prevent OOM errors and optimize utilization.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MemoryPriority(Enum):
    """Priority for memory allocation."""
    CRITICAL = 0  # Required for operation
    HIGH = 1      # Active processing
    NORMAL = 2    # Standard allocation
    LOW = 3       # Can be evicted
    CACHE = 4     # Purely cache, evict first


@dataclass
class GPUMemoryBlock:
    """Represents a block of allocated GPU memory."""
    id: str
    size_bytes: int
    owner: str  # Engine or component name
    priority: MemoryPriority
    allocated_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = datetime.now()


@dataclass
class MemoryAllocation:
    """Context for a memory allocation."""
    block: GPUMemoryBlock
    pool: "GPUMemoryPool"
    
    async def release(self) -> None:
        """Release this allocation."""
        await self.pool.release(self.block.id)


@dataclass
class GPUInfo:
    """Information about a GPU device."""
    device_id: int
    name: str
    total_memory_bytes: int
    free_memory_bytes: int
    used_memory_bytes: int
    utilization_percent: float


class GPUMemoryPool:
    """
    Unified GPU memory pool manager.
    
    Features:
    - Centralized VRAM allocation
    - Priority-based eviction
    - Memory pressure detection
    - Per-engine quotas
    - Memory usage tracking
    """
    
    def __init__(
        self,
        device_id: int = 0,
        max_memory_bytes: Optional[int] = None,
        reserved_memory_bytes: int = 512 * 1024 * 1024,  # 512MB reserved
        eviction_threshold: float = 0.85,  # Start eviction at 85% usage
    ):
        self.device_id = device_id
        self.reserved_memory_bytes = reserved_memory_bytes
        self.eviction_threshold = eviction_threshold
        
        # Get total GPU memory
        self._total_memory = max_memory_bytes or self._detect_gpu_memory()
        self._available_memory = self._total_memory - reserved_memory_bytes
        
        self._allocations: Dict[str, GPUMemoryBlock] = {}
        self._engine_quotas: Dict[str, int] = {}
        self._engine_usage: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        self._allocation_counter = 0
        
        logger.info(
            f"GPU Memory Pool initialized: "
            f"total={self._total_memory / 1e9:.2f}GB, "
            f"available={self._available_memory / 1e9:.2f}GB"
        )
    
    def _detect_gpu_memory(self) -> int:
        """Detect available GPU memory."""
        try:
            import torch
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(self.device_id)
                return props.total_memory
        except ImportError:
            logger.debug("PyTorch not available for GPU memory detection")
        
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                memory_mb = int(result.stdout.strip().split("\n")[self.device_id])
                return memory_mb * 1024 * 1024
        except Exception as e:
            logger.debug("nvidia-smi GPU memory detection failed: %s", e)
        
        # Default to 8GB if detection fails
        logger.warning("Could not detect GPU memory, defaulting to 8GB")
        return 8 * 1024 * 1024 * 1024
    
    @property
    def total_memory(self) -> int:
        """Total GPU memory in bytes."""
        return self._total_memory
    
    @property
    def available_memory(self) -> int:
        """Available memory for allocation in bytes."""
        return self._available_memory
    
    @property
    def used_memory(self) -> int:
        """Currently used memory in bytes."""
        return sum(b.size_bytes for b in self._allocations.values())
    
    @property
    def free_memory(self) -> int:
        """Free memory available for new allocations."""
        return self._available_memory - self.used_memory
    
    @property
    def utilization(self) -> float:
        """Memory utilization ratio (0-1)."""
        if self._available_memory == 0:
            return 1.0
        return self.used_memory / self._available_memory
    
    def set_engine_quota(self, engine: str, max_bytes: int) -> None:
        """Set maximum memory quota for an engine."""
        self._engine_quotas[engine] = max_bytes
        logger.info(f"Set memory quota for {engine}: {max_bytes / 1e6:.1f}MB")
    
    def get_engine_usage(self, engine: str) -> int:
        """Get current memory usage for an engine."""
        return sum(
            b.size_bytes for b in self._allocations.values()
            if b.owner == engine
        )
    
    async def allocate(
        self,
        size_bytes: int,
        owner: str,
        priority: MemoryPriority = MemoryPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[MemoryAllocation]:
        """
        Allocate GPU memory.
        
        Returns MemoryAllocation if successful, None if allocation fails.
        """
        async with self._lock:
            # Check engine quota
            if owner in self._engine_quotas:
                engine_usage = self.get_engine_usage(owner)
                if engine_usage + size_bytes > self._engine_quotas[owner]:
                    logger.warning(f"Engine {owner} would exceed quota")
                    return None
            
            # Check if eviction is needed
            if self.used_memory + size_bytes > self._available_memory:
                evicted = await self._evict(size_bytes, priority)
                if not evicted:
                    logger.warning(f"Cannot allocate {size_bytes / 1e6:.1f}MB, eviction failed")
                    return None
            
            # Create allocation
            self._allocation_counter += 1
            block_id = f"block_{self._allocation_counter}_{owner}"
            
            block = GPUMemoryBlock(
                id=block_id,
                size_bytes=size_bytes,
                owner=owner,
                priority=priority,
                metadata=metadata or {},
            )
            
            self._allocations[block_id] = block
            
            logger.debug(
                f"Allocated {size_bytes / 1e6:.1f}MB for {owner} "
                f"(total used: {self.used_memory / 1e6:.1f}MB)"
            )
            
            return MemoryAllocation(block=block, pool=self)
    
    async def release(self, block_id: str) -> bool:
        """Release a memory allocation."""
        async with self._lock:
            if block_id not in self._allocations:
                logger.warning(f"Block {block_id} not found")
                return False
            
            block = self._allocations.pop(block_id)
            logger.debug(f"Released {block.size_bytes / 1e6:.1f}MB from {block.owner}")
            return True
    
    async def _evict(self, required_bytes: int, requester_priority: MemoryPriority) -> bool:
        """
        Evict lower-priority allocations to free memory.
        
        Returns True if enough memory was freed.
        """
        target_free = required_bytes + (self._available_memory * 0.1)  # Free extra 10%
        
        # Get evictable blocks (lower priority than requester)
        evictable = [
            b for b in self._allocations.values()
            if b.priority.value > requester_priority.value
        ]
        
        if not evictable:
            return False
        
        # Sort by priority (highest first = evict first), then by last access (oldest first)
        evictable.sort(key=lambda b: (b.priority.value, b.last_accessed), reverse=True)
        
        freed = 0
        evicted_ids = []
        
        for block in evictable:
            if self.free_memory + freed >= target_free:
                break
            
            freed += block.size_bytes
            evicted_ids.append(block.id)
        
        # Perform eviction
        for block_id in evicted_ids:
            block = self._allocations.pop(block_id)
            logger.info(f"Evicted {block.owner} block ({block.size_bytes / 1e6:.1f}MB)")
        
        return self.free_memory >= required_bytes
    
    @asynccontextmanager
    async def allocate_context(
        self,
        size_bytes: int,
        owner: str,
        priority: MemoryPriority = MemoryPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for temporary allocations."""
        allocation = await self.allocate(size_bytes, owner, priority, metadata)
        if allocation is None:
            raise MemoryError(f"Cannot allocate {size_bytes / 1e6:.1f}MB for {owner}")
        
        try:
            yield allocation
        finally:
            await allocation.release()
    
    def touch(self, block_id: str) -> None:
        """Update last accessed time for a block."""
        if block_id in self._allocations:
            self._allocations[block_id].touch()
    
    async def check_pressure(self) -> bool:
        """Check if memory pressure is high."""
        return self.utilization >= self.eviction_threshold
    
    async def defragment(self) -> int:
        """
        Release stale allocations.
        
        Returns number of bytes freed.
        """
        stale_threshold = datetime.now() - timedelta(minutes=30)
        
        stale_blocks = [
            b for b in self._allocations.values()
            if b.last_accessed < stale_threshold and b.priority == MemoryPriority.CACHE
        ]
        
        freed = 0
        for block in stale_blocks:
            await self.release(block.id)
            freed += block.size_bytes
        
        if freed > 0:
            logger.info(f"Defragmented {freed / 1e6:.1f}MB from stale cache allocations")
        
        return freed
    
    def get_gpu_info(self) -> GPUInfo:
        """Get current GPU information."""
        return GPUInfo(
            device_id=self.device_id,
            name=f"GPU {self.device_id}",
            total_memory_bytes=self._total_memory,
            free_memory_bytes=self.free_memory + self.reserved_memory_bytes,
            used_memory_bytes=self.used_memory,
            utilization_percent=self.utilization * 100,
        )
    
    def get_stats(self) -> dict:
        """Get memory pool statistics."""
        by_owner = {}
        by_priority = {}
        
        for block in self._allocations.values():
            by_owner[block.owner] = by_owner.get(block.owner, 0) + block.size_bytes
            by_priority[block.priority.name] = by_priority.get(block.priority.name, 0) + block.size_bytes
        
        return {
            "total_memory_gb": round(self._total_memory / 1e9, 2),
            "available_memory_gb": round(self._available_memory / 1e9, 2),
            "used_memory_gb": round(self.used_memory / 1e9, 2),
            "free_memory_gb": round(self.free_memory / 1e9, 2),
            "utilization_percent": round(self.utilization * 100, 1),
            "allocation_count": len(self._allocations),
            "by_owner_mb": {k: round(v / 1e6, 1) for k, v in by_owner.items()},
            "by_priority_mb": {k: round(v / 1e6, 1) for k, v in by_priority.items()},
        }


# Global memory pool instance
_memory_pool: Optional[GPUMemoryPool] = None


def get_memory_pool(device_id: int = 0) -> GPUMemoryPool:
    """Get or create the global GPU memory pool."""
    global _memory_pool
    if _memory_pool is None:
        _memory_pool = GPUMemoryPool(device_id=device_id)
    return _memory_pool
