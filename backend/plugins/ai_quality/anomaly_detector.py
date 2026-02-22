"""
Statistical Anomaly Detection for Plugin Metrics.

Phase 6B: Detects anomalous plugin behavior using statistical methods.
No ML models required - uses Z-score and IQR methods.

Detection Methods:
1. Z-Score: Detects values far from mean (>3 standard deviations)
2. IQR: Detects outliers using interquartile range
3. Trend: Detects significant changes over time

Metrics Monitored:
- CPU usage
- Memory usage
- Execution time
- Error rate
- API call rate

Usage:
    detector = AnomalyDetector()

    # Learn baseline from historical data
    detector.learn_baseline("plugin-id", "cpu_usage", samples)

    # Record new samples and check for anomalies
    anomalies = detector.record_sample("plugin-id", "cpu_usage", 85.0)

    for anomaly in anomalies:
        print(f"Anomaly: {anomaly.metric} = {anomaly.value} ({anomaly.method})")
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AnomalyMethod(Enum):
    """Methods for anomaly detection."""

    ZSCORE = "zscore"
    IQR = "iqr"
    TREND = "trend"
    THRESHOLD = "threshold"


class AnomalySeverity(Enum):
    """Severity of detected anomaly."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MetricBaseline:
    """
    Baseline statistics for a metric.

    Attributes:
        plugin_id: Plugin identifier
        metric_name: Name of the metric
        mean: Mean value
        std: Standard deviation
        min: Minimum observed value
        max: Maximum observed value
        q1: First quartile (25th percentile)
        median: Median (50th percentile)
        q3: Third quartile (75th percentile)
        sample_count: Number of samples used
        last_updated: Last update timestamp
    """

    plugin_id: str
    metric_name: str
    mean: float = 0.0
    std: float = 0.0
    min: float = float("inf")
    max: float = float("-inf")
    q1: float = 0.0
    median: float = 0.0
    q3: float = 0.0
    sample_count: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)

    @property
    def iqr(self) -> float:
        """Interquartile range."""
        return self.q3 - self.q1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "metric_name": self.metric_name,
            "mean": self.mean,
            "std": self.std,
            "min": self.min,
            "max": self.max,
            "q1": self.q1,
            "median": self.median,
            "q3": self.q3,
            "iqr": self.iqr,
            "sample_count": self.sample_count,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class Anomaly:
    """
    A detected anomaly.

    Attributes:
        plugin_id: Plugin identifier
        metric_name: Name of the metric
        value: Observed value
        expected_mean: Expected mean value
        deviation: How far from expected
        method: Detection method used
        severity: Anomaly severity
        detected_at: Detection timestamp
        context: Additional context
    """

    plugin_id: str
    metric_name: str
    value: float
    expected_mean: float
    deviation: float
    method: AnomalyMethod
    severity: AnomalySeverity
    detected_at: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "metric_name": self.metric_name,
            "value": self.value,
            "expected_mean": self.expected_mean,
            "deviation": self.deviation,
            "method": self.method.value,
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat(),
            "context": self.context,
        }


class AnomalyDetector:
    """
    Statistical anomaly detector for plugin metrics.

    Uses Z-score and IQR methods to detect anomalous behavior.
    All calculations are performed locally using standard statistics.

    Example:
        detector = AnomalyDetector(z_score_threshold=3.0)

        # Learn from historical data
        historical_cpu = [10, 12, 11, 13, 10, 12, 11, 10, 12, 13]
        detector.learn_baseline("my-plugin", "cpu_usage", historical_cpu)

        # Check new values
        anomalies = detector.detect("my-plugin", "cpu_usage", 85.0)
        if anomalies:
            print("Anomaly detected!")
    """

    def __init__(
        self,
        z_score_threshold: float = 3.0,
        iqr_multiplier: float = 1.5,
        min_samples: int = 30,
        auto_learn: bool = True,
        trend_window: int = 10,
    ):
        """
        Initialize anomaly detector.

        Args:
            z_score_threshold: Z-score threshold for anomaly (default: 3.0)
            iqr_multiplier: IQR multiplier for outlier detection (default: 1.5)
            min_samples: Minimum samples before detecting (default: 30)
            auto_learn: Automatically update baseline with new samples
            trend_window: Window size for trend detection
        """
        self._z_threshold = z_score_threshold
        self._iqr_multiplier = iqr_multiplier
        self._min_samples = min_samples
        self._auto_learn = auto_learn
        self._trend_window = trend_window

        # Baselines by plugin_id -> metric_name
        self._baselines: Dict[str, Dict[str, MetricBaseline]] = {}

        # Recent samples for trend detection
        self._recent_samples: Dict[str, Dict[str, List[float]]] = {}

    def learn_baseline(
        self,
        plugin_id: str,
        metric_name: str,
        samples: List[float],
    ) -> MetricBaseline:
        """
        Learn baseline from historical samples.

        Args:
            plugin_id: Plugin identifier
            metric_name: Metric name
            samples: Historical sample values

        Returns:
            Computed MetricBaseline
        """
        if len(samples) < 2:
            raise ValueError("Need at least 2 samples to compute baseline")

        sorted_samples = sorted(samples)
        n = len(sorted_samples)

        # Compute quartiles
        q1_idx = n // 4
        q3_idx = (3 * n) // 4

        baseline = MetricBaseline(
            plugin_id=plugin_id,
            metric_name=metric_name,
            mean=statistics.mean(samples),
            std=statistics.stdev(samples) if n > 1 else 0.0,
            min=min(samples),
            max=max(samples),
            q1=sorted_samples[q1_idx],
            median=statistics.median(samples),
            q3=sorted_samples[q3_idx],
            sample_count=n,
            last_updated=datetime.utcnow(),
        )

        # Store baseline
        if plugin_id not in self._baselines:
            self._baselines[plugin_id] = {}
        self._baselines[plugin_id][metric_name] = baseline

        # Initialize recent samples
        if plugin_id not in self._recent_samples:
            self._recent_samples[plugin_id] = {}
        self._recent_samples[plugin_id][metric_name] = samples[-self._trend_window :]

        logger.info(
            f"Learned baseline for {plugin_id}.{metric_name}: "
            f"mean={baseline.mean:.2f}, std={baseline.std:.2f}"
        )

        return baseline

    def record_sample(
        self,
        plugin_id: str,
        metric_name: str,
        value: float,
        auto_learn: bool = True,
    ) -> List[Anomaly]:
        """
        Record a new sample and detect anomalies.

        Args:
            plugin_id: Plugin identifier
            metric_name: Metric name
            value: New sample value
            auto_learn: Update baseline with this sample

        Returns:
            List of detected anomalies (may be empty)
        """
        # Initialize if needed
        if plugin_id not in self._recent_samples:
            self._recent_samples[plugin_id] = {}
        if metric_name not in self._recent_samples[plugin_id]:
            self._recent_samples[plugin_id][metric_name] = []

        # Add to recent samples
        recent = self._recent_samples[plugin_id][metric_name]
        recent.append(value)

        # Keep window size
        if len(recent) > self._trend_window:
            recent.pop(0)

        # If no baseline yet, try to learn one
        if plugin_id not in self._baselines or metric_name not in self._baselines[plugin_id]:
            if len(recent) >= self._min_samples:
                self.learn_baseline(plugin_id, metric_name, recent)
            return []  # No anomaly detection without baseline

        # Detect anomalies
        anomalies = self.detect(plugin_id, metric_name, value)

        # Auto-learn (update baseline) if no anomalies
        if auto_learn and self._auto_learn and not anomalies:
            self._update_baseline(plugin_id, metric_name, value)

        return anomalies

    def detect(
        self,
        plugin_id: str,
        metric_name: str,
        value: float,
    ) -> List[Anomaly]:
        """
        Detect anomalies for a value.

        Args:
            plugin_id: Plugin identifier
            metric_name: Metric name
            value: Value to check

        Returns:
            List of detected anomalies (may be empty)
        """
        anomalies = []

        baseline = self._get_baseline(plugin_id, metric_name)
        if baseline is None:
            return []

        # Z-score detection
        z_anomaly = self._detect_zscore(baseline, value)
        if z_anomaly:
            anomalies.append(z_anomaly)

        # IQR detection
        iqr_anomaly = self._detect_iqr(baseline, value)
        if iqr_anomaly:
            anomalies.append(iqr_anomaly)

        # Trend detection
        trend_anomaly = self._detect_trend(plugin_id, metric_name, value)
        if trend_anomaly:
            anomalies.append(trend_anomaly)

        return anomalies

    def _detect_zscore(
        self,
        baseline: MetricBaseline,
        value: float,
    ) -> Optional[Anomaly]:
        """Detect anomaly using Z-score method."""
        if baseline.std == 0:
            return None

        z_score = abs(value - baseline.mean) / baseline.std

        if z_score > self._z_threshold:
            severity = self._zscore_to_severity(z_score)
            return Anomaly(
                plugin_id=baseline.plugin_id,
                metric_name=baseline.metric_name,
                value=value,
                expected_mean=baseline.mean,
                deviation=z_score,
                method=AnomalyMethod.ZSCORE,
                severity=severity,
                context={"z_score": z_score, "threshold": self._z_threshold},
            )

        return None

    def _detect_iqr(
        self,
        baseline: MetricBaseline,
        value: float,
    ) -> Optional[Anomaly]:
        """Detect anomaly using IQR method."""
        iqr = baseline.iqr
        if iqr == 0:
            return None

        lower_bound = baseline.q1 - (self._iqr_multiplier * iqr)
        upper_bound = baseline.q3 + (self._iqr_multiplier * iqr)

        if value < lower_bound or value > upper_bound:
            deviation = (
                (value - upper_bound) / iqr if value > upper_bound else (lower_bound - value) / iqr
            )
            severity = self._iqr_deviation_to_severity(deviation)

            return Anomaly(
                plugin_id=baseline.plugin_id,
                metric_name=baseline.metric_name,
                value=value,
                expected_mean=baseline.mean,
                deviation=deviation,
                method=AnomalyMethod.IQR,
                severity=severity,
                context={
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "iqr": iqr,
                },
            )

        return None

    def _detect_trend(
        self,
        plugin_id: str,
        metric_name: str,
        value: float,
    ) -> Optional[Anomaly]:
        """Detect anomaly based on recent trend."""
        recent = self._recent_samples.get(plugin_id, {}).get(metric_name, [])

        if len(recent) < self._trend_window:
            return None

        # Check for consistent increase
        baseline = self._get_baseline(plugin_id, metric_name)
        if baseline is None:
            return None

        # Simple trend: compare recent mean to baseline
        recent_mean = statistics.mean(recent)
        if baseline.std > 0:
            trend_z = (recent_mean - baseline.mean) / baseline.std

            if abs(trend_z) > self._z_threshold * 0.75:  # Slightly lower threshold
                severity = self._zscore_to_severity(abs(trend_z))
                return Anomaly(
                    plugin_id=plugin_id,
                    metric_name=metric_name,
                    value=value,
                    expected_mean=baseline.mean,
                    deviation=trend_z,
                    method=AnomalyMethod.TREND,
                    severity=severity,
                    context={
                        "recent_mean": recent_mean,
                        "baseline_mean": baseline.mean,
                        "trend_direction": "increasing" if trend_z > 0 else "decreasing",
                    },
                )

        return None

    def _get_baseline(
        self,
        plugin_id: str,
        metric_name: str,
    ) -> Optional[MetricBaseline]:
        """Get baseline for a metric."""
        return self._baselines.get(plugin_id, {}).get(metric_name)

    def _update_baseline(
        self,
        plugin_id: str,
        metric_name: str,
        value: float,
    ):
        """Update baseline with new sample (online learning)."""
        baseline = self._get_baseline(plugin_id, metric_name)
        if baseline is None:
            return

        # Welford's online algorithm for mean and variance
        n = baseline.sample_count + 1
        delta = value - baseline.mean
        new_mean = baseline.mean + delta / n
        delta2 = value - new_mean

        # Update variance incrementally
        if n > 1:
            new_var = (baseline.std**2 * (n - 2) + delta * delta2) / (n - 1)
            new_std = math.sqrt(max(0, new_var))
        else:
            new_std = 0.0

        # Update baseline
        baseline.mean = new_mean
        baseline.std = new_std
        baseline.min = min(baseline.min, value)
        baseline.max = max(baseline.max, value)
        baseline.sample_count = n
        baseline.last_updated = datetime.utcnow()

    def _zscore_to_severity(self, z_score: float) -> AnomalySeverity:
        """Map Z-score to severity."""
        if z_score > 5:
            return AnomalySeverity.CRITICAL
        elif z_score > 4:
            return AnomalySeverity.HIGH
        elif z_score > 3.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def _iqr_deviation_to_severity(self, deviation: float) -> AnomalySeverity:
        """Map IQR deviation to severity."""
        if deviation > 3:
            return AnomalySeverity.CRITICAL
        elif deviation > 2:
            return AnomalySeverity.HIGH
        elif deviation > 1.5:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW

    def get_baseline(
        self,
        plugin_id: str,
        metric_name: str,
    ) -> Optional[MetricBaseline]:
        """Get baseline for a plugin metric."""
        return self._get_baseline(plugin_id, metric_name)

    def get_all_baselines(self, plugin_id: str) -> Dict[str, MetricBaseline]:
        """Get all baselines for a plugin."""
        return self._baselines.get(plugin_id, {})

    def clear_baseline(self, plugin_id: str, metric_name: Optional[str] = None):
        """Clear baseline(s) for a plugin."""
        if plugin_id in self._baselines:
            if metric_name:
                self._baselines[plugin_id].pop(metric_name, None)
            else:
                del self._baselines[plugin_id]

        if plugin_id in self._recent_samples:
            if metric_name:
                self._recent_samples[plugin_id].pop(metric_name, None)
            else:
                del self._recent_samples[plugin_id]

    # =========================================================================
    # Q-2: Persistence Integration
    # =========================================================================

    def save_baselines_to_db(self, plugin_id: Optional[str] = None) -> int:
        """
        Save baselines to persistent storage.

        Args:
            plugin_id: If provided, only save baselines for this plugin.
                      If None, save all baselines.

        Returns:
            Number of baselines saved.
        """
        try:
            from backend.plugins.persistence.phase6_persistence import get_phase6_persistence

            persistence = get_phase6_persistence()
        except ImportError:
            logger.warning("Phase 6 persistence not available, baselines not saved")
            return 0

        count = 0
        plugins = [plugin_id] if plugin_id else list(self._baselines.keys())

        for pid in plugins:
            if pid not in self._baselines:
                continue

            for metric_name, baseline in self._baselines[pid].items():
                persistence.save_baseline(
                    plugin_id=baseline.plugin_id,
                    metric_name=baseline.metric_name,
                    mean=baseline.mean,
                    std=baseline.std,
                    min_val=baseline.min,
                    max_val=baseline.max,
                    q1=baseline.q1,
                    median=baseline.median,
                    q3=baseline.q3,
                    sample_count=baseline.sample_count,
                )
                count += 1

        logger.info(f"Saved {count} baselines to database")
        return count

    def load_baselines_from_db(self, plugin_id: Optional[str] = None) -> int:
        """
        Load baselines from persistent storage.

        Args:
            plugin_id: If provided, only load baselines for this plugin.
                      If None, this method cannot determine which plugins to load.

        Returns:
            Number of baselines loaded.
        """
        if plugin_id is None:
            logger.warning("plugin_id required to load baselines from DB")
            return 0

        try:
            from backend.plugins.persistence.phase6_persistence import get_phase6_persistence

            persistence = get_phase6_persistence()
        except ImportError:
            logger.warning("Phase 6 persistence not available, baselines not loaded")
            return 0

        persisted_baselines = persistence.get_all_baselines(plugin_id)

        if not persisted_baselines:
            return 0

        if plugin_id not in self._baselines:
            self._baselines[plugin_id] = {}

        count = 0
        for pb in persisted_baselines:
            self._baselines[plugin_id][pb.metric_name] = MetricBaseline(
                plugin_id=pb.plugin_id,
                metric_name=pb.metric_name,
                mean=pb.mean,
                std=pb.std,
                min=pb.min_val,
                max=pb.max_val,
                q1=pb.q1,
                median=pb.median,
                q3=pb.q3,
                sample_count=pb.sample_count,
                last_updated=pb.last_updated,
            )
            count += 1

        logger.info(f"Loaded {count} baselines for plugin {plugin_id} from database")
        return count

    def delete_baselines_from_db(self, plugin_id: str, metric_name: Optional[str] = None) -> int:
        """
        Delete baselines from persistent storage.

        Args:
            plugin_id: Plugin identifier.
            metric_name: If provided, only delete this metric's baseline.

        Returns:
            Number of baselines deleted.
        """
        try:
            from backend.plugins.persistence.phase6_persistence import get_phase6_persistence

            persistence = get_phase6_persistence()
        except ImportError:
            logger.warning("Phase 6 persistence not available")
            return 0

        deleted = persistence.delete_baseline(plugin_id, metric_name)
        logger.info(f"Deleted {deleted} baselines from database")
        return deleted
