"""
Pipeline Metrics for VoiceStudio (Phase 9.3.1)

Tracks Time to First Token (TTFT), end-to-end latency, and
per-stage performance metrics for the voice AI pipeline.
"""

from __future__ import annotations

import logging
import statistics
from collections import deque
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class StageMetric:
    """Metric for a single pipeline stage execution."""

    stage: str  # "stt", "llm", "tts", "total"
    latency_ms: float
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecutionMetrics:
    """Complete metrics for a single pipeline execution."""

    execution_id: str
    mode: str  # "streaming", "batch"
    stages: list[StageMetric] = field(default_factory=list)
    time_to_first_token_ms: float = 0.0
    time_to_first_audio_ms: float = 0.0
    total_latency_ms: float = 0.0
    input_length: int = 0
    output_length: int = 0
    timestamp: float = 0.0
    error: str | None = None


class PipelineMetricsCollector:
    """
    Collects and aggregates pipeline performance metrics.

    Maintains a rolling window of recent executions for
    computing percentile statistics (P50, P90, P99).
    """

    def __init__(self, window_size: int = 100):
        self._window_size = window_size
        self._executions: deque[PipelineExecutionMetrics] = deque(maxlen=window_size)
        self._ttft_samples: deque[float] = deque(maxlen=window_size)
        self._total_latency_samples: deque[float] = deque(maxlen=window_size)
        self._stage_samples: dict[str, deque[float]] = {
            "stt": deque(maxlen=window_size),
            "llm": deque(maxlen=window_size),
            "tts": deque(maxlen=window_size),
        }

    def record(self, metrics: PipelineExecutionMetrics) -> None:
        """Record a pipeline execution's metrics."""
        self._executions.append(metrics)

        if metrics.time_to_first_token_ms > 0:
            self._ttft_samples.append(metrics.time_to_first_token_ms)

        if metrics.total_latency_ms > 0:
            self._total_latency_samples.append(metrics.total_latency_ms)

        for stage_metric in metrics.stages:
            if stage_metric.stage in self._stage_samples:
                self._stage_samples[stage_metric.stage].append(stage_metric.latency_ms)

    def get_summary(self) -> dict[str, Any]:
        """Get aggregated metrics summary."""
        return {
            "total_executions": len(self._executions),
            "ttft": self._compute_percentiles(list(self._ttft_samples)),
            "total_latency": self._compute_percentiles(list(self._total_latency_samples)),
            "stages": {
                stage: self._compute_percentiles(list(samples))
                for stage, samples in self._stage_samples.items()
            },
            "error_count": sum(1 for e in self._executions if e.error),
            "window_size": self._window_size,
        }

    def get_recent(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent execution metrics."""
        recent = list(self._executions)[-count:]
        return [
            {
                "execution_id": e.execution_id,
                "mode": e.mode,
                "ttft_ms": e.time_to_first_token_ms,
                "total_ms": e.total_latency_ms,
                "error": e.error,
            }
            for e in recent
        ]

    def check_sla(self, target_p90_ms: float = 800.0) -> dict[str, Any]:
        """
        Check if pipeline meets SLA targets.

        Default target: P90 total latency < 800ms (per architectural spec).
        """
        samples = list(self._total_latency_samples)
        if not samples:
            return {"meets_sla": True, "message": "No data yet", "samples": 0}

        p90 = self._percentile(samples, 90)
        meets_sla = p90 <= target_p90_ms

        return {
            "meets_sla": meets_sla,
            "p90_ms": round(p90, 2),
            "target_ms": target_p90_ms,
            "samples": len(samples),
            "message": (
                "SLA met"
                if meets_sla
                else f"P90 ({p90:.0f}ms) exceeds target ({target_p90_ms:.0f}ms)"
            ),
        }

    @staticmethod
    def _compute_percentiles(samples: list[float]) -> dict[str, float]:
        """Compute P50, P90, P99 percentiles."""
        if not samples:
            return {"p50": 0, "p90": 0, "p99": 0, "mean": 0, "min": 0, "max": 0, "count": 0}

        sorted_samples = sorted(samples)
        return {
            "p50": round(PipelineMetricsCollector._percentile(sorted_samples, 50), 2),
            "p90": round(PipelineMetricsCollector._percentile(sorted_samples, 90), 2),
            "p99": round(PipelineMetricsCollector._percentile(sorted_samples, 99), 2),
            "mean": round(statistics.mean(sorted_samples), 2),
            "min": round(min(sorted_samples), 2),
            "max": round(max(sorted_samples), 2),
            "count": len(sorted_samples),
        }

    @staticmethod
    def _percentile(sorted_data: list[float], percentile: float) -> float:
        """Calculate a percentile from sorted data."""
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * (percentile / 100.0)
        f = int(k)
        c = f + 1
        if c >= len(sorted_data):
            return sorted_data[-1]
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


# Singleton collector
_collector: PipelineMetricsCollector | None = None


def get_metrics_collector() -> PipelineMetricsCollector:
    """Get the global metrics collector."""
    global _collector
    if _collector is None:
        _collector = PipelineMetricsCollector()
    return _collector
