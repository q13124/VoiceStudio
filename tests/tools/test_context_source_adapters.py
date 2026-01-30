from __future__ import annotations

import json
from pathlib import Path

from tools.context.core.models import AllocationContext
from tools.context.sources.conversation_adapter import ConversationSourceAdapter
from tools.context.sources.git_adapter import GitSourceAdapter
from tools.context.sources.ledger_adapter import LedgerSourceAdapter
from tools.context.sources.memory_adapter import MemorySourceAdapter
from tools.context.sources.notes_adapter import NotesSourceAdapter
from tools.context.sources.rules_adapter import RulesSourceAdapter
from tools.context.sources.state_adapter import StateSourceAdapter
from tools.context.sources.task_adapter import TaskSourceAdapter
from tools.context.sources.vector_memory_adapter import VectorMemoryAdapter


def test_state_adapter_parses_state_and_task(tmp_path: Path) -> None:
    state_path = tmp_path / "STATE.md"
    state_path.write_text(
        "\n".join(
            [
                "# VoiceStudio Session State",
                "## Current Phase",
                "- **Phase**: Implement",
                "- **Started**: 2026-01-01",
                "- **Context**: Example",
                "## Active Task",
                "- **ID**: TASK-0001",
                "- **Title**: Example task",
                "- **Priority**: Low",
                "- **Blockers**: None",
                "## Proof Index",
                "| Date | Task | Artifact | Type | Verified |",
                "| --- | --- | --- | --- | --- |",
                "| 2026-01-01 | TASK-0001 | path | Report | Manual |",
            ]
        ),
        encoding="utf-8",
    )
    adapter = StateSourceAdapter(path=state_path)
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert result.data["state"].phase == "Implement"
    assert result.data["task"].id == "TASK-0001"
    assert len(result.data["proof_index"]) == 1


def test_memory_adapter_env_fallback(monkeypatch) -> None:
    monkeypatch.setenv("CONTEXT_MEMO", "hello memory")
    adapter = MemorySourceAdapter(offline=True, mcp_enabled=False)
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert any(item.content == "hello memory" for item in result.data.get("memory", []))


def test_notes_adapter_reads_role_notes(tmp_path: Path) -> None:
    notes_dir = tmp_path / "agent_notes"
    notes_dir.mkdir()
    notes_file = notes_dir / "core-platform_notes.md"
    notes_file.write_text("notes content", encoding="utf-8")
    adapter = NotesSourceAdapter(notes_dir=str(notes_dir))
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role="core-platform"))
    assert result.success
    assert any("notes content" in item.content for item in result.data.get("memory", []))


def test_conversation_adapter_reads_history(tmp_path: Path) -> None:
    history = tmp_path / "history.jsonl"
    turns = [
        {"role": "user", "content": "hello", "timestamp": "2026-01-01T00:00:00Z"},
        {"role": "assistant", "content": "hi", "timestamp": "2026-01-01T00:01:00Z"},
    ]
    history.write_text("\n".join(json.dumps(t) for t in turns) + "\n", encoding="utf-8")
    adapter = ConversationSourceAdapter(history_path=str(history), recent_turns=5, max_turns=10)
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert result.data.get("memory")


def test_vector_memory_adapter_handles_missing_chroma() -> None:
    adapter = VectorMemoryAdapter()
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert isinstance(result.data.get("memory", []), list)


def test_git_adapter_optional_sections() -> None:
    adapter = GitSourceAdapter(include_status=False, include_shortlog=False)
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert result.data["git"].status is None
    assert result.data["git"].shortlog is None


def test_rules_adapter_parses_frontmatter(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()
    (rules_dir / "a.mdc").write_text(
        "\n".join(
            [
                "---",
                "description: \"Always apply\"",
                "alwaysApply: true",
                "---",
                "# Rule A",
            ]
        ),
        encoding="utf-8",
    )
    (rules_dir / "b.mdc").write_text(
        "\n".join(
            [
                "---",
                "description: \"Optional\"",
                "alwaysApply: false",
                "---",
                "# Rule B",
            ]
        ),
        encoding="utf-8",
    )
    adapter = RulesSourceAdapter(rules_dir=str(rules_dir), include_always_apply_only=True)
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert len(result.data["rules"]) == 1
    assert result.data["rules"][0].always_apply


def test_task_adapter_reads_brief(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    task_file = tasks_dir / "TASK-1234.md"
    task_file.write_text(
        "\n".join(
            [
                "# TASK-1234",
                "## Objective",
                "Do the thing.",
                "## Acceptance Criteria",
                "- Works",
                "## Required Proofs",
                "- pytest ...",
            ]
        ),
        encoding="utf-8",
    )
    adapter = TaskSourceAdapter(tasks_dir=str(tasks_dir))
    result = adapter.fetch(AllocationContext(task_id="TASK-1234", phase=None, role=None))
    assert result.success
    assert result.data["brief"].objective == "Do the thing."


def test_ledger_adapter_reads_open_index(tmp_path: Path) -> None:
    ledger = tmp_path / "QUALITY_LEDGER.md"
    ledger.write_text(
        "\n".join(
            [
                "# Quality Ledger",
                "## Open index (keep this near the top)",
                "| ID | State | Sev | Gate | Owner Role | Category | Title |",
                "| --- | --- | --- | --- | --- | --- | --- |",
                "| VS-0001 | DONE | S0 Blocker | B | Build | BUILD | Example |",
            ]
        ),
        encoding="utf-8",
    )
    adapter = LedgerSourceAdapter(ledger_path=ledger, include_done=True)
    result = adapter.fetch(AllocationContext(task_id=None, phase=None, role=None))
    assert result.success
    assert len(result.data["ledger"]) == 1
