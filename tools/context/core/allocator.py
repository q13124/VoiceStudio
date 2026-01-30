from __future__ import annotations

import json
from typing import Any, Dict, List

from tools.context.core.models import (
    AllocationContext,
    BudgetConstraints,
    ContextBundle,
    GitContext,
    MemoryItem,
    RuleContext,
    SourceResult,
    StateContext,
    TaskContext,
)
from tools.context.core.protocols import AllocatorProtocol


def _truncate_text(text: str | None, limit: int) -> str | None:
    if text is None or limit <= 0:
        return text
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


def _string_size(data) -> int:
    try:
        return len(json.dumps(data, ensure_ascii=False))
    except Exception:
        return len(str(data))


class ContextAllocator(AllocatorProtocol):
    """Priority-aware allocator with budget enforcement."""

    def allocate(self, sources: List[SourceResult], budget: BudgetConstraints) -> ContextBundle:
        # Sort by source priority order if provided, else keep input order.
        priority_order = budget.priority_order or []
        order_map = {name: idx for idx, name in enumerate(priority_order)}
        ordered = sorted(
            sources,
            key=lambda s: order_map.get(s.source_name, len(order_map)),
        )

        bundle = ContextBundle()
        for result in ordered:
            if not result.success:
                continue
            data = result.data
            if not isinstance(data, dict):
                continue
            if "task" in data and isinstance(data["task"], TaskContext) and not bundle.task.id:
                bundle.task = data["task"]
            if "state" in data and isinstance(data["state"], StateContext):
                bundle.state = data["state"]
            if "brief" in data and data["brief"] and bundle.brief is None:
                bundle.brief = data["brief"]
            if "rules" in data and isinstance(data["rules"], list) and not bundle.rules:
                bundle.rules = data["rules"]
            if "memory" in data and isinstance(data["memory"], list):
                bundle.memory = (bundle.memory or []) + data["memory"]
            if "git" in data and isinstance(data["git"], GitContext) and bundle.git is None:
                bundle.git = data["git"]
            if "ledger" in data and isinstance(data.get("ledger"), list) and bundle.ledger is None:
                bundle.ledger = data["ledger"]
                if "ledger_context" in data and isinstance(data["ledger_context"], str):
                    bundle.meta["ledger_context"] = data["ledger_context"]
            if "telemetry" in data and bundle.telemetry is None:
                bundle.telemetry = {
                    "telemetry": data.get("telemetry", []),
                    "slo_summary": data.get("slo_summary", ""),
                }
            if "proof_index" in data and isinstance(data.get("proof_index"), list) and bundle.proof_index is None:
                bundle.proof_index = data["proof_index"]

        self._apply_budget(bundle, budget)
        return bundle.with_meta(budget_chars=budget.total_chars)

    def _apply_budget(self, bundle: ContextBundle, budget: BudgetConstraints) -> None:
        # Task
        task_limit = budget.limit_for("task")
        bundle.task.title = _truncate_text(bundle.task.title, task_limit)
        bundle.task.blockers = _truncate_text(bundle.task.blockers, task_limit)

        # State
        state_limit = budget.limit_for("state")
        bundle.state.context = _truncate_text(bundle.state.context, state_limit)

        # Brief
        if bundle.brief:
            brief_limit = budget.limit_for("brief")
            bundle.brief.objective = _truncate_text(bundle.brief.objective, brief_limit)
            bundle.brief.acceptance = _truncate_text(bundle.brief.acceptance, brief_limit)
            bundle.brief.proofs = _truncate_text(bundle.brief.proofs, brief_limit)

        # Rules
        if bundle.rules:
            rules_limit = budget.limit_for("rules")
            remaining = rules_limit
            truncated: List[RuleContext] = []
            for rule in bundle.rules:
                desc = rule.description or ""
                if not desc:
                    truncated.append(rule)
                    continue
                if len(desc) <= remaining:
                    truncated.append(rule)
                    remaining -= len(desc)
                else:
                    rule.description = _truncate_text(desc, remaining)
                    truncated.append(rule)
                    break
            bundle.rules = truncated

        # Memory
        if bundle.memory:
            mem_limit = budget.limit_for("memory")
            acc: List[MemoryItem] = []
            remaining = mem_limit
            for item in bundle.memory:
                if remaining <= 0:
                    break
                if len(item.content) <= remaining:
                    acc.append(item)
                    remaining -= len(item.content)
                else:
                    acc.append(MemoryItem(content=_truncate_text(item.content, remaining), source=item.source))
                    break
            bundle.memory = acc

        # Git
        if bundle.git:
            git_limit = budget.limit_for("git")
            bundle.git.status = _truncate_text(bundle.git.status, git_limit)
            bundle.git.shortlog = _truncate_text(bundle.git.shortlog, git_limit)

        # Ledger
        if bundle.ledger:
            ledger_limit = budget.limit_for("ledger")
            acc_ledger: List[Dict[str, Any]] = []
            remaining = ledger_limit
            for entry in bundle.ledger:
                try:
                    sz = _string_size(entry)
                    if sz <= remaining:
                        acc_ledger.append(entry)
                        remaining -= sz
                    else:
                        break
                except Exception:
                    acc_ledger.append(entry)
                    remaining -= 200
                    if remaining <= 0:
                        break
            bundle.ledger = acc_ledger
            if "ledger_context" in bundle.meta and isinstance(bundle.meta["ledger_context"], str):
                bundle.meta["ledger_context"] = _truncate_text(bundle.meta["ledger_context"], ledger_limit)

        # Telemetry
        if bundle.telemetry and isinstance(bundle.telemetry, dict):
            telemetry_limit = budget.limit_for("telemetry")
            summary = bundle.telemetry.get("slo_summary")
            if isinstance(summary, str) and len(summary) > telemetry_limit:
                bundle.telemetry["slo_summary"] = _truncate_text(summary, telemetry_limit)
