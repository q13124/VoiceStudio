from __future__ import annotations

from typing import Dict, Iterable, List

from tools.context.core.models import AllocationContext
from tools.context.core.protocols import ContextSourceProtocol


class SourceRegistry:
    """Registry and lifecycle for context source adapters."""

    def __init__(self, sources: Iterable[ContextSourceProtocol] | None = None):
        self._sources: List[ContextSourceProtocol] = list(sources or [])

    def register(self, source: ContextSourceProtocol) -> None:
        self._sources.append(source)
        self._sources.sort(key=lambda s: s.priority, reverse=True)

    def all(self) -> List[ContextSourceProtocol]:
        return list(self._sources)

    def by_name(self) -> Dict[str, ContextSourceProtocol]:
        return {s.source_name: s for s in self._sources}


def build_default_registry(config: dict) -> SourceRegistry:
    """Instantiate the default source registry from configuration."""
    from tools.context.sources.git_adapter import GitSourceAdapter
    from tools.context.sources.memory_adapter import MemorySourceAdapter
    from tools.context.sources.rules_adapter import RulesSourceAdapter
    from tools.context.sources.state_adapter import StateSourceAdapter
    from tools.context.sources.context7_adapter import Context7Adapter
    from tools.context.sources.linear_adapter import LinearAdapter
    from tools.context.sources.github_adapter import GitHubAdapter
    from tools.context.sources.task_adapter import TaskSourceAdapter

    registry = SourceRegistry()

    # Extract configuration sections
    rules_cfg = config.get("rules", {})
    git_cfg = config.get("git", {})
    memory_cfg = config.get("memory", {})
    ledger_cfg = config.get("ledger", {})
    telemetry_cfg = config.get("telemetry", {})
    gitkraken_cfg = config.get("gitkraken", {})

    # Core adapters (always enabled)
    registry.register(StateSourceAdapter())
    registry.register(TaskSourceAdapter())
    registry.register(
        RulesSourceAdapter(
            include_always_apply_only=rules_cfg.get("include_always_apply_only", False),
            max_rules=rules_cfg.get("max_rules"),
        )
    )
    # Vector memory (optional): when enabled, runs first and results are merged with file memory
    if memory_cfg.get("vector_enabled", False):
        from tools.context.sources.vector_memory_adapter import VectorMemoryAdapter
        registry.register(
            VectorMemoryAdapter(
                persist_directory=memory_cfg.get("vector_persist_directory", ".cursor/chroma"),
                top_k=memory_cfg.get("vector_top_k", 5),
                offline=memory_cfg.get("offline", True),
            )
        )
    registry.register(
        MemorySourceAdapter(
            offline=memory_cfg.get("offline", True),
            max_results=memory_cfg.get("max_results", 5),
            query_type=memory_cfg.get("query_type", "contextual"),
            mcp_enabled=memory_cfg.get("mcp_enabled", False),
        )
    )
    # Conversation (short-term): sliding window + summarization when enabled
    conversation_cfg = config.get("conversation", {})
    if conversation_cfg.get("enabled", False):
        from tools.context.sources.conversation_adapter import ConversationSourceAdapter
        registry.register(
            ConversationSourceAdapter(
                history_path=conversation_cfg.get("history_path", ".cursor/.conversation_history.jsonl"),
                max_turns=conversation_cfg.get("max_turns", 10),
                recent_turns=conversation_cfg.get("recent_turns", 5),
                offline=True,
            )
        )
    # Agent notes (structured note-taking per role): when enabled, loads .cursor/agent_notes/{role}_notes.md
    notes_cfg = config.get("notes", {})
    if notes_cfg.get("enabled", True):
        from tools.context.sources.notes_adapter import NotesSourceAdapter
        registry.register(
            NotesSourceAdapter(
                notes_dir=notes_cfg.get("notes_dir", ".cursor/agent_notes"),
                offline=True,
            )
        )
    registry.register(
        GitSourceAdapter(
            include_status=git_cfg.get("include_status", True),
            include_shortlog=git_cfg.get("include_shortlog", True),
            shortlog_limit=git_cfg.get("shortlog_limit", 5),
        )
    )

    # Quality Ledger adapter (enabled by default)
    if ledger_cfg.get("enabled", True):
        from tools.context.sources.ledger_adapter import LedgerSourceAdapter
        
        registry.register(
            LedgerSourceAdapter(
                include_done=ledger_cfg.get("include_done", False),
            )
        )

    # Telemetry/SLO adapter (disabled by default - requires backend)
    if telemetry_cfg.get("enabled", False):
        from tools.context.sources.telemetry_adapter import TelemetrySourceAdapter
        
        registry.register(
            TelemetrySourceAdapter(
                endpoint=telemetry_cfg.get("endpoint", "http://localhost:8000/api/telemetry/slos"),
                timeout_seconds=telemetry_cfg.get("timeout_seconds", 2.0),
                include_passing=telemetry_cfg.get("include_passing", False),
            )
        )

    # GitKraken enhanced adapter (disabled by default - requires gh CLI)
    if gitkraken_cfg.get("enabled", False):
        from tools.context.sources.gitkraken_adapter import GitKrakenAdapter
        
        registry.register(
            GitKrakenAdapter(
                include_issues=gitkraken_cfg.get("include_issues", True),
                include_prs=gitkraken_cfg.get("include_prs", True),
                commit_limit=gitkraken_cfg.get("commit_limit", 5),
            )
        )

    # Overseer Issues adapter (disabled by default - requires issue store)
    issues_cfg = config.get("issues", {})
    if issues_cfg.get("enabled", False):
        from tools.context.sources.issues_adapter import IssuesSourceAdapter
        
        registry.register(
            IssuesSourceAdapter(
                max_issues=issues_cfg.get("max_issues", 10),
                severity_filter=issues_cfg.get("severity_filter", ["critical", "high"]),
                time_window_hours=issues_cfg.get("time_window_hours", 24),
                include_recommendations=issues_cfg.get("include_recommendations", True),
            )
        )

    # Audit log adapter (enabled by default - reads from .audit/)
    audit_cfg = config.get("audit", {})
    if audit_cfg.get("enabled", True):
        from tools.context.sources.audit_adapter import AuditSourceAdapter
        
        registry.register(
            AuditSourceAdapter(
                max_entries=audit_cfg.get("max_entries", 20),
                severity_filter=audit_cfg.get("severity_filter", ["error", "warning", "critical"]),
                hours_lookback=audit_cfg.get("hours_lookback", 24),
            )
        )

    # Progress tracking adapter (enabled by default - reads from ledger and state)
    progress_cfg = config.get("progress", {})
    if progress_cfg.get("enabled", True):
        from tools.context.sources.progress_adapter import ProgressSourceAdapter
        
        registry.register(
            ProgressSourceAdapter(
                include_gate_details=progress_cfg.get("include_gate_details", True),
                include_milestones=progress_cfg.get("include_milestones", True),
                max_actions=progress_cfg.get("max_actions", 5),
            )
        )

    return registry
