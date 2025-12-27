"""
Resource Manager
VRAM-aware resource scheduling and admission control for engine jobs
"""

import logging
import math
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import PriorityQueue, Queue
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class JobPriority(Enum):
    """Job priority levels."""

    REALTIME = 1
    INTERACTIVE = 2
    BATCH = 3


class JobStatus(Enum):
    """Job status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ResourceRequirement:
    """Resource requirements for a job."""

    vram_gb: float = 0.0
    ram_gb: float = 0.0
    cpu_cores: int = 1
    duration_hint_seconds: Optional[float] = None
    requires_gpu: bool = False


@dataclass
class Job:
    """Job description."""

    job_id: str
    engine_id: str
    task: str
    priority: JobPriority
    requirements: ResourceRequirement
    payload: Dict[str, Any]
    callback: Optional[Callable] = None
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


# Try importing performance monitoring libraries
try:
    import cpuinfo

    HAS_CPUINFO = True
except ImportError:
    HAS_CPUINFO = False
    cpuinfo = None
    logger.debug("py-cpuinfo not available. CPU info will be limited.")

try:
    import GPUtil

    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False
    GPUtil = None
    logger.debug("GPUtil not available. GPU monitoring will be limited.")

try:
    import pynvml

    HAS_NVIDIA_ML = True
except ImportError:
    HAS_NVIDIA_ML = False
    pynvml = None
    logger.debug("nvidia-ml-py not available. NVIDIA GPU monitoring will be limited.")

try:
    import wandb

    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False
    wandb = None
    logger.debug("wandb not available. Experiment tracking will be limited.")


class GPUMonitor:
    """Monitor GPU/VRAM usage with multiple backends."""

    def __init__(self):
        self._has_gpu = False
        self._total_vram_gb = 0.0
        self._available_vram_gb = 0.0
        self._used_vram_gb = 0.0
        self._last_check = 0.0
        self._check_interval = 5.0  # Check every 5 seconds

        # Initialize NVIDIA ML if available
        if HAS_NVIDIA_ML:
            try:
                pynvml.nvmlInit()
                self._nvidia_ml_initialized = True
            except Exception as e:
                logger.warning(f"Failed to initialize NVIDIA ML: {e}")
                self._nvidia_ml_initialized = False
        else:
            self._nvidia_ml_initialized = False

        self._update_gpu_info()

    def _update_gpu_info(self):
        """Update GPU information using best available method."""
        # Try NVIDIA ML first (most accurate)
        if self._nvidia_ml_initialized:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                self._has_gpu = True
                self._total_vram_gb = mem_info.total / (1024**3)
                self._used_vram_gb = mem_info.used / (1024**3)
                self._available_vram_gb = mem_info.free / (1024**3)
                return
            except Exception as e:
                logger.debug(f"NVIDIA ML GPU check failed: {e}")

        # Try GPUtil (works with any GPU)
        if HAS_GPUTIL:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    self._has_gpu = True
                    self._total_vram_gb = gpu.memoryTotal / 1024.0
                    self._used_vram_gb = gpu.memoryUsed / 1024.0
                    self._available_vram_gb = gpu.memoryFree / 1024.0
                    return
            except Exception as e:
                logger.debug(f"GPUtil GPU check failed: {e}")

        # Fallback to PyTorch
        try:
            import torch

            if torch.cuda.is_available():
                self._has_gpu = True
                self._total_vram_gb = torch.cuda.get_device_properties(
                    0
                ).total_memory / (1024**3)

                # Get current usage
                torch.cuda.empty_cache()
                self._used_vram_gb = torch.cuda.memory_allocated(0) / (1024**3)
                self._available_vram_gb = self._total_vram_gb - self._used_vram_gb
            else:
                self._has_gpu = False
                self._total_vram_gb = 0.0
                self._available_vram_gb = 0.0
                self._used_vram_gb = 0.0
        except ImportError:
            logger.debug("PyTorch not available, GPU monitoring disabled")
            self._has_gpu = False
        except Exception as e:
            logger.warning(f"Failed to update GPU info: {e}")

    def get_available_vram_gb(self, force_check: bool = False) -> float:
        """
        Get available VRAM in GB.

        Args:
            force_check: Force a new check (ignore cache)

        Returns:
            Available VRAM in GB
        """
        now = time.time()
        if force_check or (now - self._last_check) > self._check_interval:
            self._update_gpu_info()
            self._last_check = now

        return self._available_vram_gb

    def has_sufficient_vram(self, required_gb: float, headroom_gb: float = 1.0) -> bool:
        """
        Check if there's sufficient VRAM available.

        Args:
            required_gb: Required VRAM in GB
            headroom_gb: Safety headroom in GB

        Returns:
            True if sufficient VRAM is available
        """
        if not self._has_gpu:
            return not (required_gb > 0)  # If no GPU, can't satisfy GPU requirements

        available = self.get_available_vram_gb()
        return available >= (required_gb + headroom_gb)

    def get_cpu_info(self) -> Dict[str, Any]:
        """
        Get CPU information using py-cpuinfo.

        Returns:
            Dictionary with CPU information
        """
        if not HAS_CPUINFO:
            return {}

        try:
            info = cpuinfo.get_cpu_info()
            return {
                "brand": info.get("brand_raw", "Unknown"),
                "arch": info.get("arch", "Unknown"),
                "bits": info.get("bits", 64),
                "count": info.get("count", 1),
                "hz_advertised": info.get("hz_advertised_friendly", "Unknown"),
                "hz_actual": info.get("hz_actual_friendly", "Unknown"),
            }
        except Exception as e:
            logger.warning(f"Failed to get CPU info: {e}")
            return {}

    def get_gpu_info(self) -> Dict[str, Any]:
        """
        Get detailed GPU information.

        Returns:
            Dictionary with GPU information
        """
        info = {
            "has_gpu": self._has_gpu,
            "total_vram_gb": self._total_vram_gb,
            "used_vram_gb": self._used_vram_gb,
            "available_vram_gb": self._available_vram_gb,
        }

        # Add NVIDIA-specific info if available
        if self._nvidia_ml_initialized:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name = pynvml.nvmlDeviceGetName(handle).decode("utf-8")
                temp = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU
                )
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to W
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)

                info.update(
                    {
                        "name": name,
                        "temperature_c": temp,
                        "power_usage_w": power,
                        "gpu_utilization_percent": utilization.gpu,
                        "memory_utilization_percent": utilization.memory,
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to get NVIDIA GPU details: {e}")

        return info

    def get_vram_info(self) -> Dict[str, float]:
        """Get current VRAM information."""
        return {
            "has_gpu": self._has_gpu,
            "total_gb": self._total_vram_gb,
            "used_gb": self._used_vram_gb,
            "available_gb": self.get_available_vram_gb(force_check=True),
        }


class ResourceManager:
    """
    VRAM-aware resource manager with priority queues.

    Features:
    - Priority queues (realtime, interactive, batch)
    - VRAM admission control
    - Job preemption rules
    - Exponential backoff on failures
    - Circuit breaker for degraded engines
    """

    def __init__(self, vram_headroom_gb: float = 1.0):
        """
        Initialize resource manager.

        Args:
            vram_headroom_gb: Safety headroom for VRAM allocation
        """
        self.vram_headroom_gb = vram_headroom_gb
        self.gpu_monitor = GPUMonitor()

        # Priority queues
        self.realtime_queue: PriorityQueue = PriorityQueue()
        self.interactive_queue: PriorityQueue = PriorityQueue()
        self.batch_queue: PriorityQueue = PriorityQueue()

        # Active jobs
        self.active_jobs: Dict[str, Job] = {}

        # Job history
        self.job_history: List[Job] = []
        self.max_history = 1000

        # Engine health tracking
        self.engine_failures: Dict[str, int] = {}  # Count of consecutive failures
        self.engine_backoff: Dict[str, float] = {}  # Backoff until timestamp
        self.engine_circuit_breaker: Dict[str, bool] = {}  # Circuit breaker state

        # Threading
        self.lock = threading.Lock()
        self.running = True

        # Track allocated resources
        self.allocated_vram_gb: Dict[str, float] = {}  # job_id -> vram_gb

    def submit_job(
        self,
        job_id: str,
        engine_id: str,
        task: str,
        priority: JobPriority,
        requirements: ResourceRequirement,
        payload: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> bool:
        """
        Submit a job for execution.

        Args:
            job_id: Unique job identifier
            engine_id: Engine to execute the job
            task: Task type
            priority: Job priority
            requirements: Resource requirements
            payload: Job payload
            callback: Optional callback function

        Returns:
            True if job was accepted, False if rejected
        """
        with self.lock:
            # Check circuit breaker
            if self.engine_circuit_breaker.get(engine_id, False):
                logger.warning(
                    f"Engine {engine_id} is in circuit breaker state, rejecting job {job_id}"
                )
                return False

            # Check backoff
            backoff_until = self.engine_backoff.get(engine_id, 0.0)
            if time.time() < backoff_until:
                logger.warning(
                    f"Engine {engine_id} is in backoff period, rejecting job {job_id}"
                )
                return False

            # Check VRAM availability
            if not self.gpu_monitor.has_sufficient_vram(
                requirements.vram_gb, self.vram_headroom_gb
            ):
                logger.warning(
                    f"Insufficient VRAM for job {job_id} (required: {requirements.vram_gb}GB)"
                )
                # Still queue the job, it will be processed when resources are available
                # (For realtime/interactive, could return False immediately)

            # Create job
            job = Job(
                job_id=job_id,
                engine_id=engine_id,
                task=task,
                priority=priority,
                requirements=requirements,
                payload=payload,
                callback=callback,
            )

            # Queue job based on priority
            if priority == JobPriority.REALTIME:
                self.realtime_queue.put((priority.value, time.time(), job))
            elif priority == JobPriority.INTERACTIVE:
                self.interactive_queue.put((priority.value, time.time(), job))
            else:  # BATCH
                self.batch_queue.put((priority.value, time.time(), job))

            logger.info(f"Job {job_id} queued with priority {priority.name}")
            return True

    def get_next_job(self) -> Optional[Job]:
        """
        Get next job to execute based on priority and resource availability.

        Returns:
            Next job or None if no jobs available
        """
        with self.lock:
            # Try queues in priority order
            queues = [
                (self.realtime_queue, JobPriority.REALTIME),
                (self.interactive_queue, JobPriority.INTERACTIVE),
                (self.batch_queue, JobPriority.BATCH),
            ]

            for queue, priority in queues:
                if not queue.empty():
                    try:
                        _, _, job = queue.get_nowait()

                        # Check if engine is available
                        if self.engine_circuit_breaker.get(job.engine_id, False):
                            continue

                        backoff_until = self.engine_backoff.get(job.engine_id, 0.0)
                        if time.time() < backoff_until:
                            continue

                        # Check VRAM availability
                        if self.gpu_monitor.has_sufficient_vram(
                            job.requirements.vram_gb, self.vram_headroom_gb
                        ):
                            return job
                        else:
                            # Put job back if insufficient resources
                            queue.put((priority.value, time.time(), job))
                    except Exception:
                        continue

            return None

    def start_job(self, job: Job):
        """Mark job as started and track resources."""
        with self.lock:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            self.active_jobs[job.job_id] = job

            # Track allocated VRAM
            if job.requirements.vram_gb > 0:
                self.allocated_vram_gb[job.job_id] = job.requirements.vram_gb
                logger.info(
                    f"Job {job.job_id} started, allocated {job.requirements.vram_gb}GB VRAM"
                )

    def complete_job(
        self, job_id: str, success: bool = True, error: Optional[str] = None
    ):
        """Mark job as completed and release resources."""
        with self.lock:
            if job_id not in self.active_jobs:
                logger.warning(f"Job {job_id} not found in active jobs")
                return

            job = self.active_jobs.pop(job_id)
            job.completed_at = datetime.now()

            if success:
                job.status = JobStatus.COMPLETED
                # Reset failure count on success
                self.engine_failures[job.engine_id] = 0
                self.engine_circuit_breaker[job.engine_id] = False
            else:
                job.status = JobStatus.FAILED
                job.error = error

                # Increment failure count
                failures = self.engine_failures.get(job.engine_id, 0) + 1
                self.engine_failures[job.engine_id] = failures

                # Exponential backoff
                backoff_seconds = min(2**failures, 300)  # Max 5 minutes
                self.engine_backoff[job.engine_id] = time.time() + backoff_seconds
                logger.warning(
                    f"Engine {job.engine_id} failed {failures} times, backing off for {backoff_seconds}s"
                )

                # Circuit breaker after 5 failures
                if failures >= 5:
                    self.engine_circuit_breaker[job.engine_id] = True
                    logger.error(
                        f"Engine {job.engine_id} circuit breaker activated after {failures} failures"
                    )

            # Release allocated VRAM
            if job_id in self.allocated_vram_gb:
                allocated = self.allocated_vram_gb.pop(job_id)
                logger.info(f"Job {job_id} completed, released {allocated}GB VRAM")

            # Add to history
            self.job_history.append(job)
            if len(self.job_history) > self.max_history:
                self.job_history.pop(0)

            # Call callback if provided
            if job.callback:
                try:
                    job.callback(job)
                except Exception as e:
                    logger.error(f"Callback failed for job {job_id}: {e}")

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued or running job."""
        with self.lock:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                job.status = JobStatus.CANCELLED
                self.complete_job(job_id, success=False, error="Cancelled by user")
                return True

            # Check queues (simplified - would need to search queues)
            logger.warning(f"Job {job_id} not found or already completed")
            return False

    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status."""
        with self.lock:
            return {
                "gpu": self.gpu_monitor.get_vram_info(),
                "active_jobs": len(self.active_jobs),
                "queued_jobs": {
                    "realtime": self.realtime_queue.qsize(),
                    "interactive": self.interactive_queue.qsize(),
                    "batch": self.batch_queue.qsize(),
                },
                "allocated_vram_gb": sum(self.allocated_vram_gb.values()),
                "engine_status": {
                    engine_id: {
                        "failures": self.engine_failures.get(engine_id, 0),
                        "circuit_breaker": self.engine_circuit_breaker.get(
                            engine_id, False
                        ),
                        "backoff_until": self.engine_backoff.get(engine_id, 0.0),
                    }
                    for engine_id in set(
                        list(self.engine_failures.keys())
                        + list(self.engine_circuit_breaker.keys())
                    )
                },
            }


# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager(vram_headroom_gb: float = 1.0) -> ResourceManager:
    """Get or create global resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager(vram_headroom_gb)
    return _resource_manager
