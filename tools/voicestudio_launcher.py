#!/usr/bin/env python
"""
VoiceStudio Unified Launcher

A single entry point for starting all VoiceStudio services with:
- Dev/prod mode switching
- Health checks for all services
- Graceful startup/shutdown
- Log aggregation
- Process supervision

Usage:
    # Development mode (default)
    python tools/voicestudio_launcher.py

    # Production mode
    python tools/voicestudio_launcher.py --mode prod

    # Health check only
    python tools/voicestudio_launcher.py --health-check

    # Start specific services
    python tools/voicestudio_launcher.py --services backend engine-pool

    # With custom config
    python tools/voicestudio_launcher.py --config config/deployment.config.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import atexit
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


# ==============================================================================
# Configuration
# ==============================================================================


class LaunchMode(Enum):
    """Launch mode enumeration."""
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class ServiceState(Enum):
    """Service state enumeration."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    UNHEALTHY = "unhealthy"
    STOPPING = "stopping"
    FAILED = "failed"


@dataclass
class ServiceConfig:
    """Configuration for a single service."""
    name: str
    command: list[str]
    port: int | None = None
    health_endpoint: str | None = None
    startup_timeout: int = 60
    health_check_interval: int = 30
    depends_on: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    working_dir: Path | None = None
    required: bool = True


@dataclass
class LauncherConfig:
    """Launcher configuration."""
    mode: LaunchMode = LaunchMode.DEVELOPMENT
    services: list[str] = field(default_factory=lambda: ["all"])
    config_path: Path | None = None
    log_level: str = "INFO"
    log_file: Path | None = None
    graceful_shutdown_timeout: int = 30


# ==============================================================================
# Logging Setup
# ==============================================================================


def setup_logging(config: LauncherConfig) -> logging.Logger:
    """Setup logging for the launcher."""
    logger = logging.getLogger("voicestudio_launcher")
    logger.setLevel(getattr(logging, config.log_level.upper()))

    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Color formatting based on level
    class ColorFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[36m',      # Cyan
            'INFO': '\033[32m',       # Green
            'WARNING': '\033[33m',    # Yellow
            'ERROR': '\033[31m',      # Red
            'CRITICAL': '\033[35m',   # Magenta
        }
        RESET = '\033[0m'

        def format(self, record: logging.LogRecord) -> str:
            color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            return super().format(record)

    formatter = ColorFormatter(
        '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if configured
    if config.log_file:
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


# ==============================================================================
# Service Definitions
# ==============================================================================


def get_service_definitions(mode: LaunchMode) -> dict[str, ServiceConfig]:
    """
    Get service definitions based on launch mode.

    Returns service configurations for:
    - backend: FastAPI backend server
    - xtts-service: XTTS engine service (separate venv)
    - engine-pool: Engine worker pool
    """
    is_dev = mode == LaunchMode.DEVELOPMENT

    # Backend service
    backend_cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.api.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
    ]
    if is_dev:
        backend_cmd.append("--reload")
    else:
        backend_cmd.extend(["--workers", "4"])

    services = {
        "backend": ServiceConfig(
            name="backend",
            command=backend_cmd,
            port=8000,
            health_endpoint="/health",
            startup_timeout=30 if is_dev else 60,
            health_check_interval=30,
            working_dir=PROJECT_ROOT,
            env={"PYTHONPATH": str(PROJECT_ROOT)},
        ),
        "xtts-service": ServiceConfig(
            name="xtts-service",
            command=[
                str(PROJECT_ROOT / "runtime" / "xtts_service" / ".venv" / "Scripts" / "python.exe"),
                "-m", "uvicorn",
                "xtts_server:app",
                "--host", "127.0.0.1",
                "--port", "8001",
            ],
            port=8001,
            health_endpoint="/health",
            startup_timeout=120,  # XTTS takes time to load models
            health_check_interval=60,
            working_dir=PROJECT_ROOT / "runtime" / "xtts_service",
            depends_on=[],
            required=False,  # Optional service
        ),
        "engine-pool": ServiceConfig(
            name="engine-pool",
            command=[
                sys.executable,
                str(PROJECT_ROOT / "app" / "core" / "runtime" / "engine_pool.py"),
                "--workers", "2" if is_dev else "4",
            ],
            health_endpoint=None,  # No HTTP endpoint
            startup_timeout=30,
            depends_on=["backend"],
            working_dir=PROJECT_ROOT,
            env={"PYTHONPATH": str(PROJECT_ROOT)},
            required=False,
        ),
    }

    return services


# ==============================================================================
# Health Check
# ==============================================================================


async def check_service_health(
    service: ServiceConfig,
    timeout: float = 5.0
) -> tuple[bool, str]:
    """
    Check if a service is healthy.

    Returns:
        Tuple of (is_healthy, message)
    """
    if not service.port or not service.health_endpoint:
        return True, "No health endpoint configured"

    if httpx is None:
        return True, "httpx not installed, skipping health check"

    url = f"http://127.0.0.1:{service.port}{service.health_endpoint}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            if response.status_code == 200:
                return True, f"Healthy (status={response.status_code})"
            else:
                return False, f"Unhealthy (status={response.status_code})"
    except httpx.ConnectError:
        return False, "Connection refused"
    except httpx.TimeoutException:
        return False, "Timeout"
    except Exception as e:
        return False, f"Error: {e}"


async def wait_for_service(
    service: ServiceConfig,
    logger: logging.Logger,
    timeout: int | None = None
) -> bool:
    """
    Wait for a service to become healthy.

    Returns:
        True if service became healthy, False if timeout
    """
    timeout = timeout or service.startup_timeout
    start_time = time.time()
    check_interval = 1.0

    while time.time() - start_time < timeout:
        is_healthy, message = await check_service_health(service)
        if is_healthy:
            logger.info(f"Service '{service.name}' is healthy: {message}")
            return True

        logger.debug(f"Service '{service.name}' not ready: {message}")
        await asyncio.sleep(check_interval)
        check_interval = min(check_interval * 1.2, 5.0)  # Exponential backoff

    logger.error(f"Service '{service.name}' failed to become healthy within {timeout}s")
    return False


# ==============================================================================
# Process Manager
# ==============================================================================


class ProcessManager:
    """Manages service processes."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.processes: dict[str, subprocess.Popen] = {}
        self.states: dict[str, ServiceState] = {}
        self._shutdown_event = threading.Event()

    def start_service(self, service: ServiceConfig) -> bool:
        """Start a single service."""
        if service.name in self.processes:
            self.logger.warning(f"Service '{service.name}' is already running")
            return True

        self.states[service.name] = ServiceState.STARTING
        self.logger.info(f"Starting service '{service.name}'...")
        self.logger.debug(f"Command: {' '.join(service.command)}")

        try:
            env = os.environ.copy()
            env.update(service.env)

            # Set working directory
            cwd = service.working_dir or PROJECT_ROOT

            # Check if command exists
            if not Path(service.command[0]).exists() and not self._command_exists(service.command[0]):
                self.logger.warning(f"Command not found for '{service.name}': {service.command[0]}")
                self.states[service.name] = ServiceState.FAILED
                return False

            process = subprocess.Popen(
                service.command,
                cwd=str(cwd),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            self.processes[service.name] = process

            # Start log reader thread
            log_thread = threading.Thread(
                target=self._read_process_logs,
                args=(service.name, process),
                daemon=True
            )
            log_thread.start()

            self.states[service.name] = ServiceState.RUNNING
            self.logger.info(f"Service '{service.name}' started (PID: {process.pid})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start service '{service.name}': {e}")
            self.states[service.name] = ServiceState.FAILED
            return False

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        import shutil
        return shutil.which(command) is not None

    def _read_process_logs(self, name: str, process: subprocess.Popen) -> None:
        """Read and log process output."""
        try:
            for line in iter(process.stdout.readline, ''):  # type: ignore
                if self._shutdown_event.is_set():
                    break
                if line:
                    self.logger.debug(f"[{name}] {line.rstrip()}")
        except Exception as e:
            # Expected when process terminates or stream closes
            self.logger.debug(f"Log reader for {name} stopped: {e}")

    def stop_service(self, name: str, timeout: int = 10) -> bool:
        """Stop a single service gracefully."""
        if name not in self.processes:
            return True

        self.states[name] = ServiceState.STOPPING
        process = self.processes[name]

        self.logger.info(f"Stopping service '{name}' (PID: {process.pid})...")

        try:
            # Send SIGTERM (or equivalent on Windows)
            process.terminate()

            try:
                process.wait(timeout=timeout)
                self.logger.info(f"Service '{name}' stopped gracefully")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Service '{name}' did not stop gracefully, killing...")
                process.kill()
                process.wait(timeout=5)

            del self.processes[name]
            self.states[name] = ServiceState.STOPPED
            return True

        except Exception as e:
            self.logger.error(f"Error stopping service '{name}': {e}")
            self.states[name] = ServiceState.FAILED
            return False

    def stop_all(self, timeout: int = 30) -> None:
        """Stop all services gracefully."""
        self._shutdown_event.set()

        # Stop in reverse order of dependencies
        services = list(self.processes.keys())
        services.reverse()

        for name in services:
            self.stop_service(name, timeout=timeout // len(services) if services else timeout)

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all services."""
        status = {}
        for name, state in self.states.items():
            process = self.processes.get(name)
            status[name] = {
                "state": state.value,
                "pid": process.pid if process else None,
                "running": process is not None and process.poll() is None,
            }
        return status

    def is_running(self, name: str) -> bool:
        """Check if a service is running."""
        if name not in self.processes:
            return False
        return self.processes[name].poll() is None


# ==============================================================================
# Launcher
# ==============================================================================


class VoiceStudioLauncher:
    """Main launcher class."""

    def __init__(self, config: LauncherConfig):
        self.config = config
        self.logger = setup_logging(config)
        self.process_manager = ProcessManager(self.logger)
        self.service_definitions = get_service_definitions(config.mode)

        # Register shutdown handlers
        atexit.register(self._shutdown)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self._shutdown()
        sys.exit(0)

    def _shutdown(self) -> None:
        """Shutdown all services."""
        self.logger.info("Shutting down VoiceStudio services...")
        self.process_manager.stop_all(timeout=self.config.graceful_shutdown_timeout)
        self.logger.info("Shutdown complete")

    def _get_services_to_start(self) -> list[ServiceConfig]:
        """Get list of services to start based on configuration."""
        if "all" in self.config.services:
            return list(self.service_definitions.values())

        services = []
        for name in self.config.services:
            if name in self.service_definitions:
                services.append(self.service_definitions[name])
            else:
                self.logger.warning(f"Unknown service: {name}")

        return services

    def _resolve_dependencies(self, services: list[ServiceConfig]) -> list[ServiceConfig]:
        """Resolve service dependencies and return ordered list."""
        # Build dependency graph
        service_map = {s.name: s for s in services}
        ordered = []
        visited = set()

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)

            service = service_map.get(name)
            if service:
                for dep in service.depends_on:
                    if dep in service_map:
                        visit(dep)
                ordered.append(service)

        for service in services:
            visit(service.name)

        return ordered

    async def start(self) -> bool:
        """Start all configured services."""
        self.logger.info(f"Starting VoiceStudio in {self.config.mode.value} mode...")

        services = self._get_services_to_start()
        services = self._resolve_dependencies(services)

        if not services:
            self.logger.error("No services to start")
            return False

        self.logger.info(f"Services to start: {[s.name for s in services]}")

        # Start services in order
        for service in services:
            if not service.required:
                # Check if optional service can start
                if not self._can_start_optional_service(service):
                    self.logger.info(f"Skipping optional service '{service.name}' (requirements not met)")
                    continue

            success = self.process_manager.start_service(service)
            if not success and service.required:
                self.logger.error(f"Failed to start required service '{service.name}'")
                return False

            # Wait for service to be healthy
            if service.health_endpoint:
                is_healthy = await wait_for_service(service, self.logger)
                if not is_healthy and service.required:
                    self.logger.error(f"Required service '{service.name}' failed health check")
                    return False

        self.logger.info("All services started successfully")
        return True

    def _can_start_optional_service(self, service: ServiceConfig) -> bool:
        """Check if an optional service can be started."""
        # Check if command exists
        cmd = service.command[0]
        return Path(cmd).exists()

    async def health_check(self) -> dict[str, dict[str, Any]]:
        """Perform health check on all services."""
        results = {}

        for name, service in self.service_definitions.items():
            is_healthy, message = await check_service_health(service)
            results[name] = {
                "healthy": is_healthy,
                "message": message,
                "port": service.port,
            }

        return results

    async def run_forever(self) -> None:
        """Run the launcher and keep services alive."""
        success = await self.start()
        if not success:
            self.logger.error("Startup failed")
            return

        self.logger.info("VoiceStudio is running. Press Ctrl+C to stop.")

        # Monitor services
        try:
            while True:
                await asyncio.sleep(30)

                # Check service health
                for name, service in self.service_definitions.items():
                    if name in self.process_manager.processes:
                        if not self.process_manager.is_running(name):
                            self.logger.warning(f"Service '{name}' has stopped unexpectedly")
                            # Optionally restart
                            if service.required:
                                self.logger.info(f"Restarting service '{name}'...")
                                self.process_manager.start_service(service)

        # ALLOWED: bare except - CancelledError is expected during shutdown
        except asyncio.CancelledError:
            pass


# ==============================================================================
# CLI
# ==============================================================================


def parse_args() -> LauncherConfig:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="VoiceStudio Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start in development mode
  %(prog)s --mode prod              # Start in production mode
  %(prog)s --health-check           # Check service health
  %(prog)s --services backend       # Start only backend
  %(prog)s --log-level DEBUG        # Verbose logging
        """
    )

    parser.add_argument(
        "--mode",
        choices=["dev", "prod"],
        default="dev",
        help="Launch mode (default: dev)"
    )

    parser.add_argument(
        "--services",
        nargs="+",
        default=["all"],
        help="Services to start (default: all)"
    )

    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Perform health check and exit"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to deployment config file"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path"
    )

    args = parser.parse_args()

    return LauncherConfig(
        mode=LaunchMode.DEVELOPMENT if args.mode == "dev" else LaunchMode.PRODUCTION,
        services=args.services,
        config_path=args.config,
        log_level=args.log_level,
        log_file=args.log_file,
    )


async def main_async(config: LauncherConfig, health_check_only: bool = False) -> int:
    """Async main entry point."""
    launcher = VoiceStudioLauncher(config)

    if health_check_only:
        results = await launcher.health_check()
        print("\n=== VoiceStudio Service Health ===\n")
        all_healthy = True
        for name, status in results.items():
            # Use ASCII-safe symbols for Windows compatibility
            icon = "[OK]" if status["healthy"] else "[FAIL]"
            port_info = f" (port {status['port']})" if status["port"] else ""
            print(f"  {icon} {name}{port_info}: {status['message']}")
            if not status["healthy"]:
                all_healthy = False
        print()
        return 0 if all_healthy else 1

    await launcher.run_forever()
    return 0


def main() -> int:
    """Main entry point."""
    # Parse args first to check for health-check flag
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--health-check", action="store_true")
    known_args, _ = parser.parse_known_args()

    config = parse_args()

    try:
        return asyncio.run(main_async(config, health_check_only=known_args.health_check))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
