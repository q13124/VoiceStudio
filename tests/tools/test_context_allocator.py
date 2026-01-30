from __future__ import annotations

from tools.context.core.allocator import ContextAllocator
from tools.context.core.models import BudgetConstraints, MemoryItem, RuleContext, SourceResult, TaskContext


def _result(name: str, data: dict) -> SourceResult:
    return SourceResult(
        source_name=name,
        success=True,
        data=data,
        size_chars=100,
        fetch_time_ms=1.0,
        error=None,
    )


def test_allocator_respects_priority_order() -> None:
    allocator = ContextAllocator()
    first_task = TaskContext(id="TASK-0001", title="First")
    second_task = TaskContext(id="TASK-0002", title="Second")
    sources = [
        _result("secondary", {"task": second_task}),
        _result("primary", {"task": first_task}),
    ]
    budget = BudgetConstraints(
        total_chars=2000,
        source_limits={"task": 2000},
        priority_order=["primary", "secondary"],
    )
    bundle = allocator.allocate(sources, budget)
    assert bundle.task.id == "TASK-0001"


def test_allocator_truncates_memory_and_rules() -> None:
    allocator = ContextAllocator()
    long_text = "x" * 200
    sources = [
        _result("memory", {"memory": [MemoryItem(content=long_text, source="test")]}),
        _result("rules", {"rules": [RuleContext(path="rule.mdc", description=long_text, always_apply=True)]}),
    ]
    budget = BudgetConstraints(
        total_chars=500,
        source_limits={"memory": 50, "rules": 50},
        priority_order=["rules", "memory"],
    )
    bundle = allocator.allocate(sources, budget)
    assert bundle.memory
    assert bundle.rules
    assert len(bundle.memory[0].content) <= 50
    assert len(bundle.rules[0].description or "") <= 50
