"""
Quality Dashboard Module for VoiceStudio
Quality metrics visualization and dashboard

Compatible with:
- Python 3.10+
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Import quality metrics
try:
    from ..audio.enhanced_quality_metrics import EnhancedQualityMetrics
    from ..engines.quality_metrics import calculate_all_metrics

    HAS_QUALITY_METRICS = True
except ImportError:
    HAS_QUALITY_METRICS = False
    logger.warning("Quality metrics not available")


class QualityDashboard:
    """
    Quality Dashboard for metrics visualization and analysis.

    Supports:
    - Quality metrics aggregation
    - Historical tracking
    - Statistical analysis
    - Trend analysis
    - Quality distribution
    - Engine comparison
    - Report generation
    """

    def __init__(self, sample_rate: int = 24000):
        """
        Initialize Quality Dashboard.

        Args:
            sample_rate: Default sample rate for processing
        """
        self.sample_rate = sample_rate
        self.quality_history: List[Dict[str, Any]] = []
        self.quality_metrics = None

        if HAS_QUALITY_METRICS:
            try:
                self.quality_metrics = EnhancedQualityMetrics(sample_rate=sample_rate)
            except Exception as e:
                logger.warning(f"Failed to initialize quality metrics: {e}")

    def add_quality_record(
        self,
        audio_id: str,
        metrics: Dict[str, Any],
        engine: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        Add a quality record to the dashboard.

        Args:
            audio_id: Unique audio identifier
            metrics: Quality metrics dictionary
            engine: Optional engine name
            timestamp: Optional timestamp (defaults to now)
            metadata: Optional additional metadata
        """
        record = {
            "audio_id": audio_id,
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "metrics": metrics,
            "engine": engine,
            "metadata": metadata or {},
        }
        self.quality_history.append(record)

    def get_statistics(
        self, engine: Optional[str] = None, time_range: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get quality statistics.

        Args:
            engine: Optional engine filter
            time_range: Optional time range filter {"start": "...", "end": "..."}

        Returns:
            Dictionary with statistics
        """
        # Filter records
        records = self.quality_history
        if engine:
            records = [r for r in records if r.get("engine") == engine]
        if time_range:
            start = time_range.get("start")
            end = time_range.get("end")
            if start:
                records = [r for r in records if r["timestamp"] >= start]
            if end:
                records = [r for r in records if r["timestamp"] <= end]

        if not records:
            return {"message": "No records found"}

        # Extract metrics
        mos_scores = []
        similarities = []
        naturalness_scores = []
        snr_values = []
        quality_scores = []

        for record in records:
            metrics = record.get("metrics", {})
            if metrics.get("mos_score"):
                mos_scores.append(metrics["mos_score"])
            if metrics.get("similarity"):
                similarities.append(metrics["similarity"])
            if metrics.get("naturalness"):
                naturalness_scores.append(metrics["naturalness"])
            if metrics.get("snr_db"):
                snr_values.append(metrics["snr_db"])
            if metrics.get("overall_quality_score"):
                quality_scores.append(metrics["overall_quality_score"])

        statistics = {
            "total_records": len(records),
            "time_range": {
                "start": min(r["timestamp"] for r in records) if records else None,
                "end": max(r["timestamp"] for r in records) if records else None,
            },
        }

        # Calculate statistics for each metric
        def calc_stats(values):
            if not values:
                return None
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": sorted(values)[len(values) // 2] if values else None,
            }

        if mos_scores:
            statistics["mos_score"] = calc_stats(mos_scores)
        if similarities:
            statistics["similarity"] = calc_stats(similarities)
        if naturalness_scores:
            statistics["naturalness"] = calc_stats(naturalness_scores)
        if snr_values:
            statistics["snr_db"] = calc_stats(snr_values)
        if quality_scores:
            statistics["overall_quality"] = calc_stats(quality_scores)

        return statistics

    def get_engine_comparison(self) -> Dict[str, Any]:
        """
        Compare quality across different engines.

        Returns:
            Dictionary with engine comparison data
        """
        engine_stats = defaultdict(list)

        # Group by engine
        for record in self.quality_history:
            engine = record.get("engine", "unknown")
            metrics = record.get("metrics", {})
            quality_score = metrics.get("overall_quality_score", 0.0)
            if quality_score > 0:
                engine_stats[engine].append(quality_score)

        comparison = {}
        for engine, scores in engine_stats.items():
            comparison[engine] = {
                "count": len(scores),
                "average_quality": sum(scores) / len(scores) if scores else 0.0,
                "min_quality": min(scores) if scores else 0.0,
                "max_quality": max(scores) if scores else 0.0,
            }

        # Rank engines
        ranked_engines = sorted(
            comparison.items(), key=lambda x: x[1]["average_quality"], reverse=True
        )

        return {
            "engines": dict(comparison),
            "rankings": [
                {
                    "rank": idx + 1,
                    "engine": engine,
                    "avg_quality": data["average_quality"],
                }
                for idx, (engine, data) in enumerate(ranked_engines)
            ],
        }

    def get_trends(
        self, metric_name: str = "overall_quality_score", window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get quality trends over time.

        Args:
            metric_name: Metric name to track
            window_size: Window size for moving average

        Returns:
            Dictionary with trend data
        """
        if not self.quality_history:
            return {"message": "No quality history"}

        # Extract time series data
        time_series = []
        for record in sorted(self.quality_history, key=lambda x: x["timestamp"]):
            metrics = record.get("metrics", {})
            value = metrics.get(metric_name)
            if value is not None:
                time_series.append(
                    {
                        "timestamp": record["timestamp"],
                        "value": value,
                        "engine": record.get("engine"),
                    }
                )

        if not time_series:
            return {"message": f"No data for metric: {metric_name}"}

        # Calculate moving average
        moving_avg = []
        for i in range(len(time_series)):
            window = time_series[max(0, i - window_size + 1) : i + 1]
            avg = sum(item["value"] for item in window) / len(window)
            moving_avg.append(
                {
                    "timestamp": time_series[i]["timestamp"],
                    "value": avg,
                }
            )

        # Calculate trend direction
        if len(time_series) >= 2:
            first_half = time_series[: len(time_series) // 2]
            second_half = time_series[len(time_series) // 2 :]
            first_avg = sum(item["value"] for item in first_half) / len(first_half)
            second_avg = sum(item["value"] for item in second_half) / len(second_half)
            trend = "improving" if second_avg > first_avg else "declining"
            trend_change = second_avg - first_avg
        else:
            trend = "stable"
            trend_change = 0.0

        return {
            "metric": metric_name,
            "time_series": time_series,
            "moving_average": moving_avg,
            "trend": trend,
            "trend_change": trend_change,
            "current_value": time_series[-1]["value"] if time_series else None,
        }

    def get_quality_distribution(
        self, metric_name: str = "overall_quality_score", bins: int = 10
    ) -> Dict[str, Any]:
        """
        Get quality distribution histogram data.

        Args:
            metric_name: Metric name to analyze
            bins: Number of bins for histogram

        Returns:
            Dictionary with distribution data
        """
        values = []
        for record in self.quality_history:
            metrics = record.get("metrics", {})
            value = metrics.get(metric_name)
            if value is not None:
                values.append(value)

        if not values:
            return {"message": f"No data for metric: {metric_name}"}

        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins if max_val > min_val else 1.0

        # Create bins
        histogram = [0] * bins
        for value in values:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            histogram[bin_idx] += 1

        return {
            "metric": metric_name,
            "min": min_val,
            "max": max_val,
            "bin_width": bin_width,
            "histogram": histogram,
            "total_samples": len(values),
        }

    def generate_dashboard_report(
        self, output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Generate comprehensive dashboard report.

        Args:
            output_path: Optional output file path

        Returns:
            Report text
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("Quality Dashboard Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.utcnow().isoformat()}")
        report_lines.append("")

        # Overall statistics
        stats = self.get_statistics()
        report_lines.append("Overall Statistics")
        report_lines.append("-" * 80)
        report_lines.append(f"Total Records: {stats.get('total_records', 0)}")
        if stats.get("time_range"):
            tr = stats["time_range"]
            report_lines.append(f"Time Range: {tr.get('start')} to {tr.get('end')}")
        report_lines.append("")

        # Metric statistics
        for metric_name in [
            "mos_score",
            "similarity",
            "naturalness",
            "overall_quality",
        ]:
            if metric_name in stats:
                metric_stats = stats[metric_name]
                report_lines.append(f"{metric_name.replace('_', ' ').title()}")
                report_lines.append(f"  Count: {metric_stats.get('count', 0)}")
                report_lines.append(f"  Min: {metric_stats.get('min', 0):.3f}")
                report_lines.append(f"  Max: {metric_stats.get('max', 0):.3f}")
                report_lines.append(f"  Mean: {metric_stats.get('mean', 0):.3f}")
                report_lines.append(f"  Median: {metric_stats.get('median', 0):.3f}")
                report_lines.append("")

        # Engine comparison
        comparison = self.get_engine_comparison()
        if comparison.get("rankings"):
            report_lines.append("Engine Comparison")
            report_lines.append("-" * 80)
            for ranking in comparison["rankings"]:
                report_lines.append(
                    f"  {ranking['rank']}. {ranking['engine']}: {ranking['avg_quality']:.3f}"
                )
            report_lines.append("")

        # Trends
        trends = self.get_trends()
        if trends.get("trend"):
            report_lines.append("Quality Trends")
            report_lines.append("-" * 80)
            report_lines.append(f"Trend: {trends['trend']}")
            report_lines.append(f"Trend Change: {trends.get('trend_change', 0):.3f}")
            if trends.get("current_value") is not None:
                report_lines.append(f"Current Value: {trends['current_value']:.3f}")
            report_lines.append("")

        report_text = "\n".join(report_lines)

        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(report_text, encoding="utf-8")
            logger.info(f"Dashboard report saved to: {output_path}")

        return report_text

    def export_data(self, output_path: Union[str, Path], format: str = "json"):
        """
        Export dashboard data.

        Args:
            output_path: Output file path
            format: Export format ("json")
        """
        output_path = Path(output_path)

        if format == "json":
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "quality_history": self.quality_history,
                "statistics": self.get_statistics(),
                "engine_comparison": self.get_engine_comparison(),
                "trends": self.get_trends(),
            }
            output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.info(f"Dashboard data exported to: {output_path}")
        else:
            raise ValueError(f"Unsupported format: {format}")

    def load_data(self, input_path: Union[str, Path]):
        """
        Load dashboard data from file.

        Args:
            input_path: Input file path
        """
        input_path = Path(input_path)
        data = json.loads(input_path.read_text(encoding="utf-8"))

        if "quality_history" in data:
            self.quality_history = data["quality_history"]
            logger.info(f"Loaded {len(self.quality_history)} quality records")


def create_quality_dashboard(sample_rate: int = 24000) -> QualityDashboard:
    """
    Factory function to create a Quality Dashboard instance.

    Args:
        sample_rate: Default sample rate for processing

    Returns:
        Initialized QualityDashboard instance
    """
    return QualityDashboard(sample_rate=sample_rate)
