"""
Phase 7: System Diagnostics
Task 7.7: System diagnostics and health checks.
"""

from __future__ import annotations

import json
import logging
import platform
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class DiagnosticStatus(Enum):
    """Status of a diagnostic check."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


class DiagnosticCategory(Enum):
    """Categories of diagnostic checks."""

    SYSTEM = "system"
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    STORAGE = "storage"
    APPLICATION = "application"


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""

    name: str
    category: DiagnosticCategory
    status: DiagnosticStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    recommendation: str | None = None


@dataclass
class SystemInfo:
    """System information."""

    os_name: str
    os_version: str
    os_build: str
    architecture: str
    hostname: str
    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    ram_total_gb: float
    ram_available_gb: float
    gpu_name: str | None = None
    gpu_memory_gb: float | None = None
    python_version: str = ""
    app_version: str = ""


@dataclass
class DiagnosticsReport:
    """Complete diagnostics report."""

    timestamp: datetime
    system_info: SystemInfo
    results: list[DiagnosticResult]
    overall_status: DiagnosticStatus
    duration_seconds: float


class SystemDiagnostics:
    """Service for running system diagnostics."""

    MIN_RAM_GB = 8
    MIN_DISK_GB = 10
    MIN_PYTHON_VERSION = (3, 10)

    def __init__(self, app_path: Path | None = None):
        self._app_path = app_path or Path.cwd()

    async def run_diagnostics(self) -> DiagnosticsReport:
        """Run all diagnostic checks."""
        start_time = datetime.now()

        # Get system info
        system_info = self._get_system_info()

        # Run checks
        results = []

        # System checks
        results.extend(await self._check_system())

        # Hardware checks
        results.extend(await self._check_hardware())

        # Software checks
        results.extend(await self._check_software())

        # Storage checks
        results.extend(await self._check_storage())

        # Application checks
        results.extend(await self._check_application())

        # Determine overall status
        overall_status = DiagnosticStatus.PASS
        for result in results:
            if result.status == DiagnosticStatus.FAIL:
                overall_status = DiagnosticStatus.FAIL
                break
            elif result.status == DiagnosticStatus.WARN and overall_status != DiagnosticStatus.FAIL:
                overall_status = DiagnosticStatus.WARN

        duration = (datetime.now() - start_time).total_seconds()

        return DiagnosticsReport(
            timestamp=datetime.now(),
            system_info=system_info,
            results=results,
            overall_status=overall_status,
            duration_seconds=duration,
        )

    def _get_system_info(self) -> SystemInfo:
        """Get system information."""
        ram = psutil.virtual_memory()

        # Try to get GPU info
        gpu_name = None
        gpu_memory = None

        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        except ImportError:
            logger.debug("PyTorch not available for GPU info detection")

        return SystemInfo(
            os_name=platform.system(),
            os_version=platform.version(),
            os_build=platform.release(),
            architecture=platform.machine(),
            hostname=platform.node(),
            cpu_model=platform.processor() or "Unknown",
            cpu_cores=psutil.cpu_count(logical=False) or 1,
            cpu_threads=psutil.cpu_count(logical=True) or 1,
            ram_total_gb=ram.total / (1024**3),
            ram_available_gb=ram.available / (1024**3),
            gpu_name=gpu_name,
            gpu_memory_gb=gpu_memory,
            python_version=platform.python_version(),
            app_version="1.0.0",
        )

    async def _check_system(self) -> list[DiagnosticResult]:
        """Run system checks."""
        results = []

        # Windows version check
        if platform.system() == "Windows":
            version = platform.release()
            if version in ("10", "11"):
                results.append(
                    DiagnosticResult(
                        name="Windows Version",
                        category=DiagnosticCategory.SYSTEM,
                        status=DiagnosticStatus.PASS,
                        message=f"Windows {version} detected",
                        details={"version": version},
                    )
                )
            else:
                results.append(
                    DiagnosticResult(
                        name="Windows Version",
                        category=DiagnosticCategory.SYSTEM,
                        status=DiagnosticStatus.WARN,
                        message=f"Windows {version} may not be fully supported",
                        recommendation="Consider upgrading to Windows 10 or 11",
                    )
                )

        # Architecture check
        arch = platform.machine().lower()
        if "amd64" in arch or "x86_64" in arch:
            results.append(
                DiagnosticResult(
                    name="Architecture",
                    category=DiagnosticCategory.SYSTEM,
                    status=DiagnosticStatus.PASS,
                    message="64-bit system detected",
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="Architecture",
                    category=DiagnosticCategory.SYSTEM,
                    status=DiagnosticStatus.FAIL,
                    message=f"32-bit system ({arch}) not supported",
                    recommendation="VoiceStudio requires a 64-bit system",
                )
            )

        return results

    async def _check_hardware(self) -> list[DiagnosticResult]:
        """Run hardware checks."""
        results = []

        # RAM check
        ram = psutil.virtual_memory()
        ram_gb = ram.total / (1024**3)

        if ram_gb >= self.MIN_RAM_GB:
            results.append(
                DiagnosticResult(
                    name="RAM",
                    category=DiagnosticCategory.HARDWARE,
                    status=DiagnosticStatus.PASS,
                    message=f"{ram_gb:.1f} GB RAM available",
                    details={"total_gb": ram_gb, "available_gb": ram.available / (1024**3)},
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="RAM",
                    category=DiagnosticCategory.HARDWARE,
                    status=DiagnosticStatus.WARN,
                    message=f"Only {ram_gb:.1f} GB RAM (recommended: {self.MIN_RAM_GB} GB)",
                    recommendation=f"Consider upgrading to at least {self.MIN_RAM_GB} GB RAM",
                )
            )

        # GPU check
        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)

                results.append(
                    DiagnosticResult(
                        name="GPU (CUDA)",
                        category=DiagnosticCategory.HARDWARE,
                        status=DiagnosticStatus.PASS,
                        message=f"{gpu_name} ({gpu_memory:.1f} GB VRAM)",
                        details={"name": gpu_name, "vram_gb": gpu_memory},
                    )
                )
            else:
                results.append(
                    DiagnosticResult(
                        name="GPU (CUDA)",
                        category=DiagnosticCategory.HARDWARE,
                        status=DiagnosticStatus.WARN,
                        message="No CUDA-compatible GPU detected",
                        recommendation="GPU acceleration is recommended for faster synthesis",
                    )
                )
        except ImportError:
            results.append(
                DiagnosticResult(
                    name="GPU (CUDA)",
                    category=DiagnosticCategory.HARDWARE,
                    status=DiagnosticStatus.SKIP,
                    message="PyTorch not installed, cannot check GPU",
                )
            )

        return results

    async def _check_software(self) -> list[DiagnosticResult]:
        """Run software checks."""
        results = []

        # Python version check
        py_version = tuple(map(int, platform.python_version().split(".")[:2]))

        if py_version >= self.MIN_PYTHON_VERSION:
            results.append(
                DiagnosticResult(
                    name="Python Version",
                    category=DiagnosticCategory.SOFTWARE,
                    status=DiagnosticStatus.PASS,
                    message=f"Python {platform.python_version()}",
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="Python Version",
                    category=DiagnosticCategory.SOFTWARE,
                    status=DiagnosticStatus.FAIL,
                    message=f"Python {platform.python_version()} is too old",
                    recommendation=f"Please upgrade to Python {'.'.join(map(str, self.MIN_PYTHON_VERSION))} or later",
                )
            )

        # FFmpeg check
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            results.append(
                DiagnosticResult(
                    name="FFmpeg",
                    category=DiagnosticCategory.SOFTWARE,
                    status=DiagnosticStatus.PASS,
                    message="FFmpeg is installed",
                    details={"path": ffmpeg_path},
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="FFmpeg",
                    category=DiagnosticCategory.SOFTWARE,
                    status=DiagnosticStatus.WARN,
                    message="FFmpeg not found in PATH",
                    recommendation="Install FFmpeg for audio format conversion",
                )
            )

        return results

    async def _check_storage(self) -> list[DiagnosticResult]:
        """Run storage checks."""
        results = []

        # App directory storage
        disk = psutil.disk_usage(str(self._app_path))
        free_gb = disk.free / (1024**3)

        if free_gb >= self.MIN_DISK_GB:
            results.append(
                DiagnosticResult(
                    name="Disk Space",
                    category=DiagnosticCategory.STORAGE,
                    status=DiagnosticStatus.PASS,
                    message=f"{free_gb:.1f} GB free space",
                    details={"free_gb": free_gb, "total_gb": disk.total / (1024**3)},
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="Disk Space",
                    category=DiagnosticCategory.STORAGE,
                    status=DiagnosticStatus.WARN,
                    message=f"Only {free_gb:.1f} GB free (recommended: {self.MIN_DISK_GB} GB)",
                    recommendation="Free up disk space for models and projects",
                )
            )

        # Models directory
        models_path = self._app_path / "models"
        if models_path.exists():
            model_count = len(list(models_path.glob("*")))
            results.append(
                DiagnosticResult(
                    name="Models Directory",
                    category=DiagnosticCategory.STORAGE,
                    status=DiagnosticStatus.PASS,
                    message=f"Models directory exists ({model_count} items)",
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="Models Directory",
                    category=DiagnosticCategory.STORAGE,
                    status=DiagnosticStatus.WARN,
                    message="Models directory not found",
                    recommendation="Models will be downloaded on first use",
                )
            )

        return results

    async def _check_application(self) -> list[DiagnosticResult]:
        """Run application checks."""
        results = []

        # Config file
        config_path = self._app_path / "config" / "settings.json"
        if config_path.exists():
            results.append(
                DiagnosticResult(
                    name="Configuration",
                    category=DiagnosticCategory.APPLICATION,
                    status=DiagnosticStatus.PASS,
                    message="Configuration file exists",
                )
            )
        else:
            results.append(
                DiagnosticResult(
                    name="Configuration",
                    category=DiagnosticCategory.APPLICATION,
                    status=DiagnosticStatus.WARN,
                    message="Configuration file not found",
                    recommendation="Default settings will be used",
                )
            )

        return results

    def export_report(self, report: DiagnosticsReport, path: Path) -> None:
        """Export diagnostics report to file."""
        data = {
            "timestamp": report.timestamp.isoformat(),
            "overall_status": report.overall_status.value,
            "duration_seconds": report.duration_seconds,
            "system_info": {
                "os_name": report.system_info.os_name,
                "os_version": report.system_info.os_version,
                "architecture": report.system_info.architecture,
                "cpu_model": report.system_info.cpu_model,
                "cpu_cores": report.system_info.cpu_cores,
                "ram_total_gb": report.system_info.ram_total_gb,
                "gpu_name": report.system_info.gpu_name,
                "python_version": report.system_info.python_version,
            },
            "results": [
                {
                    "name": r.name,
                    "category": r.category.value,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details,
                    "recommendation": r.recommendation,
                }
                for r in report.results
            ],
        }

        path.write_text(json.dumps(data, indent=2))
