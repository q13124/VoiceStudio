#!/usr/bin/env python3
"""
Context System Progress Dashboard CLI.

Displays progress metrics for the context management system across roles,
adapters, sources, and integration points.

Usage:
    python -m tools.context.cli.dashboard              # ASCII table output
    python -m tools.context.cli.dashboard --json       # JSON output
    python -m tools.context.cli.dashboard --csv        # CSV output
    python -m tools.context.cli.dashboard --detailed   # Detailed breakdown
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.context.core.manager import ContextManager
from tools.context.core.registry import SourceRegistry
from tools.context.sources.base import get_source_telemetry

logger = logging.getLogger(__name__)


@dataclass
class RoleProgress:
    """Progress metrics for a single role."""
    role_name: str
    role_id: int
    config_exists: bool
    sources_configured: int
    sources_healthy: int
    last_allocation: Optional[str] = None
    total_allocations: int = 0
    avg_allocation_time_ms: float = 0.0


@dataclass
class SourceProgress:
    """Progress metrics for a single source adapter."""
    source_name: str
    adapter_class: str
    is_healthy: bool
    total_fetches: int
    failure_rate: float
    avg_fetch_time_ms: float
    offline_capable: bool
    last_error: Optional[str] = None


@dataclass
class IntegrationProgress:
    """Progress metrics for an integration point."""
    integration_name: str
    status: str  # 'ready', 'partial', 'missing'
    components_total: int
    components_ready: int
    notes: List[str] = field(default_factory=list)


@dataclass
class DashboardMetrics:
    """Complete dashboard metrics."""
    timestamp: str
    overall_progress_pct: float
    roles: List[RoleProgress]
    sources: List[SourceProgress]
    integrations: List[IntegrationProgress]
    warnings: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "overall_progress_pct": round(self.overall_progress_pct, 1),
            "roles": [
                {
                    "role_name": r.role_name,
                    "role_id": r.role_id,
                    "config_exists": r.config_exists,
                    "sources_configured": r.sources_configured,
                    "sources_healthy": r.sources_healthy,
                    "total_allocations": r.total_allocations,
                }
                for r in self.roles
            ],
            "sources": [
                {
                    "source_name": s.source_name,
                    "adapter_class": s.adapter_class,
                    "is_healthy": s.is_healthy,
                    "total_fetches": s.total_fetches,
                    "failure_rate": round(s.failure_rate, 1),
                    "avg_fetch_time_ms": round(s.avg_fetch_time_ms, 2),
                    "offline_capable": s.offline_capable,
                }
                for s in self.sources
            ],
            "integrations": [
                {
                    "integration_name": i.integration_name,
                    "status": i.status,
                    "components_total": i.components_total,
                    "components_ready": i.components_ready,
                    "progress_pct": round(i.components_ready / max(1, i.components_total) * 100, 1),
                }
                for i in self.integrations
            ],
            "warnings": self.warnings,
        }


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def collect_role_progress(config_dir: Path) -> List[RoleProgress]:
    """Collect progress metrics for all configured roles."""
    roles = []
    role_configs = sorted(config_dir.glob("roles/*.json"))
    
    # Define known roles
    known_roles = [
        (0, "overseer"),
        (1, "system-architect"),
        (2, "build-tooling"),
        (3, "ui-engineer"),
        (4, "core-platform"),
        (5, "engine-engineer"),
        (6, "release-engineer"),
        (7, "debug-agent"),
    ]
    
    for role_id, role_name in known_roles:
        config_file = config_dir / "roles" / f"{role_name}.json"
        config_exists = config_file.exists()
        
        sources_configured = 0
        if config_exists:
            try:
                with open(config_file) as f:
                    role_config = json.load(f)
                sources_configured = len(role_config.get("sources", []))
            except Exception:
                pass
        
        roles.append(RoleProgress(
            role_name=role_name,
            role_id=role_id,
            config_exists=config_exists,
            sources_configured=sources_configured,
            sources_healthy=sources_configured,  # Assume healthy until checked
        ))
    
    return roles


def collect_source_progress(registry: SourceRegistry) -> List[SourceProgress]:
    """Collect progress metrics for all source adapters."""
    sources = []
    telemetry = get_source_telemetry()
    
    for source in registry.all():
        health = telemetry.sources.get(source.source_name)
        
        sources.append(SourceProgress(
            source_name=source.source_name,
            adapter_class=source.__class__.__name__,
            is_healthy=health.is_healthy if health else True,
            total_fetches=health.total_fetches if health else 0,
            failure_rate=health.total_failures / max(1, health.total_fetches) * 100 if health else 0,
            avg_fetch_time_ms=health.avg_fetch_time_ms if health else 0,
            offline_capable=getattr(source, 'offline', True),
            last_error=health.last_error if health else None,
        ))
    
    return sources


def collect_integration_progress() -> List[IntegrationProgress]:
    """Collect progress metrics for integration points."""
    integrations = []
    
    # Check onboarding integration
    onboarding_components = [
        ("generate_onboarding.py", Path("tools/context/scripts/generate_onboarding.py").exists()),
        ("role_configs", Path("tools/context/config/roles").exists()),
        ("PART_formatter", True),  # Part of core models
    ]
    onboarding_ready = sum(1 for _, exists in onboarding_components if exists)
    integrations.append(IntegrationProgress(
        integration_name="Onboarding System",
        status="ready" if onboarding_ready == len(onboarding_components) else "partial",
        components_total=len(onboarding_components),
        components_ready=onboarding_ready,
    ))
    
    # Check handoff integration
    handoff_components = [
        ("HandoffQueue", True),  # In core models
        ("IssueStore", True),  # In core models
        ("distributor", Path("tools/context/core/distributor.py").exists()),
    ]
    handoff_ready = sum(1 for _, exists in handoff_components if exists)
    integrations.append(IntegrationProgress(
        integration_name="Handoff System",
        status="ready" if handoff_ready == len(handoff_components) else "partial",
        components_total=len(handoff_components),
        components_ready=handoff_ready,
    ))
    
    # Check STATE.md integration
    state_components = [
        ("state_adapter", Path("tools/context/sources/state_adapter.py").exists()),
        ("StateContext_model", True),
        ("proof_index_parser", True),
    ]
    state_ready = sum(1 for _, exists in state_components if exists)
    integrations.append(IntegrationProgress(
        integration_name="STATE.md Integration",
        status="ready" if state_ready == len(state_components) else "partial",
        components_total=len(state_components),
        components_ready=state_ready,
    ))
    
    # Check OpenMemory integration
    memory_components = [
        ("memory_adapter", Path("tools/context/sources/memory_adapter.py").exists()),
        ("vector_memory_adapter", Path("tools/context/sources/vector_memory_adapter.py").exists()),
        ("MemoryItem_model", True),
    ]
    memory_ready = sum(1 for _, exists in memory_components if exists)
    integrations.append(IntegrationProgress(
        integration_name="OpenMemory Integration",
        status="ready" if memory_ready == len(memory_components) else "partial",
        components_total=len(memory_components),
        components_ready=memory_ready,
    ))
    
    return integrations


def collect_warnings(roles: List[RoleProgress], sources: List[SourceProgress]) -> List[str]:
    """Collect any warnings about the system state."""
    warnings = []
    
    # Check for missing role configs
    missing_roles = [r.role_name for r in roles if not r.config_exists]
    if missing_roles:
        warnings.append(f"Missing role configs: {', '.join(missing_roles)}")
    
    # Check for unhealthy sources
    unhealthy = [s.source_name for s in sources if not s.is_healthy]
    if unhealthy:
        warnings.append(f"Unhealthy sources: {', '.join(unhealthy)}")
    
    # Check for high failure rates
    high_failure = [s.source_name for s in sources if s.failure_rate > 20]
    if high_failure:
        warnings.append(f"High failure rate (>20%): {', '.join(high_failure)}")
    
    return warnings


def collect_dashboard_metrics(manager: ContextManager) -> DashboardMetrics:
    """Collect all dashboard metrics."""
    config_dir = Path("tools/context/config")
    
    roles = collect_role_progress(config_dir)
    sources = collect_source_progress(manager.registry)
    integrations = collect_integration_progress()
    warnings = collect_warnings(roles, sources)
    
    # Calculate overall progress
    role_pct = sum(1 for r in roles if r.config_exists) / max(1, len(roles)) * 100
    source_pct = sum(1 for s in sources if s.is_healthy) / max(1, len(sources)) * 100
    integration_pct = sum(i.components_ready for i in integrations) / max(1, sum(i.components_total for i in integrations)) * 100
    overall_pct = (role_pct + source_pct + integration_pct) / 3
    
    return DashboardMetrics(
        timestamp=datetime.now().isoformat(),
        overall_progress_pct=overall_pct,
        roles=roles,
        sources=sources,
        integrations=integrations,
        warnings=warnings,
    )


def render_ascii(metrics: DashboardMetrics, detailed: bool = False) -> str:
    """Render metrics as ASCII table."""
    lines = []
    
    lines.append("")
    lines.append("=" * 70)
    lines.append("  CONTEXT SYSTEM PROGRESS DASHBOARD")
    lines.append("=" * 70)
    lines.append("")
    
    # Overall progress
    pct = metrics.overall_progress_pct
    bar_width = 40
    filled = int(pct / 100 * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    color = "\033[92m" if pct >= 80 else "\033[93m" if pct >= 50 else "\033[91m"
    reset = "\033[0m"
    lines.append(f"Overall Progress: {color}[{bar}] {pct:.1f}%{reset}")
    lines.append(f"Timestamp: {metrics.timestamp}")
    lines.append("")
    
    # Warnings
    if metrics.warnings:
        lines.append("\033[93m⚠ Warnings:\033[0m")
        for warning in metrics.warnings:
            lines.append(f"  - {warning}")
        lines.append("")
    
    # Roles section
    lines.append("-" * 70)
    lines.append("ROLES")
    lines.append("-" * 70)
    lines.append(f"{'Role':<20} {'ID':<4} {'Config':<8} {'Sources':<10}")
    lines.append("-" * 70)
    for role in metrics.roles:
        config_status = "\033[92m✓\033[0m" if role.config_exists else "\033[91m✗\033[0m"
        lines.append(f"{role.role_name:<20} {role.role_id:<4} {config_status:<8} {role.sources_configured:<10}")
    lines.append("")
    
    # Sources section
    lines.append("-" * 70)
    lines.append("SOURCE ADAPTERS")
    lines.append("-" * 70)
    lines.append(f"{'Source':<20} {'Healthy':<8} {'Fetches':<10} {'Fail%':<8} {'Offline':<8}")
    lines.append("-" * 70)
    for source in metrics.sources:
        healthy_icon = "\033[92m✓\033[0m" if source.is_healthy else "\033[91m✗\033[0m"
        offline_icon = "✓" if source.offline_capable else "-"
        lines.append(f"{source.source_name:<20} {healthy_icon:<8} {source.total_fetches:<10} {source.failure_rate:<8.1f} {offline_icon:<8}")
    lines.append("")
    
    # Integrations section
    lines.append("-" * 70)
    lines.append("INTEGRATIONS")
    lines.append("-" * 70)
    lines.append(f"{'Integration':<25} {'Status':<10} {'Progress':<15}")
    lines.append("-" * 70)
    for integration in metrics.integrations:
        status_color = "\033[92m" if integration.status == "ready" else "\033[93m" if integration.status == "partial" else "\033[91m"
        reset = "\033[0m"
        progress = f"{integration.components_ready}/{integration.components_total}"
        lines.append(f"{integration.integration_name:<25} {status_color}{integration.status:<10}{reset} {progress:<15}")
    lines.append("")
    
    if detailed:
        lines.append("-" * 70)
        lines.append("DETAILED SOURCE METRICS")
        lines.append("-" * 70)
        for source in metrics.sources:
            lines.append(f"\n{source.source_name} ({source.adapter_class}):")
            lines.append(f"  Total fetches: {source.total_fetches}")
            lines.append(f"  Failure rate: {source.failure_rate:.1f}%")
            lines.append(f"  Avg fetch time: {source.avg_fetch_time_ms:.2f}ms")
            lines.append(f"  Offline capable: {source.offline_capable}")
            if source.last_error:
                lines.append(f"  Last error: {source.last_error[:60]}...")
        lines.append("")
    
    return "\n".join(lines)


def render_json(metrics: DashboardMetrics) -> str:
    """Render metrics as JSON."""
    return json.dumps(metrics.to_dict(), indent=2)


def render_csv(metrics: DashboardMetrics) -> str:
    """Render metrics as CSV."""
    output = io.StringIO()
    
    # Write sources CSV
    writer = csv.writer(output)
    writer.writerow(["Type", "Name", "Status", "Metric1", "Metric2", "Metric3"])
    
    for role in metrics.roles:
        writer.writerow([
            "role",
            role.role_name,
            "configured" if role.config_exists else "missing",
            role.sources_configured,
            role.role_id,
            "",
        ])
    
    for source in metrics.sources:
        writer.writerow([
            "source",
            source.source_name,
            "healthy" if source.is_healthy else "unhealthy",
            source.total_fetches,
            f"{source.failure_rate:.1f}%",
            f"{source.avg_fetch_time_ms:.2f}ms",
        ])
    
    for integration in metrics.integrations:
        writer.writerow([
            "integration",
            integration.integration_name,
            integration.status,
            integration.components_ready,
            integration.components_total,
            f"{integration.components_ready / max(1, integration.components_total) * 100:.1f}%",
        ])
    
    return output.getvalue()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Display context system progress dashboard"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output as CSV",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed metrics",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config file",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        if args.config:
            manager = ContextManager.from_config(args.config)
        else:
            manager = ContextManager.from_config()
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "success": False}))
        elif args.csv:
            print("error,message")
            print(f"initialization_error,{str(e)}")
        else:
            print(f"ERROR: Failed to initialize context manager: {e}")
        return 1

    metrics = collect_dashboard_metrics(manager)
    
    if args.json:
        print(render_json(metrics))
    elif args.csv:
        print(render_csv(metrics))
    else:
        print(render_ascii(metrics, detailed=args.detailed))
    
    # Return exit code based on progress
    return 0 if metrics.overall_progress_pct >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
