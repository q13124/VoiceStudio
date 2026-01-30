from __future__ import annotations

import json
from typing import Any, Dict
from urllib.request import urlopen
from urllib.error import URLError

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter


class TelemetrySourceAdapter(BaseSourceAdapter):
    """Fetch telemetry/SLO data from backend endpoint."""

    def __init__(self, endpoint: str, timeout_seconds: float = 2.0, include_passing: bool = False, offline: bool = False):
        super().__init__(source_name="telemetry", priority=20, offline=offline)
        self._endpoint = endpoint
        self._timeout = timeout_seconds
        self._include_passing = include_passing

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> Dict[str, Any]:
            try:
                with urlopen(self._endpoint, timeout=self._timeout) as resp:
                    raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                if not self._include_passing and isinstance(data, dict):
                    failing = data.get("failing", data.get("violations", []))
                    return {"telemetry": failing, "slo_summary": data.get("summary", "")}
                return {"telemetry": data, "slo_summary": data.get("summary", "") if isinstance(data, dict) else ""}
            except (URLError, json.JSONDecodeError, ValueError):
                return {"telemetry": [], "slo_summary": ""}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        return 1000
