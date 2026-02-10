"""
Memory Pressure Detection.

Task 1.2.4: Auto-eviction under memory pressure.
Monitors system memory and triggers eviction when pressure is high.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Callable, Awaitable, Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class PressureLevel(IntEnum):
    """Memory pressure levels."""
    NORMAL = 0      # < 60% memory used
    MODERATE = 1    # 60-75% memory used
    HIGH = 2        # 75-85% memory used
    CRITICAL = 3    # 85-95% memory used
    EMERGENCY = 4   # > 95% memory used


@dataclass
class PressureEvent:
    """Memory pressure event."""
    level: PressureLevel
    previous_level: PressureLevel
    memory_used_bytes: int
    memory_total_bytes: int
    memory_percent: float
    gpu_memory_used_bytes: int = 0
    gpu_memory_total_bytes: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PressureThresholds:
    """Thresholds for pressure levels."""
    moderate: float = 0.60
    high: float = 0.75
    critical: float = 0.85
    emergency: float = 0.95


@dataclass
class DetectorConfig:
    """Configuration for pressure detector."""
    check_interval_seconds: float = 5.0
    thresholds: PressureThresholds = field(default_factory=PressureThresholds)
    enable_gpu_monitoring: bool = True
    auto_gc_on_high: bool = True
    history_size: int = 60


class MemoryPressureDetector:
    """
    Detects memory pressure and triggers callbacks.
    
    Features:
    - System memory monitoring
    - GPU memory monitoring
    - Pressure level transitions
    - Callback registration for eviction
    - Memory history tracking
    - Automatic garbage collection
    """
    
    def __init__(self, config: Optional[DetectorConfig] = None):
        self.config = config or DetectorConfig()
        
        self._current_level = PressureLevel.NORMAL
        self._callbacks: Dict[PressureLevel, List[Callable[[PressureEvent], Awaitable[None]]]] = {
            level: [] for level in PressureLevel
        }
        self._history: List[Dict[str, Any]] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    @property
    def current_level(self) -> PressureLevel:
        """Current pressure level."""
        return self._current_level
    
    @property
    def is_under_pressure(self) -> bool:
        """Whether system is under memory pressure."""
        return self._current_level >= PressureLevel.HIGH
    
    def register_callback(
        self,
        level: PressureLevel,
        callback: Callable[[PressureEvent], Awaitable[None]],
    ) -> None:
        """
        Register a callback for a pressure level.
        
        Callback is called when pressure transitions to or above this level.
        """
        self._callbacks[level].append(callback)
        logger.debug(f"Registered callback for pressure level {level.name}")
    
    def on_pressure(
        self,
        level: PressureLevel,
    ) -> Callable[[Callable[[PressureEvent], Awaitable[None]]], Callable[[PressureEvent], Awaitable[None]]]:
        """Decorator to register pressure callbacks."""
        def decorator(func: Callable[[PressureEvent], Awaitable[None]]) -> Callable[[PressureEvent], Awaitable[None]]:
            self.register_callback(level, func)
            return func
        return decorator
    
    async def start(self) -> None:
        """Start the pressure detector."""
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info("Memory pressure detector started")
    
    async def stop(self) -> None:
        """Stop the pressure detector."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Memory pressure detector stopped")
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_pressure()
                await asyncio.sleep(self.config.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Pressure detection error: {e}")
                await asyncio.sleep(1.0)
    
    async def _check_pressure(self) -> None:
        """Check current memory pressure."""
        async with self._lock:
            # Get memory stats
            mem_stats = self._get_memory_stats()
            gpu_stats = self._get_gpu_stats() if self.config.enable_gpu_monitoring else {}
            
            # Calculate pressure level
            new_level = self._calculate_level(mem_stats["percent"])
            
            # Record history
            self._record_history(mem_stats, gpu_stats, new_level)
            
            # Handle level transition
            if new_level != self._current_level:
                await self._handle_transition(new_level, mem_stats, gpu_stats)
    
    def _get_memory_stats(self) -> Dict[str, Any]:
        """Get system memory statistics."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "used": mem.used,
                "total": mem.total,
                "percent": mem.percent / 100.0,
                "available": mem.available,
            }
        except ImportError:
            # Fallback for systems without psutil
            return {
                "used": 0,
                "total": 16 * 1024 * 1024 * 1024,
                "percent": 0.5,
                "available": 8 * 1024 * 1024 * 1024,
            }
    
    def _get_gpu_stats(self) -> Dict[str, Any]:
        """Get GPU memory statistics."""
        try:
            import torch
            if torch.cuda.is_available():
                used = 0
                total = 0
                for i in range(torch.cuda.device_count()):
                    props = torch.cuda.get_device_properties(i)
                    allocated = torch.cuda.memory_allocated(i)
                    used += allocated
                    total += props.total_memory
                return {
                    "used": used,
                    "total": total,
                    "percent": used / total if total > 0 else 0,
                }
        except ImportError:
            logger.debug("PyTorch not available for GPU memory tracking")
        
        return {"used": 0, "total": 0, "percent": 0}
    
    def _calculate_level(self, memory_percent: float) -> PressureLevel:
        """Calculate pressure level from memory percentage."""
        thresholds = self.config.thresholds
        
        if memory_percent >= thresholds.emergency:
            return PressureLevel.EMERGENCY
        elif memory_percent >= thresholds.critical:
            return PressureLevel.CRITICAL
        elif memory_percent >= thresholds.high:
            return PressureLevel.HIGH
        elif memory_percent >= thresholds.moderate:
            return PressureLevel.MODERATE
        else:
            return PressureLevel.NORMAL
    
    def _record_history(
        self,
        mem_stats: Dict[str, Any],
        gpu_stats: Dict[str, Any],
        level: PressureLevel,
    ) -> None:
        """Record memory stats to history."""
        self._history.append({
            "timestamp": datetime.now().isoformat(),
            "level": level.name,
            "memory_percent": round(mem_stats["percent"] * 100, 1),
            "memory_used_gb": round(mem_stats["used"] / 1e9, 2),
            "gpu_percent": round(gpu_stats.get("percent", 0) * 100, 1),
            "gpu_used_gb": round(gpu_stats.get("used", 0) / 1e9, 2),
        })
        
        # Trim history
        if len(self._history) > self.config.history_size:
            self._history = self._history[-self.config.history_size:]
    
    async def _handle_transition(
        self,
        new_level: PressureLevel,
        mem_stats: Dict[str, Any],
        gpu_stats: Dict[str, Any],
    ) -> None:
        """Handle pressure level transition."""
        old_level = self._current_level
        self._current_level = new_level
        
        event = PressureEvent(
            level=new_level,
            previous_level=old_level,
            memory_used_bytes=mem_stats["used"],
            memory_total_bytes=mem_stats["total"],
            memory_percent=mem_stats["percent"],
            gpu_memory_used_bytes=gpu_stats.get("used", 0),
            gpu_memory_total_bytes=gpu_stats.get("total", 0),
        )
        
        logger.info(
            f"Memory pressure: {old_level.name} -> {new_level.name} "
            f"({mem_stats['percent']*100:.1f}% used)"
        )
        
        # Run garbage collection on high pressure
        if new_level >= PressureLevel.HIGH and self.config.auto_gc_on_high:
            import gc
            gc.collect()
            logger.debug("Triggered garbage collection")
        
        # Fire callbacks for this level and all lower levels
        for level in PressureLevel:
            if level <= new_level and level > old_level:
                for callback in self._callbacks[level]:
                    try:
                        await callback(event)
                    except Exception as e:
                        logger.error(f"Pressure callback error: {e}")
    
    async def force_check(self) -> PressureLevel:
        """Force an immediate pressure check."""
        await self._check_pressure()
        return self._current_level
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        mem_stats = self._get_memory_stats()
        gpu_stats = self._get_gpu_stats() if self.config.enable_gpu_monitoring else {}
        
        return {
            "level": self._current_level.name,
            "is_under_pressure": self.is_under_pressure,
            "memory": {
                "used_gb": round(mem_stats["used"] / 1e9, 2),
                "total_gb": round(mem_stats["total"] / 1e9, 2),
                "percent": round(mem_stats["percent"] * 100, 1),
            },
            "gpu": {
                "used_gb": round(gpu_stats.get("used", 0) / 1e9, 2),
                "total_gb": round(gpu_stats.get("total", 0) / 1e9, 2),
                "percent": round(gpu_stats.get("percent", 0) * 100, 1),
            } if gpu_stats else None,
            "thresholds": {
                "moderate": self.config.thresholds.moderate * 100,
                "high": self.config.thresholds.high * 100,
                "critical": self.config.thresholds.critical * 100,
                "emergency": self.config.thresholds.emergency * 100,
            },
        }
    
    def get_history(self, limit: int = 60) -> List[Dict[str, Any]]:
        """Get recent memory history."""
        return self._history[-limit:]
    
    def get_stats(self) -> dict:
        """Get detector statistics."""
        return {
            "current": self.get_current_stats(),
            "history_size": len(self._history),
            "callbacks_registered": {
                level.name: len(callbacks)
                for level, callbacks in self._callbacks.items()
            },
        }


# Global detector instance
_detector: Optional[MemoryPressureDetector] = None


def get_pressure_detector() -> MemoryPressureDetector:
    """Get or create the global pressure detector."""
    global _detector
    if _detector is None:
        _detector = MemoryPressureDetector()
    return _detector
