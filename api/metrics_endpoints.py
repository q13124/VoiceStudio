# api/metrics_endpoints.py
# API endpoints for metrics dashboard

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_metrics_dashboard import VoiceCloningMetricsDashboard, MetricType, QualityLevel, QualityMetric
from api.models import *

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

# Initialize dashboard
dashboard = VoiceCloningMetricsDashboard()

@router.post("/add-metric")
async def add_quality_metric(metric_data: Dict[str, Any]):
    """Add a quality metric"""
    try:
        # Validate metric data
        required_fields = ["metric_type", "value", "engine", "language"]
        for field in required_fields:
            if field not in metric_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

        # Create metric object
        metric = QualityMetric(
            metric_id=metric_data.get("metric_id", f"metric_{datetime.utcnow().timestamp()}"),
            metric_type=MetricType(metric_data["metric_type"]),
            value=float(metric_data["value"]),
            quality_level=determine_quality_level(float(metric_data["value"])),
            timestamp=datetime.utcnow(),
            engine=metric_data["engine"],
            language=metric_data["language"],
            user_id=metric_data.get("user_id"),
            session_id=metric_data.get("session_id"),
            metadata=metric_data.get("metadata")
        )

        # Add metric
        dashboard.add_metric(metric)

        return {
            "success": True,
            "metric_id": metric.metric_id,
            "message": "Metric added successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics(
    metric_type: Optional[str] = Query(None),
    engine: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    hours: int = Query(24),
    limit: int = Query(100)
):
    """Get quality metrics"""
    try:
        # Get recent metrics
        recent_metrics = dashboard.get_recent_metrics(hours=hours)

        # Filter metrics
        filtered_metrics = recent_metrics

        if metric_type:
            filtered_metrics = [m for m in filtered_metrics if m.metric_type.value == metric_type]

        if engine:
            filtered_metrics = [m for m in filtered_metrics if m.engine == engine]

        if language:
            filtered_metrics = [m for m in filtered_metrics if m.language == language]

        # Limit results
        filtered_metrics = filtered_metrics[:limit]

        # Convert to dict
        metrics_data = []
        for metric in filtered_metrics:
            metrics_data.append({
                "metric_id": metric.metric_id,
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "quality_level": metric.quality_level.value,
                "timestamp": metric.timestamp.isoformat(),
                "engine": metric.engine,
                "language": metric.language,
                "user_id": metric.user_id,
                "session_id": metric.session_id,
                "metadata": metric.metadata
            })

        return {
            "success": True,
            "metrics": metrics_data,
            "total_count": len(metrics_data),
            "filtered_count": len(filtered_metrics)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_metrics_summary(hours: int = Query(24)):
    """Get metrics summary"""
    try:
        # Get recent metrics
        recent_metrics = dashboard.get_recent_metrics(hours=hours)

        if not recent_metrics:
            return {
                "success": True,
                "summary": {
                    "total_metrics": 0,
                    "message": "No metrics available"
                }
            }

        # Calculate summary statistics
        summary = {
            "total_metrics": len(recent_metrics),
            "time_range_hours": hours,
            "engines": list(set([m.engine for m in recent_metrics])),
            "languages": list(set([m.language for m in recent_metrics])),
            "metric_types": list(set([m.metric_type.value for m in recent_metrics]))
        }

        # Calculate averages by metric type
        averages = {}
        for metric_type in MetricType:
            type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
            if type_metrics:
                averages[metric_type.value] = {
                    "count": len(type_metrics),
                    "average": sum(m.value for m in type_metrics) / len(type_metrics),
                    "min": min(m.value for m in type_metrics),
                    "max": max(m.value for m in type_metrics)
                }

        summary["averages"] = averages

        # Calculate quality level distribution
        quality_distribution = {}
        for quality_level in QualityLevel:
            count = len([m for m in recent_metrics if m.quality_level == quality_level])
            quality_distribution[quality_level.value] = count

        summary["quality_distribution"] = quality_distribution

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts(limit: int = Query(50)):
    """Get quality alerts"""
    try:
        # Get recent alerts
        recent_alerts = dashboard.alerts[-limit:] if dashboard.alerts else []

        return {
            "success": True,
            "alerts": recent_alerts,
            "total_count": len(dashboard.alerts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    hours: int = Query(24),
    engine: Optional[str] = Query(None),
    language: Optional[str] = Query(None)
):
    """Get chart data for specific chart type"""
    try:
        # Get recent metrics
        recent_metrics = dashboard.get_recent_metrics(hours=hours)

        # Filter metrics
        if engine:
            recent_metrics = [m for m in recent_metrics if m.engine == engine]

        if language:
            recent_metrics = [m for m in recent_metrics if m.language == language]

        # Generate chart data based on type
        if chart_type == "voice_similarity":
            chart_data = generate_voice_similarity_chart_data(recent_metrics)
        elif chart_type == "engine_performance":
            chart_data = generate_engine_performance_chart_data(recent_metrics)
        elif chart_type == "audio_quality":
            chart_data = generate_audio_quality_chart_data(recent_metrics)
        elif chart_type == "processing_time":
            chart_data = generate_processing_time_chart_data(recent_metrics)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown chart type: {chart_type}")

        return {
            "success": True,
            "chart_type": chart_type,
            "data": chart_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_metrics(
    format: str = Query("json"),
    hours: int = Query(24),
    metric_type: Optional[str] = Query(None)
):
    """Export metrics data"""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'csv'")

        # Get recent metrics
        recent_metrics = dashboard.get_recent_metrics(hours=hours)

        # Filter by metric type if specified
        if metric_type:
            recent_metrics = [m for m in recent_metrics if m.metric_type.value == metric_type]

        if format == "json":
            # Convert to JSON format
            export_data = []
            for metric in recent_metrics:
                export_data.append({
                    "metric_id": metric.metric_id,
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "quality_level": metric.quality_level.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "engine": metric.engine,
                    "language": metric.language,
                    "user_id": metric.user_id,
                    "session_id": metric.session_id,
                    "metadata": metric.metadata
                })

            return {
                "success": True,
                "format": "json",
                "data": export_data,
                "count": len(export_data)
            }

        elif format == "csv":
            # Convert to CSV format
            csv_data = []
            for metric in recent_metrics:
                csv_data.append({
                    "metric_id": metric.metric_id,
                    "metric_type": metric.metric_type.value,
                    "value": metric.value,
                    "quality_level": metric.quality_level.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "engine": metric.engine,
                    "language": metric.language,
                    "user_id": metric.user_id,
                    "session_id": metric.session_id
                })

            return {
                "success": True,
                "format": "csv",
                "data": csv_data,
                "count": len(csv_data)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def determine_quality_level(value: float) -> QualityLevel:
    """Determine quality level from value"""
    if value >= 0.9:
        return QualityLevel.EXCELLENT
    elif value >= 0.8:
        return QualityLevel.GOOD
    elif value >= 0.7:
        return QualityLevel.FAIR
    elif value >= 0.6:
        return QualityLevel.POOR
    else:
        return QualityLevel.VERY_POOR

def generate_voice_similarity_chart_data(metrics):
    """Generate voice similarity chart data"""
    similarity_metrics = [m for m in metrics if m.metric_type == MetricType.VOICE_SIMILARITY]

    chart_data = {
        "type": "line",
        "data": []
    }

    # Group by engine
    engines = set([m.engine for m in similarity_metrics])
    for engine in engines:
        engine_metrics = [m for m in similarity_metrics if m.engine == engine]
        chart_data["data"].append({
            "name": engine,
            "x": [m.timestamp.isoformat() for m in engine_metrics],
            "y": [m.value for m in engine_metrics]
        })

    return chart_data

def generate_engine_performance_chart_data(metrics):
    """Generate engine performance chart data"""
    similarity_metrics = [m for m in metrics if m.metric_type == MetricType.VOICE_SIMILARITY]

    chart_data = {
        "type": "bar",
        "data": []
    }

    # Group by engine
    engines = set([m.engine for m in similarity_metrics])
    for engine in engines:
        engine_metrics = [m for m in similarity_metrics if m.engine == engine]
        avg_score = sum(m.value for m in engine_metrics) / len(engine_metrics)

        chart_data["data"].append({
            "name": engine,
            "x": [engine],
            "y": [avg_score]
        })

    return chart_data

def generate_audio_quality_chart_data(metrics):
    """Generate audio quality chart data"""
    quality_metrics = [m for m in metrics if m.metric_type == MetricType.AUDIO_QUALITY]

    chart_data = {
        "type": "pie",
        "data": []
    }

    # Count quality levels
    quality_counts = {}
    for metric in quality_metrics:
        level = metric.quality_level.value
        quality_counts[level] = quality_counts.get(level, 0) + 1

    for level, count in quality_counts.items():
        chart_data["data"].append({
            "name": level,
            "value": count
        })

    return chart_data

def generate_processing_time_chart_data(metrics):
    """Generate processing time chart data"""
    time_metrics = [m for m in metrics if m.metric_type == MetricType.PROCESSING_TIME]

    chart_data = {
        "type": "histogram",
        "data": []
    }

    if time_metrics:
        values = [m.value for m in time_metrics]
        chart_data["data"].append({
            "name": "Processing Time",
            "x": values
        })

    return chart_data
