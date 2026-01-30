from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class AllocationContext:
    """Immutable allocation request context."""

    task_id: Optional[str]
    phase: Optional[str]
    role: Optional[str]
    include_git: bool = False
    budget_chars: int = 12000
    request_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))


@dataclass
class BudgetConstraints:
    """Budget allocation per source."""

    total_chars: int
    source_limits: Dict[str, int]
    priority_order: List[str]

    def limit_for(self, source: str) -> int:
        return self.source_limits.get(source, max(0, self.total_chars))


@dataclass
class TaskContext:
    id: Optional[str] = None
    title: Optional[str] = None
    priority: Optional[str] = None
    blockers: Optional[str] = None


@dataclass
class StateContext:
    phase: Optional[str] = None
    started: Optional[str] = None
    context: Optional[str] = None
    next_steps: List[str] = field(default_factory=list)


@dataclass
class BriefContext:
    path: Optional[str] = None
    objective: Optional[str] = None
    acceptance: Optional[str] = None
    proofs: Optional[str] = None


@dataclass
class RuleContext:
    path: str
    description: Optional[str] = None
    always_apply: bool = False


@dataclass
class MemoryItem:
    content: str
    source: Optional[str] = None


@dataclass
class GitContext:
    status: Optional[str] = None
    shortlog: Optional[str] = None


@dataclass
class SourceResult:
    source_name: str
    success: bool
    data: Any
    size_chars: int
    fetch_time_ms: float
    error: Optional[str] = None


@dataclass
class ContextBundle:
    task: TaskContext = field(default_factory=TaskContext)
    state: StateContext = field(default_factory=StateContext)
    brief: Optional[BriefContext] = None
    rules: List[RuleContext] = field(default_factory=list)
    memory: List[MemoryItem] = field(default_factory=list)
    git: Optional[GitContext] = None
    ledger: Optional[List[Dict[str, Any]]] = None
    telemetry: Optional[Dict[str, Any]] = None
    proof_index: Optional[List[Dict[str, Any]]] = None
    meta: dict = field(default_factory=dict)

    def with_meta(self, budget_chars: int) -> "ContextBundle":
        self.meta["generated_at"] = datetime.now().isoformat()
        self.meta["budget_chars"] = budget_chars
        return self

    def to_dict(self) -> Dict[str, Any]:
        def _serialize(obj: Any) -> Any:
            if hasattr(obj, "__dict__"):
                return {k: _serialize(v) for k, v in obj.__dict__.items()}
            if isinstance(obj, list):
                return [_serialize(x) for x in obj]
            return obj

        out: Dict[str, Any] = {
            "task": _serialize(self.task),
            "state": _serialize(self.state),
            "brief": _serialize(self.brief),
            "rules": _serialize(self.rules),
            "memory": _serialize(self.memory),
            "git": _serialize(self.git),
            "meta": _serialize(self.meta),
        }
        if self.ledger is not None:
            out["ledger"] = _serialize(self.ledger)
        if self.telemetry is not None:
            out["telemetry"] = _serialize(self.telemetry)
        if self.proof_index is not None:
            out["proof_index"] = _serialize(self.proof_index)
        return out

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_preamble_markdown(self) -> str:
        parts = ["# Context Bundle (P.A.R.T. Framework)", ""]
        # Prompt (Core Directives): current task, role, phase
        parts.append("## Prompt (Core Directives)")
        parts.append("")
        if self.task.id or self.task.title:
            parts.append("### Task")
            if self.task.id:
                parts.append(f"- ID: {self.task.id}")
            if self.task.title:
                parts.append(f"- Title: {self.task.title}")
            if self.task.priority:
                parts.append(f"- Priority: {self.task.priority}")
            if self.task.blockers:
                parts.append(f"- Blockers: {self.task.blockers}")
            parts.append("")
        if self.state.phase or self.state.context:
            parts.append("### State")
            if self.state.phase:
                parts.append(f"- Phase: {self.state.phase}")
            if self.state.context:
                parts.append(f"- Context: {self.state.context}")
            parts.append("")
        if self.brief:
            parts.append("### Task Brief")
            if self.brief.objective:
                parts.append(f"- Objective: {self.brief.objective}")
            if self.brief.acceptance:
                parts.append(f"- Acceptance: {self.brief.acceptance}")
            if self.brief.proofs:
                parts.append(f"- Proofs: {self.brief.proofs}")
            parts.append("")
        # Archive (Recent History): last steps, proof index
        parts.append("## Archive (Recent History)")
        parts.append("")
        if self.state.next_steps:
            parts.append("- Next steps:")
            parts.extend([f"  - {step}" for step in self.state.next_steps])
            parts.append("")
        if self.proof_index:
            for entry in self.proof_index[:15]:
                e = entry if isinstance(entry, dict) else {}
                task = e.get("task", "")
                artifact = e.get("artifact", "")
                if task or artifact:
                    parts.append(f"- [{e.get('date', '')}] {task}: {artifact}")
            parts.append("")
        # Resources (Domain Knowledge): rules, memory, ledger
        parts.append("## Resources (Domain Knowledge)")
        parts.append("")
        if self.rules:
            parts.append("### Rules")
            for rule in self.rules:
                label = f"{rule.path}"
                if rule.always_apply:
                    label += " (alwaysApply)"
                if rule.description:
                    label += f": {rule.description}"
                parts.append(f"- {label}")
            parts.append("")
        if self.memory:
            parts.append("### Memory")
            for mem in self.memory:
                src = f" ({mem.source})" if mem.source else ""
                parts.append(f"- {mem.content}{src}")
            parts.append("")
        if self.ledger:
            parts.append("### Ledger")
            for entry in self.ledger[:10]:
                sid = entry.get("id") or entry.get("entry_id")
                title = entry.get("title", "")
                if sid or title:
                    parts.append(f"- [{sid or '?'}] {title}")
            parts.append("")
        # Tools (Available Capabilities): git, telemetry, MCP
        parts.append("## Tools (Available Capabilities)")
        parts.append("")
        if self.git:
            if self.git.status:
                parts.append(f"- Git status: {self.git.status}")
            if self.git.shortlog:
                parts.append(f"- Shortlog:\n```\n{self.git.shortlog}\n```")
            parts.append("")
        if self.telemetry:
            summary = (self.telemetry or {}).get("slo_summary")
            if summary:
                parts.append("- Telemetry (SLO):")
                parts.append(summary[:2000] + ("..." if len(summary) > 2000 else ""))
        return "\n".join(parts).strip()
