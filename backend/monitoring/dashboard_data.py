"""
Phase 8: Dashboard Data Provider
Task 8.7: Data provider for monitoring dashboards.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import psutil

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """Current system metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    gpu_percent: float | None = None
    gpu_memory_mb: float | None = None


@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: datetime
    uptime_seconds: float
    active_sessions: int
    synthesis_queue_size: int
    synthesis_completed_total: int
    synthesis_failed_total: int
    engines_loaded: int
    requests_per_minute: float


@dataclass
class DashboardData:
    """Complete dashboard data."""
    system: SystemMetrics
    application: ApplicationMetrics
    active_alerts: int
    recent_errors: int
    health_status: str


class DashboardDataProvider:
    """Provider for dashboard metrics and data."""

    def __init__(self):
        self._start_time = datetime.now()
        self._synthesis_completed = 0
        self._synthesis_failed = 0
        self._request_times: list[datetime] = []
        self._active_sessions = 0

    async def get_dashboard_data(self) -> DashboardData:
        """Get complete dashboard data."""
        return DashboardData(
            system=await self.get_system_metrics(),
            application=await self.get_application_metrics(),
            active_alerts=0,
            recent_errors=0,
            health_status="healthy",
        )

    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_total_mb=memory.total / (1024 * 1024),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024 ** 3),
            disk_total_gb=disk.total / (1024 ** 3),
        )

        # Try to get GPU metrics
        try:
            import torch
            if torch.cuda.is_available():
                metrics.gpu_memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
        except ImportError:
            logger.debug("PyTorch not available for GPU memory metrics")

        return metrics

    async def get_application_metrics(self) -> ApplicationMetrics:
        """Get application metrics."""
        uptime = (datetime.now() - self._start_time).total_seconds()

        # Calculate requests per minute
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        recent_requests = [t for t in self._request_times if t >= cutoff]
        rpm = len(recent_requests)

        return ApplicationMetrics(
            timestamp=datetime.now(),
            uptime_seconds=uptime,
            active_sessions=self._active_sessions,
            synthesis_queue_size=0,
            synthesis_completed_total=self._synthesis_completed,
            synthesis_failed_total=self._synthesis_failed,
            engines_loaded=0,
            requests_per_minute=rpm,
        )

    async def get_historical_metrics(
        self,
        metric_name: str,
        period_hours: int = 24,
        resolution_minutes: int = 5
    ) -> list[tuple[datetime, float]]:
        """Get historical metrics data."""
        # Placeholder - would query from metrics storage
        return []

    def record_request(self) -> None:
        """Record an API request."""
        now = datetime.now()
        self._request_times.append(now)

        # Trim old entries
        cutoff = now - timedelta(hours=1)
        self._request_times = [t for t in self._request_times if t >= cutoff]

    def record_synthesis(self, success: bool) -> None:
        """Record a synthesis operation."""
        if success:
            self._synthesis_completed += 1
        else:
            self._synthesis_failed += 1

    def set_active_sessions(self, count: int) -> None:
        """Set the number of active sessions."""
        self._active_sessions = count
