"""
Phase 8: Monitoring and Observability Module
Exports for the monitoring subsystem.
"""

from .apm.performance_monitor import (
    PerformanceMonitor,
    OperationType,
    OperationSpan,
    PerformanceStats,
    get_monitor,
    track,
)
from .metrics.metrics_collector import (
    MetricsCollector,
    MetricType,
    Counter,
    Gauge,
    Histogram,
    Timer,
    get_collector,
)
from .health.health_check import (
    HealthCheckService,
    HealthCheck,
    HealthCheckResult,
    HealthReport,
    HealthStatus,
    DiskHealthCheck,
    MemoryHealthCheck,
    EngineHealthCheck,
)
from .logging_config import (
    LogConfig,
    LogLevel,
    configure_logging,
    get_logger,
    setup_default_logging,
)
from .error_tracking import (
    ErrorTracker,
    TrackedError,
    ErrorSeverity,
    ErrorCategory,
    ErrorContext,
    ErrorStats,
    get_tracker,
    track_error,
)
from .alerting import (
    AlertManager,
    Alert,
    AlertCondition,
    AlertSeverity,
    AlertStatus,
    AlertChannel,
    LogAlertChannel,
    FileAlertChannel,
    create_default_conditions,
)
from .dashboard_data import (
    DashboardDataProvider,
    DashboardData,
    SystemMetrics,
    ApplicationMetrics,
)

__all__ = [
    # APM
    "PerformanceMonitor",
    "OperationType",
    "OperationSpan",
    "PerformanceStats",
    "get_monitor",
    "track",
    # Metrics
    "MetricsCollector",
    "MetricType",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "get_collector",
    # Health
    "HealthCheckService",
    "HealthCheck",
    "HealthCheckResult",
    "HealthReport",
    "HealthStatus",
    "DiskHealthCheck",
    "MemoryHealthCheck",
    "EngineHealthCheck",
    # Logging
    "LogConfig",
    "LogLevel",
    "configure_logging",
    "get_logger",
    "setup_default_logging",
    # Error Tracking
    "ErrorTracker",
    "TrackedError",
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorContext",
    "ErrorStats",
    "get_tracker",
    "track_error",
    # Alerting
    "AlertManager",
    "Alert",
    "AlertCondition",
    "AlertSeverity",
    "AlertStatus",
    "AlertChannel",
    "LogAlertChannel",
    "FileAlertChannel",
    "create_default_conditions",
    # Dashboard
    "DashboardDataProvider",
    "DashboardData",
    "SystemMetrics",
    "ApplicationMetrics",
]
