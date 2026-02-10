"""
Pipeline Metrics Unit Tests (Phase 14.1.3)
"""

import pytest

from app.core.pipeline.metrics import (
    PipelineExecutionMetrics,
    PipelineMetricsCollector,
    StageMetric,
)


class TestPipelineMetricsCollector:
    """Tests for metrics collection and aggregation."""

    def setup_method(self):
        self.collector = PipelineMetricsCollector(window_size=50)

    def test_empty_summary(self):
        summary = self.collector.get_summary()
        assert summary["total_executions"] == 0
        assert summary["error_count"] == 0

    def test_record_execution(self):
        metrics = PipelineExecutionMetrics(
            execution_id="test-1",
            mode="streaming",
            total_latency_ms=500.0,
            time_to_first_token_ms=100.0,
        )
        self.collector.record(metrics)
        summary = self.collector.get_summary()
        assert summary["total_executions"] == 1

    def test_percentile_computation(self):
        for i in range(100):
            metrics = PipelineExecutionMetrics(
                execution_id=f"test-{i}",
                mode="batch",
                total_latency_ms=float(i * 10),
            )
            self.collector.record(metrics)

        summary = self.collector.get_summary()
        assert summary["total_latency"]["p50"] > 0
        assert summary["total_latency"]["p90"] > summary["total_latency"]["p50"]

    def test_sla_check_passes(self):
        for _ in range(10):
            self.collector.record(PipelineExecutionMetrics(
                execution_id="t",
                mode="streaming",
                total_latency_ms=400.0,
            ))
        sla = self.collector.check_sla(target_p90_ms=800.0)
        assert sla["meets_sla"] is True

    def test_sla_check_fails(self):
        for _ in range(10):
            self.collector.record(PipelineExecutionMetrics(
                execution_id="t",
                mode="batch",
                total_latency_ms=1200.0,
            ))
        sla = self.collector.check_sla(target_p90_ms=800.0)
        assert sla["meets_sla"] is False

    def test_stage_metrics(self):
        metrics = PipelineExecutionMetrics(
            execution_id="test-1",
            mode="batch",
            stages=[
                StageMetric(stage="stt", latency_ms=100.0),
                StageMetric(stage="llm", latency_ms=300.0),
                StageMetric(stage="tts", latency_ms=200.0),
            ],
        )
        self.collector.record(metrics)
        summary = self.collector.get_summary()
        assert summary["stages"]["stt"]["count"] == 1
        assert summary["stages"]["llm"]["mean"] == 300.0
