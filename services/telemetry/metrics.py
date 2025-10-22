
from __future__ import annotations
from typing import Dict, Any

class MetricsRegistry:
    def __init__(self) -> None:
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.hist: Dict[str, list[float]] = {}

    def inc(self, key: str, val: float = 1.0) -> None:
        self.counters[key] = self.counters.get(key, 0.0) + val

    def set_gauge(self, key: str, val: float) -> None:
        self.gauges[key] = val

    def observe(self, key: str, val: float) -> None:
        self.hist.setdefault(key, []).append(val)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "hist": {k: v[-5:] for k, v in self.hist.items()},  # last 5
        }

metrics = MetricsRegistry()
