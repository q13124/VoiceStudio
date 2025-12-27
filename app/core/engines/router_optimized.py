"""
Optimized Engine Router

Enhanced engine routing with:
- Performance tracking
- Load balancing
- Intelligent selection
- Optimized discovery
- Engine recommendations
"""

import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .router import EngineRouter
from .protocols import EngineProtocol

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    FASTEST_RESPONSE = "fastest_response"
    WEIGHTED_RANDOM = "weighted_random"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class EnginePerformanceMetrics:
    """Performance metrics for an engine."""

    engine_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    average_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    current_load: int = 0  # Number of active requests
    last_request_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    consecutive_failures: int = 0
    health_score: float = 1.0  # 0.0 to 1.0
    quality_score: float = 0.0  # From manifest or measured

    def record_request(self, response_time: float, success: bool):
        """Record a request."""
        self.total_requests += 1
        self.total_response_time += response_time
        self.average_response_time = (
            self.total_response_time / self.total_requests
        )
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
        self.last_request_time = datetime.now()

        if success:
            self.successful_requests += 1
            self.last_success_time = datetime.now()
            self.consecutive_failures = 0
        else:
            self.failed_requests += 1
            self.last_failure_time = datetime.now()
            self.consecutive_failures += 1

        # Update health score (0.0 to 1.0)
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 1.0
        )
        # Penalize consecutive failures
        failure_penalty = min(self.consecutive_failures * 0.1, 0.5)
        self.health_score = max(0.0, success_rate - failure_penalty)

    def start_request(self):
        """Mark request as started."""
        self.current_load += 1

    def end_request(self):
        """Mark request as ended."""
        self.current_load = max(0, self.current_load - 1)

    def get_score(self, strategy: LoadBalancingStrategy) -> float:
        """
        Get engine score based on strategy.

        Args:
            strategy: Load balancing strategy

        Returns:
            Score (higher is better)
        """
        if strategy == LoadBalancingStrategy.LEAST_LOADED:
            # Lower load is better
            return 1.0 / (1.0 + self.current_load)
        elif strategy == LoadBalancingStrategy.FASTEST_RESPONSE:
            # Faster is better (inverse of average time)
            if self.average_response_time > 0:
                return 1.0 / (1.0 + self.average_response_time)
            return 1.0
        elif strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            # Combined score: health, speed, load
            health_factor = self.health_score
            speed_factor = (
                1.0 / (1.0 + self.average_response_time)
                if self.average_response_time > 0
                else 1.0
            )
            load_factor = 1.0 / (1.0 + self.current_load)
            return (health_factor * 0.5 + speed_factor * 0.3 + load_factor * 0.2)
        else:
            return 1.0  # Default score


class OptimizedEngineRouter(EngineRouter):
    """
    Optimized engine router with performance tracking and load balancing.

    Features:
    - Performance tracking (response times, success rates)
    - Load balancing (multiple strategies)
    - Intelligent engine selection
    - Optimized engine discovery
    - Engine recommendations
    """

    def __init__(
        self,
        idle_timeout_seconds: float = 300.0,
        load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.PERFORMANCE_BASED,
        enable_performance_tracking: bool = True,
        performance_window_seconds: float = 3600.0,  # 1 hour
    ):
        """
        Initialize optimized engine router.

        Args:
            idle_timeout_seconds: Time before unloading idle engines
            load_balancing_strategy: Load balancing strategy
            enable_performance_tracking: Enable performance tracking
            performance_window_seconds: Time window for performance metrics
        """
        super().__init__(idle_timeout_seconds)

        self.load_balancing_strategy = load_balancing_strategy
        self.enable_performance_tracking = enable_performance_tracking
        self.performance_window_seconds = performance_window_seconds

        # Performance tracking
        self.performance_metrics: Dict[str, EnginePerformanceMetrics] = {}
        self.round_robin_index: Dict[str, int] = {}  # task_type -> index

        # Engine discovery cache
        self._discovery_cache: Dict[str, List[str]] = {}  # task_type -> engine_ids
        self._discovery_cache_time: Dict[str, float] = {}
        self._discovery_cache_ttl: float = 60.0  # 1 minute

        # Threading
        self.lock = threading.Lock()

    def get_engine(
        self,
        name: str,
        task_type: Optional[str] = None,
        **kwargs,
    ) -> Optional[EngineProtocol]:
        """
        Get or create an engine instance with performance tracking.

        Args:
            name: Engine name
            task_type: Optional task type for routing
            **kwargs: Additional arguments for engine initialization

        Returns:
            Engine instance or None if not found
        """
        start_time = time.time()

        # Get engine using parent method
        engine = super().get_engine(name, **kwargs)

        if engine and self.enable_performance_tracking:
            response_time = time.time() - start_time
            self._record_engine_access(name, response_time, success=True)

        return engine

    def select_engine(
        self,
        task_type: str,
        load_balancing_strategy: Optional[LoadBalancingStrategy] = None,
        min_health_score: float = 0.5,
        prefer_fast: bool = False,
        **kwargs,
    ) -> Optional[EngineProtocol]:
        """
        Select best engine for a task using load balancing.

        Args:
            task_type: Task type (e.g., "tts", "image_gen")
            load_balancing_strategy: Override default strategy
            min_health_score: Minimum health score required
            prefer_fast: Prefer faster engines
            **kwargs: Additional arguments for engine initialization

        Returns:
            Selected engine instance or None
        """
        strategy = (
            load_balancing_strategy
            if load_balancing_strategy
            else self.load_balancing_strategy
        )

        # Get available engines for task type
        available_engines = self._get_engines_for_task(task_type)

        if not available_engines:
            logger.warning(f"No engines available for task type: {task_type}")
            return None

        # Filter by health score
        healthy_engines = []
        for engine_id in available_engines:
            metrics = self.performance_metrics.get(engine_id)
            if metrics:
                if metrics.health_score < min_health_score:
                    continue
            healthy_engines.append(engine_id)

        if not healthy_engines:
            logger.warning(
                f"No healthy engines available for task type: {task_type} "
                f"(min_health_score: {min_health_score})"
            )
            # Fallback to all engines if none are healthy
            healthy_engines = available_engines

        # Select engine based on strategy
        selected_engine_id = self._select_engine_by_strategy(
            healthy_engines, strategy, prefer_fast
        )

        if not selected_engine_id:
            return None

        # Get engine instance
        engine = self.get_engine(selected_engine_id, task_type=task_type, **kwargs)

        if engine and self.enable_performance_tracking:
            metrics = self._get_or_create_metrics(selected_engine_id)
            metrics.start_request()

        return engine

    def _select_engine_by_strategy(
        self,
        engine_ids: List[str],
        strategy: LoadBalancingStrategy,
        prefer_fast: bool = False,
    ) -> Optional[str]:
        """
        Select engine based on strategy.

        Args:
            engine_ids: List of available engine IDs
            strategy: Load balancing strategy
            prefer_fast: Prefer faster engines

        Returns:
            Selected engine ID or None
        """
        if not engine_ids:
            return None

        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Round-robin selection
            task_type = "default"  # Could be improved
            index = self.round_robin_index.get(task_type, 0)
            selected = engine_ids[index % len(engine_ids)]
            self.round_robin_index[task_type] = (index + 1) % len(engine_ids)
            return selected

        elif strategy == LoadBalancingStrategy.LEAST_LOADED:
            # Select engine with lowest current load
            best_engine = None
            best_load = float("inf")

            for engine_id in engine_ids:
                metrics = self.performance_metrics.get(engine_id)
                if metrics:
                    load = metrics.current_load
                    if load < best_load:
                        best_load = load
                        best_engine = engine_id
                else:
                    # New engine, no load
                    return engine_id

            return best_engine or engine_ids[0]

        elif strategy == LoadBalancingStrategy.FASTEST_RESPONSE:
            # Select engine with fastest average response time
            best_engine = None
            best_time = float("inf")

            for engine_id in engine_ids:
                metrics = self.performance_metrics.get(engine_id)
                if metrics and metrics.average_response_time > 0:
                    if metrics.average_response_time < best_time:
                        best_time = metrics.average_response_time
                        best_engine = engine_id
                else:
                    # New engine, assume fast
                    return engine_id

            return best_engine or engine_ids[0]

        elif strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            # Select engine with best performance score
            best_engine = None
            best_score = -1.0

            for engine_id in engine_ids:
                metrics = self.performance_metrics.get(engine_id)
                if metrics:
                    score = metrics.get_score(strategy)
                    if prefer_fast and metrics.average_response_time > 0:
                        # Boost score for faster engines
                        speed_boost = 1.0 / (1.0 + metrics.average_response_time)
                        score = score * 0.7 + speed_boost * 0.3

                    if score > best_score:
                        best_score = score
                        best_engine = engine_id
                else:
                    # New engine, give it a chance
                    if best_score < 0.5:
                        return engine_id

            return best_engine or engine_ids[0]

        else:
            # Default: return first engine
            return engine_ids[0]

    def _get_engines_for_task(self, task_type: str) -> List[str]:
        """
        Get engines that support a task type (with caching).

        Args:
            task_type: Task type

        Returns:
            List of engine IDs
        """
        # Check cache
        cache_key = task_type
        if cache_key in self._discovery_cache:
            cache_time = self._discovery_cache_time.get(cache_key, 0)
            if time.time() - cache_time < self._discovery_cache_ttl:
                return self._discovery_cache[cache_key]

        # Discover engines
        engines = []
        for engine_id in self.list_engines():
            manifest = self.get_manifest(engine_id)
            if not manifest:
                continue

            # Check if engine supports task type
            manifest_type = manifest.get("type", "")
            manifest_subtype = manifest.get("subtype", "")

            if manifest_type == "audio" and manifest_subtype == task_type:
                engines.append(engine_id)
            elif manifest_type == task_type:
                engines.append(engine_id)

        # Update cache
        self._discovery_cache[cache_key] = engines
        self._discovery_cache_time[cache_key] = time.time()

        return engines

    def _record_engine_access(
        self, engine_id: str, response_time: float, success: bool
    ):
        """Record engine access for performance tracking."""
        with self.lock:
            metrics = self._get_or_create_metrics(engine_id)
            metrics.record_request(response_time, success)

    def _get_or_create_metrics(
        self, engine_id: str
    ) -> EnginePerformanceMetrics:
        """Get or create performance metrics for engine."""
        if engine_id not in self.performance_metrics:
            self.performance_metrics[engine_id] = EnginePerformanceMetrics(
                engine_id=engine_id
            )
        return self.performance_metrics[engine_id]

    def record_request_completion(
        self, engine_id: str, response_time: float, success: bool
    ):
        """
        Record request completion.

        Args:
            engine_id: Engine ID
            response_time: Request response time in seconds
            success: Whether request succeeded
        """
        if not self.enable_performance_tracking:
            return

        with self.lock:
            metrics = self._get_or_create_metrics(engine_id)
            metrics.record_request(response_time, success)
            metrics.end_request()

    def get_engine_recommendation(
        self,
        task_type: str,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get engine recommendation for a task.

        Args:
            task_type: Task type
            requirements: Optional requirements (e.g., {"min_quality": 0.8})

        Returns:
            Recommendation dictionary or None
        """
        available_engines = self._get_engines_for_task(task_type)

        if not available_engines:
            return None

        recommendations = []

        for engine_id in available_engines:
            manifest = self.get_manifest(engine_id)
            metrics = self.performance_metrics.get(engine_id)

            score = 0.0
            factors = {}

            # Performance factors
            if metrics:
                factors["health_score"] = metrics.health_score
                factors["average_response_time"] = metrics.average_response_time
                factors["current_load"] = metrics.current_load
                score += metrics.health_score * 0.4
                if metrics.average_response_time > 0:
                    score += (1.0 / (1.0 + metrics.average_response_time)) * 0.3
                score += (1.0 / (1.0 + metrics.current_load)) * 0.3
            else:
                # New engine, neutral score
                score = 0.5
                factors["health_score"] = 1.0
                factors["average_response_time"] = None
                factors["current_load"] = 0

            # Quality factors from manifest
            if manifest:
                quality_features = manifest.get("quality_features", {})
                if quality_features:
                    factors["quality_features"] = quality_features

            recommendations.append(
                {
                    "engine_id": engine_id,
                    "score": score,
                    "factors": factors,
                    "manifest": manifest,
                }
            )

        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)

        if recommendations:
            best = recommendations[0]
            return {
                "recommended_engine": best["engine_id"],
                "score": best["score"],
                "factors": best["factors"],
                "alternatives": [
                    {
                        "engine_id": r["engine_id"],
                        "score": r["score"],
                    }
                    for r in recommendations[1:4]  # Top 3 alternatives
                ],
            }

        return None

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance statistics
        """
        with self.lock:
            stats = {
                "total_engines_tracked": len(self.performance_metrics),
                "load_balancing_strategy": self.load_balancing_strategy.value,
                "engines": {},
            }

            for engine_id, metrics in self.performance_metrics.items():
                stats["engines"][engine_id] = {
                    "total_requests": metrics.total_requests,
                    "successful_requests": metrics.successful_requests,
                    "failed_requests": metrics.failed_requests,
                    "success_rate": (
                        metrics.successful_requests / metrics.total_requests
                        if metrics.total_requests > 0
                        else 0.0
                    ),
                    "average_response_time": metrics.average_response_time,
                    "min_response_time": (
                        metrics.min_response_time
                        if metrics.min_response_time != float("inf")
                        else None
                    ),
                    "max_response_time": metrics.max_response_time,
                    "current_load": metrics.current_load,
                    "health_score": metrics.health_score,
                    "consecutive_failures": metrics.consecutive_failures,
                }

            return stats

    def clear_performance_metrics(self, engine_id: Optional[str] = None):
        """
        Clear performance metrics.

        Args:
            engine_id: Optional engine ID to clear (None = clear all)
        """
        with self.lock:
            if engine_id:
                if engine_id in self.performance_metrics:
                    del self.performance_metrics[engine_id]
            else:
                self.performance_metrics.clear()

    def invalidate_discovery_cache(self, task_type: Optional[str] = None):
        """
        Invalidate engine discovery cache.

        Args:
            task_type: Optional task type to invalidate (None = all)
        """
        with self.lock:
            if task_type:
                if task_type in self._discovery_cache:
                    del self._discovery_cache[task_type]
                if task_type in self._discovery_cache_time:
                    del self._discovery_cache_time[task_type]
            else:
                self._discovery_cache.clear()
                self._discovery_cache_time.clear()


# Factory function
def create_optimized_router(
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.PERFORMANCE_BASED,
    enable_performance_tracking: bool = True,
) -> OptimizedEngineRouter:
    """
    Create optimized engine router.

    Args:
        load_balancing_strategy: Load balancing strategy
        enable_performance_tracking: Enable performance tracking

    Returns:
        OptimizedEngineRouter instance
    """
    return OptimizedEngineRouter(
        load_balancing_strategy=load_balancing_strategy,
        enable_performance_tracking=enable_performance_tracking,
    )


# Export
__all__ = [
    "OptimizedEngineRouter",
    "LoadBalancingStrategy",
    "EnginePerformanceMetrics",
    "create_optimized_router",
]

