"""
VoiceStudio Soak Test Suite

This module performs soak testing to verify system stability under repeated operations.
The test ensures:
- No memory leaks over 100 operations
- No latency degradation
- No crashes or hung operations
- Resource cleanup after each operation

Usage:
    python -m pytest tests/soak/test_soak_operations.py -v --tb=short
    python -m pytest tests/soak/test_soak_operations.py::test_soak_synthesis -v
"""

import gc
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from statistics import mean
from typing import Any

import psutil
import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

logger = logging.getLogger(__name__)


@dataclass
class SoakTestMetrics:
    """Metrics collected during soak testing."""

    operation_count: int = 0
    successful_count: int = 0
    failed_count: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    memory_samples_mb: list[float] = field(default_factory=list)
    start_memory_mb: float = 0.0
    end_memory_mb: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.operation_count == 0:
            return 0.0
        return self.successful_count / self.operation_count * 100

    @property
    def avg_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        return mean(self.latencies_ms)

    @property
    def p99_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.99)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    @property
    def memory_growth_mb(self) -> float:
        return self.end_memory_mb - self.start_memory_mb

    @property
    def latency_degradation_ratio(self) -> float:
        """Ratio of final latency to initial latency (>2.0 is concerning)."""
        if len(self.latencies_ms) < 10:
            return 1.0
        initial_avg = mean(self.latencies_ms[:10])
        final_avg = mean(self.latencies_ms[-10:])
        if initial_avg == 0:
            return 1.0
        return final_avg / initial_avg

    def to_report(self) -> str:
        """Generate a human-readable report."""
        lines = [
            "=" * 60,
            "SOAK TEST RESULTS",
            "=" * 60,
            f"Operations: {self.operation_count}",
            f"Success Rate: {self.success_rate:.1f}% ({self.successful_count}/{self.operation_count})",
            f"Failed: {self.failed_count}",
            "",
            "Latency Metrics:",
            f"  Average: {self.avg_latency_ms:.2f} ms",
            f"  P99: {self.p99_latency_ms:.2f} ms",
            f"  Degradation Ratio: {self.latency_degradation_ratio:.2f}x",
            "",
            "Memory Metrics:",
            f"  Start: {self.start_memory_mb:.2f} MB",
            f"  End: {self.end_memory_mb:.2f} MB",
            f"  Growth: {self.memory_growth_mb:.2f} MB",
            "",
        ]

        if self.errors:
            lines.append("Errors:")
            for err in self.errors[:10]:  # Show first 10 errors
                lines.append(f"  - {err}")
            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more")

        lines.append("=" * 60)
        return "\n".join(lines)


def get_process_memory_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


class SoakTestRunner:
    """Runs soak tests with metrics collection."""

    def __init__(
        self,
        operation_count: int = 100,
        warmup_count: int = 5,
        gc_interval: int = 20,
    ):
        self.operation_count = operation_count
        self.warmup_count = warmup_count
        self.gc_interval = gc_interval
        self.metrics = SoakTestMetrics()

    async def run_async(
        self,
        operation: Any,
        operation_name: str = "operation",
    ) -> SoakTestMetrics:
        """Run async soak test."""

        logger.info(f"Starting soak test: {operation_name}")
        logger.info(f"Operations: {self.operation_count}, Warmup: {self.warmup_count}")

        # Warmup phase
        logger.info("Running warmup...")
        for i in range(self.warmup_count):
            try:
                await operation()
            except Exception as e:
                logger.warning(f"Warmup {i} failed: {e}")

        # Force GC before measurement
        gc.collect()
        self.metrics.start_memory_mb = get_process_memory_mb()

        # Main test phase
        logger.info("Running main test phase...")
        for i in range(self.operation_count):
            self.metrics.operation_count += 1

            # Measure operation
            start_time = time.perf_counter()
            try:
                await operation()
                self.metrics.successful_count += 1
            except Exception as e:
                self.metrics.failed_count += 1
                self.metrics.errors.append(f"Op {i}: {type(e).__name__}: {e}")

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.latencies_ms.append(elapsed_ms)

            # Sample memory
            self.metrics.memory_samples_mb.append(get_process_memory_mb())

            # Periodic GC to simulate realistic cleanup
            if (i + 1) % self.gc_interval == 0:
                gc.collect()
                logger.info(f"Progress: {i + 1}/{self.operation_count}")

        # Final GC and measurement
        gc.collect()
        self.metrics.end_memory_mb = get_process_memory_mb()

        logger.info("Soak test complete")
        logger.info(self.metrics.to_report())

        return self.metrics

    def run_sync(
        self,
        operation: Any,
        operation_name: str = "operation",
    ) -> SoakTestMetrics:
        """Run sync soak test."""
        logger.info(f"Starting soak test: {operation_name}")
        logger.info(f"Operations: {self.operation_count}, Warmup: {self.warmup_count}")

        # Warmup phase
        logger.info("Running warmup...")
        for i in range(self.warmup_count):
            try:
                operation()
            except Exception as e:
                logger.warning(f"Warmup {i} failed: {e}")

        # Force GC before measurement
        gc.collect()
        self.metrics.start_memory_mb = get_process_memory_mb()

        # Main test phase
        logger.info("Running main test phase...")
        for i in range(self.operation_count):
            self.metrics.operation_count += 1

            # Measure operation
            start_time = time.perf_counter()
            try:
                operation()
                self.metrics.successful_count += 1
            except Exception as e:
                self.metrics.failed_count += 1
                self.metrics.errors.append(f"Op {i}: {type(e).__name__}: {e}")

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self.metrics.latencies_ms.append(elapsed_ms)

            # Sample memory
            self.metrics.memory_samples_mb.append(get_process_memory_mb())

            # Periodic GC
            if (i + 1) % self.gc_interval == 0:
                gc.collect()
                logger.info(f"Progress: {i + 1}/{self.operation_count}")

        # Final measurement
        gc.collect()
        self.metrics.end_memory_mb = get_process_memory_mb()

        logger.info("Soak test complete")
        logger.info(self.metrics.to_report())

        return self.metrics


# === Test Cases ===


class TestSoakStability:
    """Soak tests for system stability."""

    @pytest.mark.soak
    def test_soak_text_processing(self):
        """Soak test: Repeated text processing operations."""
        from app.core.nlp.text_processing import TextProcessor

        processor = TextProcessor()
        test_texts = [
            "Hello, this is a test of the voice synthesis system.",
            "The quick brown fox jumps over the lazy dog.",
            "VoiceStudio provides professional voice cloning capabilities.",
        ]

        text_index = [0]  # Use list for closure

        def operation():
            text = test_texts[text_index[0] % len(test_texts)]
            text_index[0] += 1
            processor.normalize_text(text)
            processor.detect_language(text)
            processor.get_phonemes(text)

        runner = SoakTestRunner(operation_count=100)
        metrics = runner.run_sync(operation, "text_processing")

        # Assertions
        assert metrics.success_rate >= 99.0, f"Success rate too low: {metrics.success_rate}%"
        assert (
            metrics.memory_growth_mb < 50
        ), f"Memory growth too high: {metrics.memory_growth_mb} MB"
        assert (
            metrics.latency_degradation_ratio < 2.0
        ), f"Latency degradation: {metrics.latency_degradation_ratio}x"

    @pytest.mark.soak
    @pytest.mark.asyncio
    async def test_soak_health_checks(self):
        """Soak test: Repeated backend health checks."""
        import httpx

        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=5.0) as client:

            async def operation():
                response = await client.get("/health")
                response.raise_for_status()

            runner = SoakTestRunner(operation_count=100)
            metrics = await runner.run_async(operation, "health_checks")

        # Backend should handle 100 health checks without issues
        assert metrics.success_rate >= 95.0, f"Success rate too low: {metrics.success_rate}%"
        assert (
            metrics.latency_degradation_ratio < 3.0
        ), f"Latency degradation: {metrics.latency_degradation_ratio}x"

    @pytest.mark.soak
    def test_soak_audio_buffer_operations(self):
        """Soak test: Repeated audio buffer allocations."""
        import numpy as np

        def operation():
            # Simulate audio buffer operations
            sample_rate = 22050
            duration = 5.0  # 5 seconds
            samples = int(sample_rate * duration)

            # Allocate buffer
            audio = np.random.randn(samples).astype(np.float32)

            # Simple processing
            audio = audio * 0.5
            audio = np.clip(audio, -1.0, 1.0)

            # Clear reference
            del audio

        runner = SoakTestRunner(operation_count=100)
        metrics = runner.run_sync(operation, "audio_buffers")

        assert metrics.success_rate == 100.0, "Audio operations should not fail"
        assert (
            metrics.memory_growth_mb < 100
        ), f"Memory leak detected: {metrics.memory_growth_mb} MB"

    @pytest.mark.soak
    def test_soak_file_operations(self):
        """Soak test: Repeated temp file creation and cleanup."""
        import tempfile

        def operation():
            # Create and cleanup temp file
            fd, path = tempfile.mkstemp(suffix=".wav")
            try:
                os.write(fd, b"RIFF" + b"\x00" * 1000)  # Minimal WAV-like content
                os.fsync(fd)
            finally:
                os.close(fd)
                os.unlink(path)

        runner = SoakTestRunner(operation_count=100)
        metrics = runner.run_sync(operation, "file_operations")

        assert metrics.success_rate == 100.0, "File operations should not fail"
        assert metrics.memory_growth_mb < 20, f"Memory growth: {metrics.memory_growth_mb} MB"


# === Report Generation ===


def generate_soak_report(metrics_list: list[tuple[str, SoakTestMetrics]], output_path: str):
    """Generate a soak test report file."""
    from datetime import datetime

    lines = [
        "# VoiceStudio Soak Test Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
    ]

    overall_pass = True

    for name, metrics in metrics_list:
        status = "PASS" if metrics.success_rate >= 99 and metrics.memory_growth_mb < 100 else "FAIL"
        if status == "FAIL":
            overall_pass = False

        lines.extend(
            [
                f"## {name}",
                f"Status: {status}",
                f"Success Rate: {metrics.success_rate:.1f}%",
                f"Avg Latency: {metrics.avg_latency_ms:.2f} ms",
                f"Memory Growth: {metrics.memory_growth_mb:.2f} MB",
                f"Latency Degradation: {metrics.latency_degradation_ratio:.2f}x",
                "",
            ]
        )

    lines.extend(
        [
            "---",
            f"Overall: {'PASS' if overall_pass else 'FAIL'}",
        ]
    )

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return overall_pass


if __name__ == "__main__":
    # Run with: python -m tests.soak.test_soak_operations
    logging.basicConfig(level=logging.INFO)
    pytest.main([__file__, "-v", "--tb=short", "-m", "soak"])
