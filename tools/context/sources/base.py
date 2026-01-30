from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.core.protocols import ContextSourceProtocol


def _estimate_size(data: Any) -> int:
    try:
        return len(json.dumps(data, ensure_ascii=False, default=str))
    except Exception:
        return len(str(data))


class BaseSourceAdapter(ContextSourceProtocol):
    """Base class for context source adapters with timing/error handling."""

    def __init__(self, source_name: str, priority: int = 0, offline: bool = True):
        self.source_name = source_name
        self.priority = priority
        self.offline = offline
        self._offline = offline

    def _measure(self, loader: Callable[[], Dict[str, Any]], context: AllocationContext) -> SourceResult:
        start = time.perf_counter()
        try:
            data = loader() or {}
            size = _estimate_size(data)
            return SourceResult(
                source_name=self.source_name,
                success=True,
                data=data,
                size_chars=size,
                fetch_time_ms=(time.perf_counter() - start) * 1000.0,
                error=None,
            )
        except Exception as exc:
            return SourceResult(
                source_name=self.source_name,
                success=False,
                data={},
                size_chars=0,
                fetch_time_ms=(time.perf_counter() - start) * 1000.0,
                error=str(exc),
            )

    def estimate_size(self, context: AllocationContext) -> int:
        return 0
