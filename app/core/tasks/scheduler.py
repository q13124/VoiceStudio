"""
Background Task Scheduler

Implements a comprehensive task scheduling system with priority management,
periodic execution, and resource-aware scheduling.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """
    Represents a background task.

    Attributes:
        id: Unique task identifier
        name: Task name/description
        func: Function to execute
        args: Positional arguments for function
        kwargs: Keyword arguments for function
        priority: Task priority
        status: Current task status
        created_at: Task creation timestamp
        scheduled_at: When task should run (None for immediate)
        interval: Repeat interval in seconds (None for one-time)
        max_retries: Maximum retry attempts on failure
        retry_count: Current retry count
        last_run: Last execution timestamp
        next_run: Next scheduled execution
        result: Task execution result
        error: Error message if failed
        resource_requirements: Resource requirements (CPU, memory, etc.)
    """

    id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: datetime | None = None
    interval: float | None = None  # Repeat interval in seconds
    max_retries: int = 0
    retry_count: int = 0
    last_run: datetime | None = None
    next_run: datetime | None = None
    result: Any = None
    error: str | None = None
    resource_requirements: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize next_run based on scheduled_at or interval."""
        if self.scheduled_at:
            self.next_run = self.scheduled_at
        elif self.interval:
            self.next_run = datetime.now() + timedelta(seconds=self.interval)
        else:
            self.next_run = datetime.now()

    def should_run(self) -> bool:
        """Check if task should run now."""
        if self.status == TaskStatus.CANCELLED:
            return False
        if self.next_run is None:
            return False
        return datetime.now() >= self.next_run

    def update_next_run(self):
        """Update next_run based on interval."""
        if self.interval:
            self.next_run = datetime.now() + timedelta(seconds=self.interval)
        else:
            self.next_run = None


class BackgroundTaskScheduler:
    """
    Background task scheduler with priority management.

    Features:
    - Priority-based task execution
    - Periodic/recurring tasks
    - Resource-aware scheduling
    - Task status tracking
    - Automatic retries
    - Task cancellation
    """

    def __init__(
        self,
        max_concurrent_tasks: int = 10,
        check_interval: float = 1.0,
        resource_aware: bool = True,
        max_cpu_percent: float = 80.0,
        max_memory_percent: float = 80.0,
    ):
        """
        Initialize the task scheduler.

        Args:
            max_concurrent_tasks: Maximum concurrent task executions
            check_interval: Interval to check for tasks (seconds)
            resource_aware: Enable resource-aware scheduling
            max_cpu_percent: Maximum CPU usage before throttling (0-100)
            max_memory_percent: Maximum memory usage before throttling (0-100)
        """
        self._tasks: dict[str, Task] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._max_concurrent_tasks = max_concurrent_tasks
        self._check_interval = check_interval
        self._scheduler_task: asyncio.Task | None = None
        self._running = False
        self._task_count = 0
        self._completed_count = 0
        self._failed_count = 0
        self._resource_aware = resource_aware and HAS_PSUTIL
        self._max_cpu_percent = max_cpu_percent
        self._max_memory_percent = max_memory_percent
        self._total_execution_time = 0.0
        self._task_execution_times: dict[str, list[float]] = {}

    def add_task(
        self,
        name: str,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        scheduled_at: datetime | None = None,
        interval: float | None = None,
        max_retries: int = 0,
        resource_requirements: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        """
        Add a task to the scheduler.

        Args:
            name: Task name/description
            func: Function to execute
            *args: Positional arguments for function
            priority: Task priority
            scheduled_at: When to run the task (None for immediate)
            interval: Repeat interval in seconds (None for one-time)
            max_retries: Maximum retry attempts on failure
            resource_requirements: Resource requirements dict
            **kwargs: Keyword arguments for function

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            scheduled_at=scheduled_at,
            interval=interval,
            max_retries=max_retries,
            resource_requirements=resource_requirements or {},
        )
        self._tasks[task_id] = task
        self._task_count += 1
        logger.info(
            f"Added task: {name} (ID: {task_id}, "
            f"Priority: {priority.name}, "
            f"Scheduled: {scheduled_at or 'immediate'})"
        )
        return task_id

    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the scheduler.

        Args:
            task_id: Task ID to remove

        Returns:
            True if task was removed, False if not found
        """
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.CANCELLED
            del self._tasks[task_id]
            logger.info(f"Removed task: {task.name} (ID: {task_id})")
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running or pending task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if task was cancelled, False if not found
        """
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.CANCELLED
            if task_id in self._running_tasks:
                self._running_tasks[task_id].cancel()
                del self._running_tasks[task_id]
            logger.info(f"Cancelled task: {task.name} (ID: {task_id})")
            return True
        return False

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
    ) -> list[Task]:
        """
        List tasks with optional filtering.

        Args:
            status: Filter by status
            priority: Filter by priority

        Returns:
            List of tasks
        """
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        return tasks

    def _check_resources(self) -> bool:
        """
        Check if system resources are available for task execution.

        Returns:
            True if resources are available, False otherwise
        """
        if not self._resource_aware:
            return True

        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > self._max_cpu_percent:
                logger.debug(
                    f"CPU usage too high: {cpu_percent:.1f}% "
                    f"(max: {self._max_cpu_percent}%)"
                )
                return False

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self._max_memory_percent:
                logger.debug(
                    f"Memory usage too high: {memory.percent:.1f}% "
                    f"(max: {self._max_memory_percent}%)"
                )
                return False

            return True
        except Exception as e:
            logger.debug(f"Resource check failed: {e}")
            return True  # Allow execution if check fails

    async def _execute_task(self, task: Task):
        """Execute a single task (enhanced with execution time tracking)."""
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()
        execution_start = time.perf_counter()

        try:
            # Execute task
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: task.func(*task.args, **task.kwargs)
                )

            execution_time = time.perf_counter() - execution_start
            self._total_execution_time += execution_time

            # Track execution time per task
            if task.id not in self._task_execution_times:
                self._task_execution_times[task.id] = []
            self._task_execution_times[task.id].append(execution_time)
            # Keep only last 100 execution times
            if len(self._task_execution_times[task.id]) > 100:
                self._task_execution_times[task.id].pop(0)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.error = None
            self._completed_count += 1
            logger.info(
                f"Task completed: {task.name} (ID: {task.id}, "
                f"time: {execution_time:.2f}s)"
            )

            # Update next run for recurring tasks
            task.update_next_run()
            if task.interval and task.next_run:
                # Reschedule recurring task
                task.status = TaskStatus.PENDING

        except Exception as e:
            execution_time = time.perf_counter() - execution_start
            task.error = str(e)
            logger.error(
                f"Task failed: {task.name} (ID: {task.id}, "
                f"time: {execution_time:.2f}s): {e}",
                exc_info=True,
            )

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                # Exponential backoff
                backoff = min(2 ** task.retry_count, 300)  # Max 5 minutes
                task.next_run = datetime.now() + timedelta(seconds=backoff)
                logger.info(
                    f"Retrying task: {task.name} "
                    f"(ID: {task.id}, attempt {task.retry_count + 1})"
                )
            else:
                task.status = TaskStatus.FAILED
                self._failed_count += 1
                logger.error(
                    f"Task failed permanently: {task.name} "
                    f"(ID: {task.id})"
                )

    async def _scheduler_loop(self):
        """Main scheduler loop (enhanced with resource awareness)."""
        while self._running:
            try:
                # Check system resources
                resources_available = self._check_resources()

                # Get tasks that should run, sorted by priority
                ready_tasks = [
                    task
                    for task in self._tasks.values()
                    if task.should_run()
                    and task.status == TaskStatus.PENDING
                    and len(self._running_tasks) < self._max_concurrent_tasks
                ]

                # Sort by priority (higher priority first)
                ready_tasks.sort(
                    key=lambda t: t.priority.value, reverse=True
                )

                # Execute ready tasks (respect resource limits)
                for task in ready_tasks:
                    if len(self._running_tasks) >= self._max_concurrent_tasks:
                        break

                    # Check resources before executing
                    if not resources_available:
                        # Only execute critical tasks when resources are low
                        if task.priority != TaskPriority.CRITICAL:
                            continue
                        # Re-check resources for critical tasks
                        if not self._check_resources():
                            logger.debug(
                                f"Deferring task {task.name} due to "
                                f"resource constraints"
                            )
                            continue

                    # Create async task
                    async_task = asyncio.create_task(self._execute_task(task))
                    self._running_tasks[task.id] = async_task

                    # Clean up completed tasks
                    async_task.add_done_callback(
                        lambda t, task_id=task.id: self._running_tasks.pop(
                            task_id, None
                        )
                    )

                # Clean up completed/failed one-time tasks
                to_remove = [
                    task_id
                    for task_id, task in self._tasks.items()
                    if task.status
                    in (TaskStatus.COMPLETED, TaskStatus.FAILED)
                    and not task.interval
                ]
                for task_id in to_remove:
                    del self._tasks[task_id]

                await asyncio.sleep(self._check_interval)

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}", exc_info=True)
                await asyncio.sleep(self._check_interval)

    def start(self):
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Background task scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if not self._running:
            logger.warning("Scheduler not running")
            return

        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()

        # Cancel all running tasks
        for task_id, async_task in list(self._running_tasks.items()):
            async_task.cancel()
            if task_id in self._tasks:
                self._tasks[task_id].status = TaskStatus.CANCELLED

        self._running_tasks.clear()
        logger.info("Background task scheduler stopped")

    def get_stats(self) -> dict[str, Any]:
        """Get scheduler statistics (enhanced)."""
        status_counts = {}
        priority_counts = {}
        for task in self._tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            priority = task.priority.name
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Calculate average execution time
        avg_execution_time = 0.0
        if self._completed_count > 0:
            avg_execution_time = self._total_execution_time / self._completed_count

        # Get resource usage if available
        resource_info = {}
        if self._resource_aware and HAS_PSUTIL:
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                resource_info = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_mb": memory.available / (1024 * 1024),
                    "max_cpu_percent": self._max_cpu_percent,
                    "max_memory_percent": self._max_memory_percent,
                }
            except Exception as e:
                logger.debug(f"Failed to get resource info: {e}")

        return {
            "running": self._running,
            "total_tasks": self._task_count,
            "active_tasks": len(self._tasks),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": self._completed_count,
            "failed_tasks": self._failed_count,
            "max_concurrent_tasks": self._max_concurrent_tasks,
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "total_execution_time": self._total_execution_time,
            "avg_execution_time": avg_execution_time,
            "resource_aware": self._resource_aware,
            "resource_info": resource_info,
        }


# Global scheduler instance
_scheduler: BackgroundTaskScheduler | None = None


def get_scheduler() -> BackgroundTaskScheduler:
    """Get the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundTaskScheduler()
    return _scheduler

