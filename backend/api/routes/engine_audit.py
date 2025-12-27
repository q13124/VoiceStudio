"""
Engine Audit API Routes

Provides endpoints for engine auditing and enhancement tracking.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.core.engines.engine_audit import EngineAuditor
from app.core.engines.engine_registry import get_engine_registry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/engines/audit", tags=["engines"])


@router.get("/all", summary="Audit all engines")
def audit_all_engines() -> Dict[str, Any]:
    """
    Audit all registered engines for completeness and enhancements.

    Returns:
        Dictionary with audit results for all engines
    """
    try:
        registry = get_engine_registry()
        auditor = EngineAuditor()

        # Get all engines
        engines = registry.get_all_engines()

        # Audit all engines
        results = auditor.audit_all_engines(engines)

        # Convert results to dictionaries
        results_dict = {}
        for name, result in results.items():
            results_dict[name] = {
                "engine_name": result.engine_name,
                "is_complete": result.is_complete,
                "score": result.score,
                "missing_methods": result.missing_methods,
                "missing_features": result.missing_features,
                "optimization_opportunities": result.optimization_opportunities,
                "quality_enhancements": result.quality_enhancements,
                "documentation_issues": result.documentation_issues,
                "features": {
                    "batch_processing": result.has_batch_processing,
                    "streaming": result.has_streaming,
                    "quality_metrics": result.has_quality_metrics,
                    "caching": result.has_caching,
                    "lazy_loading": result.has_lazy_loading,
                },
            }

        return {
            "engines": results_dict,
            "summary": auditor.get_audit_summary(),
        }
    except Exception as e:
        logger.error(f"Failed to audit engines: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to audit engines: {str(e)}"
        )


@router.get("/summary", summary="Get audit summary")
def get_audit_summary() -> Dict[str, Any]:
    """
    Get summary of engine audits.

    Returns:
        Summary statistics
    """
    try:
        registry = get_engine_registry()
        auditor = EngineAuditor()

        # Get all engines
        engines = registry.get_all_engines()

        # Audit all engines
        auditor.audit_all_engines(engines)

        # Get summary
        return auditor.get_audit_summary()
    except Exception as e:
        logger.error(f"Failed to get audit summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get audit summary: {str(e)}"
        )


@router.get("/needing-attention", summary="Get engines needing attention")
def get_engines_needing_attention(min_score: float = 70.0) -> Dict[str, Any]:
    """
    Get engines that need attention (score below threshold).

    Args:
        min_score: Minimum acceptable score (default: 70.0)

    Returns:
        List of engines needing attention
    """
    try:
        registry = get_engine_registry()
        auditor = EngineAuditor()

        # Get all engines
        engines = registry.get_all_engines()

        # Audit all engines
        auditor.audit_all_engines(engines)

        # Get engines needing attention
        needing_attention = auditor.get_engines_needing_attention(min_score)

        # Convert to dictionaries
        results = []
        for result in needing_attention:
            results.append(
                {
                    "engine_name": result.engine_name,
                    "score": result.score,
                    "missing_methods": result.missing_methods,
                    "missing_features": result.missing_features,
                    "optimization_opportunities": result.optimization_opportunities,
                    "quality_enhancements": result.quality_enhancements,
                }
            )

        return {
            "engines": results,
            "count": len(results),
            "min_score": min_score,
        }
    except Exception as e:
        logger.error(f"Failed to get engines needing attention: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get engines needing attention: {str(e)}",
        )


@router.get("/report", summary="Generate enhancement report")
def generate_enhancement_report() -> Dict[str, str]:
    """
    Generate a markdown report of enhancement opportunities.

    Returns:
        Markdown report
    """
    try:
        registry = get_engine_registry()
        auditor = EngineAuditor()

        # Get all engines
        engines = registry.get_all_engines()

        # Audit all engines
        auditor.audit_all_engines(engines)

        # Generate report
        report = auditor.generate_enhancement_report()

        return {"report": report}
    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate report: {str(e)}"
        )
