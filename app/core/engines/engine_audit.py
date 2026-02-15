"""
Engine Audit and Enhancement System

Automatically reviews engines for:
- Completeness (all required methods implemented)
- Missing features
- Optimization opportunities
- Quality enhancements
- Documentation gaps
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any

from .protocols import EngineProtocol

logger = logging.getLogger(__name__)


@dataclass
class EngineAuditResult:
    """Results of engine audit."""

    engine_name: str
    engine_class: type[EngineProtocol]
    is_complete: bool = False
    missing_methods: list[str] = field(default_factory=list)
    missing_features: list[str] = field(default_factory=list)
    optimization_opportunities: list[str] = field(default_factory=list)
    quality_enhancements: list[str] = field(default_factory=list)
    documentation_issues: list[str] = field(default_factory=list)
    has_batch_processing: bool = False
    has_streaming: bool = False
    has_quality_metrics: bool = False
    has_caching: bool = False
    has_lazy_loading: bool = False
    score: float = 0.0  # Completeness score (0-100)


class EngineAuditor:
    """
    Audits engines for completeness and enhancement opportunities.
    """

    # Required methods from EngineProtocol
    REQUIRED_METHODS = {
        "initialize",
        "cleanup",
        "is_initialized",
        "get_device",
        "get_info",
    }

    # Optional but recommended methods
    RECOMMENDED_METHODS = {
        "synthesize",
        "batch_synthesize",
        "transcribe",
        "clone_voice",
        "get_supported_languages",
        "get_supported_formats",
    }

    # Features to check for
    FEATURES = {
        "batch_processing": ["batch_synthesize", "batch_transcribe"],
        "streaming": ["stream_synthesize", "stream_transcribe"],
        "quality_metrics": ["calculate_quality", "get_quality_metrics"],
        "caching": ["_cache", "_get_cached", "cache"],
        "lazy_loading": ["_load_model", "_lazy_load"],
    }

    def __init__(self):
        """Initialize engine auditor."""
        self.audit_results: dict[str, EngineAuditResult] = {}

    def audit_engine(
        self, engine_name: str, engine_class: type[EngineProtocol]
    ) -> EngineAuditResult:
        """
        Audit a single engine.

        Args:
            engine_name: Name of the engine
            engine_class: Engine class to audit

        Returns:
            Audit result
        """
        result = EngineAuditResult(engine_name=engine_name, engine_class=engine_class)

        # Get all methods from the class
        methods = {
            name for name, _ in inspect.getmembers(engine_class, inspect.isfunction)
        }
        methods.update(
            {name for name, _ in inspect.getmembers(engine_class, inspect.ismethod)}
        )

        # Check required methods
        for method in self.REQUIRED_METHODS:
            if method not in methods:
                result.missing_methods.append(method)

        # Check recommended methods
        for method in self.RECOMMENDED_METHODS:
            if method not in methods:
                result.missing_features.append(f"Missing method: {method}")

        # Check for features
        result.has_batch_processing = any(
            feature_method in methods
            for feature_method in self.FEATURES["batch_processing"]
        )
        result.has_streaming = any(
            feature_method in methods for feature_method in self.FEATURES["streaming"]
        )
        result.has_quality_metrics = any(
            feature_method in methods
            for feature_method in self.FEATURES["quality_metrics"]
        )
        result.has_caching = any(
            feature_method in methods for feature_method in self.FEATURES["caching"]
        )
        result.has_lazy_loading = any(
            feature_method in methods
            for feature_method in self.FEATURES["lazy_loading"]
        )

        # Check for optimization opportunities
        if not result.has_caching:
            result.optimization_opportunities.append("Add model caching")
        if not result.has_lazy_loading:
            result.optimization_opportunities.append("Add lazy loading")
        if not result.has_batch_processing:
            result.optimization_opportunities.append("Add batch processing")

        # Check for quality enhancements
        if not result.has_quality_metrics:
            result.quality_enhancements.append("Add quality metrics integration")

        # Check documentation
        docstring = inspect.getdoc(engine_class)
        if not docstring or len(docstring) < 50:
            result.documentation_issues.append("Insufficient class documentation")

        # Calculate completeness score
        result.is_complete = len(result.missing_methods) == 0
        result.score = self._calculate_score(result)

        return result

    def _calculate_score(self, result: EngineAuditResult) -> float:
        """
        Calculate completeness score.

        Args:
            result: Audit result

        Returns:
            Score from 0-100
        """
        score = 100.0

        # Deduct for missing required methods
        score -= len(result.missing_methods) * 20.0

        # Deduct for missing recommended methods
        score -= len(result.missing_features) * 5.0

        # Deduct for missing features
        if not result.has_batch_processing:
            score -= 5.0
        if not result.has_streaming:
            score -= 3.0
        if not result.has_quality_metrics:
            score -= 5.0
        if not result.has_caching:
            score -= 5.0
        if not result.has_lazy_loading:
            score -= 5.0

        # Deduct for documentation issues
        score -= len(result.documentation_issues) * 2.0

        return max(0.0, min(100.0, score))

    def audit_all_engines(
        self, engine_registry: dict[str, type[EngineProtocol]]
    ) -> dict[str, EngineAuditResult]:
        """
        Audit all engines in registry.

        Args:
            engine_registry: Dictionary of engine names to classes

        Returns:
            Dictionary of audit results
        """
        results = {}
        for engine_name, engine_class in engine_registry.items():
            try:
                result = self.audit_engine(engine_name, engine_class)
                results[engine_name] = result
                self.audit_results[engine_name] = result
            except Exception as e:
                logger.error(f"Failed to audit engine {engine_name}: {e}")
                results[engine_name] = EngineAuditResult(
                    engine_name=engine_name,
                    engine_class=engine_class,
                    documentation_issues=[f"Audit failed: {e!s}"],
                )

        return results

    def get_audit_summary(self) -> dict[str, Any]:
        """
        Get summary of all audits.

        Returns:
            Summary dictionary
        """
        if not self.audit_results:
            return {"error": "No audits performed"}

        total_engines = len(self.audit_results)
        complete_engines = sum(1 for r in self.audit_results.values() if r.is_complete)
        avg_score = sum(r.score for r in self.audit_results.values()) / total_engines

        # Count features
        features_count = {
            "batch_processing": sum(
                1 for r in self.audit_results.values() if r.has_batch_processing
            ),
            "streaming": sum(1 for r in self.audit_results.values() if r.has_streaming),
            "quality_metrics": sum(
                1 for r in self.audit_results.values() if r.has_quality_metrics
            ),
            "caching": sum(1 for r in self.audit_results.values() if r.has_caching),
            "lazy_loading": sum(
                1 for r in self.audit_results.values() if r.has_lazy_loading
            ),
        }

        # Count issues
        total_missing_methods = sum(
            len(r.missing_methods) for r in self.audit_results.values()
        )
        total_missing_features = sum(
            len(r.missing_features) for r in self.audit_results.values()
        )
        total_optimizations = sum(
            len(r.optimization_opportunities) for r in self.audit_results.values()
        )
        total_quality_enhancements = sum(
            len(r.quality_enhancements) for r in self.audit_results.values()
        )

        return {
            "total_engines": total_engines,
            "complete_engines": complete_engines,
            "incomplete_engines": total_engines - complete_engines,
            "average_score": avg_score,
            "features": features_count,
            "issues": {
                "missing_methods": total_missing_methods,
                "missing_features": total_missing_features,
                "optimization_opportunities": total_optimizations,
                "quality_enhancements": total_quality_enhancements,
            },
        }

    def get_engines_needing_attention(
        self, min_score: float = 70.0
    ) -> list[EngineAuditResult]:
        """
        Get engines that need attention (score below threshold).

        Args:
            min_score: Minimum acceptable score

        Returns:
            List of engines needing attention
        """
        return [
            result for result in self.audit_results.values() if result.score < min_score
        ]

    def generate_enhancement_report(self) -> str:
        """
        Generate a markdown report of enhancement opportunities.

        Returns:
            Markdown report
        """
        lines = ["# Engine Enhancement Report\n"]

        # Summary
        summary = self.get_audit_summary()
        lines.append("## Summary\n")
        lines.append(f"- Total Engines: {summary['total_engines']}")
        lines.append(f"- Complete Engines: {summary['complete_engines']}")
        lines.append(f"- Average Score: {summary['average_score']:.1f}\n")

        # Features
        lines.append("## Feature Coverage\n")
        for feature, count in summary["features"].items():
            percentage = (count / summary["total_engines"]) * 100
            lines.append(
                f"- {feature}: {count}/{summary['total_engines']} ({percentage:.1f}%)"
            )

        # Engines needing attention
        lines.append("\n## Engines Needing Attention\n")
        needing_attention = self.get_engines_needing_attention()
        for result in sorted(needing_attention, key=lambda x: x.score):
            lines.append(f"\n### {result.engine_name} (Score: {result.score:.1f})")
            if result.missing_methods:
                lines.append(f"- Missing Methods: {', '.join(result.missing_methods)}")
            if result.missing_features:
                lines.append(f"- Missing Features: {len(result.missing_features)}")
            if result.optimization_opportunities:
                lines.append(
                    f"- Optimizations: {', '.join(result.optimization_opportunities)}"
                )
            if result.quality_enhancements:
                lines.append(
                    f"- Quality Enhancements: {', '.join(result.quality_enhancements)}"
                )

        return "\n".join(lines)


# Export
__all__ = ["EngineAuditResult", "EngineAuditor"]
