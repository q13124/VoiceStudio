from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ContextLevel(str, Enum):
    """Tiered context loading levels for progressive disclosure."""

    HIGH = "high"      # STATE, TASK (Level 1) - always loaded
    MID = "mid"        # Brief, Ledger (Level 2) - loaded if budget allows
    LOW = "low"        # Rules, Memory, Git (Level 3) - loaded if budget allows


class PartCategory(str, Enum):
    """P.A.R.T. framework categories."""

    PROMPT = "prompt"       # Core directives: task, role, phase
    ARCHIVE = "archive"     # Recent history: steps, proof index
    RESOURCES = "resources" # Domain knowledge: rules, memory, ledger
    TOOLS = "tools"         # Capabilities: git, telemetry, MCP


@dataclass(frozen=True)
class AllocationContext:
    """Immutable allocation request context."""

    task_id: str | None
    phase: str | None
    role: str | None
    include_git: bool = False
    budget_chars: int = 12000
    max_level: ContextLevel = ContextLevel.LOW  # Maximum depth to load
    request_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))


@dataclass
class BudgetConstraints:
    """Budget allocation per source."""

    total_chars: int
    source_limits: dict[str, int]
    priority_order: list[str]

    def limit_for(self, source: str) -> int:
        return self.source_limits.get(source, max(0, self.total_chars))


@dataclass
class TaskContext:
    id: str | None = None
    title: str | None = None
    priority: str | None = None
    blockers: str | None = None


@dataclass
class StateContext:
    phase: str | None = None
    started: str | None = None
    context: str | None = None
    next_steps: list[str] = field(default_factory=list)


@dataclass
class BriefContext:
    path: str | None = None
    objective: str | None = None
    acceptance: str | None = None
    proofs: str | None = None


@dataclass
class RuleContext:
    path: str
    description: str | None = None
    always_apply: bool = False


@dataclass
class MemoryItem:
    content: str
    source: str | None = None


@dataclass
class GitContext:
    status: str | None = None
    shortlog: str | None = None


@dataclass
class SourceResult:
    source_name: str
    success: bool
    data: Any
    size_chars: int
    fetch_time_ms: float
    error: str | None = None


@dataclass
class PartStructure:
    """P.A.R.T. framework structure for context organization."""

    prompt: dict[str, Any] = field(default_factory=dict)      # Core directives
    archive: dict[str, Any] = field(default_factory=dict)     # Recent history
    resources: dict[str, Any] = field(default_factory=dict)   # Domain knowledge
    tools: dict[str, Any] = field(default_factory=dict)       # Capabilities

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "archive": self.archive,
            "resources": self.resources,
            "tools": self.tools,
        }


@dataclass
class ProgressContext:
    """Project progress tracking context."""

    current_gate: str = ""
    current_phase: str = ""
    progress_percent: float = 0.0
    blockers_count: int = 0
    in_progress_count: int = 0
    next_actions: list[str] = field(default_factory=list)
    gate_details: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ContextBundle:
    task: TaskContext = field(default_factory=TaskContext)
    state: StateContext = field(default_factory=StateContext)
    brief: BriefContext | None = None
    rules: list[RuleContext] = field(default_factory=list)
    memory: list[MemoryItem] = field(default_factory=list)
    git: GitContext | None = None
    ledger: list[dict[str, Any]] | None = None
    telemetry: dict[str, Any] | None = None
    proof_index: list[dict[str, Any]] | None = None
    progress: ProgressContext | None = None
    meta: dict = field(default_factory=dict)

    # P.A.R.T. structure metadata
    _part_structure: PartStructure | None = field(default=None, init=False, repr=False)

    def with_meta(self, budget_chars: int) -> ContextBundle:
        self.meta["generated_at"] = datetime.now().isoformat()
        self.meta["budget_chars"] = budget_chars
        return self

    def to_dict(self) -> dict[str, Any]:
        def _serialize(obj: Any) -> Any:
            if hasattr(obj, "__dict__"):
                return {k: _serialize(v) for k, v in obj.__dict__.items()}
            if isinstance(obj, list):
                return [_serialize(x) for x in obj]
            return obj

        out: dict[str, Any] = {
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
        if self.progress is not None:
            out["progress"] = _serialize(self.progress)
        return out

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_part_structure(self) -> PartStructure:
        """Convert bundle to P.A.R.T. framework structure."""
        part = PartStructure()

        # PROMPT: Core directives (task, role, phase, objective)
        part.prompt["task"] = {
            "id": self.task.id,
            "title": self.task.title,
            "priority": self.task.priority,
            "blockers": self.task.blockers,
        }
        part.prompt["state"] = {
            "phase": self.state.phase,
            "context": self.state.context,
        }
        if self.brief:
            part.prompt["objective"] = self.brief.objective
            part.prompt["acceptance"] = self.brief.acceptance
        part.prompt["role"] = self.meta.get("role")

        # ARCHIVE: Recent history (next steps, proof index, progress)
        part.archive["next_steps"] = self.state.next_steps or []
        part.archive["proof_index"] = self.proof_index or []
        part.archive["started"] = self.state.started
        if self.progress:
            part.archive["progress"] = {
                "current_gate": self.progress.current_gate,
                "progress_percent": self.progress.progress_percent,
                "blockers_count": self.progress.blockers_count,
                "in_progress_count": self.progress.in_progress_count,
                "next_actions": self.progress.next_actions,
            }

        # RESOURCES: Domain knowledge (rules, memory, ledger)
        part.resources["rules"] = [
            {"path": r.path, "description": r.description, "always_apply": r.always_apply}
            for r in self.rules
        ]
        part.resources["memory"] = [
            {"content": m.content, "source": m.source}
            for m in self.memory
        ]
        part.resources["ledger"] = self.ledger or []
        part.resources["ledger_context"] = self.meta.get("ledger_context")

        # TOOLS: Capabilities (git, telemetry, MCP)
        if self.git:
            part.tools["git"] = {
                "status": self.git.status,
                "shortlog": self.git.shortlog,
            }
        if self.telemetry:
            part.tools["telemetry"] = self.telemetry
        part.tools["mcp_available"] = self.meta.get("mcp_available", False)

        self._part_structure = part
        return part

    def to_part_markdown(self) -> str:
        """Render P.A.R.T. structure as markdown."""
        part = self.to_part_structure()
        lines = ["# Context Bundle (P.A.R.T. Framework)", ""]

        # P: PROMPT
        lines.append("## P: PROMPT (Core Directives)")
        lines.append("")
        if part.prompt.get("task", {}).get("id"):
            lines.append(f"**Task**: {part.prompt['task']['id']} — {part.prompt['task']['title']}")
        if part.prompt.get("state", {}).get("phase"):
            lines.append(f"**Phase**: {part.prompt['state']['phase']}")
        if part.prompt.get("role"):
            lines.append(f"**Role**: {part.prompt['role']}")
        if part.prompt.get("objective"):
            lines.append(f"**Objective**: {part.prompt['objective'][:200]}...")
        lines.append("")

        # A: ARCHIVE
        lines.append("## A: ARCHIVE (Recent History)")
        lines.append("")
        steps = part.archive.get("next_steps", [])
        if steps:
            lines.append("**Next Steps**:")
            lines.extend([f"- {step}" for step in steps[:5]])
            lines.append("")
        proof = part.archive.get("proof_index", [])
        if proof:
            lines.append("**Recent Proof** (last 5):")
            for entry in proof[:5]:
                lines.append(f"- [{entry.get('date')}] {entry.get('task')}: {entry.get('artifact', '')[:80]}")
            lines.append("")

        # R: RESOURCES
        lines.append("## R: RESOURCES (Domain Knowledge)")
        lines.append("")
        rules = part.resources.get("rules", [])
        if rules:
            lines.append(f"**Rules** ({len(rules)} loaded):")
            for rule in rules[:8]:
                lines.append(f"- {rule['path']}")
            lines.append("")
        memory = part.resources.get("memory", [])
        if memory:
            lines.append(f"**Memory** ({len(memory)} items):")
            for mem in memory[:5]:
                lines.append(f"- {mem['content'][:120]}...")
            lines.append("")
        ledger = part.resources.get("ledger", [])
        if ledger:
            lines.append(f"**Ledger** ({len(ledger)} entries):")
            for entry in ledger[:5]:
                lines.append(f"- [{entry.get('id')}] {entry.get('title', '')[:80]}")
            lines.append("")

        # T: TOOLS
        lines.append("## T: TOOLS (Available Capabilities)")
        lines.append("")
        git = part.tools.get("git", {})
        if git.get("status"):
            lines.append(f"**Git**: {git['status'][:100]}...")
        if part.tools.get("telemetry"):
            lines.append("**Telemetry**: Available")
        if part.tools.get("mcp_available"):
            lines.append("**MCP**: Enabled")
        lines.append("")

        return "\n".join(lines)

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
        # Archive (Recent History): progress, last steps, proof index
        parts.append("## Archive (Recent History)")
        parts.append("")
        if self.progress:
            parts.append("### Progress")
            parts.append(f"- Current Gate: {self.progress.current_gate}")
            parts.append(f"- Progress: {self.progress.progress_percent:.1f}%")
            if self.progress.blockers_count > 0:
                parts.append(f"- Blockers: {self.progress.blockers_count}")
            if self.progress.in_progress_count > 0:
                parts.append(f"- In Progress: {self.progress.in_progress_count}")
            if self.progress.next_actions:
                parts.append("- Next Actions:")
                for action in self.progress.next_actions[:5]:
                    parts.append(f"  - {action}")
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
