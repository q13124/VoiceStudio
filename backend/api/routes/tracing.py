"""
Tracing API Routes — Phase 5.1

Provides API endpoints for trace management, export, and analysis.
All operations are local-first and require no external dependencies.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.services.telemetry import get_telemetry_service, SpanStatus
from backend.services.trace_export import (
    TraceExporter,
    TraceAnalyzer,
    TraceSummary,
    get_trace_exporter,
    get_trace_analyzer,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tracing", tags=["tracing"])


# =============================================================================
# Response Models
# =============================================================================

class SpanResponse(BaseModel):
    """Response model for a span."""
    trace_id: str
    span_id: str
    name: str
    duration_ms: float
    status: str
    parent_span_id: Optional[str] = None
    error: Optional[str] = None


class TraceSummaryResponse(BaseModel):
    """Response model for trace summary."""
    total_traces: int
    total_spans: int
    avg_duration_ms: float
    min_duration_ms: float
    max_duration_ms: float
    p50_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    error_rate: float


class OperationStats(BaseModel):
    """Statistics for an operation."""
    operation: str
    count: int
    avg_ms: float
    p50_ms: float
    p95_ms: float
    error_rate: float


class ExportResponse(BaseModel):
    """Response for trace export."""
    success: bool
    filepath: str
    trace_count: int
    span_count: int
    message: str


class TraceTreeNode(BaseModel):
    """Tree node for trace visualization."""
    span_id: str
    name: str
    duration_ms: float
    status: str
    children: List["TraceTreeNode"] = []


TraceTreeNode.model_rebuild()


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/summary", response_model=TraceSummaryResponse)
async def get_trace_summary(
    limit: int = Query(1000, ge=1, le=10000, description="Maximum spans to analyze"),
):
    """
    Get summary statistics for recent traces.
    
    Returns aggregated metrics including:
    - Total traces and spans
    - Duration statistics (avg, p50, p95, p99)
    - Error rate
    """
    try:
        exporter = get_trace_exporter()
        spans = exporter.get_traces(limit)
        summary = exporter.calculate_summary(spans)
        
        return TraceSummaryResponse(
            total_traces=summary.total_traces,
            total_spans=summary.total_spans,
            avg_duration_ms=summary.avg_duration_ms,
            min_duration_ms=summary.min_duration_ms,
            max_duration_ms=summary.max_duration_ms,
            p50_duration_ms=summary.p50_duration_ms,
            p95_duration_ms=summary.p95_duration_ms,
            p99_duration_ms=summary.p99_duration_ms,
            error_rate=summary.error_rate,
        )
    except Exception as e:
        logger.error(f"Error getting trace summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=List[SpanResponse])
async def get_recent_spans(
    limit: int = Query(100, ge=1, le=1000, description="Maximum spans to return"),
    operation: Optional[str] = Query(None, description="Filter by operation name"),
    status: Optional[str] = Query(None, description="Filter by status (ok, error)"),
):
    """
    Get recent spans from the telemetry service.
    
    Supports filtering by operation name and status.
    """
    try:
        exporter = get_trace_exporter()
        
        def filter_fn(span):
            if operation and operation not in span.name:
                return False
            if status and span.status.value != status:
                return False
            return True
        
        spans = exporter.get_traces(limit, filter_fn)
        
        return [
            SpanResponse(
                trace_id=s.trace_id,
                span_id=s.span_id,
                name=s.name,
                duration_ms=s.duration_ms,
                status=s.status.value,
                parent_span_id=s.parent_span_id,
                error=s.error,
            )
            for s in spans[:limit]
        ]
    except Exception as e:
        logger.error(f"Error getting recent spans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations", response_model=List[OperationStats])
async def get_operation_statistics(
    limit: int = Query(1000, ge=1, le=10000, description="Maximum spans to analyze"),
):
    """
    Get performance statistics per operation.
    
    Returns count, average duration, percentiles, and error rate for each operation.
    """
    try:
        analyzer = get_trace_analyzer()
        stats = analyzer.get_operation_stats(limit)
        
        return [
            OperationStats(
                operation=name,
                count=data["count"],
                avg_ms=data["avg_ms"],
                p50_ms=data["p50_ms"],
                p95_ms=data["p95_ms"],
                error_rate=data["error_rate"],
            )
            for name, data in sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)
        ]
    except Exception as e:
        logger.error(f"Error getting operation statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slow-spans", response_model=List[SpanResponse])
async def get_slow_spans(
    threshold_ms: float = Query(1000, ge=0, description="Duration threshold in ms"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum spans to return"),
):
    """
    Get spans slower than the specified threshold.
    
    Useful for identifying performance bottlenecks.
    """
    try:
        analyzer = get_trace_analyzer()
        slow_spans = analyzer.find_slow_spans(threshold_ms, limit)
        
        return [
            SpanResponse(
                trace_id=s.trace_id,
                span_id=s.span_id,
                name=s.name,
                duration_ms=s.duration_ms,
                status=s.status.value,
                parent_span_id=s.parent_span_id,
                error=s.error,
            )
            for s in slow_spans[:limit]
        ]
    except Exception as e:
        logger.error(f"Error getting slow spans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors", response_model=List[SpanResponse])
async def get_error_spans(
    limit: int = Query(100, ge=1, le=1000, description="Maximum spans to return"),
):
    """
    Get spans with errors.
    
    Useful for debugging and error analysis.
    """
    try:
        analyzer = get_trace_analyzer()
        error_spans = analyzer.find_errors(limit)
        
        return [
            SpanResponse(
                trace_id=s.trace_id,
                span_id=s.span_id,
                name=s.name,
                duration_ms=s.duration_ms,
                status=s.status.value,
                parent_span_id=s.parent_span_id,
                error=s.error,
            )
            for s in error_spans[:limit]
        ]
    except Exception as e:
        logger.error(f"Error getting error spans: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trace/{trace_id}/tree", response_model=TraceTreeNode)
async def get_trace_tree(trace_id: str):
    """
    Get a tree structure for a specific trace.
    
    Useful for visualizing the call hierarchy of a trace.
    """
    try:
        analyzer = get_trace_analyzer()
        tree = analyzer.get_trace_tree(trace_id)
        
        if not tree:
            raise HTTPException(status_code=404, detail=f"Trace {trace_id} not found")
        
        return tree
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trace tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=ExportResponse)
async def export_traces(
    limit: int = Query(1000, ge=1, le=10000, description="Maximum spans to export"),
    filename: Optional[str] = Query(None, description="Output filename"),
):
    """
    Export traces to a JSON file.
    
    The file is saved to .buildlogs/traces/ directory.
    """
    try:
        exporter = get_trace_exporter()
        spans = exporter.get_traces(limit)
        grouped = exporter.group_by_trace(spans)
        
        filepath = exporter.export_to_json(filename, limit, include_summary=True)
        
        return ExportResponse(
            success=True,
            filepath=str(filepath),
            trace_count=len(grouped),
            span_count=len(spans),
            message=f"Successfully exported {len(grouped)} traces to {filepath}",
        )
    except Exception as e:
        logger.error(f"Error exporting traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))
