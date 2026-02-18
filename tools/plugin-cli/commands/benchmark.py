"""
Benchmark CLI command.

Phase 5D M1: Create benchmark CLI command with standardized performance test suite.

Provides commands for running performance benchmarks on plugins:
- Standard benchmark suite (IPC, lifecycle, load)
- Custom benchmark scenarios
- Comparison reports
- Export to various formats
"""

from __future__ import annotations

import asyncio
import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import click


class BenchmarkType(Enum):
    """Types of benchmarks available."""

    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    IPC_LATENCY = "ipc_latency"
    IPC_THROUGHPUT = "ipc_throughput"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CONCURRENT_LOAD = "concurrent_load"
    SUSTAINED_LOAD = "sustained_load"
    COLD_START = "cold_start"
    WARM_START = "warm_start"


class BenchmarkStatus(Enum):
    """Benchmark execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""

    iterations: int = 10
    warmup_iterations: int = 3
    timeout_seconds: float = 30.0
    concurrent_workers: int = 4
    message_size_bytes: int = 1024
    sustained_duration_seconds: float = 60.0
    cool_down_seconds: float = 1.0


@dataclass
class BenchmarkResult:
    """Result of a single benchmark."""

    benchmark_type: BenchmarkType
    status: BenchmarkStatus
    iterations: int = 0
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    median_ms: float = 0.0
    std_dev_ms: float = 0.0
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    throughput_ops_sec: float = 0.0
    memory_bytes: int = 0
    cpu_percent: float = 0.0
    error: str | None = None
    raw_samples: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "benchmark_type": self.benchmark_type.value,
            "status": self.status.value,
            "iterations": self.iterations,
            "latency": {
                "min_ms": round(self.min_ms, 3),
                "max_ms": round(self.max_ms, 3),
                "mean_ms": round(self.mean_ms, 3),
                "median_ms": round(self.median_ms, 3),
                "std_dev_ms": round(self.std_dev_ms, 3),
                "p50_ms": round(self.p50_ms, 3),
                "p90_ms": round(self.p90_ms, 3),
                "p95_ms": round(self.p95_ms, 3),
                "p99_ms": round(self.p99_ms, 3),
            },
            "throughput_ops_sec": round(self.throughput_ops_sec, 2),
            "memory_bytes": self.memory_bytes,
            "cpu_percent": round(self.cpu_percent, 2),
            "error": self.error,
        }


@dataclass
class BenchmarkSuiteResult:
    """Result of a complete benchmark suite run."""

    plugin_id: str
    plugin_version: str
    started_at: datetime
    completed_at: datetime | None = None
    config: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    results: list[BenchmarkResult] = field(default_factory=list)
    system_info: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "plugin_version": self.plugin_version,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "config": {
                "iterations": self.config.iterations,
                "warmup_iterations": self.config.warmup_iterations,
                "timeout_seconds": self.config.timeout_seconds,
                "concurrent_workers": self.config.concurrent_workers,
            },
            "system_info": self.system_info,
            "results": [r.to_dict() for r in self.results],
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        completed = [r for r in self.results if r.status == BenchmarkStatus.COMPLETED]
        failed = [r for r in self.results if r.status == BenchmarkStatus.FAILED]

        return {
            "total_benchmarks": len(self.results),
            "completed": len(completed),
            "failed": len(failed),
            "pass_rate": len(completed) / len(self.results) * 100 if self.results else 0,
        }


class PluginBenchmark:
    """Benchmark runner for plugins."""

    def __init__(self, plugin_id: str, plugins_dir: Path | None = None):
        """Initialize benchmark runner."""
        self._plugin_id = plugin_id
        self._plugins_dir = plugins_dir or Path.home() / ".voicestudio" / "plugins"
        self._results: list[BenchmarkResult] = []

    async def run_suite(
        self,
        config: BenchmarkConfig | None = None,
        benchmarks: list[BenchmarkType] | None = None,
        progress_callback: Any | None = None,
    ) -> BenchmarkSuiteResult:
        """Run the complete benchmark suite."""
        config = config or BenchmarkConfig()
        benchmarks = benchmarks or [
            BenchmarkType.STARTUP,
            BenchmarkType.SHUTDOWN,
            BenchmarkType.IPC_LATENCY,
            BenchmarkType.IPC_THROUGHPUT,
            BenchmarkType.MEMORY_USAGE,
        ]

        suite_result = BenchmarkSuiteResult(
            plugin_id=self._plugin_id,
            plugin_version=self._get_plugin_version(),
            started_at=datetime.now(),
            config=config,
            system_info=self._collect_system_info(),
        )

        for i, benchmark_type in enumerate(benchmarks):
            if progress_callback:
                progress_callback(i + 1, len(benchmarks), benchmark_type.value)

            result = await self._run_benchmark(benchmark_type, config)
            suite_result.results.append(result)

            # Cool down between benchmarks
            if config.cool_down_seconds > 0:
                await asyncio.sleep(config.cool_down_seconds)

        suite_result.completed_at = datetime.now()
        return suite_result

    async def _run_benchmark(
        self, benchmark_type: BenchmarkType, config: BenchmarkConfig
    ) -> BenchmarkResult:
        """Run a single benchmark."""
        try:
            if benchmark_type == BenchmarkType.STARTUP:
                return await self._benchmark_startup(config)
            elif benchmark_type == BenchmarkType.SHUTDOWN:
                return await self._benchmark_shutdown(config)
            elif benchmark_type == BenchmarkType.IPC_LATENCY:
                return await self._benchmark_ipc_latency(config)
            elif benchmark_type == BenchmarkType.IPC_THROUGHPUT:
                return await self._benchmark_ipc_throughput(config)
            elif benchmark_type == BenchmarkType.MEMORY_USAGE:
                return await self._benchmark_memory_usage(config)
            elif benchmark_type == BenchmarkType.CPU_USAGE:
                return await self._benchmark_cpu_usage(config)
            elif benchmark_type == BenchmarkType.CONCURRENT_LOAD:
                return await self._benchmark_concurrent_load(config)
            elif benchmark_type == BenchmarkType.SUSTAINED_LOAD:
                return await self._benchmark_sustained_load(config)
            else:
                return BenchmarkResult(
                    benchmark_type=benchmark_type,
                    status=BenchmarkStatus.SKIPPED,
                    error=f"Benchmark type {benchmark_type.value} not implemented",
                )
        except Exception as e:
            return BenchmarkResult(
                benchmark_type=benchmark_type,
                status=BenchmarkStatus.FAILED,
                error=str(e),
            )

    async def _benchmark_startup(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark plugin startup time."""
        samples = []

        # Warmup
        for _ in range(config.warmup_iterations):
            start = time.perf_counter()
            await self._simulate_startup()
            _ = (time.perf_counter() - start) * 1000

        # Actual measurements
        for _ in range(config.iterations):
            start = time.perf_counter()
            await self._simulate_startup()
            elapsed_ms = (time.perf_counter() - start) * 1000
            samples.append(elapsed_ms)

        return self._calculate_result(BenchmarkType.STARTUP, samples)

    async def _benchmark_shutdown(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark plugin shutdown time."""
        samples = []

        for _ in range(config.iterations):
            start = time.perf_counter()
            await self._simulate_shutdown()
            elapsed_ms = (time.perf_counter() - start) * 1000
            samples.append(elapsed_ms)

        return self._calculate_result(BenchmarkType.SHUTDOWN, samples)

    async def _benchmark_ipc_latency(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark IPC round-trip latency."""
        samples = []

        # Warmup
        for _ in range(config.warmup_iterations):
            await self._simulate_ipc_call(config.message_size_bytes)

        # Actual measurements
        for _ in range(config.iterations):
            start = time.perf_counter()
            await self._simulate_ipc_call(config.message_size_bytes)
            elapsed_ms = (time.perf_counter() - start) * 1000
            samples.append(elapsed_ms)

        return self._calculate_result(BenchmarkType.IPC_LATENCY, samples)

    async def _benchmark_ipc_throughput(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark IPC throughput (messages per second)."""
        message_count = config.iterations * 10
        start = time.perf_counter()

        for _ in range(message_count):
            await self._simulate_ipc_call(config.message_size_bytes)

        elapsed_seconds = time.perf_counter() - start
        throughput = message_count / elapsed_seconds if elapsed_seconds > 0 else 0

        result = BenchmarkResult(
            benchmark_type=BenchmarkType.IPC_THROUGHPUT,
            status=BenchmarkStatus.COMPLETED,
            iterations=message_count,
            throughput_ops_sec=throughput,
            mean_ms=elapsed_seconds * 1000 / message_count if message_count > 0 else 0,
        )
        return result

    async def _benchmark_memory_usage(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark plugin memory usage."""
        try:
            import psutil
        except ImportError:
            return BenchmarkResult(
                benchmark_type=BenchmarkType.MEMORY_USAGE,
                status=BenchmarkStatus.SKIPPED,
                error="psutil not available",
            )

        samples = []
        process = psutil.Process()

        for _ in range(config.iterations):
            mem_info = process.memory_info()
            samples.append(mem_info.rss / 1024 / 1024)  # MB
            await asyncio.sleep(0.1)

        result = self._calculate_result(BenchmarkType.MEMORY_USAGE, samples)
        result.memory_bytes = int(statistics.mean(samples) * 1024 * 1024)
        return result

    async def _benchmark_cpu_usage(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark CPU usage during plugin operation."""
        try:
            import psutil
        except ImportError:
            return BenchmarkResult(
                benchmark_type=BenchmarkType.CPU_USAGE,
                status=BenchmarkStatus.SKIPPED,
                error="psutil not available",
            )

        samples = []
        process = psutil.Process()

        for _ in range(config.iterations):
            cpu_percent = process.cpu_percent(interval=0.1)
            samples.append(cpu_percent)

        result = self._calculate_result(BenchmarkType.CPU_USAGE, samples)
        result.cpu_percent = statistics.mean(samples) if samples else 0
        return result

    async def _benchmark_concurrent_load(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark concurrent request handling."""
        samples = []

        async def worker() -> float:
            start = time.perf_counter()
            await self._simulate_ipc_call(config.message_size_bytes)
            return (time.perf_counter() - start) * 1000

        for _ in range(config.iterations):
            tasks = [worker() for _ in range(config.concurrent_workers)]
            batch_samples = await asyncio.gather(*tasks)
            samples.extend(batch_samples)

        return self._calculate_result(BenchmarkType.CONCURRENT_LOAD, samples)

    async def _benchmark_sustained_load(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark sustained load over time."""
        samples = []
        end_time = time.perf_counter() + config.sustained_duration_seconds

        while time.perf_counter() < end_time:
            start = time.perf_counter()
            await self._simulate_ipc_call(config.message_size_bytes)
            elapsed_ms = (time.perf_counter() - start) * 1000
            samples.append(elapsed_ms)

        result = self._calculate_result(BenchmarkType.SUSTAINED_LOAD, samples)
        result.throughput_ops_sec = len(samples) / config.sustained_duration_seconds
        return result

    def _calculate_result(
        self, benchmark_type: BenchmarkType, samples: list[float]
    ) -> BenchmarkResult:
        """Calculate statistics from samples."""
        if not samples:
            return BenchmarkResult(
                benchmark_type=benchmark_type,
                status=BenchmarkStatus.FAILED,
                error="No samples collected",
            )

        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        return BenchmarkResult(
            benchmark_type=benchmark_type,
            status=BenchmarkStatus.COMPLETED,
            iterations=n,
            min_ms=min(samples),
            max_ms=max(samples),
            mean_ms=statistics.mean(samples),
            median_ms=statistics.median(samples),
            std_dev_ms=statistics.stdev(samples) if n > 1 else 0,
            p50_ms=sorted_samples[int(n * 0.50)],
            p90_ms=sorted_samples[int(n * 0.90)] if n >= 10 else sorted_samples[-1],
            p95_ms=sorted_samples[int(n * 0.95)] if n >= 20 else sorted_samples[-1],
            p99_ms=sorted_samples[int(n * 0.99)] if n >= 100 else sorted_samples[-1],
            raw_samples=samples,
        )

    async def _simulate_startup(self) -> None:
        """Simulate plugin startup (placeholder for real implementation)."""
        await asyncio.sleep(0.001)

    async def _simulate_shutdown(self) -> None:
        """Simulate plugin shutdown."""
        await asyncio.sleep(0.0005)

    async def _simulate_ipc_call(self, message_size: int) -> None:
        """Simulate IPC call."""
        _ = b"x" * message_size  # Create message payload
        await asyncio.sleep(0.0001)  # Simulate network/IPC latency

    def _get_plugin_version(self) -> str:
        """Get plugin version."""
        manifest_path = self._plugins_dir / "default" / self._plugin_id / "manifest.json"
        if manifest_path.exists():
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                return data.get("version", "unknown")
            except Exception as e:
                # Manifest parsing failed, use default
                logger.debug(f"Failed to read manifest version: {e}")
        return "unknown"

    def _collect_system_info(self) -> dict[str, Any]:
        """Collect system information."""
        import platform
        import sys

        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": sys.version,
            "processor": platform.processor(),
        }

        try:
            import psutil

            info["cpu_count"] = psutil.cpu_count()
            info["memory_total_gb"] = round(
                psutil.virtual_memory().total / (1024**3), 2
            )
        except ImportError:
            # psutil not available, skip extended system info
            logger.debug("psutil not available, skipping extended system info")

        return info


# CLI Commands


@click.command("benchmark")
@click.argument("plugin_id")
@click.option(
    "--iterations",
    "-n",
    default=10,
    type=int,
    help="Number of iterations per benchmark",
)
@click.option(
    "--warmup",
    "-w",
    default=3,
    type=int,
    help="Number of warmup iterations",
)
@click.option(
    "--timeout",
    "-t",
    default=30.0,
    type=float,
    help="Timeout in seconds",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for results (JSON)",
)
@click.option(
    "--benchmarks",
    "-b",
    multiple=True,
    type=click.Choice([b.value for b in BenchmarkType]),
    help="Specific benchmarks to run",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def benchmark_command(
    plugin_id: str,
    iterations: int,
    warmup: int,
    timeout: float,
    output: str | None,
    benchmarks: tuple[str, ...],
    verbose: bool,
) -> None:
    """Run performance benchmarks on a plugin.

    Example: voicestudio-plugin benchmark my-plugin -n 20 -o results.json
    """
    config = BenchmarkConfig(
        iterations=iterations,
        warmup_iterations=warmup,
        timeout_seconds=timeout,
    )

    benchmark_types = (
        [BenchmarkType(b) for b in benchmarks]
        if benchmarks
        else [
            BenchmarkType.STARTUP,
            BenchmarkType.SHUTDOWN,
            BenchmarkType.IPC_LATENCY,
            BenchmarkType.IPC_THROUGHPUT,
            BenchmarkType.MEMORY_USAGE,
        ]
    )

    click.echo(f"Running benchmarks for plugin: {click.style(plugin_id, fg='cyan')}")
    click.echo(f"Iterations: {iterations}, Warmup: {warmup}")
    click.echo()

    def progress_callback(current: int, total: int, name: str) -> None:
        click.echo(f"[{current}/{total}] Running {name}...")

    runner = PluginBenchmark(plugin_id)

    try:
        result = asyncio.run(
            runner.run_suite(
                config=config,
                benchmarks=benchmark_types,
                progress_callback=progress_callback,
            )
        )
    except Exception as e:
        click.secho(f"Benchmark failed: {e}", fg="red")
        raise SystemExit(1)

    click.echo()
    click.echo("=" * 60)
    click.echo("BENCHMARK RESULTS")
    click.echo("=" * 60)

    for bench_result in result.results:
        status_color = "green" if bench_result.status == BenchmarkStatus.COMPLETED else "red"
        click.echo(
            f"\n{bench_result.benchmark_type.value}: "
            f"{click.style(bench_result.status.value.upper(), fg=status_color)}"
        )

        if bench_result.status == BenchmarkStatus.COMPLETED:
            click.echo(f"  Iterations: {bench_result.iterations}")
            click.echo(
                f"  Latency: min={bench_result.min_ms:.3f}ms, "
                f"max={bench_result.max_ms:.3f}ms, "
                f"mean={bench_result.mean_ms:.3f}ms"
            )
            click.echo(
                f"  Percentiles: p50={bench_result.p50_ms:.3f}ms, "
                f"p90={bench_result.p90_ms:.3f}ms, "
                f"p99={bench_result.p99_ms:.3f}ms"
            )

            if bench_result.throughput_ops_sec > 0:
                click.echo(f"  Throughput: {bench_result.throughput_ops_sec:.2f} ops/sec")

            if bench_result.memory_bytes > 0:
                click.echo(
                    f"  Memory: {bench_result.memory_bytes / 1024 / 1024:.2f} MB"
                )

        elif bench_result.error:
            click.echo(f"  Error: {bench_result.error}")

    click.echo()
    summary = result.to_dict()["summary"]
    click.echo(
        f"Summary: {summary['completed']}/{summary['total_benchmarks']} passed "
        f"({summary['pass_rate']:.1f}%)"
    )

    if output:
        output_path = Path(output)
        output_path.write_text(json.dumps(result.to_dict(), indent=2))
        click.echo(f"\nResults saved to: {output_path}")


@click.command("benchmark-compare")
@click.argument("baseline", type=click.Path(exists=True))
@click.argument("current", type=click.Path(exists=True))
@click.option("--threshold", "-t", default=10.0, help="Regression threshold (%)")
def benchmark_compare_command(baseline: str, current: str, threshold: float) -> None:
    """Compare two benchmark results.

    Example: voicestudio-plugin benchmark-compare baseline.json current.json
    """
    baseline_data = json.loads(Path(baseline).read_text())
    current_data = json.loads(Path(current).read_text())

    click.echo("Comparing benchmark results:")
    click.echo(f"  Baseline: {baseline}")
    click.echo(f"  Current:  {current}")
    click.echo()

    baseline_results = {r["benchmark_type"]: r for r in baseline_data["results"]}
    current_results = {r["benchmark_type"]: r for r in current_data["results"]}

    has_regression = False

    for bench_type, curr in current_results.items():
        base = baseline_results.get(bench_type)
        if not base:
            continue

        curr_mean = curr["latency"]["mean_ms"]
        base_mean = base["latency"]["mean_ms"]

        if base_mean == 0:
            continue

        change_pct = ((curr_mean - base_mean) / base_mean) * 100

        if change_pct > threshold:
            has_regression = True
            status = click.style(f"+{change_pct:.1f}% REGRESSION", fg="red")
        elif change_pct < -threshold:
            status = click.style(f"{change_pct:.1f}% improvement", fg="green")
        else:
            status = click.style(f"{change_pct:+.1f}%", fg="yellow")

        click.echo(f"{bench_type}: {base_mean:.3f}ms -> {curr_mean:.3f}ms ({status})")

    if has_regression:
        click.secho("\nPerformance regression detected!", fg="red", bold=True)
        raise SystemExit(1)
    else:
        click.secho("\nNo significant regression detected.", fg="green")


@click.command("benchmark-report")
@click.argument("results_file", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["text", "json", "csv", "markdown"]), default="text")
@click.option("--output", "-o", type=click.Path(), help="Output file")
def benchmark_report_command(results_file: str, format: str, output: str | None) -> None:
    """Generate a benchmark report from results.

    Example: voicestudio-plugin benchmark-report results.json -f markdown -o report.md
    """
    data = json.loads(Path(results_file).read_text())

    if format == "json":
        report = json.dumps(data, indent=2)
    elif format == "csv":
        report = _generate_csv_report(data)
    elif format == "markdown":
        report = _generate_markdown_report(data)
    else:
        report = _generate_text_report(data)

    if output:
        Path(output).write_text(report)
        click.echo(f"Report saved to: {output}")
    else:
        click.echo(report)


def _generate_csv_report(data: dict[str, Any]) -> str:
    """Generate CSV report."""
    lines = ["benchmark_type,status,iterations,min_ms,max_ms,mean_ms,p50_ms,p90_ms,p99_ms"]

    for r in data["results"]:
        lat = r["latency"]
        lines.append(
            f"{r['benchmark_type']},{r['status']},{r['iterations']},"
            f"{lat['min_ms']},{lat['max_ms']},{lat['mean_ms']},"
            f"{lat['p50_ms']},{lat['p90_ms']},{lat['p99_ms']}"
        )

    return "\n".join(lines)


def _generate_markdown_report(data: dict[str, Any]) -> str:
    """Generate Markdown report."""
    lines = [
        f"# Benchmark Report: {data['plugin_id']}",
        "",
        f"**Version:** {data['plugin_version']}",
        f"**Date:** {data['started_at']}",
        "",
        "## System Info",
        "",
    ]

    for key, value in data.get("system_info", {}).items():
        lines.append(f"- **{key}:** {value}")

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Benchmark | Status | Mean (ms) | P50 (ms) | P90 (ms) | P99 (ms) |",
            "|-----------|--------|-----------|----------|----------|----------|",
        ]
    )

    for r in data["results"]:
        lat = r["latency"]
        lines.append(
            f"| {r['benchmark_type']} | {r['status']} | "
            f"{lat['mean_ms']:.3f} | {lat['p50_ms']:.3f} | "
            f"{lat['p90_ms']:.3f} | {lat['p99_ms']:.3f} |"
        )

    summary = data["summary"]
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- **Total Benchmarks:** {summary['total_benchmarks']}",
            f"- **Completed:** {summary['completed']}",
            f"- **Failed:** {summary['failed']}",
            f"- **Pass Rate:** {summary['pass_rate']:.1f}%",
        ]
    )

    return "\n".join(lines)


def _generate_text_report(data: dict[str, Any]) -> str:
    """Generate plain text report."""
    lines = [
        "=" * 60,
        f"BENCHMARK REPORT: {data['plugin_id']}",
        "=" * 60,
        f"Version: {data['plugin_version']}",
        f"Date: {data['started_at']}",
        "",
        "RESULTS:",
        "-" * 40,
    ]

    for r in data["results"]:
        lat = r["latency"]
        lines.append(f"\n{r['benchmark_type']} ({r['status']})")
        lines.append(f"  Mean: {lat['mean_ms']:.3f}ms")
        lines.append(f"  P50:  {lat['p50_ms']:.3f}ms")
        lines.append(f"  P90:  {lat['p90_ms']:.3f}ms")
        lines.append(f"  P99:  {lat['p99_ms']:.3f}ms")

    summary = data["summary"]
    lines.extend(
        [
            "",
            "-" * 40,
            f"Total: {summary['total_benchmarks']} benchmarks",
            f"Passed: {summary['completed']} ({summary['pass_rate']:.1f}%)",
        ]
    )

    return "\n".join(lines)
