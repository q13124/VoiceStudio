"""
Phase 7: Startup Service
Task 7.6: Application startup and initialization.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class StartupPhase(Enum):
    """Startup phases."""
    INITIALIZING = "initializing"
    LOADING_CONFIG = "loading_config"
    CHECKING_PREREQUISITES = "checking_prerequisites"
    LOADING_ENGINES = "loading_engines"
    CONNECTING_BACKEND = "connecting_backend"
    RESTORING_STATE = "restoring_state"
    READY = "ready"
    ERROR = "error"


@dataclass
class StartupProgress:
    """Startup progress information."""
    phase: StartupPhase
    progress_percent: float = 0.0
    message: str = ""
    current_item: str | None = None
    total_items: int = 0
    completed_items: int = 0


@dataclass
class StartupResult:
    """Result of startup process."""
    success: bool
    duration_seconds: float
    phases_completed: list[StartupPhase]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class StartupConfig:
    """Startup configuration."""
    skip_engine_loading: bool = False
    skip_backend_connection: bool = False
    skip_state_restore: bool = False
    timeout_seconds: int = 60
    parallel_loading: bool = True


class StartupTask:
    """A task to run during startup."""

    def __init__(
        self,
        name: str,
        phase: StartupPhase,
        func: Callable[[], Any],
        required: bool = True,
        timeout: float = 30.0
    ):
        self.name = name
        self.phase = phase
        self.func = func
        self.required = required
        self.timeout = timeout
        self.completed = False
        self.error: str | None = None


class StartupService:
    """Service for managing application startup."""

    def __init__(self, config: StartupConfig | None = None):
        self._config = config or StartupConfig()
        self._tasks: list[StartupTask] = []
        self._progress = StartupProgress(phase=StartupPhase.INITIALIZING)
        self._progress_callbacks: list[Callable[[StartupProgress], None]] = []
        self._start_time: datetime | None = None

    @property
    def progress(self) -> StartupProgress:
        """Get current startup progress."""
        return self._progress

    def add_task(self, task: StartupTask) -> None:
        """Add a startup task."""
        self._tasks.append(task)

    def add_progress_callback(self, callback: Callable[[StartupProgress], None]) -> None:
        """Add a progress callback."""
        self._progress_callbacks.append(callback)

    async def run(self) -> StartupResult:
        """Run the startup process."""
        self._start_time = datetime.now()

        result = StartupResult(
            success=True,
            duration_seconds=0.0,
            phases_completed=[],
        )

        try:
            # Group tasks by phase
            phases = [
                StartupPhase.LOADING_CONFIG,
                StartupPhase.CHECKING_PREREQUISITES,
                StartupPhase.LOADING_ENGINES,
                StartupPhase.CONNECTING_BACKEND,
                StartupPhase.RESTORING_STATE,
            ]

            total_tasks = len(self._tasks)
            completed_tasks = 0

            for phase in phases:
                # Check if phase should be skipped
                if self._should_skip_phase(phase):
                    continue

                self._update_progress(phase, f"Starting {phase.value}...")

                # Get tasks for this phase
                phase_tasks = [t for t in self._tasks if t.phase == phase]

                if not phase_tasks:
                    result.phases_completed.append(phase)
                    continue

                # Run tasks
                if self._config.parallel_loading and len(phase_tasks) > 1:
                    # Run in parallel
                    tasks = [self._run_task(t) for t in phase_tasks]
                    await asyncio.gather(*tasks, return_exceptions=True)
                else:
                    # Run sequentially
                    for task in phase_tasks:
                        await self._run_task(task)
                        completed_tasks += 1
                        self._update_progress(
                            phase,
                            f"Completed {task.name}",
                            progress=completed_tasks / total_tasks * 100
                        )

                # Check for errors
                for task in phase_tasks:
                    if task.error:
                        if task.required:
                            result.success = False
                            result.errors.append(f"{task.name}: {task.error}")
                        else:
                            result.warnings.append(f"{task.name}: {task.error}")

                if not result.success:
                    break

                result.phases_completed.append(phase)

            # Final state
            if result.success:
                self._update_progress(StartupPhase.READY, "Application ready", 100)
            else:
                self._update_progress(StartupPhase.ERROR, "Startup failed")

        except Exception as e:
            logger.error(f"Startup error: {e}")
            result.success = False
            result.errors.append(str(e))
            self._update_progress(StartupPhase.ERROR, str(e))

        result.duration_seconds = (datetime.now() - self._start_time).total_seconds()

        return result

    async def _run_task(self, task: StartupTask) -> None:
        """Run a single startup task."""
        try:
            self._progress.current_item = task.name

            if asyncio.iscoroutinefunction(task.func):
                await asyncio.wait_for(task.func(), timeout=task.timeout)
            else:
                await asyncio.get_event_loop().run_in_executor(None, task.func)

            task.completed = True

        except asyncio.TimeoutError:
            task.error = f"Timeout after {task.timeout}s"
            logger.error(f"Task {task.name} timed out")

        except Exception as e:
            task.error = str(e)
            logger.error(f"Task {task.name} failed: {e}")

    def _should_skip_phase(self, phase: StartupPhase) -> bool:
        """Check if a phase should be skipped."""
        if phase == StartupPhase.LOADING_ENGINES and self._config.skip_engine_loading:
            return True

        if phase == StartupPhase.CONNECTING_BACKEND and self._config.skip_backend_connection:
            return True

        return bool(phase == StartupPhase.RESTORING_STATE and self._config.skip_state_restore)

    def _update_progress(
        self,
        phase: StartupPhase,
        message: str,
        progress: float = 0.0
    ) -> None:
        """Update startup progress."""
        self._progress.phase = phase
        self._progress.message = message
        self._progress.progress_percent = progress

        for callback in self._progress_callbacks:
            try:
                callback(self._progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")


def create_default_startup_tasks() -> list[StartupTask]:
    """Create default startup tasks."""
    tasks = []

    # Config loading
    tasks.append(StartupTask(
        name="Load configuration",
        phase=StartupPhase.LOADING_CONFIG,
        func=lambda: None,  # Placeholder
        required=True,
    ))

    tasks.append(StartupTask(
        name="Load user preferences",
        phase=StartupPhase.LOADING_CONFIG,
        func=lambda: None,
        required=False,
    ))

    # Prerequisites
    tasks.append(StartupTask(
        name="Check Python environment",
        phase=StartupPhase.CHECKING_PREREQUISITES,
        func=lambda: None,
        required=True,
    ))

    tasks.append(StartupTask(
        name="Check GPU availability",
        phase=StartupPhase.CHECKING_PREREQUISITES,
        func=lambda: None,
        required=False,
    ))

    # Engines
    tasks.append(StartupTask(
        name="Initialize voice engines",
        phase=StartupPhase.LOADING_ENGINES,
        func=lambda: None,
        required=True,
    ))

    tasks.append(StartupTask(
        name="Load voice models",
        phase=StartupPhase.LOADING_ENGINES,
        func=lambda: None,
        required=False,
    ))

    # Backend
    tasks.append(StartupTask(
        name="Start backend server",
        phase=StartupPhase.CONNECTING_BACKEND,
        func=lambda: None,
        required=True,
    ))

    # State
    tasks.append(StartupTask(
        name="Restore last session",
        phase=StartupPhase.RESTORING_STATE,
        func=lambda: None,
        required=False,
    ))

    return tasks
