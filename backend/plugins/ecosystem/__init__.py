"""
VoiceStudio Plugin System — Phase 6D: Ecosystem Growth & Analytics.

This module provides ecosystem growth tools including developer
analytics and featured plugin management.

See: docs/design/PLUGIN_PHASE6_STRATEGIC_MATURITY_PLAN.md
"""

from backend.plugins.ecosystem.developer_analytics import (
    DeveloperAnalytics,
    DeveloperStats,
    PluginMetrics,
)
from backend.plugins.ecosystem.featured_plugins import (
    FeaturedPlugin,
    FeaturedPluginsManager,
    FeatureReason,
)

__all__ = [
    "DeveloperAnalytics",
    "DeveloperStats",
    "FeatureReason",
    "FeaturedPlugin",
    "FeaturedPluginsManager",
    "PluginMetrics",
]
