"""
AI Governor (Enhanced) Module for VoiceStudio
Intelligent engine selection and governance system

Compatible with:
- Python 3.10+
"""

import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Import engine hook
try:
    from ..runtime.engine_hook import EngineHook

    HAS_ENGINE_HOOK = True
except ImportError:
    HAS_ENGINE_HOOK = False
    logger.warning("Engine hook not available")


class AIGovernor:
    """
    AI Governor for intelligent engine selection and governance.

    Supports:
    - Engine selection decisions
    - A/B test exploration and recording
    - Reward model guidance
    - Quality-based routing
    - Performance tracking
    - Policy enforcement
    """

    def __init__(
        self,
        engine_hook: Optional[EngineHook] = None,
        reward_model_path: Optional[Path] = None,
        ab_test_data_path: Optional[Path] = None,
    ):
        """
        Initialize AI Governor.

        Args:
            engine_hook: Optional EngineHook instance
            reward_model_path: Optional path to reward model data
            ab_test_data_path: Optional path to A/B test data
        """
        self.engine_hook = engine_hook or (EngineHook() if HAS_ENGINE_HOOK else None)
        self.reward_model_path = reward_model_path or Path(".reward_model.json")
        self.ab_test_data_path = ab_test_data_path or Path(".ab_test_data.json")

        # Performance tracking
        self._engine_performance: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._decision_history: List[Dict[str, Any]] = []
        self._ab_test_results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Reward model data
        self._reward_model: Dict[str, Any] = {}
        self._load_reward_model()

        # A/B test data
        self._ab_test_data: Dict[str, Any] = {}
        self._load_ab_test_data()

    def select_engine(
        self,
        task_type: str,
        requirements: Optional[Dict[str, Any]] = None,
        quality_priority: float = 0.5,
        speed_priority: float = 0.5,
    ) -> Optional[str]:
        """
        Select the best engine for a task.

        Args:
            task_type: Task type (e.g., "tts", "voice_cloning")
            requirements: Optional task requirements
            quality_priority: Quality priority (0.0-1.0)
            speed_priority: Speed priority (0.0-1.0)

        Returns:
            Selected engine name or None
        """
        if not self.engine_hook:
            logger.error("Engine hook not available")
            return None

        # Get available engines
        available_engines = self.engine_hook.list_available_engines()

        if not available_engines:
            logger.warning("No engines available")
            return None

        # Score engines
        scored_engines = []
        for engine_name in available_engines:
            score = self._score_engine(
                engine_name=engine_name,
                task_type=task_type,
                requirements=requirements,
                quality_priority=quality_priority,
                speed_priority=speed_priority,
            )
            scored_engines.append((engine_name, score))

        # Sort by score
        scored_engines.sort(key=lambda x: x[1], reverse=True)

        if not scored_engines:
            return None

        selected_engine = scored_engines[0][0]

        # Record decision
        self._record_decision(
            task_type=task_type,
            selected_engine=selected_engine,
            candidates=available_engines,
            scores=dict(scored_engines),
            requirements=requirements,
        )

        logger.info(f"Selected engine '{selected_engine}' for task '{task_type}'")
        return selected_engine

    def run_ab_test(
        self,
        task_type: str,
        engines: List[str],
        test_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run an A/B test comparing multiple engines.

        Args:
            task_type: Task type
            engines: List of engines to test
            test_config: Optional test configuration

        Returns:
            Dictionary with A/B test results
        """
        test_id = f"{task_type}_{datetime.utcnow().isoformat()}"
        test_config = test_config or {}

        logger.info(f"Starting A/B test {test_id} with engines: {engines}")

        # Run test for each engine
        results = {}
        for engine_name in engines:
            try:
                engine = (
                    self.engine_hook.get_engine(engine_name)
                    if self.engine_hook
                    else None
                )
                if not engine:
                    logger.warning(f"Engine '{engine_name}' not available for A/B test")
                    continue

                # Record test execution
                test_result = {
                    "engine": engine_name,
                    "task_type": task_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "config": test_config,
                }

                # Store result
                results[engine_name] = test_result
                self._ab_test_results[test_id].append(test_result)

            except Exception as e:
                logger.error(f"Error in A/B test for engine '{engine_name}': {e}")
                results[engine_name] = {"error": str(e)}

        # Save A/B test data
        self._save_ab_test_data()

        return {
            "test_id": test_id,
            "task_type": task_type,
            "engines": engines,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def record_performance(
        self,
        engine_name: str,
        task_type: str,
        metrics: Dict[str, Any],
    ):
        """
        Record performance metrics for an engine.

        Args:
            engine_name: Engine name
            task_type: Task type
            metrics: Performance metrics dictionary
        """
        key = f"{engine_name}_{task_type}"

        if key not in self._engine_performance:
            self._engine_performance[key] = {
                "engine": engine_name,
                "task_type": task_type,
                "metrics_history": [],
                "average_metrics": {},
            }

        # Add metrics to history
        self._engine_performance[key]["metrics_history"].append(
            {
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Update average metrics
        history = self._engine_performance[key]["metrics_history"]
        if history:
            avg_metrics = {}
            for metric_name in metrics.keys():
                values = [
                    entry["metrics"].get(metric_name)
                    for entry in history
                    if entry["metrics"].get(metric_name) is not None
                ]
                if values:
                    if isinstance(values[0], (int, float)):
                        avg_metrics[metric_name] = sum(values) / len(values)
                    else:
                        avg_metrics[metric_name] = values[
                            -1
                        ]  # Use latest for non-numeric

            self._engine_performance[key]["average_metrics"] = avg_metrics

        logger.debug(f"Recorded performance for {engine_name} on {task_type}")

    def apply_reward_model(self, engine_name: str, task_type: str) -> float:
        """
        Apply reward model to get reward score for an engine.

        Args:
            engine_name: Engine name
            task_type: Task type

        Returns:
            Reward score (0.0-1.0)
        """
        key = f"{engine_name}_{task_type}"

        # Get reward from model
        reward = self._reward_model.get(key, {}).get("reward", 0.5)

        # Adjust based on performance
        if key in self._engine_performance:
            avg_metrics = self._engine_performance[key].get("average_metrics", {})
            quality_score = avg_metrics.get("quality_score", 0.5)
            latency_ms = avg_metrics.get("latency_ms", 1000.0)

            # Adjust reward based on quality and latency
            quality_adjustment = (quality_score - 0.5) * 0.3
            latency_adjustment = max(0, (1000.0 - latency_ms) / 1000.0) * 0.2

            reward = reward + quality_adjustment + latency_adjustment
            reward = max(0.0, min(1.0, reward))  # Clamp to [0, 1]

        return reward

    def _score_engine(
        self,
        engine_name: str,
        task_type: str,
        requirements: Optional[Dict[str, Any]],
        quality_priority: float,
        speed_priority: float,
    ) -> float:
        """
        Score an engine for a task.

        Args:
            engine_name: Engine name
            task_type: Task type
            requirements: Optional requirements
            quality_priority: Quality priority
            speed_priority: Speed priority

        Returns:
            Score (0.0-1.0)
        """
        score = 0.0

        # Base reward score
        reward = self.apply_reward_model(engine_name, task_type)
        score += reward * 0.4

        # Performance-based score
        key = f"{engine_name}_{task_type}"
        if key in self._engine_performance:
            avg_metrics = self._engine_performance[key].get("average_metrics", {})
            quality_score = avg_metrics.get("quality_score", 0.5)
            latency_ms = avg_metrics.get("latency_ms", 1000.0)

            # Quality contribution
            score += quality_score * quality_priority * 0.3

            # Speed contribution (lower latency is better)
            speed_score = max(0, (2000.0 - latency_ms) / 2000.0)
            score += speed_score * speed_priority * 0.3

        return score

    def _record_decision(
        self,
        task_type: str,
        selected_engine: str,
        candidates: List[str],
        scores: Dict[str, float],
        requirements: Optional[Dict[str, Any]],
    ):
        """Record a decision for analysis."""
        decision = {
            "task_type": task_type,
            "selected_engine": selected_engine,
            "candidates": candidates,
            "scores": scores,
            "requirements": requirements,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._decision_history.append(decision)

        # Keep only recent history (last 1000 decisions)
        if len(self._decision_history) > 1000:
            self._decision_history = self._decision_history[-1000:]

    def _load_reward_model(self):
        """Load reward model from file."""
        if self.reward_model_path.exists():
            try:
                with open(self.reward_model_path, "r", encoding="utf-8") as f:
                    self._reward_model = json.load(f)
                logger.info("Loaded reward model")
            except Exception as e:
                logger.warning(f"Failed to load reward model: {e}")
                self._reward_model = {}

    def _save_reward_model(self):
        """Save reward model to file atomically (tmp + replace)."""
        tmp_path = None
        try:
            self.reward_model_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.reward_model_path.with_suffix(
                self.reward_model_path.suffix + ".tmp"
            )
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._reward_model, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.reward_model_path)
            logger.info(f"Saved reward model to {self.reward_model_path}")
        except Exception as e:
            if tmp_path is not None and tmp_path.exists():
                try:
                    tmp_path.unlink()
                # ALLOWED: bare except - Best effort cleanup, failure is acceptable
                except Exception as cleanup_e:
                    logger.debug(f"Cleanup of temp file failed (non-critical): {cleanup_e}")
            logger.error(f"Failed to save reward model: {e}")

    def _load_ab_test_data(self):
        """Load A/B test data from file."""
        if self.ab_test_data_path.exists():
            try:
                with open(self.ab_test_data_path, "r", encoding="utf-8") as f:
                    self._ab_test_data = json.load(f)
                    self._ab_test_results = self._ab_test_data.get("results", {})
                logger.info("Loaded A/B test data")
            except Exception as e:
                logger.warning(f"Failed to load A/B test data: {e}")
                self._ab_test_data = {}

    def _save_ab_test_data(self):
        """Save A/B test data to file atomically (tmp + replace)."""
        tmp_path = None
        try:
            self.ab_test_data_path.parent.mkdir(parents=True, exist_ok=True)
            self._ab_test_data["results"] = self._ab_test_results
            tmp_path = self.ab_test_data_path.with_suffix(
                self.ab_test_data_path.suffix + ".tmp"
            )
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._ab_test_data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.ab_test_data_path)
            logger.info(f"Saved A/B test data to {self.ab_test_data_path}")
        except Exception as e:
            if tmp_path is not None and tmp_path.exists():
                try:
                    tmp_path.unlink()
                # ALLOWED: bare except - Best effort cleanup, failure is acceptable
                except Exception as cleanup_e:
                    logger.debug(f"Cleanup of temp file failed (non-critical): {cleanup_e}")
            logger.error(f"Failed to save A/B test data: {e}")

    def get_governance_stats(self) -> Dict[str, Any]:
        """
        Get governance statistics.

        Returns:
            Dictionary with governance statistics
        """
        return {
            "total_decisions": len(self._decision_history),
            "engine_performance_count": len(self._engine_performance),
            "ab_test_count": len(self._ab_test_results),
            "reward_model_entries": len(self._reward_model),
        }


def create_ai_governor(
    engine_hook: Optional[EngineHook] = None,
    reward_model_path: Optional[Path] = None,
    ab_test_data_path: Optional[Path] = None,
) -> AIGovernor:
    """
    Factory function to create an AI Governor instance.

    Args:
        engine_hook: Optional EngineHook instance
        reward_model_path: Optional path to reward model data
        ab_test_data_path: Optional path to A/B test data

    Returns:
        Initialized AIGovernor instance
    """
    return AIGovernor(
        engine_hook=engine_hook,
        reward_model_path=reward_model_path,
        ab_test_data_path=ab_test_data_path,
    )
