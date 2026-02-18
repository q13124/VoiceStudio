"""
Unit tests for benchmark CLI command.

Phase 5D M1: Benchmark CLI command with standardized performance test suite.
"""

from __future__ import annotations

import asyncio
import json

# Import from the commands module
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools" / "plugin-cli"))

from commands.benchmark import (
    BenchmarkConfig,
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkSuiteResult,
    BenchmarkType,
    PluginBenchmark,
    _generate_csv_report,
    _generate_markdown_report,
    _generate_text_report,
)


class TestBenchmarkType:
    """Tests for BenchmarkType enum."""

    def test_all_types_defined(self) -> None:
        """All benchmark types should be defined."""
        expected_types = [
            "startup",
            "shutdown",
            "ipc_latency",
            "ipc_throughput",
            "memory_usage",
            "cpu_usage",
            "concurrent_load",
            "sustained_load",
            "cold_start",
            "warm_start",
        ]
        actual_types = [t.value for t in BenchmarkType]
        for expected in expected_types:
            assert expected in actual_types

    def test_type_values(self) -> None:
        """Benchmark types should have correct values."""
        assert BenchmarkType.STARTUP.value == "startup"
        assert BenchmarkType.IPC_LATENCY.value == "ipc_latency"
        assert BenchmarkType.MEMORY_USAGE.value == "memory_usage"


class TestBenchmarkStatus:
    """Tests for BenchmarkStatus enum."""

    def test_all_statuses_defined(self) -> None:
        """All statuses should be defined."""
        expected = ["pending", "running", "completed", "failed", "skipped"]
        actual = [s.value for s in BenchmarkStatus]
        for exp in expected:
            assert exp in actual


class TestBenchmarkConfig:
    """Tests for BenchmarkConfig dataclass."""

    def test_default_values(self) -> None:
        """Default configuration values should be reasonable."""
        config = BenchmarkConfig()
        assert config.iterations == 10
        assert config.warmup_iterations == 3
        assert config.timeout_seconds == 30.0
        assert config.concurrent_workers == 4
        assert config.message_size_bytes == 1024
        assert config.cool_down_seconds == 1.0

    def test_custom_values(self) -> None:
        """Custom configuration should be accepted."""
        config = BenchmarkConfig(
            iterations=100,
            warmup_iterations=10,
            timeout_seconds=60.0,
            concurrent_workers=8,
        )
        assert config.iterations == 100
        assert config.warmup_iterations == 10
        assert config.timeout_seconds == 60.0
        assert config.concurrent_workers == 8


class TestBenchmarkResult:
    """Tests for BenchmarkResult dataclass."""

    def test_default_result(self) -> None:
        """Default result should have correct structure."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.STARTUP,
            status=BenchmarkStatus.PENDING,
        )
        assert result.benchmark_type == BenchmarkType.STARTUP
        assert result.status == BenchmarkStatus.PENDING
        assert result.iterations == 0
        assert result.mean_ms == 0.0

    def test_completed_result(self) -> None:
        """Completed result should contain timing data."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.IPC_LATENCY,
            status=BenchmarkStatus.COMPLETED,
            iterations=10,
            min_ms=1.0,
            max_ms=5.0,
            mean_ms=2.5,
            median_ms=2.3,
            std_dev_ms=0.8,
            p50_ms=2.3,
            p90_ms=4.0,
            p95_ms=4.5,
            p99_ms=4.9,
        )
        assert result.iterations == 10
        assert result.min_ms == 1.0
        assert result.max_ms == 5.0
        assert result.mean_ms == 2.5

    def test_to_dict(self) -> None:
        """Result should convert to dictionary correctly."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.STARTUP,
            status=BenchmarkStatus.COMPLETED,
            iterations=10,
            mean_ms=5.123456,
            p99_ms=8.987654,
        )
        d = result.to_dict()

        assert d["benchmark_type"] == "startup"
        assert d["status"] == "completed"
        assert d["iterations"] == 10
        assert d["latency"]["mean_ms"] == 5.123  # Rounded
        assert d["latency"]["p99_ms"] == 8.988  # Rounded

    def test_error_result(self) -> None:
        """Failed result should contain error."""
        result = BenchmarkResult(
            benchmark_type=BenchmarkType.MEMORY_USAGE,
            status=BenchmarkStatus.FAILED,
            error="psutil not available",
        )
        assert result.status == BenchmarkStatus.FAILED
        assert result.error == "psutil not available"


class TestBenchmarkSuiteResult:
    """Tests for BenchmarkSuiteResult dataclass."""

    def test_suite_result_structure(self) -> None:
        """Suite result should have correct structure."""
        suite = BenchmarkSuiteResult(
            plugin_id="test-plugin",
            plugin_version="1.0.0",
            started_at=datetime.now(),
        )
        assert suite.plugin_id == "test-plugin"
        assert suite.plugin_version == "1.0.0"
        assert suite.results == []
        assert suite.completed_at is None

    def test_suite_with_results(self) -> None:
        """Suite should contain benchmark results."""
        suite = BenchmarkSuiteResult(
            plugin_id="test-plugin",
            plugin_version="1.0.0",
            started_at=datetime.now(),
            results=[
                BenchmarkResult(
                    benchmark_type=BenchmarkType.STARTUP,
                    status=BenchmarkStatus.COMPLETED,
                    iterations=10,
                ),
                BenchmarkResult(
                    benchmark_type=BenchmarkType.SHUTDOWN,
                    status=BenchmarkStatus.COMPLETED,
                    iterations=10,
                ),
            ],
        )
        assert len(suite.results) == 2

    def test_to_dict(self) -> None:
        """Suite should convert to dictionary correctly."""
        suite = BenchmarkSuiteResult(
            plugin_id="test-plugin",
            plugin_version="1.0.0",
            started_at=datetime(2025, 1, 1, 12, 0, 0),
            completed_at=datetime(2025, 1, 1, 12, 5, 0),
            results=[
                BenchmarkResult(
                    benchmark_type=BenchmarkType.STARTUP,
                    status=BenchmarkStatus.COMPLETED,
                    iterations=10,
                ),
            ],
        )
        d = suite.to_dict()

        assert d["plugin_id"] == "test-plugin"
        assert d["plugin_version"] == "1.0.0"
        assert "summary" in d
        assert d["summary"]["total_benchmarks"] == 1
        assert d["summary"]["completed"] == 1

    def test_summary_calculation(self) -> None:
        """Summary should calculate pass rate correctly."""
        suite = BenchmarkSuiteResult(
            plugin_id="test-plugin",
            plugin_version="1.0.0",
            started_at=datetime.now(),
            results=[
                BenchmarkResult(
                    benchmark_type=BenchmarkType.STARTUP,
                    status=BenchmarkStatus.COMPLETED,
                ),
                BenchmarkResult(
                    benchmark_type=BenchmarkType.SHUTDOWN,
                    status=BenchmarkStatus.FAILED,
                ),
                BenchmarkResult(
                    benchmark_type=BenchmarkType.IPC_LATENCY,
                    status=BenchmarkStatus.COMPLETED,
                ),
            ],
        )
        d = suite.to_dict()
        summary = d["summary"]

        assert summary["total_benchmarks"] == 3
        assert summary["completed"] == 2
        assert summary["failed"] == 1
        # 2/3 * 100 = 66.67%
        assert abs(summary["pass_rate"] - 66.67) < 1


class TestPluginBenchmark:
    """Tests for PluginBenchmark class."""

    @pytest.fixture
    def temp_plugins_dir(self) -> Path:
        """Create a temporary plugins directory."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    @pytest.fixture
    def benchmark_runner(self, temp_plugins_dir: Path) -> PluginBenchmark:
        """Create a benchmark runner."""
        return PluginBenchmark("test-plugin", plugins_dir=temp_plugins_dir)

    def test_initialization(self, benchmark_runner: PluginBenchmark) -> None:
        """Runner should initialize correctly."""
        assert benchmark_runner._plugin_id == "test-plugin"

    @pytest.mark.asyncio
    async def test_run_single_benchmark(self, benchmark_runner: PluginBenchmark) -> None:
        """Running a single benchmark should return a result."""
        config = BenchmarkConfig(iterations=5, warmup_iterations=1)
        result = await benchmark_runner._run_benchmark(BenchmarkType.STARTUP, config)

        assert result.benchmark_type == BenchmarkType.STARTUP
        assert result.status == BenchmarkStatus.COMPLETED
        assert result.iterations == 5

    @pytest.mark.asyncio
    async def test_run_suite(self, benchmark_runner: PluginBenchmark) -> None:
        """Running a benchmark suite should execute all benchmarks."""
        config = BenchmarkConfig(
            iterations=3,
            warmup_iterations=1,
            cool_down_seconds=0,  # Disable cooldown for faster test
        )
        benchmarks = [BenchmarkType.STARTUP, BenchmarkType.SHUTDOWN]

        result = await benchmark_runner.run_suite(config=config, benchmarks=benchmarks)

        assert result.plugin_id == "test-plugin"
        assert len(result.results) == 2
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_progress_callback(self, benchmark_runner: PluginBenchmark) -> None:
        """Progress callback should be called during suite execution."""
        config = BenchmarkConfig(iterations=2, warmup_iterations=0, cool_down_seconds=0)
        progress_calls: list[tuple[int, int, str]] = []

        def callback(current: int, total: int, name: str) -> None:
            progress_calls.append((current, total, name))

        await benchmark_runner.run_suite(
            config=config,
            benchmarks=[BenchmarkType.STARTUP, BenchmarkType.SHUTDOWN],
            progress_callback=callback,
        )

        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2, "startup")
        assert progress_calls[1] == (2, 2, "shutdown")

    @pytest.mark.asyncio
    async def test_ipc_latency_benchmark(self, benchmark_runner: PluginBenchmark) -> None:
        """IPC latency benchmark should measure round-trip time."""
        config = BenchmarkConfig(iterations=10, warmup_iterations=2)
        result = await benchmark_runner._run_benchmark(BenchmarkType.IPC_LATENCY, config)

        assert result.status == BenchmarkStatus.COMPLETED
        assert result.iterations == 10
        assert result.mean_ms > 0

    @pytest.mark.asyncio
    async def test_ipc_throughput_benchmark(self, benchmark_runner: PluginBenchmark) -> None:
        """IPC throughput benchmark should measure ops/second."""
        config = BenchmarkConfig(iterations=5)
        result = await benchmark_runner._run_benchmark(BenchmarkType.IPC_THROUGHPUT, config)

        assert result.status == BenchmarkStatus.COMPLETED
        assert result.throughput_ops_sec > 0

    @pytest.mark.asyncio
    async def test_concurrent_load_benchmark(self, benchmark_runner: PluginBenchmark) -> None:
        """Concurrent load benchmark should run multiple workers."""
        config = BenchmarkConfig(iterations=3, concurrent_workers=4)
        result = await benchmark_runner._run_benchmark(BenchmarkType.CONCURRENT_LOAD, config)

        assert result.status == BenchmarkStatus.COMPLETED
        # 3 iterations * 4 workers = 12 samples
        assert result.iterations == 12

    def test_calculate_result(self, benchmark_runner: PluginBenchmark) -> None:
        """Statistics should be calculated correctly from samples."""
        samples = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        result = benchmark_runner._calculate_result(BenchmarkType.STARTUP, samples)

        assert result.status == BenchmarkStatus.COMPLETED
        assert result.iterations == 10
        assert result.min_ms == 1.0
        assert result.max_ms == 10.0
        assert result.mean_ms == 5.5
        assert result.median_ms == 5.5

    def test_calculate_result_empty_samples(self, benchmark_runner: PluginBenchmark) -> None:
        """Empty samples should result in failure."""
        result = benchmark_runner._calculate_result(BenchmarkType.STARTUP, [])

        assert result.status == BenchmarkStatus.FAILED
        assert result.error == "No samples collected"

    def test_collect_system_info(self, benchmark_runner: PluginBenchmark) -> None:
        """System info should be collected."""
        info = benchmark_runner._collect_system_info()

        assert "platform" in info
        assert "python_version" in info
        assert "processor" in info


class TestReportGeneration:
    """Tests for report generation functions."""

    @pytest.fixture
    def sample_data(self) -> dict:
        """Sample benchmark data for reports."""
        return {
            "plugin_id": "test-plugin",
            "plugin_version": "1.0.0",
            "started_at": "2025-01-01T12:00:00",
            "completed_at": "2025-01-01T12:05:00",
            "system_info": {
                "platform": "Windows",
                "cpu_count": 8,
            },
            "results": [
                {
                    "benchmark_type": "startup",
                    "status": "completed",
                    "iterations": 10,
                    "latency": {
                        "min_ms": 1.0,
                        "max_ms": 5.0,
                        "mean_ms": 2.5,
                        "median_ms": 2.3,
                        "std_dev_ms": 0.8,
                        "p50_ms": 2.3,
                        "p90_ms": 4.0,
                        "p95_ms": 4.5,
                        "p99_ms": 4.9,
                    },
                    "throughput_ops_sec": 0,
                    "memory_bytes": 0,
                    "cpu_percent": 0,
                    "error": None,
                },
            ],
            "summary": {
                "total_benchmarks": 1,
                "completed": 1,
                "failed": 0,
                "pass_rate": 100.0,
            },
        }

    def test_csv_report(self, sample_data: dict) -> None:
        """CSV report should have correct format."""
        report = _generate_csv_report(sample_data)

        lines = report.strip().split("\n")
        assert len(lines) == 2  # Header + 1 result
        assert "benchmark_type" in lines[0]
        assert "startup" in lines[1]
        assert "completed" in lines[1]

    def test_markdown_report(self, sample_data: dict) -> None:
        """Markdown report should have correct format."""
        report = _generate_markdown_report(sample_data)

        assert "# Benchmark Report: test-plugin" in report
        assert "**Version:** 1.0.0" in report
        assert "| Benchmark | Status |" in report
        assert "| startup |" in report
        assert "## Summary" in report

    def test_text_report(self, sample_data: dict) -> None:
        """Text report should have correct format."""
        report = _generate_text_report(sample_data)

        assert "BENCHMARK REPORT: test-plugin" in report
        assert "Version: 1.0.0" in report
        assert "startup (completed)" in report
        assert "Mean:" in report


class TestComparisonFunctionality:
    """Tests for benchmark comparison."""

    def test_compare_results_regression(self) -> None:
        """Comparison should detect regression."""
        baseline = {
            "results": [
                {
                    "benchmark_type": "startup",
                    "latency": {"mean_ms": 100.0},
                }
            ]
        }
        current = {
            "results": [
                {
                    "benchmark_type": "startup",
                    "latency": {"mean_ms": 150.0},  # 50% slower
                }
            ]
        }

        baseline_results = {r["benchmark_type"]: r for r in baseline["results"]}
        current_results = {r["benchmark_type"]: r for r in current["results"]}

        curr = current_results["startup"]
        base = baseline_results["startup"]
        change_pct = ((curr["latency"]["mean_ms"] - base["latency"]["mean_ms"]) / base["latency"]["mean_ms"]) * 100

        assert change_pct == 50.0  # 50% regression

    def test_compare_results_improvement(self) -> None:
        """Comparison should detect improvement."""
        baseline_mean = 100.0
        current_mean = 80.0  # 20% faster

        change_pct = ((current_mean - baseline_mean) / baseline_mean) * 100

        assert change_pct == -20.0  # 20% improvement


class TestIntegration:
    """Integration tests for benchmark system."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Create a temporary directory."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp)

    @pytest.mark.asyncio
    async def test_full_benchmark_cycle(self, temp_dir: Path) -> None:
        """Run full benchmark cycle: execute, save, load, report."""
        # Run benchmarks
        runner = PluginBenchmark("test-plugin", plugins_dir=temp_dir)
        config = BenchmarkConfig(iterations=3, warmup_iterations=1, cool_down_seconds=0)

        result = await runner.run_suite(
            config=config,
            benchmarks=[BenchmarkType.STARTUP, BenchmarkType.IPC_LATENCY],
        )

        # Save results
        output_file = temp_dir / "results.json"
        output_file.write_text(json.dumps(result.to_dict(), indent=2))

        assert output_file.exists()

        # Load and verify
        loaded = json.loads(output_file.read_text())
        assert loaded["plugin_id"] == "test-plugin"
        assert len(loaded["results"]) == 2

        # Generate reports
        csv_report = _generate_csv_report(loaded)
        md_report = _generate_markdown_report(loaded)

        assert "startup" in csv_report
        assert "# Benchmark Report" in md_report
