"""
Self Optimizer Module for VoiceStudio
Automatic system optimization and self-improvement

Compatible with:
- Python 3.10+
"""

from __future__ import annotations

import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import AI Governor
try:
    from .ai_governor import AIGovernor

    HAS_AI_GOVERNOR = True
except ImportError:
    HAS_AI_GOVERNOR = False
    logger.warning("AI Governor not available")

# Import parameter optimizer
try:
    from app.core.training.parameter_optimizer import ParameterOptimizer

    HAS_PARAMETER_OPTIMIZER = True
except ImportError:
    HAS_PARAMETER_OPTIMIZER = False
    logger.warning("Parameter optimizer not available")


class SelfOptimizer:
    """
    Self Optimizer for automatic system optimization.

    Supports:
    - Automatic parameter optimization
    - Performance optimization
    - Quality optimization
    - Engine selection optimization
    - Continuous learning
    - Optimization history tracking
    """

    def __init__(
        self,
        ai_governor: AIGovernor | None = None,
        optimization_data_path: Path | None = None,
    ):
        """
        Initialize Self Optimizer.

        Args:
            ai_governor: Optional AI Governor instance
            optimization_data_path: Optional path to optimization data
        """
        self.ai_governor = ai_governor
        self.optimization_data_path = optimization_data_path or Path(".optimization_data.json")

        # Optimization tracking
        self._optimization_history: list[dict[str, Any]] = []
        self._optimization_results: dict[str, Any] = defaultdict(dict)
        self._performance_baseline: dict[str, Any] = {}

        # Load optimization data
        self._load_optimization_data()

    def optimize_engine_selection(
        self,
        task_type: str,
        sample_tasks: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Optimize engine selection for a task type.

        Args:
            task_type: Task type to optimize
            sample_tasks: Optional sample tasks for testing

        Returns:
            Dictionary with optimization results
        """
        if not self.ai_governor:
            logger.error("AI Governor not available")
            return {"error": "AI Governor not available"}

        logger.info(f"Optimizing engine selection for task type: {task_type}")

        # Get available engines
        if hasattr(self.ai_governor, "engine_hook") and self.ai_governor.engine_hook:
            available_engines = self.ai_governor.engine_hook.list_available_engines()
        else:
            available_engines = []

        if not available_engines:
            return {"error": "No engines available"}

        # Test each engine
        engine_scores = {}
        for engine_name in available_engines:
            try:
                # Record performance for this engine
                if sample_tasks:
                    total_quality = 0.0
                    total_latency = 0.0
                    count = 0

                    for task in sample_tasks[:5]:  # Limit to 5 samples
                        # Simulate task execution
                        metrics = {
                            "quality_score": task.get("quality_score", 0.5),
                            "latency_ms": task.get("latency_ms", 1000.0),
                        }

                        self.ai_governor.record_performance(
                            engine_name=engine_name,
                            task_type=task_type,
                            metrics=metrics,
                        )

                        total_quality += metrics["quality_score"]
                        total_latency += metrics["latency_ms"]
                        count += 1

                    if count > 0:
                        avg_quality = total_quality / count
                        avg_latency = total_latency / count

                        # Score based on quality and latency
                        score = avg_quality * 0.7 + (1.0 - min(avg_latency / 2000.0, 1.0)) * 0.3
                        engine_scores[engine_name] = score

            except Exception as e:
                logger.warning(f"Error testing engine {engine_name}: {e}")
                continue

        # Find best engine
        if engine_scores:
            best_engine = max(engine_scores.items(), key=lambda x: x[1])
            result = {
                "task_type": task_type,
                "best_engine": best_engine[0],
                "best_score": best_engine[1],
                "all_scores": engine_scores,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Store result
            self._optimization_results[f"engine_selection_{task_type}"] = result
            self._optimization_history.append(
                {
                    "type": "engine_selection",
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Save optimization data
            self._save_optimization_data()

            logger.info(
                f"Optimized engine selection: {best_engine[0]} (score: {best_engine[1]:.3f})"
            )
            return result

        return {"error": "No valid engine scores"}

    def optimize_parameters(
        self,
        engine_name: str,
        task_type: str,
        parameter_space: dict[str, list[Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Optimize parameters for an engine and task.

        Args:
            engine_name: Engine name
            task_type: Task type
            parameter_space: Optional parameter space definition

        Returns:
            Dictionary with optimization results
        """
        if not HAS_PARAMETER_OPTIMIZER:
            logger.error("Parameter optimizer not available")
            return {"error": "Parameter optimizer not available"}

        logger.info(f"Optimizing parameters for {engine_name} on {task_type}")

        # Default parameter space if not provided
        if parameter_space is None:
            parameter_space = {
                "quality_priority": [0.3, 0.5, 0.7],
                "speed_priority": [0.3, 0.5, 0.7],
            }

        # Use parameter optimizer
        ParameterOptimizer(optimization_strategy="grid_search", max_iterations=9)

        # Optimize (simplified - would need actual training data)
        best_params = {}
        best_score = 0.0

        # Grid search over parameter space
        for quality_priority in parameter_space.get("quality_priority", [0.5]):
            for speed_priority in parameter_space.get("speed_priority", [0.5]):
                # Score this parameter combination
                score = self._score_parameters(
                    engine_name=engine_name,
                    task_type=task_type,
                    quality_priority=quality_priority,
                    speed_priority=speed_priority,
                )

                if score > best_score:
                    best_score = score
                    best_params = {
                        "quality_priority": quality_priority,
                        "speed_priority": speed_priority,
                    }

        result = {
            "engine_name": engine_name,
            "task_type": task_type,
            "best_parameters": best_params,
            "best_score": best_score,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store result
        self._optimization_results[f"parameters_{engine_name}_{task_type}"] = result
        self._optimization_history.append(
            {
                "type": "parameter_optimization",
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Save optimization data
        self._save_optimization_data()

        logger.info(f"Optimized parameters: {best_params} (score: {best_score:.3f})")
        return result

    def optimize_performance(
        self, component: str, metrics: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Optimize performance for a component.

        Args:
            component: Component name (e.g., "engine_router", "audio_processing")
            metrics: Optional performance metrics

        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Optimizing performance for component: {component}")

        # Baseline performance
        if component not in self._performance_baseline:
            self._performance_baseline[component] = metrics or {}

        # Compare with baseline
        improvements = {}
        if metrics:
            baseline = self._performance_baseline[component]
            for metric_name, current_value in metrics.items():
                baseline_value = baseline.get(metric_name)
                if (
                    baseline_value is not None
                    and isinstance(current_value, (int, float))
                    and baseline_value > 0
                ):
                    improvement = ((baseline_value - current_value) / baseline_value) * 100.0
                    improvements[metric_name] = improvement

        result = {
            "component": component,
            "metrics": metrics,
            "baseline": self._performance_baseline[component],
            "improvements": improvements,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store result
        self._optimization_results[f"performance_{component}"] = result
        self._optimization_history.append(
            {
                "type": "performance_optimization",
                "result": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Update baseline
        if metrics:
            self._performance_baseline[component] = metrics

        # Save optimization data
        self._save_optimization_data()

        logger.info(f"Performance optimization complete for {component}")
        return result

    def continuous_optimization(self, optimization_interval: int = 3600) -> dict[str, Any]:
        """
        Run continuous optimization cycle.

        Args:
            optimization_interval: Interval between optimizations in seconds

        Returns:
            Dictionary with optimization results
        """
        logger.info("Starting continuous optimization cycle")

        results: dict[str, Any] = {
            "engine_selections": {},
            "parameters": {},
            "performance": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Optimize engine selections for common task types
        common_task_types = ["tts", "voice_cloning", "transcription"]
        for task_type in common_task_types:
            try:
                result = self.optimize_engine_selection(task_type)
                if "error" not in result:
                    results["engine_selections"][task_type] = result
            except Exception as e:
                logger.warning(f"Failed to optimize engine selection for {task_type}: {e}")

        # Optimize parameters for common engines
        if self.ai_governor and hasattr(self.ai_governor, "engine_hook"):
            if self.ai_governor.engine_hook:
                common_engines = self.ai_governor.engine_hook.list_available_engines()[:3]
                for engine_name in common_engines:
                    try:
                        result = self.optimize_parameters(engine_name, "tts")
                        if "error" not in result:
                            results["parameters"][engine_name] = result
                    except Exception as e:
                        logger.warning(f"Failed to optimize parameters for {engine_name}: {e}")

        logger.info("Continuous optimization cycle complete")
        return results

    def _score_parameters(
        self,
        engine_name: str,
        task_type: str,
        quality_priority: float,
        speed_priority: float,
    ) -> float:
        """
        Score parameter combination.

        Args:
            engine_name: Engine name
            task_type: Task type
            quality_priority: Quality priority
            speed_priority: Speed priority

        Returns:
            Score (0.0-1.0)
        """
        if not self.ai_governor:
            return 0.5

        # Get performance metrics
        key = f"{engine_name}_{task_type}"
        if hasattr(self.ai_governor, "_engine_performance"):
            performance = self.ai_governor._engine_performance.get(key, {})
            avg_metrics = performance.get("average_metrics", {})
            quality_score = avg_metrics.get("quality_score", 0.5)
            latency_ms = avg_metrics.get("latency_ms", 1000.0)
        else:
            quality_score = 0.5
            latency_ms = 1000.0

        # Score based on priorities
        quality_contribution = quality_score * quality_priority
        speed_contribution = (1.0 - min(latency_ms / 2000.0, 1.0)) * speed_priority

        return float(quality_contribution + speed_contribution)

    def _load_optimization_data(self):
        """Load optimization data from file."""
        if self.optimization_data_path.exists():
            try:
                with open(self.optimization_data_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._optimization_results = data.get("results", {})
                    self._optimization_history = data.get("history", [])
                    self._performance_baseline = data.get("baseline", {})
                logger.info("Loaded optimization data")
            except Exception as e:
                logger.warning(f"Failed to load optimization data: {e}")

    def _save_optimization_data(self):
        """Save optimization data to file atomically (tmp + replace)."""
        tmp_path = None
        try:
            self.optimization_data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "results": self._optimization_results,
                "history": self._optimization_history[-1000:],  # Keep last 1000
                "baseline": self._performance_baseline,
            }
            tmp_path = self.optimization_data_path.with_suffix(
                self.optimization_data_path.suffix + ".tmp"
            )
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.optimization_data_path)
            logger.info(f"Saved optimization data to {self.optimization_data_path}")
        except Exception as e:
            if tmp_path is not None and tmp_path.exists():
                try:
                    tmp_path.unlink()
                # ALLOWED: bare except - Best effort cleanup, failure is acceptable
                except Exception:
                    pass
            logger.error(f"Failed to save optimization data: {e}")

    def get_optimization_stats(self) -> dict[str, Any]:
        """
        Get optimization statistics.

        Returns:
            Dictionary with optimization statistics
        """
        return {
            "total_optimizations": len(self._optimization_history),
            "optimization_results_count": len(self._optimization_results),
            "performance_baselines_count": len(self._performance_baseline),
            "recent_optimizations": (
                self._optimization_history[-10:] if self._optimization_history else []
            ),
        }


def create_self_optimizer(
    ai_governor: AIGovernor | None = None,
    optimization_data_path: Path | None = None,
) -> SelfOptimizer:
    """
    Factory function to create a Self Optimizer instance.

    Args:
        ai_governor: Optional AI Governor instance
        optimization_data_path: Optional path to optimization data

    Returns:
        Initialized SelfOptimizer instance
    """
    return SelfOptimizer(ai_governor=ai_governor, optimization_data_path=optimization_data_path)
