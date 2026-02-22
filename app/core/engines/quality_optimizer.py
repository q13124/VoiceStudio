"""
Automated Quality Optimization for Voice Cloning
Automatically adjusts synthesis parameters to achieve target quality levels
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Quality thresholds for professional studio standards
PROFESSIONAL_THRESHOLDS = {
    "mos_score": 4.0,
    "similarity": 0.85,
    "naturalness": 0.80,
    "snr_db": 30.0,
    "artifact_score": 0.1,
}

# Quality tiers and their requirements
QUALITY_TIERS = {
    "fast": {
        "mos_score": 3.5,
        "similarity": 0.75,
        "naturalness": 0.70,
        "snr_db": 25.0,
    },
    "standard": {
        "mos_score": 4.0,
        "similarity": 0.80,
        "naturalness": 0.75,
        "snr_db": 28.0,
    },
    "high": {
        "mos_score": 4.3,
        "similarity": 0.85,
        "naturalness": 0.80,
        "snr_db": 30.0,
    },
    "ultra": {
        "mos_score": 4.5,
        "similarity": 0.90,
        "naturalness": 0.85,
        "snr_db": 32.0,
    },
}


class QualityOptimizer:
    """
    Automated quality optimization system.

    Analyzes quality metrics and suggests parameter adjustments
    to achieve target quality levels.
    """

    def __init__(self, target_tier: str = "standard"):
        """
        Initialize quality optimizer.

        Args:
            target_tier: Target quality tier ("fast", "standard", "high", "ultra")
        """
        self.target_tier = target_tier
        self.target_metrics = QUALITY_TIERS.get(target_tier, QUALITY_TIERS["standard"])
        self.optimization_history: list[dict[str, Any]] = []

    def analyze_quality(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze quality metrics and determine if optimization is needed.

        Args:
            metrics: Quality metrics dictionary

        Returns:
            Analysis results with recommendations
        """
        analysis: dict[str, Any] = {
            "meets_target": True,
            "deficiencies": [],
            "recommendations": [],
            "quality_score": 0.0,
        }

        # Check each metric against target
        for metric_name, target_value in self.target_metrics.items():
            actual_value = metrics.get(metric_name, 0.0)

            if actual_value < target_value:
                analysis["meets_target"] = False
                deficiency = {
                    "metric": metric_name,
                    "actual": actual_value,
                    "target": target_value,
                    "gap": target_value - actual_value,
                }
                analysis["deficiencies"].append(deficiency)

        # Calculate overall quality score (weighted average)
        weights = {
            "mos_score": 0.3,
            "similarity": 0.3,
            "naturalness": 0.25,
            "snr_db": 0.15,
        }

        quality_score = 0.0
        total_weight = 0.0

        for metric_name, weight in weights.items():
            if metric_name in metrics and metric_name in self.target_metrics:
                actual = metrics[metric_name]
                target = self.target_metrics[metric_name]

                # Normalize to 0-1 scale
                if metric_name == "mos_score":
                    normalized = actual / 5.0
                    target_normalized = target / 5.0
                elif metric_name == "snr_db":
                    normalized = min(actual / 50.0, 1.0)
                    target_normalized = min(target / 50.0, 1.0)
                else:
                    normalized = actual
                    target_normalized = target

                # Score based on how close to target
                score = 1.0 if normalized >= target_normalized else normalized / target_normalized

                quality_score += score * weight
                total_weight += weight

        if total_weight > 0:
            analysis["quality_score"] = quality_score / total_weight
        else:
            analysis["quality_score"] = 0.0

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis["deficiencies"])

        return analysis

    def _generate_recommendations(self, deficiencies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Generate optimization recommendations based on deficiencies.

        Args:
            deficiencies: List of quality deficiencies

        Returns:
            List of recommendations
        """
        recommendations = []

        for deficiency in deficiencies:
            metric = deficiency["metric"]
            gap = deficiency["gap"]

            if metric == "mos_score":
                recommendations.append(
                    {
                        "action": "enhance_quality",
                        "parameter": "enhance_quality",
                        "value": True,
                        "reason": f"MOS score {gap:.2f} below target. Enable quality enhancement.",
                        "priority": "high" if gap > 0.5 else "medium",
                    }
                )
                recommendations.append(
                    {
                        "action": "use_higher_quality_engine",
                        "parameter": "engine",
                        "value": "tortoise",
                        "reason": "Tortoise engine provides highest MOS scores.",
                        "priority": "medium",
                    }
                )

            elif metric == "similarity":
                recommendations.append(
                    {
                        "action": "improve_reference_audio",
                        "parameter": "reference_audio",
                        "value": None,
                        "reason": f"Similarity {gap:.2f} below target. Use higher quality reference audio.",
                        "priority": "high",
                    }
                )
                recommendations.append(
                    {
                        "action": "enable_voice_profile_matching",
                        "parameter": "match_voice_profile",
                        "value": True,
                        "reason": "Voice profile matching improves similarity.",
                        "priority": "medium",
                    }
                )

            elif metric == "naturalness":
                recommendations.append(
                    {
                        "action": "enable_prosody_enhancement",
                        "parameter": "enhance_prosody",
                        "value": True,
                        "reason": f"Naturalness {gap:.2f} below target. Enable prosody enhancement.",
                        "priority": "high" if gap > 0.1 else "medium",
                    }
                )
                recommendations.append(
                    {
                        "action": "use_chatterbox_engine",
                        "parameter": "engine",
                        "value": "chatterbox",
                        "reason": "Chatterbox engine provides high naturalness.",
                        "priority": "medium",
                    }
                )

            elif metric == "snr_db":
                recommendations.append(
                    {
                        "action": "increase_denoising",
                        "parameter": "denoise_strength",
                        "value": 0.9,
                        "reason": f"SNR {gap:.1f} dB below target. Increase denoising strength.",
                        "priority": "high" if gap > 5.0 else "medium",
                    }
                )
                recommendations.append(
                    {
                        "action": "enable_advanced_denoising",
                        "parameter": "advanced_denoise",
                        "value": True,
                        "reason": "Advanced denoising improves SNR.",
                        "priority": "medium",
                    }
                )

        return recommendations

    def optimize_parameters(
        self,
        current_metrics: dict[str, Any],
        current_params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Optimize synthesis parameters based on quality metrics.

        Args:
            current_metrics: Current quality metrics
            current_params: Current synthesis parameters

        Returns:
            Optimized parameters dictionary
        """
        analysis = self.analyze_quality(current_metrics)

        optimized_params = current_params.copy()

        # Apply recommendations
        for recommendation in analysis["recommendations"]:
            action = recommendation["action"]
            recommendation["parameter"]
            value = recommendation["value"]
            priority = recommendation.get("priority", "medium")

            # Only apply high/medium priority recommendations
            if priority in ["high", "medium"]:
                if action == "enhance_quality":
                    optimized_params["enhance_quality"] = True
                elif action == "use_higher_quality_engine":
                    optimized_params["engine"] = value
                elif action == "enable_voice_profile_matching":
                    optimized_params["match_voice_profile"] = True
                elif action == "enable_prosody_enhancement":
                    optimized_params["enhance_prosody"] = True
                elif action == "increase_denoising":
                    optimized_params["denoise_strength"] = value
                elif action == "enable_advanced_denoising":
                    optimized_params["advanced_denoise"] = True

        # Record optimization
        self.optimization_history.append(
            {
                "metrics": current_metrics,
                "original_params": current_params,
                "optimized_params": optimized_params,
                "analysis": analysis,
            }
        )

        return optimized_params

    def suggest_engine(self, target_metrics: dict[str, Any] | None = None) -> str:
        """
        Suggest best engine based on target quality requirements.

        Args:
            target_metrics: Optional target metrics (uses tier defaults if not provided)

        Returns:
            Suggested engine name
        """
        if target_metrics is None:
            target_metrics = self.target_metrics

        # Engine quality profiles (estimated)
        engine_profiles = {
            "xtts": {
                "mos_score": 4.0,
                "similarity": 0.82,
                "naturalness": 0.78,
                "snr_db": 28.0,
                "speed": "fast",
            },
            "chatterbox": {
                "mos_score": 4.3,
                "similarity": 0.87,
                "naturalness": 0.85,
                "snr_db": 30.0,
                "speed": "medium",
            },
            "tortoise": {
                "mos_score": 4.5,
                "similarity": 0.90,
                "naturalness": 0.88,
                "snr_db": 32.0,
                "speed": "slow",
            },
        }

        # Score each engine
        best_engine = "xtts"
        best_score = 0.0

        for engine_name, profile in engine_profiles.items():
            score = 0.0
            meets_all = True

            for metric_name, target_value in target_metrics.items():
                if metric_name in profile:
                    engine_value = profile[metric_name]
                    if not isinstance(engine_value, (int, float)):
                        continue
                    if engine_value >= target_value:
                        score += 1.0
                    else:
                        meets_all = False
                        score += max(0.0, engine_value / target_value)

            if meets_all and score > best_score:
                best_score = score
                best_engine = engine_name

        return best_engine

    def get_optimization_summary(self) -> dict[str, Any]:
        """
        Get summary of optimization history.

        Returns:
            Summary dictionary
        """
        if not self.optimization_history:
            return {"total_optimizations": 0}

        total = len(self.optimization_history)
        avg_quality_score = np.mean(
            [opt["analysis"]["quality_score"] for opt in self.optimization_history]
        )

        return {
            "total_optimizations": total,
            "average_quality_score": float(avg_quality_score),
            "target_tier": self.target_tier,
            "target_metrics": self.target_metrics,
        }


def optimize_synthesis_for_quality(
    metrics: dict[str, Any],
    current_params: dict[str, Any],
    target_tier: str = "standard",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Convenience function to optimize synthesis parameters.

    Args:
        metrics: Current quality metrics
        current_params: Current synthesis parameters
        target_tier: Target quality tier

    Returns:
        Tuple of (optimized_params, analysis)
    """
    optimizer = QualityOptimizer(target_tier=target_tier)
    analysis = optimizer.analyze_quality(metrics)
    optimized_params = optimizer.optimize_parameters(metrics, current_params)

    return optimized_params, analysis
