"""GPU resource management module."""

from backend.core.gpu.memory_pool import (
    GPUMemoryBlock,
    GPUMemoryPool,
    MemoryAllocation,
    MemoryPriority,
    get_memory_pool,
)
from backend.core.gpu.vram_scheduler import (
    ENGINE_VRAM_REQUIREMENTS,
    SchedulerState,
    VRAMRequirement,
    VRAMScheduler,
    get_vram_scheduler,
)

__all__ = [
    "ENGINE_VRAM_REQUIREMENTS",
    "GPUMemoryBlock",
    # Memory pool
    "GPUMemoryPool",
    "MemoryAllocation",
    "MemoryPriority",
    "SchedulerState",
    "VRAMRequirement",
    # VRAM scheduler
    "VRAMScheduler",
    "get_memory_pool",
    "get_vram_scheduler",
]
