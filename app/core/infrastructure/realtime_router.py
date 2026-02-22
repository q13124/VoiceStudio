"""
Realtime Router Module for VoiceStudio
Intelligent real-time request routing system

Compatible with:
- Python 3.10+
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

# Import engine router
try:
    from app.core.engines.router import EngineRouter

    HAS_ENGINE_ROUTER = True
except ImportError:
    HAS_ENGINE_ROUTER = False
    logger.warning("Engine router not available")


class RealtimeRouter:
    """
    Realtime Router for intelligent real-time request routing.

    Supports:
    - Latency-based routing
    - Quality-based routing
    - Load balancing
    - Health monitoring
    - Adaptive routing
    - Priority queuing
    - Request tracking
    """

    def __init__(
        self,
        engine_router: EngineRouter | None = None,
        latency_weight: float = 0.4,
        quality_weight: float = 0.4,
        load_weight: float = 0.2,
    ):
        """
        Initialize Realtime Router.

        Args:
            engine_router: Optional EngineRouter instance
            latency_weight: Weight for latency in routing decisions (0.0-1.0)
            quality_weight: Weight for quality in routing decisions (0.0-1.0)
            load_weight: Weight for load in routing decisions (0.0-1.0)
        """
        self.engine_router = engine_router
        self.latency_weight = latency_weight
        self.quality_weight = quality_weight
        self.load_weight = load_weight

        # Performance tracking
        self._latency_history: dict[str, list[float]] = defaultdict(list)
        self._quality_history: dict[str, list[float]] = defaultdict(list)
        self._request_counts: dict[str, int] = defaultdict(int)
        self._active_requests: dict[str, int] = defaultdict(int)
        self._last_request_time: dict[str, float] = {}

        # Routing statistics
        self._routing_stats: dict[str, Any] = {
            "total_requests": 0,
            "routing_decisions": defaultdict(int),
            "average_latency": {},
            "average_quality": {},
        }

    def route_request(
        self,
        task_type: str,
        engines: list[str] | None = None,
        quality_priority: float = 0.5,
        latency_priority: float = 0.5,
        min_quality: float | None = None,
        max_latency: float | None = None,
    ) -> str | None:
        """
        Route a request to the best engine.

        Args:
            task_type: Task type (e.g., "tts", "voice_cloning")
            engines: Optional list of candidate engines
            quality_priority: Quality priority (0.0-1.0)
            latency_priority: Latency priority (0.0-1.0)
            min_quality: Minimum quality threshold
            max_latency: Maximum latency threshold

        Returns:
            Best engine name or None
        """
        if not HAS_ENGINE_ROUTER or not self.engine_router:
            logger.error("Engine router not available")
            return None

        # Get candidate engines
        if engines is None:
            engines = self.engine_router.list_engines()

        if not engines:
            return None

        # Score engines
        scored_engines = []
        for engine_name in engines:
            score = 0.0
            reasons = []

            # Latency score (lower is better)
            avg_latency = self._get_average_latency(engine_name)
            if avg_latency is not None:
                if max_latency and avg_latency > max_latency:
                    continue  # Skip engines exceeding max latency
                latency_score = 1.0 / (1.0 + avg_latency / 1000.0)  # Normalize
                score += latency_score * self.latency_weight * latency_priority
                reasons.append(f"latency:{avg_latency:.1f}ms")

            # Quality score (higher is better)
            avg_quality = self._get_average_quality(engine_name)
            if avg_quality is not None:
                if min_quality and avg_quality < min_quality:
                    continue  # Skip engines below min quality
                score += avg_quality * self.quality_weight * quality_priority
                reasons.append(f"quality:{avg_quality:.3f}")

            # Load score (lower active requests is better)
            active_load = self._active_requests.get(engine_name, 0)
            load_score = 1.0 / (1.0 + active_load / 10.0)  # Normalize
            score += load_score * self.load_weight
            reasons.append(f"load:{active_load}")

            scored_engines.append((engine_name, score, reasons))

        if not scored_engines:
            return None

        # Sort by score
        scored_engines.sort(key=lambda x: x[1], reverse=True)

        # Select best engine
        best_engine = scored_engines[0][0]
        self._routing_stats["routing_decisions"][best_engine] += 1
        self._routing_stats["total_requests"] += 1

        logger.debug(
            f"Routed {task_type} to {best_engine} "
            f"(score: {scored_engines[0][1]:.3f}, reasons: {', '.join(scored_engines[0][2])})"
        )

        return best_engine

    async def route_request_async(
        self,
        task_type: str,
        engines: list[str] | None = None,
        quality_priority: float = 0.5,
        latency_priority: float = 0.5,
        min_quality: float | None = None,
        max_latency: float | None = None,
    ) -> str | None:
        """
        Route a request asynchronously.

        Args:
            task_type: Task type
            engines: Optional list of candidate engines
            quality_priority: Quality priority
            latency_priority: Latency priority
            min_quality: Minimum quality threshold
            max_latency: Maximum latency threshold

        Returns:
            Best engine name or None
        """
        return self.route_request(
            task_type=task_type,
            engines=engines,
            quality_priority=quality_priority,
            latency_priority=latency_priority,
            min_quality=min_quality,
            max_latency=max_latency,
        )

    def record_latency(self, engine_name: str, latency_ms: float):
        """
        Record latency for an engine.

        Args:
            engine_name: Engine name
            latency_ms: Latency in milliseconds
        """
        self._latency_history[engine_name].append(latency_ms)

        # Keep only recent history (last 100 requests)
        if len(self._latency_history[engine_name]) > 100:
            self._latency_history[engine_name] = self._latency_history[engine_name][-100:]

        # Update statistics
        avg_latency = sum(self._latency_history[engine_name]) / len(
            self._latency_history[engine_name]
        )
        self._routing_stats["average_latency"][engine_name] = avg_latency

    def record_quality(self, engine_name: str, quality_score: float):
        """
        Record quality score for an engine.

        Args:
            engine_name: Engine name
            quality_score: Quality score (0.0-1.0)
        """
        self._quality_history[engine_name].append(quality_score)

        # Keep only recent history (last 100 requests)
        if len(self._quality_history[engine_name]) > 100:
            self._quality_history[engine_name] = self._quality_history[engine_name][-100:]

        # Update statistics
        avg_quality = sum(self._quality_history[engine_name]) / len(
            self._quality_history[engine_name]
        )
        self._routing_stats["average_quality"][engine_name] = avg_quality

    def start_request(self, engine_name: str):
        """
        Mark a request as started for an engine.

        Args:
            engine_name: Engine name
        """
        self._active_requests[engine_name] += 1
        self._request_counts[engine_name] += 1
        self._last_request_time[engine_name] = time.time()

    def end_request(self, engine_name: str, latency_ms: float | None = None):
        """
        Mark a request as ended for an engine.

        Args:
            engine_name: Engine name
            latency_ms: Optional latency in milliseconds
        """
        if self._active_requests[engine_name] > 0:
            self._active_requests[engine_name] -= 1

        if latency_ms is not None:
            self.record_latency(engine_name, latency_ms)

    def _get_average_latency(self, engine_name: str) -> float | None:
        """
        Get average latency for an engine.

        Args:
            engine_name: Engine name

        Returns:
            Average latency in milliseconds or None
        """
        if engine_name not in self._latency_history or not self._latency_history[engine_name]:
            return None
        return sum(self._latency_history[engine_name]) / len(self._latency_history[engine_name])

    def _get_average_quality(self, engine_name: str) -> float | None:
        """
        Get average quality for an engine.

        Args:
            engine_name: Engine name

        Returns:
            Average quality score (0.0-1.0) or None
        """
        if engine_name not in self._quality_history or not self._quality_history[engine_name]:
            return None
        return sum(self._quality_history[engine_name]) / len(self._quality_history[engine_name])

    def get_routing_stats(self) -> dict[str, Any]:
        """
        Get routing statistics.

        Returns:
            Dictionary with routing statistics
        """
        stats = {
            "total_requests": self._routing_stats["total_requests"],
            "routing_decisions": dict(self._routing_stats["routing_decisions"]),
            "average_latency": dict(self._routing_stats["average_latency"]),
            "average_quality": dict(self._routing_stats["average_quality"]),
            "active_requests": dict(self._active_requests),
            "total_requests_by_engine": dict(self._request_counts),
        }

        return stats

    def get_engine_performance(self, engine_name: str) -> dict[str, Any]:
        """
        Get performance metrics for an engine.

        Args:
            engine_name: Engine name

        Returns:
            Dictionary with performance metrics
        """
        return {
            "engine_name": engine_name,
            "average_latency_ms": self._get_average_latency(engine_name),
            "average_quality": self._get_average_quality(engine_name),
            "active_requests": self._active_requests.get(engine_name, 0),
            "total_requests": self._request_counts.get(engine_name, 0),
            "last_request_time": self._last_request_time.get(engine_name),
        }

    def reset_stats(self):
        """Reset routing statistics."""
        self._latency_history.clear()
        self._quality_history.clear()
        self._request_counts.clear()
        self._active_requests.clear()
        self._last_request_time.clear()
        self._routing_stats = {
            "total_requests": 0,
            "routing_decisions": defaultdict(int),
            "average_latency": {},
            "average_quality": {},
        }
        logger.info("Routing statistics reset")


def create_realtime_router(
    engine_router: EngineRouter | None = None,
    latency_weight: float = 0.4,
    quality_weight: float = 0.4,
    load_weight: float = 0.2,
) -> RealtimeRouter:
    """
    Factory function to create a Realtime Router instance.

    Args:
        engine_router: Optional EngineRouter instance
        latency_weight: Weight for latency in routing decisions
        quality_weight: Weight for quality in routing decisions
        load_weight: Weight for load in routing decisions

    Returns:
        Initialized RealtimeRouter instance
    """
    return RealtimeRouter(
        engine_router=engine_router,
        latency_weight=latency_weight,
        quality_weight=quality_weight,
        load_weight=load_weight,
    )
