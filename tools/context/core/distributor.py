"""
Context Distributor - Automatic role context assembly and distribution.

This module provides automatic context distribution to roles based on their
responsibilities, project state, and current tasks.

ADR-015: Integrated with ContextManager for budget-aware allocation.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from tools.context.core.manager import ContextManager
from tools.context.core.models import AllocationContext, ContextBundle, ContextLevel

logger = logging.getLogger(__name__)


@dataclass
class RoleContextConfig:
    """Configuration for a role's context needs."""

    role_id: str
    short_name: str
    primary_gates: List[str] = field(default_factory=list)
    context_level: ContextLevel = ContextLevel.MID
    include_git: bool = False
    include_issues: bool = True
    include_ledger: bool = True
    budget_chars: int = 12000
    sources_priority: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleContextConfig":
        """Create from dictionary."""
        return cls(
            role_id=data.get("id", ""),
            short_name=data.get("short_name", ""),
            primary_gates=data.get("primary_gates", []),
            context_level=ContextLevel(data.get("context_level", "mid")),
            include_git=data.get("include_git", False),
            include_issues=data.get("include_issues", True),
            include_ledger=data.get("include_ledger", True),
            budget_chars=data.get("budget_chars", 12000),
            sources_priority=data.get("sources_priority", []),
        )


@dataclass
class DistributionRecord:
    """Record of context distribution to a role."""

    role_id: str
    task_id: Optional[str]
    phase: Optional[str]
    timestamp: datetime
    bundle_size_chars: int
    sources_included: List[str]
    context_level: str
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role_id": self.role_id,
            "task_id": self.task_id,
            "phase": self.phase,
            "timestamp": self.timestamp.isoformat(),
            "bundle_size_chars": self.bundle_size_chars,
            "sources_included": self.sources_included,
            "context_level": self.context_level,
            "success": self.success,
            "error": self.error,
        }


class ContextDistributor:
    """
    Automatic context distribution to roles.

    Features:
    - Role-aware context assembly based on responsibilities
    - Budget-aware allocation via ContextManager
    - Distribution tracking and history
    - Automatic updates on state changes
    """

    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        config_path: Optional[Path] = None,
        history_size: int = 100,
    ):
        """
        Initialize context distributor.

        Args:
            context_manager: ContextManager instance (created if None)
            config_path: Path to role context config
            history_size: Max distribution records to keep
        """
        self._context_manager = context_manager or self._create_manager()
        self._config_path = config_path or Path("tools/context/config/distribution.json")
        self._role_configs: Dict[str, RoleContextConfig] = {}
        self._distribution_history: List[DistributionRecord] = []
        self._history_size = history_size
        self._active_distributions: Dict[str, ContextBundle] = {}
        self._load_config()

    def _create_manager(self) -> Optional[ContextManager]:
        """Create ContextManager with default config."""
        try:
            return ContextManager.from_config()
        except Exception as e:
            logger.warning("Failed to create ContextManager: %s", e)
            return None

    def _load_config(self) -> None:
        """Load role context configurations."""
        if not self._config_path.exists():
            # Load from roles config instead
            roles_path = Path("tools/onboarding/config/roles.json")
            if roles_path.exists():
                self._load_from_roles_config(roles_path)
            return

        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = json.load(f)

            for role_data in data.get("roles", []):
                config = RoleContextConfig.from_dict(role_data)
                self._role_configs[config.role_id] = config
                if config.short_name:
                    self._role_configs[config.short_name] = config

        except Exception as e:
            logger.warning("Failed to load distribution config: %s", e)

    def _load_from_roles_config(self, path: Path) -> None:
        """Load minimal config from onboarding roles.json."""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            for role_id, role_data in data.items():
                config = RoleContextConfig(
                    role_id=role_id,
                    short_name=role_data.get("short_name", ""),
                    primary_gates=role_data.get("primary_gates", []),
                    context_level=ContextLevel.MID,
                    include_git="git" in role_data.get("short_name", "").lower()
                    or role_id in ["2", "build-tooling"],
                )
                self._role_configs[role_id] = config
                if config.short_name:
                    self._role_configs[config.short_name] = config

        except Exception as e:
            logger.warning("Failed to load roles config: %s", e)

    def get_role_config(self, role_id: str) -> Optional[RoleContextConfig]:
        """Get context configuration for a role."""
        return self._role_configs.get(role_id)

    def distribute(
        self,
        role_id: str,
        task_id: Optional[str] = None,
        phase: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Optional[ContextBundle]:
        """
        Distribute context to a role.

        Args:
            role_id: Role ID or short name
            task_id: Optional task ID for context
            phase: Optional phase name
            force_refresh: Skip cache and reload

        Returns:
            ContextBundle for the role, or None on failure
        """
        if self._context_manager is None:
            logger.warning("ContextManager not available, cannot distribute")
            return None

        # Get role config
        role_config = self.get_role_config(role_id)
        if role_config is None:
            # Use default config
            role_config = RoleContextConfig(
                role_id=role_id,
                short_name=role_id,
            )

        # Check cache unless forced
        cache_key = f"{role_id}:{task_id}:{phase}"
        if not force_refresh and cache_key in self._active_distributions:
            return self._active_distributions[cache_key]

        # Build allocation context
        ctx = AllocationContext(
            task_id=task_id,
            phase=phase,
            role=role_config.short_name or role_id,
            include_git=role_config.include_git,
            budget_chars=role_config.budget_chars,
            max_level=role_config.context_level,
        )

        # Allocate context
        try:
            bundle = self._context_manager.allocate(ctx)

            # Record distribution
            sources = self._extract_sources(bundle)
            record = DistributionRecord(
                role_id=role_id,
                task_id=task_id,
                phase=phase,
                timestamp=datetime.now(),
                bundle_size_chars=len(bundle.to_json()),
                sources_included=sources,
                context_level=role_config.context_level.value,
                success=True,
            )
            self._add_record(record)

            # Cache
            self._active_distributions[cache_key] = bundle

            logger.info(
                "Distributed context to role %s: %d chars, %d sources",
                role_id,
                record.bundle_size_chars,
                len(sources),
            )

            return bundle

        except Exception as e:
            record = DistributionRecord(
                role_id=role_id,
                task_id=task_id,
                phase=phase,
                timestamp=datetime.now(),
                bundle_size_chars=0,
                sources_included=[],
                context_level=role_config.context_level.value,
                success=False,
                error=str(e),
            )
            self._add_record(record)
            logger.error("Failed to distribute context to role %s: %s", role_id, e)
            return None

    def _extract_sources(self, bundle: ContextBundle) -> List[str]:
        """Extract list of sources included in bundle."""
        sources = []
        if bundle.task and bundle.task.id:
            sources.append("task")
        if bundle.state and bundle.state.phase:
            sources.append("state")
        if bundle.brief:
            sources.append("brief")
        if bundle.rules:
            sources.append("rules")
        if bundle.memory:
            sources.append("memory")
        if bundle.git:
            sources.append("git")
        if bundle.ledger:
            sources.append("ledger")
        if bundle.telemetry:
            sources.append("telemetry")
        if bundle.proof_index:
            sources.append("proof_index")
        if bundle.progress:
            sources.append("progress")
        return sources

    def _add_record(self, record: DistributionRecord) -> None:
        """Add distribution record, maintaining history size limit."""
        self._distribution_history.append(record)
        if len(self._distribution_history) > self._history_size:
            self._distribution_history = self._distribution_history[-self._history_size :]

    def distribute_to_all(
        self,
        task_id: Optional[str] = None,
        phase: Optional[str] = None,
        roles: Optional[List[str]] = None,
    ) -> Dict[str, Optional[ContextBundle]]:
        """
        Distribute context to multiple roles.

        Args:
            task_id: Optional task ID
            phase: Optional phase name
            roles: List of role IDs (uses all configured if None)

        Returns:
            Dict mapping role_id to ContextBundle (or None on failure)
        """
        if roles is None:
            # Get unique role IDs (not aliases)
            seen: Set[str] = set()
            roles = []
            for config in self._role_configs.values():
                if config.role_id not in seen:
                    seen.add(config.role_id)
                    roles.append(config.role_id)

        results = {}
        for role_id in roles:
            results[role_id] = self.distribute(
                role_id=role_id,
                task_id=task_id,
                phase=phase,
            )

        return results

    def get_history(
        self,
        role_id: Optional[str] = None,
        limit: int = 20,
    ) -> List[DistributionRecord]:
        """
        Get distribution history.

        Args:
            role_id: Filter by role ID (all if None)
            limit: Max records to return

        Returns:
            List of distribution records
        """
        records = self._distribution_history
        if role_id:
            records = [r for r in records if r.role_id == role_id]
        return records[-limit:]

    def get_active_distribution(self, role_id: str) -> Optional[ContextBundle]:
        """Get currently cached context for a role."""
        for key, bundle in self._active_distributions.items():
            if key.startswith(f"{role_id}:"):
                return bundle
        return None

    def invalidate(self, role_id: Optional[str] = None) -> int:
        """
        Invalidate cached distributions.

        Args:
            role_id: Role to invalidate (all if None)

        Returns:
            Number of invalidated entries
        """
        if role_id is None:
            count = len(self._active_distributions)
            self._active_distributions.clear()
            return count

        to_remove = [
            key for key in self._active_distributions if key.startswith(f"{role_id}:")
        ]
        for key in to_remove:
            del self._active_distributions[key]
        return len(to_remove)

    def get_status(self) -> Dict[str, Any]:
        """Get distributor status summary."""
        return {
            "configured_roles": len(
                set(c.role_id for c in self._role_configs.values())
            ),
            "active_distributions": len(self._active_distributions),
            "history_size": len(self._distribution_history),
            "context_manager_available": self._context_manager is not None,
            "recent_failures": sum(
                1 for r in self._distribution_history[-20:] if not r.success
            ),
        }


# Global distributor instance
_global_distributor: Optional[ContextDistributor] = None


def get_distributor() -> ContextDistributor:
    """Get or create global context distributor."""
    global _global_distributor
    if _global_distributor is None:
        _global_distributor = ContextDistributor()
    return _global_distributor


def distribute_to_role(
    role_id: str,
    task_id: Optional[str] = None,
    phase: Optional[str] = None,
) -> Optional[ContextBundle]:
    """Convenience function to distribute context to a role."""
    return get_distributor().distribute(role_id, task_id, phase)
