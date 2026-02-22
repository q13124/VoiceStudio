"""
Quality Consistency Monitoring Utilities (IDEA 59).

Provides quality consistency tracking and monitoring across projects and voice profiles.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Quality standards thresholds
QUALITY_STANDARDS = {
    "professional": {
        "mos_score": 4.0,
        "similarity": 0.85,
        "naturalness": 0.80,
        "snr_db": 20.0,
        "artifact_score": 0.1,
    },
    "high": {
        "mos_score": 3.5,
        "similarity": 0.75,
        "naturalness": 0.70,
        "snr_db": 18.0,
        "artifact_score": 0.2,
    },
    "standard": {
        "mos_score": 3.0,
        "similarity": 0.65,
        "naturalness": 0.60,
        "snr_db": 15.0,
        "artifact_score": 0.3,
    },
    "minimum": {
        "mos_score": 2.5,
        "similarity": 0.50,
        "naturalness": 0.50,
        "snr_db": 12.0,
        "artifact_score": 0.4,
    },
}


class QualityConsistencyMonitor:
    """Monitor quality consistency across projects and profiles."""

    def __init__(self):
        self.quality_history: dict[str, list[dict[str, Any]]] = {}
        self.quality_standards: dict[str, dict[str, float]] = {}

    def set_quality_standard(self, project_id: str, standard_name: str = "professional") -> bool:
        """
        Set quality standard for a project.

        Args:
            project_id: Project identifier
            standard_name: Standard name (professional, high, standard, minimum)

        Returns:
            True if standard was set successfully
        """
        if standard_name not in QUALITY_STANDARDS:
            logger.warning(f"Unknown quality standard: {standard_name}")
            return False

        if project_id not in self.quality_standards:
            self.quality_standards[project_id] = {}

        self.quality_standards[project_id] = QUALITY_STANDARDS[standard_name].copy()
        logger.info(f"Set quality standard '{standard_name}' for project {project_id}")
        return True

    def record_quality_metrics(
        self,
        project_id: str,
        profile_id: str | None,
        metrics: dict[str, Any],
        audio_id: str | None = None,
    ) -> bool:
        """
        Record quality metrics for tracking.

        Args:
            project_id: Project identifier
            profile_id: Voice profile identifier (optional)
            metrics: Quality metrics dictionary
            audio_id: Audio identifier (optional)

        Returns:
            True if metrics were recorded
        """
        if project_id not in self.quality_history:
            self.quality_history[project_id] = []

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "profile_id": profile_id,
            "audio_id": audio_id,
            "metrics": metrics.copy(),
        }

        self.quality_history[project_id].append(record)
        logger.debug(f"Recorded quality metrics for project {project_id}")
        return True

    def check_quality_consistency(
        self, project_id: str, time_period_days: int = 30
    ) -> dict[str, Any]:
        """
        Check quality consistency for a project.

        Args:
            project_id: Project identifier
            time_period_days: Number of days to analyze

        Returns:
            Consistency report dictionary
        """
        if project_id not in self.quality_history:
            return {
                "project_id": project_id,
                "has_data": False,
                "message": "No quality data available for this project",
            }

        # Get standard for project
        standard = self.quality_standards.get(project_id, QUALITY_STANDARDS["professional"])

        # Filter records by time period
        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        recent_records = [
            r
            for r in self.quality_history[project_id]
            if datetime.fromisoformat(r["timestamp"]) >= cutoff_date
        ]

        if not recent_records:
            return {
                "project_id": project_id,
                "has_data": False,
                "message": f"No quality data in the last {time_period_days} days",
            }

        # Calculate statistics
        metrics_list = [r["metrics"] for r in recent_records]

        statistics = self._calculate_statistics(metrics_list)
        violations = self._check_violations(metrics_list, standard)
        trends = self._calculate_trends(recent_records)

        consistency_score = self._calculate_consistency_score(statistics, violations, standard)

        return {
            "project_id": project_id,
            "has_data": True,
            "time_period_days": time_period_days,
            "total_samples": len(recent_records),
            "standard": standard,
            "consistency_score": consistency_score,
            "statistics": statistics,
            "violations": violations,
            "trends": trends,
            "is_consistent": consistency_score >= 0.8,
            "recommendations": self._generate_recommendations(statistics, violations, standard),
        }

    def check_all_projects_consistency(self, time_period_days: int = 30) -> dict[str, Any]:
        """
        Check quality consistency across all projects.

        Args:
            time_period_days: Number of days to analyze

        Returns:
            Summary report for all projects
        """
        all_reports = {}
        total_violations = 0
        total_samples = 0
        consistent_projects = 0

        for project_id in self.quality_history:
            report = self.check_quality_consistency(project_id, time_period_days)
            all_reports[project_id] = report

            if report.get("has_data", False):
                total_samples += report.get("total_samples", 0)
                violations_count = len(report.get("violations", []))
                total_violations += violations_count

                if report.get("is_consistent", False):
                    consistent_projects += 1

        overall_consistency = consistent_projects / len(all_reports) if all_reports else 0.0

        return {
            "total_projects": len(all_reports),
            "projects_with_data": sum(1 for r in all_reports.values() if r.get("has_data", False)),
            "consistent_projects": consistent_projects,
            "overall_consistency": overall_consistency,
            "total_samples": total_samples,
            "total_violations": total_violations,
            "projects": all_reports,
        }

    def get_quality_trends(self, project_id: str, time_period_days: int = 30) -> dict[str, Any]:
        """
        Get quality trends for a project.

        Args:
            project_id: Project identifier
            time_period_days: Number of days to analyze

        Returns:
            Trends dictionary
        """
        if project_id not in self.quality_history:
            return {
                "project_id": project_id,
                "has_data": False,
                "message": "No quality data available",
            }

        cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)
        recent_records = [
            r
            for r in self.quality_history[project_id]
            if datetime.fromisoformat(r["timestamp"]) >= cutoff_date
        ]

        if not recent_records:
            return {
                "project_id": project_id,
                "has_data": False,
                "message": f"No data in the last {time_period_days} days",
            }

        # Group by day
        daily_metrics: dict[str, list[dict[str, Any]]] = {}
        for record in recent_records:
            date = datetime.fromisoformat(record["timestamp"]).date().isoformat()
            if date not in daily_metrics:
                daily_metrics[date] = []
            daily_metrics[date].append(record["metrics"])

        # Calculate daily averages
        daily_averages = {}
        for date, metrics_list in daily_metrics.items():
            daily_averages[date] = self._calculate_statistics(metrics_list)

        return {
            "project_id": project_id,
            "has_data": True,
            "time_period_days": time_period_days,
            "daily_averages": daily_averages,
            "overall_trend": self._calculate_overall_trend(daily_averages),
        }

    def _calculate_statistics(
        self, metrics_list: list[dict[str, Any]]
    ) -> dict[str, dict[str, float]]:
        """Calculate statistics for a list of metrics."""
        if not metrics_list:
            return {}

        # Extract all metric values
        metric_names: set[str] = set()
        for metrics in metrics_list:
            metric_names.update(metrics.keys())

        statistics = {}
        for metric_name in metric_names:
            values = [
                float(metrics.get(metric_name, 0))
                for metrics in metrics_list
                if metrics.get(metric_name) is not None
            ]

            if values:
                statistics[metric_name] = {
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "std": self._calculate_std(values),
                }

        return statistics

    def _calculate_std(self, values: list[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        std: float = variance**0.5
        return std

    def _check_violations(
        self, metrics_list: list[dict[str, Any]], standard: dict[str, float]
    ) -> list[dict[str, Any]]:
        """Check for quality standard violations."""
        violations = []

        for idx, metrics in enumerate(metrics_list):
            violation: dict[str, Any] = {
                "sample_index": idx,
                "violated_metrics": [],
            }

            for metric_name, threshold in standard.items():
                value = metrics.get(metric_name)
                if value is not None:
                    # For artifact_score, lower is better
                    if metric_name == "artifact_score":
                        if value > threshold:
                            violation["violated_metrics"].append(
                                {
                                    "metric": metric_name,
                                    "value": value,
                                    "threshold": threshold,
                                }
                            )
                    else:
                        # For other metrics, higher is better
                        if value < threshold:
                            violation["violated_metrics"].append(
                                {
                                    "metric": metric_name,
                                    "value": value,
                                    "threshold": threshold,
                                }
                            )

            if violation["violated_metrics"]:
                violations.append(violation)

        return violations

    def _calculate_trends(self, records: list[dict[str, Any]]) -> dict[str, str]:
        """Calculate trends (improving, declining, stable)."""
        if len(records) < 2:
            return {}

        # Split into first half and second half
        mid = len(records) // 2
        first_half = [r["metrics"] for r in records[:mid]]
        second_half = [r["metrics"] for r in records[mid:]]

        first_stats = self._calculate_statistics(first_half)
        second_stats = self._calculate_statistics(second_half)

        trends = {}
        for metric_name in first_stats:
            if metric_name in second_stats:
                first_mean = first_stats[metric_name]["mean"]
                second_mean = second_stats[metric_name]["mean"]

                if metric_name == "artifact_score":
                    # For artifact_score, lower is better
                    if second_mean < first_mean * 0.95:
                        trends[metric_name] = "improving"
                    elif second_mean > first_mean * 1.05:
                        trends[metric_name] = "declining"
                    else:
                        trends[metric_name] = "stable"
                else:
                    # For other metrics, higher is better
                    if second_mean > first_mean * 1.05:
                        trends[metric_name] = "improving"
                    elif second_mean < first_mean * 0.95:
                        trends[metric_name] = "declining"
                    else:
                        trends[metric_name] = "stable"

        return trends

    def _calculate_consistency_score(
        self,
        statistics: dict[str, dict[str, float]],
        violations: list[dict[str, Any]],
        standard: dict[str, float],
    ) -> float:
        """Calculate overall consistency score (0.0-1.0)."""
        if not statistics:
            return 0.0

        # Base score from violation rate
        sample_counts = []
        for stat in statistics.values():
            val = stat.get("mean")
            if isinstance(val, (list, tuple)):
                sample_counts.append(len(val))
            else:
                sample_counts.append(1)
        total_samples = len(violations) + max(sample_counts, default=1)
        violation_rate = len(violations) / max(total_samples, 1)
        base_score = 1.0 - violation_rate

        # Adjust for standard deviation (lower std = more consistent)
        std_scores = []
        for _metric_name, stats in statistics.items():
            if "std" in stats and "mean" in stats and stats["mean"] > 0:
                cv = stats["std"] / stats["mean"]  # Coefficient of variation
                std_score = max(0.0, 1.0 - cv)  # Lower CV = higher score
                std_scores.append(std_score)

        if std_scores:
            consistency_adjustment = sum(std_scores) / len(std_scores)
            base_score = (base_score + consistency_adjustment) / 2.0

        return max(0.0, min(1.0, base_score))

    def _calculate_overall_trend(
        self, daily_averages: dict[str, dict[str, dict[str, float]]]
    ) -> str:
        """Calculate overall trend direction."""
        if len(daily_averages) < 2:
            return "insufficient_data"

        dates = sorted(daily_averages.keys())
        first_date = dates[0]
        last_date = dates[-1]

        first_metrics = daily_averages[first_date]
        last_metrics = daily_averages[last_date]

        improving_count = 0
        declining_count = 0

        for metric_name in first_metrics:
            if metric_name in last_metrics:
                first_mean = first_metrics[metric_name].get("mean", 0)
                last_mean = last_metrics[metric_name].get("mean", 0)

                if metric_name == "artifact_score":
                    if last_mean < first_mean:
                        improving_count += 1
                    elif last_mean > first_mean:
                        declining_count += 1
                else:
                    if last_mean > first_mean:
                        improving_count += 1
                    elif last_mean < first_mean:
                        declining_count += 1

        if improving_count > declining_count:
            return "improving"
        elif declining_count > improving_count:
            return "declining"
        else:
            return "stable"

    def _generate_recommendations(
        self,
        statistics: dict[str, dict[str, float]],
        violations: list[dict[str, Any]],
        standard: dict[str, float],
    ) -> list[dict[str, Any]]:
        """Generate recommendations for maintaining quality."""
        recommendations: list[dict[str, Any]] = []

        if not statistics:
            return recommendations

        # Check each metric against standard
        for metric_name, stats in statistics.items():
            threshold = standard.get(metric_name)
            if threshold is None:
                continue

            mean = stats.get("mean", 0)

            if metric_name == "artifact_score":
                if mean > threshold:
                    recommendations.append(
                        {
                            "metric": metric_name,
                            "priority": "high",
                            "message": f"Artifact score ({mean:.2f}) exceeds threshold ({threshold:.2f}). Consider using quality enhancement.",
                            "action": "enable_quality_enhancement",
                        }
                    )
            else:
                if mean < threshold:
                    gap = threshold - mean
                    recommendations.append(
                        {
                            "metric": metric_name,
                            "priority": "high" if gap > threshold * 0.2 else "medium",
                            "message": f"{metric_name.replace('_', ' ').title()} ({mean:.2f}) below threshold ({threshold:.2f}).",
                            "action": "review_engine_settings",
                        }
                    )

        # Check for high variance (inconsistency)
        for metric_name, stats in statistics.items():
            if "std" in stats and "mean" in stats:
                if stats["mean"] > 0:
                    cv = stats["std"] / stats["mean"]
                    if cv > 0.2:  # High coefficient of variation
                        recommendations.append(
                            {
                                "metric": metric_name,
                                "priority": "medium",
                                "message": f"High variance in {metric_name.replace('_', ' ')}. Quality is inconsistent.",
                                "action": "standardize_settings",
                            }
                        )

        return recommendations


# Global monitor instance
_quality_consistency_monitor = QualityConsistencyMonitor()


def get_quality_consistency_monitor() -> QualityConsistencyMonitor:
    """Get the global quality consistency monitor instance."""
    return _quality_consistency_monitor
