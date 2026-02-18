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
from typing import Any

from tools.context.core.manager import ContextManager
from tools.context.core.models import AllocationContext, ContextBundle, ContextLevel

logger = logging.getLogger(__name__)


@dataclass
class RoleContextConfig:
    """Configuration for a role's context needs."""

    role_id: str
    short_name: str
    primary_gates: list[str] = field(default_factory=list)
    context_level: ContextLevel = ContextLevel.MID
    include_git: bool = False
    include_issues: bool = True
    include_ledger: bool = True
    budget_chars: int = 12000
    sources_priority: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RoleContextConfig:
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
    task_id: str | None
    phase: str | None
    timestamp: datetime
    bundle_size_chars: int
    sources_included: list[str]
    context_level: str
    success: bool
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
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
        context_manager: ContextManager | None = None,
        config_path: Path | None = None,
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
        self._role_configs: dict[str, RoleContextConfig] = {}
        self._distribution_history: list[DistributionRecord] = []
        self._history_size = history_size
        self._active_distributions: dict[str, ContextBundle] = {}
        self._load_config()

    def _create_manager(self) -> ContextManager | None:
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

    def get_role_config(self, role_id: str) -> RoleContextConfig | None:
        """Get context configuration for a role."""
        return self._role_configs.get(role_id)

    def distribute(
        self,
        role_id: str,
        task_id: str | None = None,
        phase: str | None = None,
        force_refresh: bool = False,
    ) -> ContextBundle | None:
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

    def _extract_sources(self, bundle: ContextBundle) -> list[str]:
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
        task_id: str | None = None,
        phase: str | None = None,
        roles: list[str] | None = None,
    ) -> dict[str, ContextBundle | None]:
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
            seen: set[str] = set()
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
        role_id: str | None = None,
        limit: int = 20,
    ) -> list[DistributionRecord]:
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

    def get_active_distribution(self, role_id: str) -> ContextBundle | None:
        """Get currently cached context for a role."""
        for key, bundle in self._active_distributions.items():
            if key.startswith(f"{role_id}:"):
                return bundle
        return None

    def invalidate(self, role_id: str | None = None) -> int:
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

    def get_status(self) -> dict[str, Any]:
        """Get distributor status summary."""
        return {
            "configured_roles": len(
                {c.role_id for c in self._role_configs.values()}
            ),
            "active_distributions": len(self._active_distributions),
            "history_size": len(self._distribution_history),
            "context_manager_available": self._context_manager is not None,
            "recent_failures": sum(
                1 for r in self._distribution_history[-20:] if not r.success
            ),
        }


    def get_plan_context(self) -> dict[str, Any]:
        """Get current plan context from distribution config."""
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = json.load(f)
            return data.get("plan", {})
        except Exception as e:
            # GAP-PY-001: Config file may not exist yet
            logger.debug(f"Failed to load plan context: {e}")
            return {}

    def get_phase_ownership(self, phase: int) -> dict[str, Any]:
        """Get ownership info for a specific phase."""
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = json.load(f)
            ownership = data.get("phase_ownership", {})
            return ownership.get(str(phase), {})
        except Exception as e:
            # GAP-PY-001: Config file may not exist yet
            logger.debug(f"Failed to load phase ownership: {e}")
            return {}

    def get_role_for_current_phase(self) -> str | None:
        """Get the primary role for the current plan phase."""
        plan = self.get_plan_context()
        current_phase = plan.get("current_phase")
        if current_phase:
            ownership = self.get_phase_ownership(current_phase)
            return ownership.get("primary")
        return None

    def distribute_for_current_phase(
        self, force_refresh: bool = False
    ) -> dict[str, ContextBundle | None]:
        """
        Distribute context to all roles involved in the current phase.

        This is the main autonomous distribution method that:
        1. Reads the current phase from the plan
        2. Identifies primary, secondary, and validator roles
        3. Distributes appropriate context to each

        Returns:
            Dict mapping role_id to ContextBundle
        """
        plan = self.get_plan_context()
        current_phase = plan.get("current_phase", 1)
        current_task = plan.get("current_task")

        ownership = self.get_phase_ownership(current_phase)
        if not ownership:
            logger.warning("No ownership defined for phase %s", current_phase)
            return {}

        roles_to_distribute = []

        # Primary role always gets context
        primary = ownership.get("primary")
        if primary:
            roles_to_distribute.append(primary)

        # Secondary role gets context
        secondary = ownership.get("secondary")
        if secondary:
            roles_to_distribute.append(secondary)

        # Validator gets context
        validator = ownership.get("validator")
        if validator:
            roles_to_distribute.append(validator)

        # Overseer always gets context
        if "0" not in roles_to_distribute:
            roles_to_distribute.append("0")

        results = {}
        phase_name = ownership.get("name", f"Phase {current_phase}")

        for role_id in roles_to_distribute:
            if force_refresh:
                self.invalidate(role_id)
            results[role_id] = self.distribute(
                role_id=role_id,
                task_id=current_task,
                phase=phase_name,
            )

        logger.info(
            "Distributed context for phase %s to %d roles",
            current_phase,
            len(results),
        )

        return results

    def update_current_task(self, task_id: str) -> None:
        """
        Update the current task in the distribution config.

        This triggers automatic context refresh for affected roles.
        """
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = json.load(f)

            if "plan" not in data:
                data["plan"] = {}

            data["plan"]["current_task"] = task_id

            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Invalidate and redistribute
            self.invalidate()
            self.distribute_for_current_phase(force_refresh=True)

            logger.info(
                "Updated current task to %s and redistributed", task_id
            )

        except Exception as e:
            logger.error("Failed to update current task: %s", e)

    def advance_phase(self, new_phase: int) -> None:
        """
        Advance to a new phase and redistribute context.

        This triggers automatic context refresh for all affected roles.
        """
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = json.load(f)

            if "plan" not in data:
                data["plan"] = {}

            old_phase = data["plan"].get("current_phase", 0)
            data["plan"]["current_phase"] = new_phase
            data["plan"]["current_task"] = None  # Reset task on phase change

            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Invalidate all and redistribute
            self.invalidate()
            self.distribute_for_current_phase(force_refresh=True)

            logger.info(
                "Advanced from phase %s to phase %s and redistributed context",
                old_phase,
                new_phase,
            )

        except Exception as e:
            logger.error("Failed to advance phase: %s", e)

    def get_role_auto_context(self, role_id: str) -> dict[str, bool]:
        """Get auto-context flags for a role from distribution config."""
        try:
            with open(self._config_path, encoding="utf-8") as f:
                data = json.load(f)

            for role_data in data.get("roles", []):
                is_match = (
                    role_data.get("id") == role_id
                    or role_data.get("short_name") == role_id
                )
                if is_match:
                    return role_data.get("auto_context", {})

            return {}
        except Exception:
            return {}


# Global distributor instance
_global_distributor: ContextDistributor | None = None


def get_distributor() -> ContextDistributor:
    """Get or create global context distributor."""
    global _global_distributor
    if _global_distributor is None:
        _global_distributor = ContextDistributor()
    return _global_distributor


def distribute_to_role(
    role_id: str,
    task_id: str | None = None,
    phase: str | None = None,
) -> ContextBundle | None:
    """Convenience function to distribute context to a role."""
    return get_distributor().distribute(role_id, task_id, phase)


def distribute_for_phase() -> dict[str, ContextBundle | None]:
    """Convenience function to distribute context for the current phase."""
    return get_distributor().distribute_for_current_phase()


def update_task(task_id: str) -> None:
    """Convenience function to update current task and redistribute."""
    get_distributor().update_current_task(task_id)


def advance_to_phase(phase: int) -> None:
    """Convenience function to advance phase and redistribute."""
    get_distributor().advance_phase(phase)
