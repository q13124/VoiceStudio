"""
Training Module Audit and Enhancement System

Automatically reviews training modules for:
- Completeness (all features implemented)
- Missing features
- Optimization opportunities
- Error handling improvements
- Performance enhancements
- Analytics capabilities
- Checkpoint management
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TrainingModuleAuditResult:
    """Results of training module audit."""

    module_name: str
    module_class: type
    is_complete: bool = False
    missing_features: list[str] = field(default_factory=list)
    optimization_opportunities: list[str] = field(default_factory=list)
    error_handling_issues: list[str] = field(default_factory=list)
    performance_issues: list[str] = field(default_factory=list)
    has_analytics: bool = False
    has_checkpoint_management: bool = False
    has_progress_monitoring: bool = False
    has_parameter_optimization: bool = False
    has_quality_tracking: bool = False
    score: float = 0.0  # Completeness score (0-100)


class TrainingModuleAuditor:
    """
    Audits training modules for completeness and enhancements.
    """

    # Recommended features for training modules
    RECOMMENDED_FEATURES = {
        "analytics": ["get_analytics", "analyze_training", "get_metrics"],
        "checkpoint_management": [
            "save_checkpoint",
            "load_checkpoint",
            "list_checkpoints",
            "delete_checkpoint",
        ],
        "progress_monitoring": [
            "get_progress",
            "update_progress",
            "monitor_training",
        ],
        "parameter_optimization": [
            "optimize_parameters",
            "get_best_parameters",
            "parameter_search",
        ],
        "quality_tracking": [
            "track_quality",
            "get_quality_metrics",
            "evaluate_quality",
        ],
    }

    def __init__(self):
        """Initialize training module auditor."""
        self.audit_results: dict[str, TrainingModuleAuditResult] = {}

    def audit_module(
        self, module_name: str, module_class: type
    ) -> TrainingModuleAuditResult:
        """
        Audit a single training module.

        Args:
            module_name: Name of the module
            module_class: Module class to audit

        Returns:
            Audit result
        """
        result = TrainingModuleAuditResult(
            module_name=module_name, module_class=module_class
        )

        # Get all methods from the class
        methods = {name for name, _ in inspect.getmembers(module_class, inspect.isfunction)}
        methods.update(
            {name for name, _ in inspect.getmembers(module_class, inspect.ismethod)}
        )

        # Check for features
        result.has_analytics = any(
            feature_method in methods
            for feature_method in self.RECOMMENDED_FEATURES["analytics"]
        )
        result.has_checkpoint_management = any(
            feature_method in methods
            for feature_method in self.RECOMMENDED_FEATURES["checkpoint_management"]
        )
        result.has_progress_monitoring = any(
            feature_method in methods
            for feature_method in self.RECOMMENDED_FEATURES["progress_monitoring"]
        )
        result.has_parameter_optimization = any(
            feature_method in methods
            for feature_method in self.RECOMMENDED_FEATURES["parameter_optimization"]
        )
        result.has_quality_tracking = any(
            feature_method in methods
            for feature_method in self.RECOMMENDED_FEATURES["quality_tracking"]
        )

        # Check for missing features
        if not result.has_analytics:
            result.missing_features.append("Training analytics")
        if not result.has_checkpoint_management:
            result.missing_features.append("Checkpoint management")
        if not result.has_progress_monitoring:
            result.missing_features.append("Progress monitoring")
        if not result.has_parameter_optimization:
            result.missing_features.append("Parameter optimization")
        if not result.has_quality_tracking:
            result.missing_features.append("Quality tracking")

        # Check source code for optimization opportunities
        try:
            source = inspect.getsource(module_class)
            if "for " in source and "range(" in source:
                if "torch" in source or "numpy" in source:
                    if "vectorize" not in source and "batch" not in source.lower():
                        result.optimization_opportunities.append(
                            "Consider batch processing for training loops"
                        )

            # Check for error handling
            if "try:" not in source or "except" not in source:
                result.error_handling_issues.append("Missing error handling")
            elif source.count("except") < 2:
                result.error_handling_issues.append(
                    "Limited error handling coverage"
                )

            # Check for performance issues
            if "deepcopy" in source:
                result.performance_issues.append(
                    "Consider shallow copy or views instead of deepcopy"
                )

            # Check for checkpoint management
            if "checkpoint" not in source.lower():
                result.missing_features.append("Checkpoint management")

        except (OSError, TypeError):
            # Can't read source (might be C extension or builtin)
            ...

        # Calculate completeness score
        result.is_complete = len(result.missing_features) == 0
        result.score = self._calculate_score(result)

        return result

    def _calculate_score(self, result: TrainingModuleAuditResult) -> float:
        """
        Calculate completeness score.

        Args:
            result: Audit result

        Returns:
            Score from 0-100
        """
        score = 100.0

        # Deduct for missing features
        score -= len(result.missing_features) * 10.0

        # Deduct for optimization opportunities
        score -= len(result.optimization_opportunities) * 5.0

        # Deduct for error handling issues
        score -= len(result.error_handling_issues) * 5.0

        # Deduct for performance issues
        score -= len(result.performance_issues) * 3.0

        return max(0.0, min(100.0, score))

    def audit_all_modules(
        self, modules: dict[str, type]
    ) -> dict[str, TrainingModuleAuditResult]:
        """
        Audit all modules.

        Args:
            modules: Dictionary of module names to classes

        Returns:
            Dictionary of audit results
        """
        results = {}
        for module_name, module_class in modules.items():
            try:
                result = self.audit_module(module_name, module_class)
                results[module_name] = result
                self.audit_results[module_name] = result
            except Exception as e:
                logger.error(f"Failed to audit module {module_name}: {e}")
                results[module_name] = TrainingModuleAuditResult(
                    module_name=module_name,
                    module_class=module_class,
                    error_handling_issues=[f"Audit failed: {e!s}"],
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

        total_modules = len(self.audit_results)
        complete_modules = sum(
            1 for r in self.audit_results.values() if r.is_complete
        )
        avg_score = (
            sum(r.score for r in self.audit_results.values()) / total_modules
        )

        # Count features
        features_count = {
            "analytics": sum(
                1 for r in self.audit_results.values() if r.has_analytics
            ),
            "checkpoint_management": sum(
                1
                for r in self.audit_results.values()
                if r.has_checkpoint_management
            ),
            "progress_monitoring": sum(
                1
                for r in self.audit_results.values()
                if r.has_progress_monitoring
            ),
            "parameter_optimization": sum(
                1
                for r in self.audit_results.values()
                if r.has_parameter_optimization
            ),
            "quality_tracking": sum(
                1
                for r in self.audit_results.values()
                if r.has_quality_tracking
            ),
        }

        # Count issues
        total_missing_features = sum(
            len(r.missing_features) for r in self.audit_results.values()
        )
        total_optimizations = sum(
            len(r.optimization_opportunities)
            for r in self.audit_results.values()
        )
        total_error_handling = sum(
            len(r.error_handling_issues) for r in self.audit_results.values()
        )
        total_performance = sum(
            len(r.performance_issues) for r in self.audit_results.values()
        )

        return {
            "total_modules": total_modules,
            "complete_modules": complete_modules,
            "incomplete_modules": total_modules - complete_modules,
            "average_score": avg_score,
            "features": features_count,
            "issues": {
                "missing_features": total_missing_features,
                "optimization_opportunities": total_optimizations,
                "error_handling_issues": total_error_handling,
                "performance_issues": total_performance,
            },
        }

    def get_modules_needing_attention(
        self, min_score: float = 70.0
    ) -> list[TrainingModuleAuditResult]:
        """
        Get modules that need attention (score below threshold).

        Args:
            min_score: Minimum acceptable score

        Returns:
            List of modules needing attention
        """
        return [
            result
            for result in self.audit_results.values()
            if result.score < min_score
        ]

    def generate_enhancement_report(self) -> str:
        """
        Generate a markdown report of enhancement opportunities.

        Returns:
            Markdown report
        """
        lines = ["# Training Module Enhancement Report\n"]

        # Summary
        summary = self.get_audit_summary()
        lines.append("## Summary\n")
        lines.append(f"- Total Modules: {summary['total_modules']}")
        lines.append(f"- Complete Modules: {summary['complete_modules']}")
        lines.append(f"- Average Score: {summary['average_score']:.1f}\n")

        # Features
        lines.append("## Feature Coverage\n")
        for feature, count in summary["features"].items():
            percentage = (count / summary["total_modules"]) * 100
            lines.append(
                f"- {feature}: {count}/{summary['total_modules']} "
                f"({percentage:.1f}%)"
            )

        # Modules needing attention
        lines.append("\n## Modules Needing Attention\n")
        needing_attention = self.get_modules_needing_attention()
        for result in sorted(needing_attention, key=lambda x: x.score):
            lines.append(
                f"\n### {result.module_name} (Score: {result.score:.1f})"
            )
            if result.missing_features:
                lines.append(
                    f"- Missing Features: {', '.join(result.missing_features)}"
                )
            if result.optimization_opportunities:
                lines.append(
                    f"- Optimizations: {', '.join(result.optimization_opportunities)}"
                )
            if result.error_handling_issues:
                lines.append(
                    f"- Error Handling: {', '.join(result.error_handling_issues)}"
                )
            if result.performance_issues:
                lines.append(
                    f"- Performance: {', '.join(result.performance_issues)}"
                )

        return "\n".join(lines)


# Export
__all__ = ["TrainingModuleAuditResult", "TrainingModuleAuditor"]

