"""
Plugin Subprocess Runner.

Phase 4 Enhancement: Manages plugin subprocess lifecycle including
spawning, monitoring, and termination.

The runner:
    - Spawns isolated Python subprocesses for plugins
    - Establishes IPC bridge communication
    - Monitors process health via heartbeat
    - Enforces resource limits (planned)
    - Handles graceful and forced termination
"""

import asyncio
import logging
import os
import sys
import signal
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable

from .bridge import IPCBridge, BridgeState
from .protocol import HostMethods, Request, Response, Notification

logger = logging.getLogger(__name__)


class ProcessState(str, Enum):
    """States of a plugin subprocess."""

    NOT_STARTED = "not_started"
    STARTING = "starting"
    RUNNING = "running"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"
    KILLED = "killed"


@dataclass
class RunnerConfig:
    """Configuration for plugin subprocess runner."""

    # Plugin info
    plugin_id: str
    plugin_path: Path
    entry_module: str

    # Process settings
    python_executable: str = field(default_factory=lambda: sys.executable)
    working_directory: Optional[Path] = None
    env_vars: Dict[str, str] = field(default_factory=dict)

    # Timeouts (milliseconds)
    startup_timeout_ms: int = 10000
    shutdown_timeout_ms: int = 5000
    heartbeat_interval_ms: int = 5000
    heartbeat_timeout_ms: int = 15000

    # Resource limits (future implementation)
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[int] = None

    # Permissions (passed to subprocess)
    permissions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginRunner:
    """
    Manages a single plugin subprocess.

    Handles the complete lifecycle from spawning to termination,
    including IPC bridge setup and health monitoring.
    """

    config: RunnerConfig
    state: ProcessState = ProcessState.NOT_STARTED

    # Process handle
    _process: Optional[asyncio.subprocess.Process] = field(default=None, repr=False)
    _bridge: IPCBridge = field(default_factory=IPCBridge, repr=False)

    # Monitoring
    _heartbeat_task: Optional[asyncio.Task] = field(default=None, repr=False)
    _last_heartbeat: float = field(default=0.0, repr=False)

    # Callbacks
    _on_state_change: List = field(default_factory=list, repr=False)
    _on_crash: List = field(default_factory=list, repr=False)

    def __post_init__(self):
        """Initialize internal state."""
        self._on_state_change = []
        self._on_crash = []

    @property
    def bridge(self) -> IPCBridge:
        """Get the IPC bridge for this runner."""
        return self._bridge

    @property
    def pid(self) -> Optional[int]:
        """Get the subprocess PID if running."""
        if self._process:
            return self._process.pid
        return None

    @property
    def is_running(self) -> bool:
        """Check if the subprocess is running."""
        return self.state in (
            ProcessState.RUNNING,
            ProcessState.INITIALIZING,
            ProcessState.ACTIVE,
        )

    async def start(self) -> None:
        """
        Start the plugin subprocess.

        Spawns the subprocess, establishes IPC, and waits for
        the plugin to complete initialization.

        Raises:
            RuntimeError: If already running or start fails
            TimeoutError: If startup times out
        """
        if self.state not in (ProcessState.NOT_STARTED, ProcessState.STOPPED):
            raise RuntimeError(f"Cannot start in state {self.state}")

        self._set_state(ProcessState.STARTING)

        try:
            await self._spawn_subprocess()
            await self._establish_bridge()
            await self._initialize_plugin()

            self._set_state(ProcessState.ACTIVE)
            self._start_heartbeat()

            logger.info(
                f"Plugin subprocess started: {self.config.plugin_id} (PID: {self.pid})"
            )

        except Exception as e:
            logger.error(f"Failed to start plugin subprocess: {e}")
            await self._cleanup()
            self._set_state(ProcessState.CRASHED)
            raise

    async def stop(self, force: bool = False) -> None:
        """
        Stop the plugin subprocess.

        Args:
            force: If True, kill immediately without graceful shutdown

        Raises:
            TimeoutError: If graceful shutdown times out
        """
        if not self.is_running:
            return

        self._set_state(ProcessState.STOPPING)
        self._stop_heartbeat()

        if force:
            await self._force_kill()
        else:
            await self._graceful_shutdown()

    async def invoke_capability(
        self,
        capability: str,
        params: Optional[Dict[str, Any]] = None,
        timeout_ms: Optional[int] = None,
    ) -> Any:
        """
        Invoke a plugin capability.

        Args:
            capability: The capability name
            params: Optional parameters
            timeout_ms: Optional timeout override

        Returns:
            The capability result

        Raises:
            RuntimeError: If plugin is not active
        """
        if self.state != ProcessState.ACTIVE:
            raise RuntimeError(f"Cannot invoke capability in state {self.state}")

        return await self._bridge.send_request(
            HostMethods.INVOKE_CAPABILITY,
            {"capability": capability, "params": params or {}},
            timeout_ms,
        )

    def on_state_change(self, callback) -> None:
        """Register a callback for state changes."""
        self._on_state_change.append(callback)

    def on_crash(self, callback) -> None:
        """Register a callback for crash events."""
        self._on_crash.append(callback)

    async def _spawn_subprocess(self) -> None:
        """Spawn the plugin subprocess."""
        # Build the subprocess entry script
        entry_script = self._build_entry_script()

        # Build environment
        env = os.environ.copy()
        env.update(self.config.env_vars)
        env["VOICESTUDIO_PLUGIN_ID"] = self.config.plugin_id
        env["VOICESTUDIO_PLUGIN_PATH"] = str(self.config.plugin_path)
        env["VOICESTUDIO_SUBPROCESS"] = "1"

        # Working directory
        cwd = self.config.working_directory or self.config.plugin_path

        logger.debug(f"Spawning subprocess for {self.config.plugin_id}")

        self._process = await asyncio.create_subprocess_exec(
            self.config.python_executable,
            "-c",
            entry_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=cwd,
        )

        self._set_state(ProcessState.RUNNING)

        # Start stderr reader
        asyncio.create_task(self._read_stderr())

    def _build_entry_script(self) -> str:
        """Build the Python script to run in the subprocess."""
        # Get the backend path for fallback import
        backend_root = Path(__file__).parent.parent.parent.parent
        
        # This script bootstraps the plugin in the subprocess
        return f'''
import sys
import os
import asyncio
import json

# Add plugin path to sys.path
plugin_path = os.environ.get("VOICESTUDIO_PLUGIN_PATH", "")
if plugin_path:
    sys.path.insert(0, plugin_path)

# Import the subprocess client module
# This will be provided by the SDK
try:
    from voicestudio_sdk.subprocess_client import SubprocessClient
    client = SubprocessClient()
    asyncio.run(client.run("{self.config.entry_module}"))
except ImportError:
    # Fallback: minimal bootstrap without SDK
    # Add backend root to path for fallback import
    backend_root = r"{backend_root}"
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
    
    from backend.plugins.sandbox.subprocess_bootstrap import run_plugin_subprocess
    asyncio.run(run_plugin_subprocess("{self.config.entry_module}"))
'''

    async def _establish_bridge(self) -> None:
        """Establish IPC bridge with subprocess."""
        if not self._process or not self._process.stdin or not self._process.stdout:
            raise RuntimeError("Process streams not available")

        # Create stream reader/writer from process pipes
        reader = self._process.stdout
        writer = self._process.stdin

        # Connect bridge
        self._bridge.connect(reader, writer)
        await self._bridge.start_reading()

        logger.debug(f"IPC bridge established for {self.config.plugin_id}")

    async def _initialize_plugin(self) -> None:
        """Initialize the plugin in the subprocess."""
        self._set_state(ProcessState.INITIALIZING)

        try:
            # Send initialization request
            result = await self._bridge.send_request(
                HostMethods.INITIALIZE,
                {
                    "plugin_id": self.config.plugin_id,
                    "permissions": self.config.permissions,
                },
                timeout_ms=self.config.startup_timeout_ms,
            )

            logger.debug(f"Plugin initialized: {result}")

        except TimeoutError:
            raise TimeoutError(
                f"Plugin {self.config.plugin_id} initialization timed out"
            )

    async def _graceful_shutdown(self) -> None:
        """Attempt graceful shutdown of the subprocess."""
        try:
            # Send shutdown request
            await self._bridge.send_request(
                HostMethods.SHUTDOWN,
                timeout_ms=self.config.shutdown_timeout_ms,
            )

            # Wait for process to exit
            await asyncio.wait_for(
                self._process.wait(),
                timeout=self.config.shutdown_timeout_ms / 1000.0,
            )

            self._set_state(ProcessState.STOPPED)

        except (TimeoutError, asyncio.TimeoutError):
            logger.warning(
                f"Graceful shutdown timed out for {self.config.plugin_id}, forcing"
            )
            await self._force_kill()

        finally:
            await self._cleanup()

    async def _force_kill(self) -> None:
        """Force kill the subprocess."""
        if self._process and self._process.returncode is None:
            try:
                self._process.kill()
                await self._process.wait()
            except ProcessLookupError:
                # SAFETY: ProcessLookupError occurs when the process has already
                # terminated before we could kill it. This is expected during
                # force-kill scenarios and requires no further action.
                pass

        self._set_state(ProcessState.KILLED)
        await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up resources after subprocess ends."""
        self._stop_heartbeat()

        if self._bridge.state != BridgeState.DISCONNECTED:
            await self._bridge.close()

        self._process = None

    def _start_heartbeat(self) -> None:
        """Start heartbeat monitoring."""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    def _stop_heartbeat(self) -> None:
        """Stop heartbeat monitoring."""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            self._heartbeat_task = None

    async def _heartbeat_loop(self) -> None:
        """Monitor plugin health via heartbeat."""
        import time

        while self.is_running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval_ms / 1000.0)

                # Send heartbeat
                await self._bridge.send_notification(
                    HostMethods.HEARTBEAT,
                    {"timestamp": time.time()},
                )
                self._last_heartbeat = time.time()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat failed for {self.config.plugin_id}: {e}")

                # Check if process is still running
                if self._process and self._process.returncode is not None:
                    self._set_state(ProcessState.CRASHED)
                    self._fire_crash_callbacks()
                    break

    async def _read_stderr(self) -> None:
        """Read and log subprocess stderr."""
        if not self._process or not self._process.stderr:
            return

        while True:
            try:
                line = await self._process.stderr.readline()
                if not line:
                    break
                logger.debug(f"[{self.config.plugin_id}] {line.decode().strip()}")
            except Exception:
                break

    def _set_state(self, new_state: ProcessState) -> None:
        """Update state and fire callbacks."""
        old_state = self.state
        self.state = new_state
        logger.debug(f"Plugin {self.config.plugin_id}: {old_state} -> {new_state}")

        for callback in self._on_state_change:
            try:
                callback(self.config.plugin_id, old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")

    def _fire_crash_callbacks(self) -> None:
        """Fire crash callbacks."""
        for callback in self._on_crash:
            try:
                callback(self.config.plugin_id)
            except Exception as e:
                logger.error(f"Error in crash callback: {e}")
