from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from tools.context.core.allocator import ContextAllocator
from tools.context.core.exceptions import ConfigValidationError, SourceFetchError
from tools.context.core.models import (
    AllocationContext,
    BudgetConstraints,
    ContextBundle,
    SourceResult,
)
from tools.context.core.registry import SourceRegistry, build_default_registry
from tools.context.infra.cache import InMemoryCache
from tools.context.infra.validation import validate_config

if TYPE_CHECKING:
    from tools.overseer.agent.registry import AgentRegistry

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path("tools/context/config/context-sources.json")


class ContextManager:
    """Facade for assembling context bundles."""

    def __init__(
        self,
        config: dict,
        registry: SourceRegistry,
        allocator: ContextAllocator | None = None,
        cache_ttl_seconds: int = 60,
        agent_registry: Optional["AgentRegistry"] = None,
    ):
        self.config = config
        self.registry = registry
        self.allocator = allocator or ContextAllocator()
        self.cache = InMemoryCache(max_entries=16)
        self.cache_ttl_seconds = cache_ttl_seconds
        self._agent_registry = agent_registry

    @classmethod
    def from_config(cls, config_path: Path = DEFAULT_CONFIG_PATH) -> "ContextManager":
        config = _load_config(config_path)
        errors = validate_config(config)
        if errors:
            raise ConfigValidationError(errors)
        registry = build_default_registry(config)
        return cls(config=config, registry=registry)

    def _build_budget(self, context: AllocationContext) -> BudgetConstraints:
        base_budgets = dict(self.config.get("budgets", {}))
        base_weights = dict(self.config.get("weights", {}))

        role_profiles = self.config.get("roles", {})
        if context.role and context.role in role_profiles:
            profile = role_profiles[context.role]
            base_budgets.update(profile.get("budgets", {}))
            base_weights.update(profile.get("weights", {}))

        total = int(base_budgets.get("total_chars", context.budget_chars))
        source_limits = {
            "state": int(base_budgets.get("state_chars", 2000)),
            "task": int(base_budgets.get("task_chars", 2000)),
            "brief": int(base_budgets.get("brief_chars", 3000)),
            "ledger": int(base_budgets.get("ledger_chars", 2500)),
            "rules": int(base_budgets.get("rules_chars", 2000)),
            "memory": int(base_budgets.get("memory_chars", 2000)),
            "telemetry": int(base_budgets.get("telemetry_chars", 1000)),
            "git": int(base_budgets.get("git_chars", 1000)),
        }
        priority_order = sorted(base_weights.keys(), key=lambda k: base_weights[k], reverse=True)
        return BudgetConstraints(total_chars=total, source_limits=source_limits, priority_order=priority_order)

    def _validate_agent_if_enabled(self, ctx: AllocationContext) -> None:
        """Optional: validate/lookup agent in registry when role is set (ADR-015). Does not block."""
        if not ctx.role or not self._agent_registry:
            return
        try:
            from tools.overseer.agent.role_mapping import role_to_agent_role
            from tools.overseer.agent.identity import AgentState
            ar = role_to_agent_role(ctx.role)
            agents = self._agent_registry.get_by_role(ar)
            if agents and not any(a.is_active() for a in agents):
                logger.debug("Context allocation: no active agent for role %s", ctx.role)
        except Exception as e:
            logger.debug("Context Manager agent registry lookup skipped: %s", e)

    def allocate(self, context: AllocationContext | None = None) -> ContextBundle:
        ctx = context or AllocationContext(
            task_id=None,
            phase=None,
            role=None,
            include_git=False,
            budget_chars=self.config.get("budgets", {}).get("total_chars", 12000),
        )

        self._validate_agent_if_enabled(ctx)

        cache_key = f"{ctx.task_id}:{ctx.phase}:{ctx.role}:{ctx.include_git}:{ctx.budget_chars}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        results: List[SourceResult] = []
        for source in self.registry.all():
            try:
                results.append(source.fetch(ctx))
            except Exception as exc:
                results.append(
                    SourceResult(
                        source_name=source.source_name,
                        success=False,
                        data={},
                        size_chars=0,
                        fetch_time_ms=0,
                        error=str(exc),
                    )
                )

        budget = self._build_budget(ctx)
        bundle = self.allocator.allocate(results, budget)
        self.cache.put(cache_key, bundle, ttl_seconds=self.cache_ttl_seconds)
        return bundle


def _load_config(path: Path) -> Dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    roles_dir = path.parent / "roles"
    if roles_dir.exists():
        config["roles"] = config.get("roles") or {}
        for f in sorted(roles_dir.glob("*.json")):
            try:
                config["roles"][f.stem] = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                pass
    return config
