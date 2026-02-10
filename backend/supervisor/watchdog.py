"""
Process Watchdog for FastAPI Backend.

Task 1.1.1: Backend process supervisor with auto-restart capability.
Monitors the FastAPI process and automatically restarts it on failure.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """State of the monitored process."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"
    RESTARTING = "restarting"


@dataclass
class WatchdogConfig:
    """Configuration for the process watchdog."""
    
    # Process configuration
    command: list[str] = field(default_factory=lambda: ["python", "-m", "uvicorn", "backend.api.main:app"])
    working_directory: str = "."
    environment: dict[str, str] = field(default_factory=dict)
    
    # Restart policy
    max_restarts: int = 5
    restart_window_seconds: int = 300  # 5 minutes
    restart_delay_seconds: float = 2.0
    restart_delay_max_seconds: float = 60.0
    restart_delay_multiplier: float = 2.0
    
    # Health check configuration
    health_check_interval_seconds: float = 10.0
    health_check_timeout_seconds: float = 5.0
    health_check_url: str = "http://localhost:8001/health"
    health_check_max_failures: int = 3
    
    # Graceful shutdown
    graceful_shutdown_timeout_seconds: float = 30.0
    
    # Logging
    log_file: Optional[str] = None
    capture_output: bool = True


@dataclass
class RestartRecord:
    """Record of a process restart."""
    timestamp: datetime
    reason: str
    exit_code: Optional[int] = None


class ProcessWatchdog:
    """
    Watchdog that monitors and auto-restarts the FastAPI backend process.
    
    Features:
    - Automatic restart on crash with exponential backoff
    - Health check monitoring
    - Graceful shutdown support
    - Restart rate limiting to prevent restart loops
    - Event callbacks for monitoring integration
    """
    
    def __init__(self, config: Optional[WatchdogConfig] = None):
        self.config = config or WatchdogConfig()
        self._process: Optional[subprocess.Popen] = None
        self._state = ProcessState.STOPPED
        self._restart_history: list[RestartRecord] = []
        self._current_restart_delay = self.config.restart_delay_seconds
        self._health_check_failures = 0
        self._should_run = False
        self._lock = asyncio.Lock()
        
        # Callbacks
        self._on_state_change: Optional[Callable[[ProcessState, ProcessState], None]] = None
        self._on_restart: Optional[Callable[[RestartRecord], None]] = None
        self._on_health_check_failure: Optional[Callable[[int], None]] = None
    
    @property
    def state(self) -> ProcessState:
        """Current state of the monitored process."""
        return self._state
    
    @property
    def is_running(self) -> bool:
        """Whether the process is currently running."""
        return self._state == ProcessState.RUNNING
    
    @property
    def pid(self) -> Optional[int]:
        """Process ID of the monitored process."""
        return self._process.pid if self._process else None
    
    @property
    def restart_count(self) -> int:
        """Number of restarts in the current window."""
        cutoff = datetime.now() - timedelta(seconds=self.config.restart_window_seconds)
        return sum(1 for r in self._restart_history if r.timestamp > cutoff)
    
    def set_callbacks(
        self,
        on_state_change: Optional[Callable[[ProcessState, ProcessState], None]] = None,
        on_restart: Optional[Callable[[RestartRecord], None]] = None,
        on_health_check_failure: Optional[Callable[[int], None]] = None,
    ) -> None:
        """Set event callbacks for monitoring."""
        self._on_state_change = on_state_change
        self._on_restart = on_restart
        self._on_health_check_failure = on_health_check_failure
    
    def _set_state(self, new_state: ProcessState) -> None:
        """Update state and fire callback."""
        old_state = self._state
        if old_state != new_state:
            self._state = new_state
            logger.info(f"Process state changed: {old_state.value} -> {new_state.value}")
            if self._on_state_change:
                try:
                    self._on_state_change(old_state, new_state)
                except Exception as e:
                    logger.warning(f"State change callback error: {e}")
    
    def _record_restart(self, reason: str, exit_code: Optional[int] = None) -> RestartRecord:
        """Record a restart event."""
        record = RestartRecord(
            timestamp=datetime.now(),
            reason=reason,
            exit_code=exit_code,
        )
        self._restart_history.append(record)
        
        # Clean old records
        cutoff = datetime.now() - timedelta(seconds=self.config.restart_window_seconds * 2)
        self._restart_history = [r for r in self._restart_history if r.timestamp > cutoff]
        
        if self._on_restart:
            try:
                self._on_restart(record)
            except Exception as e:
                logger.warning(f"Restart callback error: {e}")
        
        return record
    
    def _can_restart(self) -> bool:
        """Check if restart is allowed based on restart policy."""
        return self.restart_count < self.config.max_restarts
    
    def _get_restart_delay(self) -> float:
        """Get the delay before next restart (exponential backoff)."""
        delay = self._current_restart_delay
        self._current_restart_delay = min(
            self._current_restart_delay * self.config.restart_delay_multiplier,
            self.config.restart_delay_max_seconds,
        )
        return delay
    
    def _reset_restart_delay(self) -> None:
        """Reset restart delay after successful health check."""
        self._current_restart_delay = self.config.restart_delay_seconds
    
    async def start(self) -> bool:
        """Start the monitored process."""
        async with self._lock:
            if self._state in (ProcessState.RUNNING, ProcessState.STARTING):
                logger.warning("Process already running or starting")
                return False
            
            self._should_run = True
            return await self._start_process()
    
    async def _start_process(self) -> bool:
        """Internal method to start the process."""
        self._set_state(ProcessState.STARTING)
        
        try:
            env = os.environ.copy()
            env.update(self.config.environment)
            
            self._process = subprocess.Popen(
                self.config.command,
                cwd=self.config.working_directory,
                env=env,
                stdout=subprocess.PIPE if self.config.capture_output else None,
                stderr=subprocess.PIPE if self.config.capture_output else None,
            )
            
            # Wait briefly to check for immediate failure
            await asyncio.sleep(1.0)
            
            if self._process.poll() is not None:
                exit_code = self._process.returncode
                logger.error(f"Process failed to start (exit code: {exit_code})")
                self._set_state(ProcessState.FAILED)
                return False
            
            self._set_state(ProcessState.RUNNING)
            self._health_check_failures = 0
            logger.info(f"Process started successfully (PID: {self._process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            self._set_state(ProcessState.FAILED)
            return False
    
    async def stop(self, graceful: bool = True) -> bool:
        """Stop the monitored process."""
        async with self._lock:
            self._should_run = False
            
            if not self._process or self._state == ProcessState.STOPPED:
                return True
            
            self._set_state(ProcessState.STOPPING)
            
            try:
                if graceful:
                    # Send SIGTERM for graceful shutdown
                    self._process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        await asyncio.wait_for(
                            asyncio.get_event_loop().run_in_executor(
                                None, self._process.wait
                            ),
                            timeout=self.config.graceful_shutdown_timeout_seconds,
                        )
                    except asyncio.TimeoutError:
                        logger.warning("Graceful shutdown timeout, killing process")
                        self._process.kill()
                        self._process.wait()
                else:
                    self._process.kill()
                    self._process.wait()
                
                self._set_state(ProcessState.STOPPED)
                logger.info("Process stopped successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error stopping process: {e}")
                return False
    
    async def restart(self, reason: str = "manual") -> bool:
        """Restart the monitored process."""
        async with self._lock:
            self._set_state(ProcessState.RESTARTING)
            
            # Stop current process
            if self._process:
                try:
                    self._process.terminate()
                    await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, self._process.wait
                        ),
                        timeout=self.config.graceful_shutdown_timeout_seconds,
                    )
                except asyncio.TimeoutError:
                    self._process.kill()
                    self._process.wait()
            
            self._record_restart(reason)
            
            # Start new process
            return await self._start_process()
    
    async def health_check(self) -> bool:
        """Perform a health check on the process."""
        if not self._process or self._state != ProcessState.RUNNING:
            return False
        
        # Check if process is still alive
        if self._process.poll() is not None:
            return False
        
        # HTTP health check
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=self.config.health_check_timeout_seconds),
                ) as response:
                    if response.status == 200:
                        self._health_check_failures = 0
                        self._reset_restart_delay()
                        return True
                    else:
                        logger.warning(f"Health check returned status {response.status}")
        except ImportError:
            # aiohttp not available, just check process is alive
            return True
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
        
        self._health_check_failures += 1
        if self._on_health_check_failure:
            try:
                self._on_health_check_failure(self._health_check_failures)
            except Exception as callback_err:
                logger.warning(f"Health check failure callback raised error: {callback_err}")
        
        return False
    
    async def monitor(self) -> None:
        """
        Main monitoring loop.
        
        Continuously monitors the process and performs automatic restarts.
        Call this in an async task to enable auto-restart functionality.
        """
        logger.info("Starting process monitor loop")
        
        while self._should_run:
            try:
                # Check process state
                if self._process and self._process.poll() is not None:
                    exit_code = self._process.returncode
                    logger.warning(f"Process exited unexpectedly (exit code: {exit_code})")
                    
                    if self._should_run and self._can_restart():
                        delay = self._get_restart_delay()
                        logger.info(f"Scheduling restart in {delay:.1f} seconds")
                        await asyncio.sleep(delay)
                        
                        if self._should_run:
                            await self.restart(f"crashed (exit code: {exit_code})")
                    elif not self._can_restart():
                        logger.error("Max restarts exceeded, entering failed state")
                        self._set_state(ProcessState.FAILED)
                        break
                
                # Perform health check
                if self._state == ProcessState.RUNNING:
                    healthy = await self.health_check()
                    
                    if not healthy and self._health_check_failures >= self.config.health_check_max_failures:
                        logger.warning("Health check failures exceeded threshold")
                        if self._should_run and self._can_restart():
                            await self.restart("health check failures")
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(5.0)
        
        logger.info("Process monitor loop stopped")
    
    def get_status(self) -> dict:
        """Get current watchdog status."""
        return {
            "state": self._state.value,
            "pid": self.pid,
            "restart_count": self.restart_count,
            "health_check_failures": self._health_check_failures,
            "restart_history": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "reason": r.reason,
                    "exit_code": r.exit_code,
                }
                for r in self._restart_history[-10:]  # Last 10 restarts
            ],
        }


# Convenience function for starting the watchdog
async def run_watchdog(config: Optional[WatchdogConfig] = None) -> None:
    """Run the process watchdog as the main entry point."""
    watchdog = ProcessWatchdog(config)
    
    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(watchdog.stop()))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass
    
    await watchdog.start()
    await watchdog.monitor()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_watchdog())
