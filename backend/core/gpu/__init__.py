"""GPU resource management module."""

from backend.core.gpu.memory_pool import (
    GPUMemoryPool,
    GPUMemoryBlock,
    MemoryAllocation,
    MemoryPriority,
    get_memory_pool,
)
from backend.core.gpu.vram_scheduler import (
    VRAMScheduler,
    VRAMRequirement,
    SchedulerState,
    ENGINE_VRAM_REQUIREMENTS,
    get_vram_scheduler,
)

__all__ = [
    # Memory pool
    "GPUMemoryPool",
    "GPUMemoryBlock",
    "MemoryAllocation",
    "MemoryPriority",
    "get_memory_pool",
    # VRAM scheduler
    "VRAMScheduler",
    "VRAMRequirement",
    "SchedulerState",
    "ENGINE_VRAM_REQUIREMENTS",
    "get_vram_scheduler",
]
