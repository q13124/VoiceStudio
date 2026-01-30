from __future__ import annotations

from typing import Protocol

from tools.context.core.models import AllocationContext, BudgetConstraints, ContextBundle, SourceResult


class ContextSourceProtocol(Protocol):
    """Protocol for context source adapters."""

    source_name: str
    priority: int
    offline: bool

    def fetch(self, context: AllocationContext) -> SourceResult:
        ...

    def estimate_size(self, context: AllocationContext) -> int:
        ...


class AllocatorProtocol(Protocol):
    """Protocol for context allocators."""

    def allocate(self, sources: list[SourceResult], budget: BudgetConstraints) -> ContextBundle:
        ...
