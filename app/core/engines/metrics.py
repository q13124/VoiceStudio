"""
Engine Metrics Collection — Phase 5.2.4

Provides metrics collection for synthesis, transcription, and other engine
operations. Supports histogram-style metrics for latency distribution analysis.
All operations are local-first with file-based persistence.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Default histogram buckets for latency metrics (in milliseconds)
DEFAULT_LATENCY_BUCKETS = [
    10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, float("inf")
]

# Default histogram buckets for audio duration (in seconds)
DEFAULT_DURATION_BUCKETS = [
    0.5, 1, 2, 5, 10, 30, 60, 120, 300, float("inf")
]

# Default histogram buckets for throughput (characters per second)
DEFAULT_THROUGHPUT_BUCKETS = [
    5, 10, 25, 50, 100, 200, 500, 1000, 2000, float("inf")
]

# Default histogram buckets for audio throughput (samples per second for real-time factor)
DEFAULT_RTF_BUCKETS = [
    0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, float("inf")
]

# Metrics storage directory
METRICS_DIR = Path(".voicestudio/metrics")


@dataclass
class HistogramBucket:
    """A single histogram bucket."""

    le: float  # Less than or equal to
    count: int = 0


@dataclass
class Histogram:
    """
    Histogram metric for distribution analysis.

    Tracks count, sum, and bucket distribution for latency/duration metrics.
    """

    name: str
    help_text: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    buckets: list[HistogramBucket] = field(default_factory=list)
    count: int = 0
    sum_value: float = 0.0
    last_value: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def observe(self, value: float) -> None:
        """Record an observation in the histogram."""
        self.count += 1
        self.sum_value += value
        self.last_value = value
        self.last_updated = time.time()

        for bucket in self.buckets:
            if value <= bucket.le:
                bucket.count += 1

    def get_percentile(self, percentile: float) -> float:
        """
        Estimate a percentile from bucket distribution.

        This is an approximation based on bucket boundaries.
        """
        if self.count == 0:
            return 0.0

        target = percentile / 100.0 * self.count
        cumulative = 0

        for i, bucket in enumerate(self.buckets):
            if cumulative + bucket.count >= target:
                # Linear interpolation within bucket
                prev_le = 0.0 if i == 0 else self.buckets[i - 1].le

                if bucket.count == 0:
                    return bucket.le

                fraction = (target - cumulative) / bucket.count
                return prev_le + fraction * (bucket.le - prev_le)

            cumulative += bucket.count

        return self.buckets[-1].le if self.buckets else 0.0

    @property
    def mean(self) -> float:
        """Calculate mean of observations."""
        return self.sum_value / self.count if self.count > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert histogram to dictionary for serialization."""
        return {
            "name": self.name,
            "help_text": self.help_text,
            "labels": self.labels,
            "count": self.count,
            "sum": self.sum_value,
            "mean": self.mean,
            "last_value": self.last_value,
            "last_updated": self.last_updated,
            "buckets": [
                {"le": b.le, "count": b.count}
                for b in self.buckets
            ],
        }


@dataclass
class Counter:
    """Simple counter metric."""

    name: str
    help_text: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    value: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def inc(self, amount: float = 1.0) -> None:
        """Increment the counter."""
        self.value += amount
        self.last_updated = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert counter to dictionary."""
        return {
            "name": self.name,
            "help_text": self.help_text,
            "labels": self.labels,
            "value": self.value,
            "last_updated": self.last_updated,
        }


class EngineMetricsCollector:
    """
    Collects and stores metrics for VoiceStudio engines.

    Thread-safe singleton that tracks synthesis, transcription, and
    engine operation metrics with histogram support.
    """

    _instance: Optional["EngineMetricsCollector"] = None
    _lock = threading.Lock()

    # Histograms
    _synthesis_latency: dict[str, Histogram]
    _transcription_latency: dict[str, Histogram]
    _audio_duration: dict[str, Histogram]
    _synthesis_throughput: dict[str, Histogram]  # chars/sec
    _transcription_rtf: dict[str, Histogram]  # real-time factor

    # Counters
    _synthesis_count: dict[str, Counter]
    _synthesis_errors: dict[str, Counter]
    _transcription_count: dict[str, Counter]
    _transcription_errors: dict[str, Counter]
    _total_chars_synthesized: dict[str, Counter]
    _total_audio_generated_seconds: dict[str, Counter]

    def __new__(cls) -> "EngineMetricsCollector":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._init_metrics()
                    cls._instance = instance
        return cls._instance

    def _init_metrics(self) -> None:
        """Initialize all metric stores."""
        self._synthesis_latency = {}
        self._transcription_latency = {}
        self._audio_duration = {}
        self._synthesis_throughput = {}
        self._transcription_rtf = {}
        self._synthesis_count = {}
        self._synthesis_errors = {}
        self._transcription_count = {}
        self._transcription_errors = {}
        self._total_chars_synthesized = {}
        self._total_audio_generated_seconds = {}

        # Ensure metrics directory exists
        METRICS_DIR.mkdir(parents=True, exist_ok=True)

    def _create_latency_histogram(
        self,
        name: str,
        help_text: str,
        labels: dict[str, str] | None = None,
    ) -> Histogram:
        """Create a new latency histogram with default buckets."""
        buckets = [
            HistogramBucket(le=le) for le in DEFAULT_LATENCY_BUCKETS
        ]
        return Histogram(
            name=name,
            help_text=help_text,
            labels=labels or {},
            buckets=buckets,
        )

    def _create_duration_histogram(
        self,
        name: str,
        help_text: str,
        labels: dict[str, str] | None = None,
    ) -> Histogram:
        """Create a new audio duration histogram."""
        buckets = [
            HistogramBucket(le=le) for le in DEFAULT_DURATION_BUCKETS
        ]
        return Histogram(
            name=name,
            help_text=help_text,
            labels=labels or {},
            buckets=buckets,
        )

    def _create_throughput_histogram(
        self,
        name: str,
        help_text: str,
        labels: dict[str, str] | None = None,
    ) -> Histogram:
        """Create a new throughput histogram (chars/sec)."""
        buckets = [
            HistogramBucket(le=le) for le in DEFAULT_THROUGHPUT_BUCKETS
        ]
        return Histogram(
            name=name,
            help_text=help_text,
            labels=labels or {},
            buckets=buckets,
        )

    def _create_rtf_histogram(
        self,
        name: str,
        help_text: str,
        labels: dict[str, str] | None = None,
    ) -> Histogram:
        """Create a new real-time factor histogram."""
        buckets = [
            HistogramBucket(le=le) for le in DEFAULT_RTF_BUCKETS
        ]
        return Histogram(
            name=name,
            help_text=help_text,
            labels=labels or {},
            buckets=buckets,
        )

    def _get_key(self, engine: str, extra: str | None = None) -> str:
        """Generate a unique key for the metric."""
        if extra:
            return f"{engine}:{extra}"
        return engine

    # =========================================================================
    # Synthesis Metrics
    # =========================================================================

    def record_synthesis_latency(
        self,
        engine: str,
        latency_ms: float,
        quality_preset: str = "standard",
    ) -> None:
        """
        Record synthesis operation latency.

        Args:
            engine: Engine name (e.g., 'xtts', 'chatterbox')
            latency_ms: Latency in milliseconds
            quality_preset: Quality preset used
        """
        key = self._get_key(engine, quality_preset)

        with self._lock:
            if key not in self._synthesis_latency:
                self._synthesis_latency[key] = self._create_latency_histogram(
                    name="voicestudio_synthesis_latency_ms",
                    help_text="Synthesis operation latency in milliseconds",
                    labels={"engine": engine, "quality": quality_preset},
                )

            self._synthesis_latency[key].observe(latency_ms)

        logger.debug(
            "Recorded synthesis latency: engine=%s latency=%.2fms",
            engine, latency_ms
        )

    def record_synthesis_complete(
        self,
        engine: str,
        audio_duration_seconds: float,
        success: bool = True,
    ) -> None:
        """
        Record a completed synthesis operation.

        Args:
            engine: Engine name
            audio_duration_seconds: Duration of generated audio
            success: Whether synthesis succeeded
        """
        with self._lock:
            # Record count
            if engine not in self._synthesis_count:
                self._synthesis_count[engine] = Counter(
                    name="voicestudio_synthesis_total",
                    help_text="Total synthesis operations",
                    labels={"engine": engine},
                )
            self._synthesis_count[engine].inc()

            # Record errors
            if not success:
                if engine not in self._synthesis_errors:
                    self._synthesis_errors[engine] = Counter(
                        name="voicestudio_synthesis_errors_total",
                        help_text="Total synthesis errors",
                        labels={"engine": engine},
                    )
                self._synthesis_errors[engine].inc()

            # Record audio duration
            if success and audio_duration_seconds > 0:
                if engine not in self._audio_duration:
                    hist = self._create_duration_histogram(
                        name="voicestudio_audio_duration_seconds",
                        help_text="Audio duration in seconds",
                        labels={"engine": engine},
                    )
                    self._audio_duration[engine] = hist
                self._audio_duration[engine].observe(audio_duration_seconds)

                # Track total audio generated
                if engine not in self._total_audio_generated_seconds:
                    self._total_audio_generated_seconds[engine] = Counter(
                        name="voicestudio_total_audio_generated_seconds",
                        help_text="Total audio duration generated in seconds",
                        labels={"engine": engine},
                    )
                self._total_audio_generated_seconds[engine].inc(audio_duration_seconds)

    def record_synthesis_throughput(
        self,
        engine: str,
        chars_processed: int,
        latency_ms: float,
        audio_duration_seconds: float = 0,
        quality_preset: str = "standard",
    ) -> None:
        """
        Record synthesis throughput metrics.

        Args:
            engine: Engine name
            chars_processed: Number of characters synthesized
            latency_ms: Latency in milliseconds
            audio_duration_seconds: Duration of generated audio
            quality_preset: Quality preset used
        """
        if latency_ms <= 0:
            return

        # Calculate throughput in chars/sec
        chars_per_second = chars_processed / (latency_ms / 1000.0)

        key = self._get_key(engine, quality_preset)

        with self._lock:
            # Record chars/sec throughput
            if key not in self._synthesis_throughput:
                self._synthesis_throughput[key] = self._create_throughput_histogram(
                    name="voicestudio_synthesis_throughput_chars_per_sec",
                    help_text="Synthesis throughput in characters per second",
                    labels={"engine": engine, "quality": quality_preset},
                )
            self._synthesis_throughput[key].observe(chars_per_second)

            # Track total chars synthesized
            if engine not in self._total_chars_synthesized:
                self._total_chars_synthesized[engine] = Counter(
                    name="voicestudio_total_chars_synthesized",
                    help_text="Total characters synthesized",
                    labels={"engine": engine},
                )
            self._total_chars_synthesized[engine].inc(chars_processed)

        # Calculate real-time factor if audio duration provided
        rtf_info = ""
        if audio_duration_seconds > 0:
            rtf = (latency_ms / 1000.0) / audio_duration_seconds
            rtf_info = f" RTF={rtf:.2f}"

        logger.debug(
            "Synthesis throughput: engine=%s chars=%d rate=%.1f chars/sec%s",
            engine, chars_processed, chars_per_second, rtf_info
        )

    # =========================================================================
    # Transcription Metrics
    # =========================================================================

    def record_transcription_latency(
        self,
        engine: str,
        latency_ms: float,
        audio_length_seconds: float = 0,
    ) -> None:
        """
        Record transcription operation latency.

        Args:
            engine: Engine name (e.g., 'whisper', 'faster_whisper')
            latency_ms: Latency in milliseconds
            audio_length_seconds: Length of audio transcribed
        """
        key = self._get_key(engine)

        with self._lock:
            if key not in self._transcription_latency:
                hist = self._create_latency_histogram(
                    name="voicestudio_transcription_latency_ms",
                    help_text="Transcription latency in ms",
                    labels={"engine": engine},
                )
                self._transcription_latency[key] = hist

            self._transcription_latency[key].observe(latency_ms)

            # Track real-time factor if audio length provided
            if audio_length_seconds > 0:
                rtf = (latency_ms / 1000) / audio_length_seconds

                if key not in self._transcription_rtf:
                    self._transcription_rtf[key] = self._create_rtf_histogram(
                        name="voicestudio_transcription_rtf",
                        help_text="Transcription real-time factor (processing time / audio length)",
                        labels={"engine": engine},
                    )
                self._transcription_rtf[key].observe(rtf)

                logger.debug(
                    "Transcription: engine=%s latency=%.2fms RTF=%.2f",
                    engine, latency_ms, rtf
                )

    def record_transcription_complete(
        self,
        engine: str,
        success: bool = True,
    ) -> None:
        """Record a completed transcription operation."""
        with self._lock:
            if engine not in self._transcription_count:
                self._transcription_count[engine] = Counter(
                    name="voicestudio_transcription_total",
                    help_text="Total transcription operations",
                    labels={"engine": engine},
                )
            self._transcription_count[engine].inc()

            if not success:
                if engine not in self._transcription_errors:
                    self._transcription_errors[engine] = Counter(
                        name="voicestudio_transcription_errors_total",
                        help_text="Total transcription errors",
                        labels={"engine": engine},
                    )
                self._transcription_errors[engine].inc()

    # =========================================================================
    # Retrieval Methods
    # =========================================================================

    def get_synthesis_stats(
        self, engine: str | None = None
    ) -> dict[str, Any]:
        """Get synthesis statistics for an engine or all engines."""
        with self._lock:
            if engine:
                return self._get_engine_stats(engine, "synthesis")
            return {
                eng: self._get_engine_stats(eng, "synthesis")
                for eng in self._synthesis_count
            }

    def get_transcription_stats(
        self, engine: str | None = None
    ) -> dict[str, Any]:
        """Get transcription statistics."""
        with self._lock:
            if engine:
                return self._get_engine_stats(engine, "transcription")
            return {
                eng: self._get_engine_stats(eng, "transcription")
                for eng in self._transcription_count
            }

    def _get_engine_stats(self, engine: str, op_type: str) -> dict[str, Any]:
        """Get stats for a specific engine and operation type."""
        stats: dict[str, Any] = {"engine": engine, "type": op_type}

        if op_type == "synthesis":
            count = self._synthesis_count.get(engine)
            errors = self._synthesis_errors.get(engine)
            stats["total_count"] = count.value if count else 0
            stats["error_count"] = errors.value if errors else 0

            # Get latency percentiles
            for key, hist in self._synthesis_latency.items():
                if key.startswith(engine):
                    stats["latency_p50_ms"] = hist.get_percentile(50)
                    stats["latency_p95_ms"] = hist.get_percentile(95)
                    stats["latency_p99_ms"] = hist.get_percentile(99)
                    stats["latency_mean_ms"] = hist.mean
                    break

            # Get throughput percentiles
            for key, hist in self._synthesis_throughput.items():
                if key.startswith(engine):
                    stats["throughput_p50_chars_per_sec"] = hist.get_percentile(50)
                    stats["throughput_p95_chars_per_sec"] = hist.get_percentile(95)
                    stats["throughput_mean_chars_per_sec"] = hist.mean
                    break

            # Total chars synthesized
            chars_counter = self._total_chars_synthesized.get(engine)
            if chars_counter:
                stats["total_chars_synthesized"] = chars_counter.value

            # Total audio generated
            audio_counter = self._total_audio_generated_seconds.get(engine)
            if audio_counter:
                stats["total_audio_generated_seconds"] = audio_counter.value

        elif op_type == "transcription":
            count = self._transcription_count.get(engine)
            errors = self._transcription_errors.get(engine)
            stats["total_count"] = count.value if count else 0
            stats["error_count"] = errors.value if errors else 0

            hist = self._transcription_latency.get(engine)
            if hist:
                stats["latency_p50_ms"] = hist.get_percentile(50)
                stats["latency_p95_ms"] = hist.get_percentile(95)
                stats["latency_p99_ms"] = hist.get_percentile(99)
                stats["latency_mean_ms"] = hist.mean

            # Get RTF percentiles
            rtf_hist = self._transcription_rtf.get(engine)
            if rtf_hist:
                stats["rtf_p50"] = rtf_hist.get_percentile(50)
                stats["rtf_p95"] = rtf_hist.get_percentile(95)
                stats["rtf_mean"] = rtf_hist.mean

        return stats

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all collected metrics."""
        with self._lock:
            synth_lat = {
                k: v.to_dict()
                for k, v in self._synthesis_latency.items()
            }
            trans_lat = {
                k: v.to_dict()
                for k, v in self._transcription_latency.items()
            }
            audio_dur = {
                k: v.to_dict()
                for k, v in self._audio_duration.items()
            }
            synth_throughput = {
                k: v.to_dict()
                for k, v in self._synthesis_throughput.items()
            }
            trans_rtf = {
                k: v.to_dict()
                for k, v in self._transcription_rtf.items()
            }
            synth_cnt = {
                k: v.to_dict()
                for k, v in self._synthesis_count.items()
            }
            synth_err = {
                k: v.to_dict()
                for k, v in self._synthesis_errors.items()
            }
            trans_cnt = {
                k: v.to_dict()
                for k, v in self._transcription_count.items()
            }
            trans_err = {
                k: v.to_dict()
                for k, v in self._transcription_errors.items()
            }
            chars_synth = {
                k: v.to_dict()
                for k, v in self._total_chars_synthesized.items()
            }
            audio_gen = {
                k: v.to_dict()
                for k, v in self._total_audio_generated_seconds.items()
            }
            return {
                "synthesis_latency": synth_lat,
                "synthesis_throughput": synth_throughput,
                "transcription_latency": trans_lat,
                "transcription_rtf": trans_rtf,
                "audio_duration": audio_dur,
                "synthesis_count": synth_cnt,
                "synthesis_errors": synth_err,
                "transcription_count": trans_cnt,
                "transcription_errors": trans_err,
                "total_chars_synthesized": chars_synth,
                "total_audio_generated_seconds": audio_gen,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    # =========================================================================
    # Persistence
    # =========================================================================

    def save_to_file(self) -> Path:
        """Save current metrics to file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        filepath = METRICS_DIR / f"engine_metrics_{timestamp}.json"

        with self._lock:
            metrics_data = self.get_all_metrics()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2, default=str)

        logger.info("Saved engine metrics to %s", filepath)
        return filepath

    def reset(self) -> None:
        """Reset all metrics (for testing)."""
        with self._lock:
            self._init_metrics()


def get_engine_metrics() -> EngineMetricsCollector:
    """Get the global engine metrics collector instance."""
    return EngineMetricsCollector()


# =============================================================================
# Convenience Functions
# =============================================================================


def record_synthesis(
    engine: str,
    latency_ms: float,
    audio_duration_seconds: float = 0,
    quality_preset: str = "standard",
    success: bool = True,
    chars_processed: int = 0,
) -> None:
    """
    Convenience function to record a complete synthesis operation.

    Args:
        engine: Engine name
        latency_ms: Operation latency in milliseconds
        audio_duration_seconds: Duration of generated audio
        quality_preset: Quality preset used
        success: Whether operation succeeded
        chars_processed: Number of characters synthesized (for throughput metrics)
    """
    collector = get_engine_metrics()
    collector.record_synthesis_latency(
        engine, latency_ms, quality_preset
    )
    collector.record_synthesis_complete(
        engine, audio_duration_seconds, success
    )
    if chars_processed > 0:
        collector.record_synthesis_throughput(
            engine, chars_processed, latency_ms, audio_duration_seconds, quality_preset
        )


def record_transcription(
    engine: str,
    latency_ms: float,
    audio_length_seconds: float = 0,
    success: bool = True,
) -> None:
    """
    Convenience function to record a complete transcription operation.

    Args:
        engine: Engine name
        latency_ms: Operation latency in milliseconds
        audio_length_seconds: Length of audio transcribed
        success: Whether operation succeeded
    """
    collector = get_engine_metrics()
    collector.record_transcription_latency(
        engine, latency_ms, audio_length_seconds
    )
    collector.record_transcription_complete(engine, success)
