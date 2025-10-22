#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Metrics Dashboard Integration
Integration with API and VoiceStudio architecture
"""

import os
import json
from pathlib import Path


class MetricsDashboardIntegrator:
    def __init__(self):
        self.repo_path = Path("C:/Users/Tyler/VoiceStudio")
        self.api_path = self.repo_path / "api"
        self.services_path = self.repo_path / "services"
        self.tools_path = self.repo_path / "tools"
        self.docs_path = self.repo_path / "docs"

    def create_dashboard_config(self):
        """Create metrics dashboard configuration"""
        dashboard_config = {
            "dashboard": {
                "enabled": True,
                "host": "127.0.0.1",
                "port": 8050,
                "refresh_interval": 30,
                "max_data_points": 1000,
                "auto_refresh": True,
                "theme": "bootstrap",
            },
            "quality_thresholds": {
                "excellent": 0.9,
                "good": 0.8,
                "fair": 0.7,
                "poor": 0.6,
                "very_poor": 0.0,
            },
            "chart_types": {
                "voice_similarity": "line",
                "audio_quality": "bar",
                "processing_time": "histogram",
                "success_rate": "gauge",
                "engine_performance": "scatter",
                "user_satisfaction": "pie",
            },
            "alert_thresholds": {
                "low_quality": 0.6,
                "slow_processing": 60.0,
                "low_success_rate": 0.8,
                "high_error_rate": 0.1,
            },
            "metrics": {
                "voice_similarity": {
                    "enabled": True,
                    "weight": 0.4,
                    "description": "Voice similarity score",
                },
                "audio_quality": {
                    "enabled": True,
                    "weight": 0.3,
                    "description": "Audio quality assessment",
                },
                "processing_time": {
                    "enabled": True,
                    "weight": 0.1,
                    "description": "Processing time in seconds",
                },
                "success_rate": {
                    "enabled": True,
                    "weight": 0.2,
                    "description": "Operation success rate",
                },
            },
            "storage": {
                "db_path": "voicestudio.db",
                "backup_interval_hours": 24,
                "retention_days": 30,
            },
            "monitoring": {
                "enable_alerts": True,
                "alert_email": None,
                "alert_webhook": None,
                "log_level": "INFO",
            },
        }

        config_path = self.repo_path / "config" / "metrics_dashboard.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(dashboard_config, f, indent=2)

        print(f"Created metrics dashboard config: {config_path}")

    def create_dashboard_api_endpoints(self):
        """Create API endpoints for metrics dashboard"""
        endpoints_content = '''# api/metrics_endpoints.py
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
'''

        endpoints_path = self.api_path / "metrics_endpoints.py"
        with open(endpoints_path, "w", encoding="utf-8") as f:
            f.write(endpoints_content)

        print(f"Created metrics API endpoints: {endpoints_path}")

    def create_dashboard_worker(self):
        """Create metrics dashboard worker"""
        worker_content = '''# workers/metrics_dashboard_worker.py
# Metrics dashboard worker for VoiceStudio

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_metrics_dashboard import VoiceCloningMetricsDashboard, MetricType, QualityLevel, QualityMetric

class MetricsDashboardWorker:
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/metrics_dashboard.json"
        self.dashboard = VoiceCloningMetricsDashboard(self.config_path)

    def add_metric(self, metric_data):
        """Add a quality metric"""
        try:
            # Create metric object
            metric = QualityMetric(
                metric_id=metric_data.get("metric_id", f"metric_{time.time()}"),
                metric_type=MetricType(metric_data["metric_type"]),
                value=float(metric_data["value"]),
                quality_level=self.determine_quality_level(float(metric_data["value"])),
                timestamp=metric_data.get("timestamp", time.time()),
                engine=metric_data["engine"],
                language=metric_data["language"],
                user_id=metric_data.get("user_id"),
                session_id=metric_data.get("session_id"),
                metadata=metric_data.get("metadata")
            )

            # Add metric
            self.dashboard.add_metric(metric)

            return {"success": True, "metric_id": metric.metric_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_metrics_summary(self, hours=24):
        """Get metrics summary"""
        try:
            recent_metrics = self.dashboard.get_recent_metrics(hours=hours)

            if not recent_metrics:
                return {"success": True, "summary": {"total_metrics": 0}}

            # Calculate summary
            summary = {
                "total_metrics": len(recent_metrics),
                "engines": list(set([m.engine for m in recent_metrics])),
                "languages": list(set([m.language for m in recent_metrics])),
                "metric_types": list(set([m.metric_type.value for m in recent_metrics]))
            }

            # Calculate averages
            averages = {}
            for metric_type in MetricType:
                type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
                if type_metrics:
                    averages[metric_type.value] = {
                        "count": len(type_metrics),
                        "average": sum(m.value for m in type_metrics) / len(type_metrics)
                    }

            summary["averages"] = averages

            return {"success": True, "summary": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_alerts(self, limit=50):
        """Get alerts"""
        try:
            recent_alerts = self.dashboard.alerts[-limit:] if self.dashboard.alerts else []
            return {"success": True, "alerts": recent_alerts}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def determine_quality_level(self, value):
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

def main():
    """Main function for worker"""
    import argparse

    parser = argparse.ArgumentParser(description="VoiceStudio Metrics Dashboard Worker")
    parser.add_argument("--action", choices=["add", "summary", "alerts"], required=True,
                       help="Action to perform")
    parser.add_argument("--metric-data", help="JSON file with metric data")
    parser.add_argument("--hours", type=int, default=24, help="Hours for summary")
    parser.add_argument("--limit", type=int, default=50, help="Limit for alerts")

    args = parser.parse_args()

    worker = MetricsDashboardWorker()

    if args.action == "add":
        if not args.metric_data:
            print("Error: --metric-data required for add action")
            sys.exit(1)

        # Load metric data
        with open(args.metric_data, 'r', encoding='utf-8') as f:
            metric_data = json.load(f)

        result = worker.add_metric(metric_data)
        print(json.dumps(result))

    elif args.action == "summary":
        result = worker.get_metrics_summary(args.hours)
        print(json.dumps(result))

    elif args.action == "alerts":
        result = worker.get_alerts(args.limit)
        print(json.dumps(result))

if __name__ == "__main__":
    main()
'''

        worker_path = self.repo_path / "workers" / "metrics_dashboard_worker.py"
        with open(worker_path, "w", encoding="utf-8") as f:
            f.write(worker_content)

        print(f"Created metrics dashboard worker: {worker_path}")

    def create_dashboard_launcher(self):
        """Create dashboard launcher script"""
        launcher_content = '''#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Metrics Dashboard Launcher
Launch the quality metrics dashboard
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_metrics_dashboard import VoiceCloningMetricsDashboard

def main():
    parser = argparse.ArgumentParser(description="VoiceStudio Metrics Dashboard Launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard host")
    parser.add_argument("--port", type=int, default=8050, help="Dashboard port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--generate-samples", type=int, help="Generate sample metrics")
    parser.add_argument("--config", help="Configuration file path")

    args = parser.parse_args()

    try:
        # Create dashboard
        dashboard = VoiceCloningMetricsDashboard(args.config)

        # Generate sample data if requested
        if args.generate_samples:
            dashboard.generate_sample_metrics(args.generate_samples)
            print(f"Generated {args.generate_samples} sample metrics")

        # Run dashboard
        print(f"Starting VoiceStudio Metrics Dashboard on {args.host}:{args.port}")
        print("Press Ctrl+C to stop")

        dashboard.run_dashboard(host=args.host, port=args.port, debug=args.debug)

    except KeyboardInterrupt:
        print("\\nDashboard stopped by user")
    except Exception as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        launcher_path = self.tools_path / "launch_metrics_dashboard.py"
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write(launcher_content)

        print(f"Created dashboard launcher: {launcher_path}")

    def create_dashboard_documentation(self):
        """Create metrics dashboard documentation"""
        docs_content = """# VoiceStudio Ultimate - Quality Metrics Dashboard

## Overview

VoiceStudio Ultimate features a comprehensive quality metrics dashboard that provides real-time monitoring and analysis of voice cloning performance, quality metrics, and system health.

## Features

- **Real-Time Monitoring**: Live updates of quality metrics and performance data
- **Interactive Charts**: Dynamic charts with Plotly for voice similarity, engine performance, audio quality, and processing time
- **Quality Alerts**: Automated alerts for quality issues and performance degradation
- **Multi-Engine Support**: Performance comparison across different voice cloning engines
- **Export Capabilities**: Export metrics data in JSON and CSV formats
- **REST API**: Complete API for metrics collection and retrieval
- **Database Storage**: Persistent storage of metrics data with SQLite
- **Customizable Thresholds**: Configurable quality thresholds and alert levels

## Dashboard Components

### Summary Cards
- **Overall Quality**: Average voice similarity score
- **Success Rate**: Percentage of successful operations
- **Average Processing Time**: Mean processing time in seconds
- **Active Engines**: Number of active voice cloning engines

### Charts
- **Voice Similarity Over Time**: Line chart showing similarity trends
- **Engine Performance Comparison**: Bar chart comparing engine performance
- **Audio Quality Distribution**: Pie chart showing quality level distribution
- **Processing Time Distribution**: Histogram of processing times

### Alerts
- **Quality Alerts**: Real-time alerts for quality issues
- **Performance Alerts**: Alerts for slow processing or low success rates
- **System Alerts**: System health and error alerts

## Quality Metrics

### Voice Similarity
- **Metric Type**: Voice similarity score (0.0 - 1.0)
- **Description**: Measures similarity between cloned and reference voices
- **Quality Levels**: Excellent (0.9+), Good (0.8+), Fair (0.7+), Poor (0.6+), Very Poor (<0.6)

### Audio Quality
- **Metric Type**: Audio quality assessment (0.0 - 1.0)
- **Description**: Overall audio quality including clarity, naturalness, and artifacts
- **Quality Levels**: Based on comprehensive audio analysis

### Processing Time
- **Metric Type**: Processing time in seconds
- **Description**: Time taken to complete voice cloning operations
- **Thresholds**: Alert if processing time exceeds 60 seconds

### Success Rate
- **Metric Type**: Success rate (0.0 - 1.0)
- **Description**: Percentage of successful voice cloning operations
- **Thresholds**: Alert if success rate drops below 80%

## API Endpoints

### Add Metric

#### POST /api/v1/metrics/add-metric

Add a quality metric to the dashboard.

**Request:**
```json
{
  "metric_type": "voice_similarity",
  "value": 0.85,
  "engine": "xtts",
  "language": "en",
  "user_id": "user123",
  "session_id": "session456",
  "metadata": {
    "text_length": 50,
    "reference_duration": 3.2
  }
}
```

**Response:**
```json
{
  "success": true,
  "metric_id": "metric_1642780800.123",
  "message": "Metric added successfully"
}
```

### Get Metrics

#### GET /api/v1/metrics/metrics

Get quality metrics with optional filtering.

**Parameters:**
- `metric_type`: Filter by metric type
- `engine`: Filter by engine
- `language`: Filter by language
- `hours`: Time range in hours (default: 24)
- `limit`: Maximum number of results (default: 100)

**Response:**
```json
{
  "success": true,
  "metrics": [
    {
      "metric_id": "metric_1642780800.123",
      "metric_type": "voice_similarity",
      "value": 0.85,
      "quality_level": "good",
      "timestamp": "2025-01-21T12:00:00Z",
      "engine": "xtts",
      "language": "en",
      "user_id": "user123",
      "session_id": "session456",
      "metadata": {
        "text_length": 50,
        "reference_duration": 3.2
      }
    }
  ],
  "total_count": 1,
  "filtered_count": 1
}
```

### Get Summary

#### GET /api/v1/metrics/summary

Get metrics summary statistics.

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_metrics": 150,
    "time_range_hours": 24,
    "engines": ["xtts", "openvoice", "cosyvoice"],
    "languages": ["en", "es", "fr"],
    "metric_types": ["voice_similarity", "audio_quality", "processing_time"],
    "averages": {
      "voice_similarity": {
        "count": 50,
        "average": 0.87,
        "min": 0.65,
        "max": 0.98
      },
      "audio_quality": {
        "count": 50,
        "average": 0.82,
        "min": 0.58,
        "max": 0.95
      }
    },
    "quality_distribution": {
      "excellent": 15,
      "good": 25,
      "fair": 8,
      "poor": 2,
      "very_poor": 0
    }
  }
}
```

### Get Alerts

#### GET /api/v1/metrics/alerts

Get quality alerts.

**Response:**
```json
{
  "success": true,
  "alerts": [
    {
      "id": "alert_123",
      "message": "Low voice similarity detected",
      "severity": "high",
      "timestamp": "2025-01-21T12:30:00Z",
      "data": {
        "average_similarity": 0.55,
        "threshold": 0.6
      }
    }
  ],
  "total_count": 1
}
```

### Export Metrics

#### GET /api/v1/metrics/export

Export metrics data.

**Parameters:**
- `format`: Export format ("json" or "csv")
- `hours`: Time range in hours (default: 24)
- `metric_type`: Filter by metric type

**Response:**
```json
{
  "success": true,
  "format": "json",
  "data": [...],
  "count": 150
}
```

## Command Line Usage

### Launch Dashboard

```bash
python tools/launch_metrics_dashboard.py \\
  --host 127.0.0.1 \\
  --port 8050 \\
  --debug
```

### Generate Sample Data

```bash
python tools/launch_metrics_dashboard.py \\
  --generate-samples 100
```

### Worker Usage

```bash
# Add metric
python workers/metrics_dashboard_worker.py \\
  --action add \\
  --metric-data metric.json

# Get summary
python workers/metrics_dashboard_worker.py \\
  --action summary \\
  --hours 24

# Get alerts
python workers/metrics_dashboard_worker.py \\
  --action alerts \\
  --limit 50
```

## Configuration

### Dashboard Settings

```json
{
  "dashboard": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 8050,
    "refresh_interval": 30,
    "max_data_points": 1000,
    "auto_refresh": true,
    "theme": "bootstrap"
  }
}
```

### Quality Thresholds

```json
{
  "quality_thresholds": {
    "excellent": 0.9,
    "good": 0.8,
    "fair": 0.7,
    "poor": 0.6,
    "very_poor": 0.0
  }
}
```

### Alert Thresholds

```json
{
  "alert_thresholds": {
    "low_quality": 0.6,
    "slow_processing": 60.0,
    "low_success_rate": 0.8,
    "high_error_rate": 0.1
  }
}
```

## Integration

### VoiceStudio Integration
- **Automatic Metrics**: Metrics automatically collected from voice cloning operations
- **Real-Time Updates**: Dashboard updates in real-time as operations complete
- **Engine Monitoring**: Performance monitoring across all voice cloning engines
- **Quality Tracking**: Continuous quality assessment and tracking

### API Integration
- **REST API**: Complete REST API for metrics collection and retrieval
- **WebSocket Support**: Real-time updates via WebSocket connections
- **Export Options**: Multiple export formats for data analysis
- **Custom Dashboards**: Build custom dashboards using the API

## Performance

### Dashboard Performance
- **Refresh Rate**: 30-second auto-refresh interval
- **Data Points**: Up to 1000 data points in memory
- **Database**: SQLite for persistent storage
- **Charts**: Plotly for interactive visualizations

### Scalability
- **Concurrent Users**: Supports multiple concurrent dashboard users
- **Data Retention**: Configurable data retention periods
- **Storage**: Efficient storage with automatic cleanup
- **Memory Usage**: Optimized memory usage for large datasets

## Best Practices

### Metrics Collection
- **Consistent Timing**: Collect metrics at consistent intervals
- **Quality Validation**: Validate metric values before storage
- **Error Handling**: Implement proper error handling for failed operations
- **Metadata**: Include relevant metadata for better analysis

### Dashboard Usage
- **Regular Monitoring**: Monitor dashboard regularly for quality issues
- **Alert Configuration**: Configure appropriate alert thresholds
- **Data Export**: Export data regularly for backup and analysis
- **Performance Tuning**: Adjust refresh rates based on system performance

### Integration
- **API Usage**: Use API endpoints for custom integrations
- **WebSocket**: Use WebSocket for real-time updates
- **Batch Operations**: Use batch operations for bulk metrics
- **Error Recovery**: Implement error recovery for failed operations

## Use Cases

### Quality Assurance
- **Real-Time Monitoring**: Monitor voice cloning quality in real-time
- **Performance Tracking**: Track performance across different engines
- **Quality Alerts**: Receive alerts for quality issues
- **Trend Analysis**: Analyze quality trends over time

### System Optimization
- **Performance Analysis**: Analyze processing times and bottlenecks
- **Engine Comparison**: Compare performance across engines
- **Resource Monitoring**: Monitor system resource usage
- **Capacity Planning**: Plan system capacity based on usage patterns

### Research and Development
- **Quality Research**: Research voice cloning quality factors
- **Performance Studies**: Study performance characteristics
- **Algorithm Development**: Develop and test new algorithms
- **Benchmarking**: Benchmark against quality standards

---

**Quality Metrics Dashboard** - Comprehensive voice cloning quality monitoring and analysis
"""

        docs_path = self.docs_path / "metrics_dashboard.md"
        with open(docs_path, "w", encoding="utf-8") as f:
            f.write(docs_content)

        print(f"Created metrics dashboard documentation: {docs_path}")

    def create_dashboard_integration(self):
        """Integrate metrics dashboard with main API server"""
        api_server_path = self.repo_path / "voice_studio_api_server.py"

        # Read existing API server
        with open(api_server_path, "r", encoding="utf-8") as f:
            api_content = f.read()

        # Add metrics endpoints import
        if "metrics_endpoints" not in api_content:
            # Add import
            api_content = api_content.replace(
                "from api.batch_endpoints import router as batch_router",
                "from api.batch_endpoints import router as batch_router\nfrom api.metrics_endpoints import router as metrics_router",
            )

            # Add router
            api_content = api_content.replace(
                "self.app.include_router(batch_router)",
                "self.app.include_router(batch_router)\n        self.app.include_router(metrics_router)",
            )

            # Write updated API server
            with open(api_server_path, "w", encoding="utf-8") as f:
                f.write(api_content)

            print(f"Updated API server with metrics endpoints: {api_server_path}")

    def run_dashboard_integration(self):
        """Run complete metrics dashboard integration"""
        print("VoiceStudio Ultimate - Metrics Dashboard Integration")
        print("=" * 60)

        self.create_dashboard_config()
        self.create_dashboard_api_endpoints()
        self.create_dashboard_worker()
        self.create_dashboard_launcher()
        self.create_dashboard_documentation()
        self.create_dashboard_integration()

        print("\n" + "=" * 60)
        print("METRICS DASHBOARD INTEGRATION COMPLETE")
        print("=" * 60)
        print("Configuration: Metrics dashboard settings")
        print("API Endpoints: REST API for metrics collection")
        print("Worker Integration: VoiceStudio worker integration")
        print("Dashboard Launcher: Easy dashboard launching")
        print("Documentation: Complete usage documentation")
        print("API Integration: Integrated with main API server")
        print("\nFeatures:")
        print("- Real-time quality metrics monitoring")
        print("- Interactive charts with Plotly")
        print("- Quality alerts and notifications")
        print("- Multi-engine performance comparison")
        print("- Export capabilities (JSON, CSV)")
        print("- Comprehensive REST API")
        print("- Professional documentation and examples")


def main():
    integrator = MetricsDashboardIntegrator()
    integrator.run_dashboard_integration()


if __name__ == "__main__":
    main()
