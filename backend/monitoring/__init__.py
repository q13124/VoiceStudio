"""
Phase 8: Monitoring and Observability Module
Exports for the monitoring subsystem.
"""

from .alerting import (
    Alert,
    AlertChannel,
    AlertCondition,
    AlertManager,
    AlertSeverity,
    AlertStatus,
    FileAlertChannel,
    LogAlertChannel,
    create_default_conditions,
)
from .apm.performance_monitor import (
    OperationSpan,
    OperationType,
    PerformanceMonitor,
    PerformanceStats,
    get_monitor,
    track,
)
from .dashboard_data import (
    ApplicationMetrics,
    DashboardData,
    DashboardDataProvider,
    SystemMetrics,
)
from .error_tracking import (
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    ErrorStats,
    ErrorTracker,
    TrackedError,
    get_tracker,
    track_error,
)
from .health.health_check import (
    DiskHealthCheck,
    EngineHealthCheck,
    HealthCheck,
    HealthCheckResult,
    HealthCheckService,
    HealthReport,
    HealthStatus,
    MemoryHealthCheck,
)
from .logging_config import (
    LogConfig,
    LogLevel,
    configure_logging,
    get_logger,
    setup_default_logging,
)
from .metrics.metrics_collector import (
    Counter,
    Gauge,
    Histogram,
    MetricsCollector,
    MetricType,
    Timer,
    get_collector,
)

__all__ = [
    "Alert",
    "AlertChannel",
    "AlertCondition",
    # Alerting
    "AlertManager",
    "AlertSeverity",
    "AlertStatus",
    "ApplicationMetrics",
    "Counter",
    "DashboardData",
    # Dashboard
    "DashboardDataProvider",
    "DiskHealthCheck",
    "EngineHealthCheck",
    "ErrorCategory",
    "ErrorContext",
    "ErrorSeverity",
    "ErrorStats",
    # Error Tracking
    "ErrorTracker",
    "FileAlertChannel",
    "Gauge",
    "HealthCheck",
    "HealthCheckResult",
    # Health
    "HealthCheckService",
    "HealthReport",
    "HealthStatus",
    "Histogram",
    "LogAlertChannel",
    # Logging
    "LogConfig",
    "LogLevel",
    "MemoryHealthCheck",
    "MetricType",
    # Metrics
    "MetricsCollector",
    "OperationSpan",
    "OperationType",
    # APM
    "PerformanceMonitor",
    "PerformanceStats",
    "SystemMetrics",
    "Timer",
    "TrackedError",
    "configure_logging",
    "create_default_conditions",
    "get_collector",
    "get_logger",
    "get_monitor",
    "get_tracker",
    "setup_default_logging",
    "track",
    "track_error",
]
