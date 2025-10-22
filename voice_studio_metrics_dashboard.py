#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Quality Metrics Dashboard
Comprehensive voice cloning quality metrics dashboard
"""

import os
import json
import time
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import csv
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import threading
from queue import Queue, Empty
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, deque
import sqlite3
import sqlalchemy
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc


class MetricType(Enum):
    """Quality metric types"""

    VOICE_SIMILARITY = "voice_similarity"
    AUDIO_QUALITY = "audio_quality"
    PROCESSING_TIME = "processing_time"
    SUCCESS_RATE = "success_rate"
    ENGINE_PERFORMANCE = "engine_performance"
    USER_SATISFACTION = "user_satisfaction"


class QualityLevel(Enum):
    """Quality levels"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    VERY_POOR = "very_poor"


@dataclass
class QualityMetric:
    """Quality metric data"""

    metric_id: str
    metric_type: MetricType
    value: float
    quality_level: QualityLevel
    timestamp: datetime
    engine: str
    language: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class DashboardConfig:
    """Dashboard configuration"""

    refresh_interval: int = 30
    max_data_points: int = 1000
    quality_thresholds: Dict[str, float] = None
    chart_types: Dict[str, str] = None
    alert_thresholds: Dict[str, float] = None


# Database models
Base = declarative_base()


class QualityMetricDB(Base):
    __tablename__ = "quality_metrics"

    id = Column(Integer, primary_key=True)
    metric_id = Column(String(50), unique=True, nullable=False)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    quality_level = Column(String(20), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    engine = Column(String(50), nullable=False)
    language = Column(String(10), nullable=False)
    user_id = Column(String(50))
    session_id = Column(String(50))
    metadata = Column(Text)


class VoiceCloningMetricsDashboard:
    """Voice cloning quality metrics dashboard"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/voicestudio.config.json"
        self.config = self.load_config()

        # Dashboard settings
        self.dashboard_config = DashboardConfig(
            refresh_interval=self.config.get("dashboard", {}).get(
                "refresh_interval", 30
            ),
            max_data_points=self.config.get("dashboard", {}).get(
                "max_data_points", 1000
            ),
            quality_thresholds=self.config.get("dashboard", {}).get(
                "quality_thresholds",
                {
                    "excellent": 0.9,
                    "good": 0.8,
                    "fair": 0.7,
                    "poor": 0.6,
                    "very_poor": 0.0,
                },
            ),
            chart_types=self.config.get("dashboard", {}).get(
                "chart_types",
                {
                    "voice_similarity": "line",
                    "audio_quality": "bar",
                    "processing_time": "histogram",
                    "success_rate": "gauge",
                    "engine_performance": "scatter",
                },
            ),
            alert_thresholds=self.config.get("dashboard", {}).get(
                "alert_thresholds",
                {"low_quality": 0.6, "slow_processing": 60.0, "low_success_rate": 0.8},
            ),
        )

        # Database setup
        self.db_path = Path(
            self.config.get("storage", {}).get("db_path", "voicestudio.db")
        )
        self.setup_database()

        # Data storage
        self.metrics_data: deque = deque(maxlen=self.dashboard_config.max_data_points)
        self.alerts: List[Dict[str, Any]] = []

        # Setup logging
        self.setup_logging()

        # Initialize dashboard
        self.setup_dashboard()

    def load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "dashboard": {
                "refresh_interval": 30,
                "max_data_points": 1000,
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
                },
                "alert_thresholds": {
                    "low_quality": 0.6,
                    "slow_processing": 60.0,
                    "low_success_rate": 0.8,
                },
            },
            "storage": {"db_path": "voicestudio.db"},
        }

    def setup_database(self):
        """Setup database"""
        try:
            # Create database engine
            self.engine = create_engine(f"sqlite:///{self.db_path}")

            # Create tables
            Base.metadata.create_all(self.engine)

            # Create session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

            self.logger.info(f"Database setup complete: {self.db_path}")

        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            raise

    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def setup_dashboard(self):
        """Setup dashboard application"""
        try:
            # Initialize Dash app
            self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

            # Define layout
            self.app.layout = self.create_dashboard_layout()

            # Setup callbacks
            self.setup_callbacks()

            self.logger.info("Dashboard setup complete")

        except Exception as e:
            self.logger.error(f"Dashboard setup failed: {e}")
            raise

    def create_dashboard_layout(self):
        """Create dashboard layout"""
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H1(
                                    "VoiceStudio Ultimate - Quality Metrics Dashboard",
                                    className="text-center mb-4",
                                ),
                                html.Hr(),
                            ]
                        )
                    ]
                ),
                # Summary Cards
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Overall Quality",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="overall-quality",
                                                    className="text-success",
                                                ),
                                                html.P(
                                                    "Average voice similarity score",
                                                    className="card-text",
                                                ),
                                            ]
                                        )
                                    ],
                                    className="mb-3",
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Success Rate",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="success-rate",
                                                    className="text-info",
                                                ),
                                                html.P(
                                                    "Successful operations percentage",
                                                    className="card-text",
                                                ),
                                            ]
                                        )
                                    ],
                                    className="mb-3",
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Avg Processing Time",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="avg-processing-time",
                                                    className="text-warning",
                                                ),
                                                html.P(
                                                    "Average processing time in seconds",
                                                    className="card-text",
                                                ),
                                            ]
                                        )
                                    ],
                                    className="mb-3",
                                )
                            ],
                            width=3,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Active Engines",
                                                    className="card-title",
                                                ),
                                                html.H2(
                                                    id="active-engines",
                                                    className="text-primary",
                                                ),
                                                html.P(
                                                    "Number of active engines",
                                                    className="card-text",
                                                ),
                                            ]
                                        )
                                    ],
                                    className="mb-3",
                                )
                            ],
                            width=3,
                        ),
                    ]
                ),
                # Charts Row
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Voice Similarity Over Time"),
                                        dbc.CardBody(
                                            [dcc.Graph(id="voice-similarity-chart")]
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Engine Performance Comparison"),
                                        dbc.CardBody(
                                            [dcc.Graph(id="engine-performance-chart")]
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Audio Quality Distribution"),
                                        dbc.CardBody(
                                            [dcc.Graph(id="audio-quality-chart")]
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Processing Time Distribution"),
                                        dbc.CardBody(
                                            [dcc.Graph(id="processing-time-chart")]
                                        ),
                                    ]
                                )
                            ],
                            width=6,
                        ),
                    ],
                    className="mb-4",
                ),
                # Alerts Row
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader("Quality Alerts"),
                                        dbc.CardBody([html.Div(id="alerts-list")]),
                                    ]
                                )
                            ],
                            width=12,
                        )
                    ]
                ),
                # Auto-refresh interval
                dcc.Interval(
                    id="interval-component",
                    interval=self.dashboard_config.refresh_interval * 1000,
                    n_intervals=0,
                ),
            ],
            fluid=True,
        )

    def setup_callbacks(self):
        """Setup dashboard callbacks"""

        @self.app.callback(
            [
                Output("overall-quality", "children"),
                Output("success-rate", "children"),
                Output("avg-processing-time", "children"),
                Output("active-engines", "children"),
            ],
            [Input("interval-component", "n_intervals")],
        )
        def update_summary_cards(n):
            """Update summary cards"""
            try:
                # Get recent metrics
                recent_metrics = self.get_recent_metrics(hours=24)

                # Calculate overall quality
                similarity_metrics = [
                    m
                    for m in recent_metrics
                    if m.metric_type == MetricType.VOICE_SIMILARITY
                ]
                overall_quality = (
                    np.mean([m.value for m in similarity_metrics])
                    if similarity_metrics
                    else 0.0
                )

                # Calculate success rate
                success_metrics = [
                    m
                    for m in recent_metrics
                    if m.metric_type == MetricType.SUCCESS_RATE
                ]
                success_rate = (
                    np.mean([m.value for m in success_metrics])
                    if success_metrics
                    else 0.0
                )

                # Calculate average processing time
                time_metrics = [
                    m
                    for m in recent_metrics
                    if m.metric_type == MetricType.PROCESSING_TIME
                ]
                avg_processing_time = (
                    np.mean([m.value for m in time_metrics]) if time_metrics else 0.0
                )

                # Count active engines
                active_engines = len(set([m.engine for m in recent_metrics]))

                return (
                    f"{overall_quality:.2f}",
                    f"{success_rate:.1%}",
                    f"{avg_processing_time:.1f}s",
                    f"{active_engines}",
                )

            except Exception as e:
                self.logger.error(f"Error updating summary cards: {e}")
                return "N/A", "N/A", "N/A", "N/A"

        @self.app.callback(
            Output("voice-similarity-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_voice_similarity_chart(n):
            """Update voice similarity chart"""
            try:
                # Get recent metrics
                recent_metrics = self.get_recent_metrics(hours=24)
                similarity_metrics = [
                    m
                    for m in recent_metrics
                    if m.metric_type == MetricType.VOICE_SIMILARITY
                ]

                if not similarity_metrics:
                    return go.Figure()

                # Create chart
                fig = go.Figure()

                # Group by engine
                engines = set([m.engine for m in similarity_metrics])
                for engine in engines:
                    engine_metrics = [
                        m for m in similarity_metrics if m.engine == engine
                    ]
                    timestamps = [m.timestamp for m in engine_metrics]
                    values = [m.value for m in engine_metrics]

                    fig.add_trace(
                        go.Scatter(
                            x=timestamps,
                            y=values,
                            mode="lines+markers",
                            name=engine,
                            line=dict(width=2),
                        )
                    )

                fig.update_layout(
                    title="Voice Similarity Over Time",
                    xaxis_title="Time",
                    yaxis_title="Similarity Score",
                    hovermode="x unified",
                )

                return fig

            except Exception as e:
                self.logger.error(f"Error updating voice similarity chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("engine-performance-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_engine_performance_chart(n):
            """Update engine performance chart"""
            try:
                # Get recent metrics
                recent_metrics = self.get_recent_metrics(hours=24)

                # Group by engine
                engine_data = defaultdict(list)
                for metric in recent_metrics:
                    if metric.metric_type == MetricType.VOICE_SIMILARITY:
                        engine_data[metric.engine].append(metric.value)

                if not engine_data:
                    return go.Figure()

                # Create chart
                fig = go.Figure()

                engines = list(engine_data.keys())
                avg_scores = [np.mean(engine_data[engine]) for engine in engines]
                std_scores = [np.std(engine_data[engine]) for engine in engines]

                fig.add_trace(
                    go.Bar(
                        x=engines,
                        y=avg_scores,
                        error_y=dict(type="data", array=std_scores),
                        name="Average Similarity Score",
                    )
                )

                fig.update_layout(
                    title="Engine Performance Comparison",
                    xaxis_title="Engine",
                    yaxis_title="Average Similarity Score",
                    showlegend=False,
                )

                return fig

            except Exception as e:
                self.logger.error(f"Error updating engine performance chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("audio-quality-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_audio_quality_chart(n):
            """Update audio quality chart"""
            try:
                # Get recent metrics
                recent_metrics = self.get_recent_metrics(hours=24)
                quality_metrics = [
                    m
                    for m in recent_metrics
                    if m.metric_type == MetricType.AUDIO_QUALITY
                ]

                if not quality_metrics:
                    return go.Figure()

                # Count quality levels
                quality_counts = defaultdict(int)
                for metric in quality_metrics:
                    quality_counts[metric.quality_level.value] += 1

                # Create pie chart
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=list(quality_counts.keys()),
                            values=list(quality_counts.values()),
                            hole=0.3,
                        )
                    ]
                )

                fig.update_layout(title="Audio Quality Distribution", showlegend=True)

                return fig

            except Exception as e:
                self.logger.error(f"Error updating audio quality chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("processing-time-chart", "figure"),
            [Input("interval-component", "n_intervals")],
        )
        def update_processing_time_chart(n):
            """Update processing time chart"""
            try:
                # Get recent metrics
                recent_metrics = self.get_recent_metrics(hours=24)
                time_metrics = [
                    m
                    for m in recent_metrics
                    if m.metric_type == MetricType.PROCESSING_TIME
                ]

                if not time_metrics:
                    return go.Figure()

                # Create histogram
                values = [m.value for m in time_metrics]

                fig = go.Figure(
                    data=[
                        go.Histogram(
                            x=values, nbinsx=20, name="Processing Time Distribution"
                        )
                    ]
                )

                fig.update_layout(
                    title="Processing Time Distribution",
                    xaxis_title="Processing Time (seconds)",
                    yaxis_title="Frequency",
                    showlegend=False,
                )

                return fig

            except Exception as e:
                self.logger.error(f"Error updating processing time chart: {e}")
                return go.Figure()

        @self.app.callback(
            Output("alerts-list", "children"),
            [Input("interval-component", "n_intervals")],
        )
        def update_alerts(n):
            """Update alerts list"""
            try:
                # Check for alerts
                self.check_alerts()

                if not self.alerts:
                    return html.P("No alerts", className="text-muted")

                # Create alert components
                alert_components = []
                for alert in self.alerts[-10:]:  # Show last 10 alerts
                    color = "danger" if alert["severity"] == "high" else "warning"
                    alert_components.append(
                        dbc.Alert(
                            f"{alert['message']} - {alert['timestamp']}",
                            color=color,
                            dismissable=True,
                            className="mb-2",
                        )
                    )

                return alert_components

            except Exception as e:
                self.logger.error(f"Error updating alerts: {e}")
                return html.P("Error loading alerts", className="text-danger")

    def add_metric(self, metric: QualityMetric):
        """Add a quality metric"""
        try:
            # Add to in-memory storage
            self.metrics_data.append(metric)

            # Add to database
            db_metric = QualityMetricDB(
                metric_id=metric.metric_id,
                metric_type=metric.metric_type.value,
                value=metric.value,
                quality_level=metric.quality_level.value,
                timestamp=metric.timestamp,
                engine=metric.engine,
                language=metric.language,
                user_id=metric.user_id,
                session_id=metric.session_id,
                metadata=json.dumps(metric.metadata) if metric.metadata else None,
            )

            self.session.add(db_metric)
            self.session.commit()

            self.logger.debug(f"Added metric: {metric.metric_id}")

        except Exception as e:
            self.logger.error(f"Error adding metric: {e}")
            self.session.rollback()

    def get_recent_metrics(self, hours: int = 24) -> List[QualityMetric]:
        """Get recent metrics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            # Query database
            db_metrics = (
                self.session.query(QualityMetricDB)
                .filter(QualityMetricDB.timestamp >= cutoff_time)
                .all()
            )

            # Convert to QualityMetric objects
            metrics = []
            for db_metric in db_metrics:
                metric = QualityMetric(
                    metric_id=db_metric.metric_id,
                    metric_type=MetricType(db_metric.metric_type),
                    value=db_metric.value,
                    quality_level=QualityLevel(db_metric.quality_level),
                    timestamp=db_metric.timestamp,
                    engine=db_metric.engine,
                    language=db_metric.language,
                    user_id=db_metric.user_id,
                    session_id=db_metric.session_id,
                    metadata=(
                        json.loads(db_metric.metadata) if db_metric.metadata else None
                    ),
                )
                metrics.append(metric)

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting recent metrics: {e}")
            return []

    def check_alerts(self):
        """Check for quality alerts"""
        try:
            recent_metrics = self.get_recent_metrics(hours=1)

            # Check for low quality
            similarity_metrics = [
                m
                for m in recent_metrics
                if m.metric_type == MetricType.VOICE_SIMILARITY
            ]
            if similarity_metrics:
                avg_similarity = np.mean([m.value for m in similarity_metrics])
                if (
                    avg_similarity
                    < self.dashboard_config.alert_thresholds["low_quality"]
                ):
                    self.add_alert(
                        "Low voice similarity detected",
                        "high",
                        {
                            "average_similarity": avg_similarity,
                            "threshold": self.dashboard_config.alert_thresholds[
                                "low_quality"
                            ],
                        },
                    )

            # Check for slow processing
            time_metrics = [
                m for m in recent_metrics if m.metric_type == MetricType.PROCESSING_TIME
            ]
            if time_metrics:
                avg_time = np.mean([m.value for m in time_metrics])
                if avg_time > self.dashboard_config.alert_thresholds["slow_processing"]:
                    self.add_alert(
                        "Slow processing detected",
                        "medium",
                        {
                            "average_time": avg_time,
                            "threshold": self.dashboard_config.alert_thresholds[
                                "slow_processing"
                            ],
                        },
                    )

            # Check for low success rate
            success_metrics = [
                m for m in recent_metrics if m.metric_type == MetricType.SUCCESS_RATE
            ]
            if success_metrics:
                avg_success = np.mean([m.value for m in success_metrics])
                if (
                    avg_success
                    < self.dashboard_config.alert_thresholds["low_success_rate"]
                ):
                    self.add_alert(
                        "Low success rate detected",
                        "high",
                        {
                            "success_rate": avg_success,
                            "threshold": self.dashboard_config.alert_thresholds[
                                "low_success_rate"
                            ],
                        },
                    )

        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")

    def add_alert(self, message: str, severity: str, data: Dict[str, Any]):
        """Add an alert"""
        alert = {
            "id": str(uuid.uuid4()),
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        self.alerts.append(alert)

        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

        self.logger.warning(f"Alert: {message}")

    def generate_sample_metrics(self, count: int = 100):
        """Generate sample metrics for testing"""
        engines = ["xtts", "openvoice", "cosyvoice", "tortoise"]
        languages = ["en", "es", "fr", "de", "it"]

        for i in range(count):
            # Generate random metric
            metric_type = np.random.choice(list(MetricType))
            engine = np.random.choice(engines)
            language = np.random.choice(languages)

            # Generate value based on metric type
            if metric_type == MetricType.VOICE_SIMILARITY:
                value = np.random.normal(0.85, 0.1)
                value = max(0.0, min(1.0, value))
            elif metric_type == MetricType.AUDIO_QUALITY:
                value = np.random.normal(0.8, 0.15)
                value = max(0.0, min(1.0, value))
            elif metric_type == MetricType.PROCESSING_TIME:
                value = np.random.normal(45, 15)
                value = max(5.0, value)
            elif metric_type == MetricType.SUCCESS_RATE:
                value = np.random.normal(0.95, 0.05)
                value = max(0.0, min(1.0, value))
            else:
                value = np.random.random()

            # Determine quality level
            if value >= self.dashboard_config.quality_thresholds["excellent"]:
                quality_level = QualityLevel.EXCELLENT
            elif value >= self.dashboard_config.quality_thresholds["good"]:
                quality_level = QualityLevel.GOOD
            elif value >= self.dashboard_config.quality_thresholds["fair"]:
                quality_level = QualityLevel.FAIR
            elif value >= self.dashboard_config.quality_thresholds["poor"]:
                quality_level = QualityLevel.POOR
            else:
                quality_level = QualityLevel.VERY_POOR

            # Create metric
            metric = QualityMetric(
                metric_id=f"sample_{i}",
                metric_type=metric_type,
                value=value,
                quality_level=quality_level,
                timestamp=datetime.utcnow() - timedelta(hours=np.random.randint(0, 24)),
                engine=engine,
                language=language,
                metadata={"sample": True},
            )

            self.add_metric(metric)

    def run_dashboard(
        self, host: str = "127.0.0.1", port: int = 8050, debug: bool = False
    ):
        """Run the dashboard"""
        try:
            self.logger.info(f"Starting dashboard on {host}:{port}")
            self.app.run_server(host=host, port=port, debug=debug)
        except Exception as e:
            self.logger.error(f"Error running dashboard: {e}")
            raise


def main():
    """Main function for testing dashboard"""
    import argparse

    parser = argparse.ArgumentParser(
        description="VoiceStudio Quality Metrics Dashboard"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard host")
    parser.add_argument("--port", type=int, default=8050, help="Dashboard port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--generate-samples", type=int, help="Generate sample metrics")

    args = parser.parse_args()

    # Create dashboard
    dashboard = VoiceCloningMetricsDashboard()

    # Generate sample data if requested
    if args.generate_samples:
        dashboard.generate_sample_metrics(args.generate_samples)
        print(f"Generated {args.generate_samples} sample metrics")

    # Run dashboard
    dashboard.run_dashboard(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
