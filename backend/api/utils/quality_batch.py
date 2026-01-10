"""
Quality-Based Batch Processing Utilities (IDEA 57).

Provides utilities for quality-focused batch processing operations,
including quality metrics calculation, prioritization, validation, and reporting.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def calculate_batch_quality_score(
    quality_metrics: Optional[Dict[str, Any]],
) -> Optional[float]:
    """
    Calculate overall quality score from quality metrics dictionary.

    Args:
        quality_metrics: Dictionary of quality metrics (MOS, similarity, etc.)

    Returns:
        Overall quality score (0.0-1.0) or None if metrics unavailable
    """
    if not quality_metrics or not isinstance(quality_metrics, dict):
        return None

    # Try to get existing quality_score first
    if "quality_score" in quality_metrics:
        score = quality_metrics["quality_score"]
        if isinstance(score, (int, float)):
            return float(score)

    # Calculate from individual metrics
    mos = quality_metrics.get("mos_score")
    similarity = quality_metrics.get("similarity")
    naturalness = quality_metrics.get("naturalness")

    scores = []

    # Normalize MOS (1-5 scale) to 0-1
    if mos is not None and isinstance(mos, (int, float)):
        mos_norm = (float(mos) - 1.0) / 4.0
        scores.append(mos_norm)

    # Similarity is already 0-1
    if similarity is not None and isinstance(similarity, (int, float)):
        scores.append(float(similarity))

    # Naturalness is already 0-1
    if naturalness is not None and isinstance(naturalness, (int, float)):
        scores.append(float(naturalness))

    if not scores:
        return None

    # Average available scores
    return sum(scores) / len(scores)


def validate_batch_quality(
    quality_score: Optional[float],
    quality_threshold: Optional[float],
    tolerance_percent: float = 10.0,
) -> Optional[str]:
    """
    Validate batch job quality against threshold.

    Args:
        quality_score: Overall quality score (0.0-1.0)
        quality_threshold: Minimum quality threshold (0.0-1.0)
        tolerance_percent: Percentage tolerance for warning (default: 10%)

    Returns:
        "pass", "warning", "fail", or None if validation not applicable
    """
    if quality_threshold is None or quality_score is None:
        return None

    threshold = float(quality_threshold)
    score = float(quality_score)

    if score >= threshold:
        return "pass"
    elif score >= threshold * (1.0 - tolerance_percent / 100.0):
        return "warning"
    else:
        return "fail"


def prioritize_batch_jobs(
    jobs: List[Dict[str, Any]],
    quality_threshold: Optional[float] = None,
    prioritize_high_quality: bool = True,
) -> List[Dict[str, Any]]:
    """
    Prioritize batch jobs based on quality requirements.

    Args:
        jobs: List of batch job dictionaries
        quality_threshold: Minimum quality threshold (optional)
        prioritize_high_quality: If True, prioritize high-quality jobs first

    Returns:
        Sorted list of jobs by priority
    """

    def get_priority(job: Dict[str, Any]) -> tuple:
        """Calculate priority score for a job."""
        priority_score = 0

        # Check if job has quality threshold requirement
        job_threshold = job.get("quality_threshold")
        job_score = job.get("quality_score")

        if quality_threshold is not None or job_threshold is not None:
            threshold = quality_threshold or job_threshold or 0.0

            if prioritize_high_quality:
                # Prioritize jobs with higher quality requirements
                if job_threshold is not None:
                    priority_score += float(job_threshold) * 100

                # Prioritize jobs that already passed quality check
                if job.get("quality_status") == "pass":
                    priority_score += 50
                elif job.get("quality_status") == "warning":
                    priority_score += 25
            else:
                # Prioritize jobs with lower quality requirements (faster)
                if job_threshold is not None:
                    priority_score -= float(job_threshold) * 100

        # Prioritize by creation time (older first)
        created = job.get("created")
        if created:
            try:
                if isinstance(created, str):
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                else:
                    created_dt = created
                # Older jobs get higher priority (subtract timestamp)
                priority_score -= created_dt.timestamp()
            except:
                ...

        return (-priority_score,)  # Negative for descending sort

    return sorted(jobs, key=get_priority)


def generate_batch_quality_report(
    job: Dict[str, Any], all_jobs: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate quality report for a batch job.

    Args:
        job: Batch job dictionary
        all_jobs: Optional list of all jobs for comparison

    Returns:
        Quality report dictionary
    """
    quality_metrics = job.get("quality_metrics") or {}
    quality_score = job.get("quality_score")
    quality_status = job.get("quality_status")
    quality_threshold = job.get("quality_threshold")

    report = {
        "job_id": job.get("id"),
        "job_name": job.get("name"),
        "quality_score": quality_score,
        "quality_status": quality_status,
        "quality_threshold": quality_threshold,
        "metrics": {},
        "summary": {},
    }

    # Extract individual metrics
    if isinstance(quality_metrics, dict):
        report["metrics"] = {
            "mos_score": quality_metrics.get("mos_score"),
            "similarity": quality_metrics.get("similarity"),
            "naturalness": quality_metrics.get("naturalness"),
            "snr_db": quality_metrics.get("snr_db"),
            "artifact_score": (
                quality_metrics.get("artifacts", {}).get("artifact_score")
                if isinstance(quality_metrics.get("artifacts"), dict)
                else None
            ),
            "has_clicks": (
                quality_metrics.get("artifacts", {}).get("has_clicks")
                if isinstance(quality_metrics.get("artifacts"), dict)
                else None
            ),
            "has_distortion": (
                quality_metrics.get("artifacts", {}).get("has_distortion")
                if isinstance(quality_metrics.get("artifacts"), dict)
                else None
            ),
        }

    # Generate summary
    if quality_score is not None:
        if quality_threshold is not None:
            threshold_met = quality_score >= quality_threshold
            report["summary"]["threshold_met"] = threshold_met
            if quality_threshold > 0:
                report["summary"]["threshold_percentage"] = (
                    quality_score / quality_threshold
                ) * 100

        # Quality rating
        if quality_score >= 0.9:
            report["summary"]["rating"] = "excellent"
        elif quality_score >= 0.75:
            report["summary"]["rating"] = "good"
        elif quality_score >= 0.6:
            report["summary"]["rating"] = "acceptable"
        elif quality_score >= 0.4:
            report["summary"]["rating"] = "poor"
        else:
            report["summary"]["rating"] = "very_poor"

    # Comparison with other jobs (if provided)
    if all_jobs:
        completed_jobs = [
            j
            for j in all_jobs
            if j.get("status") == "completed" and j.get("quality_score") is not None
        ]

        if completed_jobs:
            scores = [float(j.get("quality_score", 0)) for j in completed_jobs]
            report["comparison"] = {
                "average_quality": sum(scores) / len(scores) if scores else None,
                "min_quality": min(scores) if scores else None,
                "max_quality": max(scores) if scores else None,
                "total_completed": len(completed_jobs),
                "rank": None,
            }

            # Calculate rank
            if quality_score is not None:
                higher_scores = sum(1 for s in scores if s > quality_score)
                report["comparison"]["rank"] = higher_scores + 1
                report["comparison"]["percentile"] = (
                    (1.0 - (higher_scores / len(scores))) * 100 if scores else None
                )

    return report


def calculate_batch_statistics(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate quality statistics for a batch of jobs.

    Args:
        jobs: List of batch job dictionaries

    Returns:
        Statistics dictionary
    """
    completed_jobs = [j for j in jobs if j.get("status") == "completed"]

    stats = {
        "total_jobs": len(jobs),
        "completed_jobs": len(completed_jobs),
        "jobs_with_quality": 0,
        "average_quality": None,
        "min_quality": None,
        "max_quality": None,
        "quality_distribution": {
            "excellent": 0,  # >= 0.9
            "good": 0,  # >= 0.75
            "acceptable": 0,  # >= 0.6
            "poor": 0,  # >= 0.4
            "very_poor": 0,  # < 0.4
        },
        "status_distribution": {"pass": 0, "warning": 0, "fail": 0},
    }

    quality_scores = []
    for job in completed_jobs:
        quality_score = job.get("quality_score")
        if quality_score is not None:
            stats["jobs_with_quality"] += 1
            score = float(quality_score)
            quality_scores.append(score)

            # Distribution by rating
            if score >= 0.9:
                stats["quality_distribution"]["excellent"] += 1
            elif score >= 0.75:
                stats["quality_distribution"]["good"] += 1
            elif score >= 0.6:
                stats["quality_distribution"]["acceptable"] += 1
            elif score >= 0.4:
                stats["quality_distribution"]["poor"] += 1
            else:
                stats["quality_distribution"]["very_poor"] += 1

            # Status distribution
            quality_status = job.get("quality_status")
            if quality_status in stats["status_distribution"]:
                stats["status_distribution"][quality_status] += 1

    if quality_scores:
        stats["average_quality"] = sum(quality_scores) / len(quality_scores)
        stats["min_quality"] = min(quality_scores)
        stats["max_quality"] = max(quality_scores)

    return stats
