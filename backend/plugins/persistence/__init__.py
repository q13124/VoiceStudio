"""
Plugin Persistence Layer.

Provides SQLite-based persistence for plugin metrics and Phase 6 data.
"""

from backend.plugins.metrics.persistence import (
    AggregatedMetric,
    MetricRecord,
    MetricsPersistence,
    RetentionPolicy,
    get_metrics_persistence,
    reset_persistence,
)
from backend.plugins.persistence.phase6_persistence import (
    PersistedAnalyticsEvent,
    PersistedBaseline,
    PersistedConsentRecord,
    PersistedDataDeclaration,
    PersistedPluginMetrics,
    Phase6Persistence,
    get_phase6_persistence,
    reset_phase6_persistence,
)

__all__ = [
    "AggregatedMetric",
    "MetricRecord",
    # Original metrics persistence
    "MetricsPersistence",
    "PersistedAnalyticsEvent",
    "PersistedBaseline",
    "PersistedConsentRecord",
    "PersistedDataDeclaration",
    "PersistedPluginMetrics",
    # Phase 6 persistence
    "Phase6Persistence",
    "RetentionPolicy",
    "get_metrics_persistence",
    "get_phase6_persistence",
    "reset_persistence",
    "reset_phase6_persistence",
]
