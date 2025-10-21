#!/usr/bin/env python3
"""
VOICESTUDIO GOD-TIER SERVICE ANALYTICS PLUGIN
Advanced Service Analytics and Reporting Plugin
Maximum Performance Analytics and Insights
Version: 1.0.0 "Ultimate Analytics Plugin"
"""

import sys
import os
import time
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict

# PyQt6 imports
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QGroupBox, QFrame, QScrollArea, QTextEdit, QComboBox,
    QCheckBox, QSpinBox, QSlider, QListWidget, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QDoubleSpinBox, QDateEdit, QTimeEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter

# Import base plugin class
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from service_health_dashboard_plugins import BasePlugin, PluginMetadata

# Plugin metadata
PLUGIN_NAME = "analytics"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Advanced Service Analytics and Reporting"
PLUGIN_AUTHOR = "VoiceStudio Team"
PLUGIN_CATEGORY = "analytics"
PLUGIN_DEPENDENCIES = []
PLUGIN_CONFIG_SCHEMA = {
    "update_interval": {"type": "integer", "min": 1, "max": 60, "default": 5},
    "enable_charts": {"type": "boolean", "default": True},
    "chart_type": {"type": "choice", "choices": ["line", "bar", "pie"], "default": "line"},
    "enable_alerts": {"type": "boolean", "default": True},
    "performance_threshold": {"type": "float", "min": 0.0, "max": 100.0, "default": 80.0},
    "data_retention_days": {"type": "integer", "min": 1, "max": 365, "default": 30}
}

@dataclass
class AnalyticsData:
    """Analytics data structure"""
    timestamp: datetime
    service_name: str
    response_time: float
    health_score: float
    uptime: float
    memory_usage: float
    cpu_usage: float
    retry_count: int
    status: str

class ServiceAnalyticsPlugin(BasePlugin):
    """Advanced Service Analytics Plugin"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.analytics_data: List[AnalyticsData] = []
        self.summary_stats = {}
        self.charts = {}
        self.alerts = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_analytics)
        
        # Default configuration
        self.config = {
            "update_interval": 5,
            "enable_charts": True,
            "chart_type": "line",
            "enable_alerts": True,
            "performance_threshold": 80.0,
            "data_retention_days": 30
        }
    
    def initialize(self, dashboard: 'ServiceHealthDashboardGUI') -> bool:
        """Initialize the analytics plugin"""
        try:
            self.dashboard = dashboard
            self.update_timer.start(self.config["update_interval"] * 1000)
            
            # Register hooks
            self.register_hook("service_updated", self.on_service_updated)
            self.register_hook("service_status_changed", self.on_service_status_changed)
            
            logger.info("Service Analytics Plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize analytics plugin: {e}")
            return False
    
    def create_widget(self) -> QWidget:
        """Create the analytics widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Service Analytics")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2E86AB;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_analytics)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Summary statistics
        self.setup_summary_section(layout)
        
        # Analytics table
        self.setup_analytics_table(layout)
        
        # Charts section
        if self.config["enable_charts"]:
            self.setup_charts_section(layout)
        
        # Alerts section
        if self.config["enable_alerts"]:
            self.setup_alerts_section(layout)
        
        widget.setLayout(layout)
        return widget
    
    def setup_summary_section(self, layout: QVBoxLayout):
        """Setup summary statistics section"""
        summary_group = QGroupBox("Summary Statistics")
        summary_layout = QGridLayout()
        
        # Summary labels
        self.total_services_label = QLabel("Total Services: 0")
        self.healthy_services_label = QLabel("Healthy Services: 0")
        self.avg_response_time_label = QLabel("Avg Response Time: 0.000s")
        self.avg_health_score_label = QLabel("Avg Health Score: 0.0")
        self.total_uptime_label = QLabel("Total Uptime: 0.0s")
        
        # Style summary labels
        for label in [self.total_services_label, self.healthy_services_label, 
                     self.avg_response_time_label, self.avg_health_score_label, 
                     self.total_uptime_label]:
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        
        summary_layout.addWidget(self.total_services_label, 0, 0)
        summary_layout.addWidget(self.healthy_services_label, 0, 1)
        summary_layout.addWidget(self.avg_response_time_label, 1, 0)
        summary_layout.addWidget(self.avg_health_score_label, 1, 1)
        summary_layout.addWidget(self.total_uptime_label, 2, 0)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
    
    def setup_analytics_table(self, layout: QVBoxLayout):
        """Setup analytics table"""
        table_group = QGroupBox("Service Analytics")
        table_layout = QVBoxLayout()
        
        # Analytics table
        self.analytics_table = QTableWidget()
        self.analytics_table.setColumnCount(8)
        self.analytics_table.setHorizontalHeaderLabels([
            "Service", "Status", "Response Time", "Health Score", 
            "Uptime", "Memory Usage", "CPU Usage", "Last Updated"
        ])
        
        # Set table properties
        self.analytics_table.setAlternatingRowColors(True)
        self.analytics_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.analytics_table.horizontalHeader().setStretchLastSection(True)
        self.analytics_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #cccccc;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #4ECDC4;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        table_layout.addWidget(self.analytics_table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
    
    def setup_charts_section(self, layout: QVBoxLayout):
        """Setup charts section"""
        charts_group = QGroupBox("Performance Charts")
        charts_layout = QVBoxLayout()
        
        # Chart controls
        controls_layout = QHBoxLayout()
        
        chart_type_label = QLabel("Chart Type:")
        controls_layout.addWidget(chart_type_label)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Response Time", "Health Score", "Memory Usage", "CPU Usage"])
        self.chart_type_combo.currentTextChanged.connect(self.update_chart)
        controls_layout.addWidget(self.chart_type_combo)
        
        controls_layout.addStretch()
        
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_data)
        controls_layout.addWidget(export_btn)
        
        charts_layout.addLayout(controls_layout)
        
        # Chart area
        self.chart_area = QLabel("Chart Area")
        self.chart_area.setMinimumHeight(200)
        self.chart_area.setStyleSheet("""
            border: 1px solid #cccccc;
            background-color: #f9f9f9;
            border-radius: 5px;
        """)
        self.chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        charts_layout.addWidget(self.chart_area)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
    
    def setup_alerts_section(self, layout: QVBoxLayout):
        """Setup alerts section"""
        alerts_group = QGroupBox("Performance Alerts")
        alerts_layout = QVBoxLayout()
        
        # Alerts list
        self.alerts_list = QListWidget()
        self.alerts_list.setMaximumHeight(150)
        self.alerts_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            QListWidgetItem {
                padding: 5px;
                border-bottom: 1px solid #eeeeee;
            }
        """)
        alerts_layout.addWidget(self.alerts_list)
        
        # Alert controls
        alert_controls_layout = QHBoxLayout()
        
        clear_alerts_btn = QPushButton("Clear Alerts")
        clear_alerts_btn.clicked.connect(self.clear_alerts)
        alert_controls_layout.addWidget(clear_alerts_btn)
        
        alert_controls_layout.addStretch()
        
        alerts_group.setLayout(alerts_layout)
        layout.addWidget(alerts_group)
    
    def update_data(self, service_data: Dict[str, Any]) -> None:
        """Update analytics data with service information"""
        try:
            # Create analytics data entry
            analytics_entry = AnalyticsData(
                timestamp=datetime.now(),
                service_name=service_data.get('name', 'unknown'),
                response_time=service_data.get('response_time', 0.0),
                health_score=service_data.get('health_score', 0.0),
                uptime=service_data.get('uptime', 0.0),
                memory_usage=service_data.get('memory_usage', 0.0),
                cpu_usage=service_data.get('cpu_usage', 0.0),
                retry_count=service_data.get('retry_count', 0),
                status=service_data.get('status', 'unknown')
            )
            
            # Add to analytics data
            self.analytics_data.append(analytics_entry)
            
            # Clean old data
            self.cleanup_old_data()
            
            # Update summary statistics
            self.update_summary_stats()
            
            # Check for alerts
            if self.config["enable_alerts"]:
                self.check_alerts(analytics_entry)
            
        except Exception as e:
            logger.error(f"Error updating analytics data: {e}")
    
    def update_analytics(self):
        """Update analytics display"""
        try:
            # Update analytics table
            self.update_analytics_table()
            
            # Update charts
            if self.config["enable_charts"]:
                self.update_chart()
            
        except Exception as e:
            logger.error(f"Error updating analytics display: {e}")
    
    def update_analytics_table(self):
        """Update the analytics table"""
        if not hasattr(self, 'analytics_table'):
            return
        
        # Get latest data for each service
        latest_data = {}
        for entry in self.analytics_data:
            if entry.service_name not in latest_data or entry.timestamp > latest_data[entry.service_name].timestamp:
                latest_data[entry.service_name] = entry
        
        # Update table
        self.analytics_table.setRowCount(len(latest_data))
        
        for row, (service_name, data) in enumerate(latest_data.items()):
            # Service name
            self.analytics_table.setItem(row, 0, QTableWidgetItem(service_name.replace('_', ' ').title()))
            
            # Status
            status_item = QTableWidgetItem(data.status.title())
            if data.status == 'healthy':
                status_item.setBackground(QColor("#4ECDC4"))
            elif data.status == 'unhealthy':
                status_item.setBackground(QColor("#FF6B6B"))
            else:
                status_item.setBackground(QColor("#FECA57"))
            self.analytics_table.setItem(row, 1, status_item)
            
            # Response time
            self.analytics_table.setItem(row, 2, QTableWidgetItem(f"{data.response_time:.3f}s"))
            
            # Health score
            self.analytics_table.setItem(row, 3, QTableWidgetItem(f"{data.health_score:.1f}"))
            
            # Uptime
            self.analytics_table.setItem(row, 4, QTableWidgetItem(f"{data.uptime:.1f}s"))
            
            # Memory usage
            self.analytics_table.setItem(row, 5, QTableWidgetItem(f"{data.memory_usage:.1f}MB"))
            
            # CPU usage
            self.analytics_table.setItem(row, 6, QTableWidgetItem(f"{data.cpu_usage:.1f}%"))
            
            # Last updated
            self.analytics_table.setItem(row, 7, QTableWidgetItem(data.timestamp.strftime("%H:%M:%S")))
    
    def update_chart(self):
        """Update the chart display"""
        if not hasattr(self, 'chart_area'):
            return
        
        chart_type = self.chart_type_combo.currentText()
        
        # Create simple text-based chart representation
        chart_text = f"{chart_type} Chart\n\n"
        
        # Get latest data for each service
        latest_data = {}
        for entry in self.analytics_data:
            if entry.service_name not in latest_data or entry.timestamp > latest_data[entry.service_name].timestamp:
                latest_data[entry.service_name] = entry
        
        # Add chart data
        for service_name, data in latest_data.items():
            if chart_type == "Response Time":
                value = data.response_time
                unit = "s"
            elif chart_type == "Health Score":
                value = data.health_score
                unit = "%"
            elif chart_type == "Memory Usage":
                value = data.memory_usage
                unit = "MB"
            elif chart_type == "CPU Usage":
                value = data.cpu_usage
                unit = "%"
            else:
                value = 0
                unit = ""
            
            chart_text += f"{service_name}: {value:.1f}{unit}\n"
        
        self.chart_area.setText(chart_text)
    
    def update_summary_stats(self):
        """Update summary statistics"""
        if not self.analytics_data:
            return
        
        # Calculate summary statistics
        total_services = len(set(entry.service_name for entry in self.analytics_data))
        healthy_services = len(set(entry.service_name for entry in self.analytics_data if entry.status == 'healthy'))
        
        avg_response_time = sum(entry.response_time for entry in self.analytics_data) / len(self.analytics_data)
        avg_health_score = sum(entry.health_score for entry in self.analytics_data) / len(self.analytics_data)
        total_uptime = sum(entry.uptime for entry in self.analytics_data)
        
        # Update labels
        if hasattr(self, 'total_services_label'):
            self.total_services_label.setText(f"Total Services: {total_services}")
        if hasattr(self, 'healthy_services_label'):
            self.healthy_services_label.setText(f"Healthy Services: {healthy_services}")
        if hasattr(self, 'avg_response_time_label'):
            self.avg_response_time_label.setText(f"Avg Response Time: {avg_response_time:.3f}s")
        if hasattr(self, 'avg_health_score_label'):
            self.avg_health_score_label.setText(f"Avg Health Score: {avg_health_score:.1f}")
        if hasattr(self, 'total_uptime_label'):
            self.total_uptime_label.setText(f"Total Uptime: {total_uptime:.1f}s")
    
    def check_alerts(self, data: AnalyticsData):
        """Check for performance alerts"""
        threshold = self.config["performance_threshold"]
        
        # Check health score threshold
        if data.health_score < threshold:
            alert_message = f"Low health score for {data.service_name}: {data.health_score:.1f}%"
            self.add_alert(alert_message, "warning")
        
        # Check response time threshold
        if data.response_time > 5.0:  # 5 seconds threshold
            alert_message = f"High response time for {data.service_name}: {data.response_time:.3f}s"
            self.add_alert(alert_message, "error")
        
        # Check retry count
        if data.retry_count > 3:
            alert_message = f"High retry count for {data.service_name}: {data.retry_count}"
            self.add_alert(alert_message, "error")
    
    def add_alert(self, message: str, level: str = "info"):
        """Add an alert"""
        alert_entry = {
            "timestamp": datetime.now(),
            "message": message,
            "level": level
        }
        
        self.alerts.append(alert_entry)
        
        # Update alerts list
        if hasattr(self, 'alerts_list'):
            alert_item = QListWidgetItem(f"[{alert_entry['timestamp'].strftime('%H:%M:%S')}] {message}")
            
            if level == "error":
                alert_item.setBackground(QColor("#FFB6C1"))  # Light red
            elif level == "warning":
                alert_item.setBackground(QColor("#FFF8DC"))  # Light yellow
            else:
                alert_item.setBackground(QColor("#E6F3FF"))  # Light blue
            
            self.alerts_list.addItem(alert_item)
            
            # Auto-scroll to bottom
            self.alerts_list.scrollToBottom()
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        if hasattr(self, 'alerts_list'):
            self.alerts_list.clear()
    
    def cleanup_old_data(self):
        """Cleanup old analytics data"""
        retention_days = self.config["data_retention_days"]
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        self.analytics_data = [
            entry for entry in self.analytics_data 
            if entry.timestamp > cutoff_time
        ]
    
    def export_data(self):
        """Export analytics data"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                None, "Export Analytics Data", "analytics_data.json", "JSON Files (*.json)"
            )
            
            if file_path:
                export_data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "analytics_data": [asdict(entry) for entry in self.analytics_data],
                    "summary_stats": self.summary_stats,
                    "alerts": self.alerts
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                QMessageBox.information(None, "Export Complete", f"Analytics data exported to {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            QMessageBox.critical(None, "Export Error", f"Failed to export data: {e}")
    
    def refresh_analytics(self):
        """Refresh analytics display"""
        self.update_analytics()
    
    def on_service_updated(self, service_name: str, service_data: Dict[str, Any]):
        """Handle service update event"""
        self.update_data(service_data)
    
    def on_service_status_changed(self, service_name: str, new_status: str):
        """Handle service status change event"""
        if new_status == 'unhealthy':
            self.add_alert(f"Service {service_name} is now unhealthy", "error")
        elif new_status == 'healthy':
            self.add_alert(f"Service {service_name} is now healthy", "info")
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        logger.info("Service Analytics Plugin cleaned up")

# Create plugin instance
def create_plugin():
    """Create analytics plugin instance"""
    metadata = PluginMetadata(
        name=PLUGIN_NAME,
        version=PLUGIN_VERSION,
        description=PLUGIN_DESCRIPTION,
        author=PLUGIN_AUTHOR,
        category=PLUGIN_CATEGORY,
        dependencies=PLUGIN_DEPENDENCIES,
        config_schema=PLUGIN_CONFIG_SCHEMA
    )
    
    return ServiceAnalyticsPlugin(metadata)

if __name__ == "__main__":
    print("VoiceStudio God-Tier Service Analytics Plugin")
    print("Advanced Service Analytics and Reporting")
    print("Maximum Performance Analytics and Insights")
    print("Version: 1.0.0 'Ultimate Analytics Plugin'")
