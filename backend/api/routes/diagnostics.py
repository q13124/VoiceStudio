"""
Diagnostics API Routes — Phase 5.3

Provides API endpoints for system diagnostics and troubleshooting.
All operations are local-first and require no external dependencies.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.services.diagnostics import (
    DiagnosticsService,
    DiagnosticReport,
    DiagnosticCheck,
    get_diagnostics_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


# =============================================================================
# Response Models
# =============================================================================


class DiagnosticCheckResponse(BaseModel):
    """Response model for a diagnostic check."""
    
    name: str
    category: str
    status: str
    message: str
    details: Dict = {}
    duration_ms: float = 0.0


class DiagnosticReportResponse(BaseModel):
    """Response model for diagnostic report."""
    
    generated_at: str
    hostname: str
    platform: str
    python_version: str
    overall_status: str
    checks: List[DiagnosticCheckResponse]
    environment: Dict
    recommendations: List[str]


class QuickStatusResponse(BaseModel):
    """Response model for quick status."""
    
    timestamp: str
    hostname: str
    platform: str
    python_version: str
    diagnostics_available: bool


class SaveReportResponse(BaseModel):
    """Response model for save report."""
    
    success: bool
    filepath: str
    message: str


# =============================================================================
# Helper Functions
# =============================================================================


def _convert_check(check: DiagnosticCheck) -> DiagnosticCheckResponse:
    """Convert internal check to response model."""
    return DiagnosticCheckResponse(
        name=check.name,
        category=check.category,
        status=check.status,
        message=check.message,
        details=check.details,
        duration_ms=check.duration_ms,
    )


def _convert_report(report: DiagnosticReport) -> DiagnosticReportResponse:
    """Convert internal report to response model."""
    return DiagnosticReportResponse(
        generated_at=report.generated_at,
        hostname=report.hostname,
        platform=report.platform,
        python_version=report.python_version,
        overall_status=report.overall_status,
        checks=[_convert_check(c) for c in report.checks],
        environment=report.environment,
        recommendations=report.recommendations,
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/status", response_model=QuickStatusResponse)
async def get_quick_status():
    """
    Get quick system status.
    
    Returns a lightweight status check without running full diagnostics.
    """
    try:
        service = get_diagnostics_service()
        status = service.get_quick_status()
        return QuickStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting quick status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/run", response_model=DiagnosticReportResponse)
async def run_diagnostics(
    include_sensitive: bool = Query(
        False,
        description="Include sensitive information in report"
    ),
):
    """
    Run full system diagnostics.
    
    Performs comprehensive system checks including:
    - Python environment
    - System resources (CPU, memory, disk)
    - Required dependencies
    - Path configuration
    - Backend services
    - Network connectivity
    
    Returns a detailed report with recommendations.
    """
    try:
        service = get_diagnostics_service()
        report = service.run_diagnostics(include_sensitive)
        return _convert_report(report)
    except Exception as e:
        logger.error(f"Error running diagnostics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/checks", response_model=List[DiagnosticCheckResponse])
async def get_checks(
    category: Optional[str] = Query(
        None,
        description="Filter by category"
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by status (pass, warn, fail)"
    ),
):
    """
    Run diagnostics and get individual check results.
    
    Allows filtering by category and status.
    """
    try:
        service = get_diagnostics_service()
        report = service.run_diagnostics(include_sensitive=False)
        
        checks = report.checks
        
        if category:
            checks = [c for c in checks if c.category == category]
        
        if status:
            checks = [c for c in checks if c.status == status]
        
        return [_convert_check(c) for c in checks]
    except Exception as e:
        logger.error(f"Error getting checks: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/categories")
async def get_categories():
    """
    Get available diagnostic categories.
    """
    return {
        "categories": [
            "environment",
            "resources",
            "dependencies",
            "paths",
            "services",
            "network",
        ]
    }


@router.post("/save", response_model=SaveReportResponse)
async def save_diagnostic_report(
    filename: Optional[str] = Query(
        None,
        description="Custom filename for the report"
    ),
):
    """
    Run diagnostics and save report to file.
    
    The report is saved to .buildlogs/diagnostics/ directory.
    """
    try:
        service = get_diagnostics_service()
        report = service.run_diagnostics(include_sensitive=False)
        filepath = service.save_report(report, filename)
        
        return SaveReportResponse(
            success=True,
            filepath=str(filepath),
            message=f"Diagnostic report saved to {filepath}",
        )
    except Exception as e:
        logger.error(f"Error saving diagnostic report: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/recommendations")
async def get_recommendations():
    """
    Get recommendations based on current system state.
    """
    try:
        service = get_diagnostics_service()
        report = service.run_diagnostics(include_sensitive=False)
        
        return {
            "overall_status": report.overall_status,
            "recommendations": report.recommendations,
            "issues_found": len([c for c in report.checks if c.status != "pass"]),
            "total_checks": len(report.checks),
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/environment")
async def get_environment_info():
    """
    Get environment configuration.
    
    Returns relevant environment variables and system information.
    """
    try:
        service = get_diagnostics_service()
        report = service.run_diagnostics(include_sensitive=False)
        
        return {
            "environment": report.environment,
            "hostname": report.hostname,
            "platform": report.platform,
            "python_version": report.python_version,
        }
    except Exception as e:
        logger.error(f"Error getting environment info: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
