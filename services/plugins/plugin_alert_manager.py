#!/usr/bin/env python3
"""
VOICESTUDIO GOD-TIER SERVICE ALERT MANAGER PLUGIN
Advanced Alert Management and Notification Plugin
Maximum Alert Intelligence and Notification System
Version: 1.0.0 "Ultimate Alert Manager Plugin"
"""

import sys
import os
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# PyQt6 imports
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QProgressBar,
    QGroupBox, QFrame, QScrollArea, QTextEdit, QComboBox,
    QCheckBox, QSpinBox, QSlider, QListWidget, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout,
    QLineEdit, QDoubleSpinBox, QDateEdit, QTimeEdit, QButtonGroup,
    QRadioButton, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter

# Import base plugin class
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from service_health_dashboard_plugins import BasePlugin, PluginMetadata

# Plugin metadata
PLUGIN_NAME = "alert_manager"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Advanced Alert Management and Notification System"
PLUGIN_AUTHOR = "VoiceStudio Team"
PLUGIN_CATEGORY = "alerts"
PLUGIN_DEPENDENCIES = []
PLUGIN_CONFIG_SCHEMA = {
    "enable_notifications": {"type": "boolean", "default": True},
    "alert_threshold": {"type": "float", "min": 0.0, "max": 100.0, "default": 80.0},
    "notification_sound": {"type": "boolean", "default": False},
    "email_notifications": {"type": "boolean", "default": False},
    "sms_notifications": {"type": "boolean", "default": False},
    "webhook_url": {"type": "string", "default": ""},
    "alert_retention_days": {"type": "integer", "min": 1, "max": 365, "default": 30},
    "auto_acknowledge": {"type": "boolean", "default": False}
}

class AlertLevel(Enum):
    """Alert levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    timestamp: datetime
    service_name: str
    level: AlertLevel
    status: AlertStatus
    title: str
    message: str
    source: str
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

@dataclass
class AlertRule:
    """Alert rule configuration"""
    id: str
    name: str
    enabled: bool
    service_pattern: str
    condition: str
    threshold: float
    level: AlertLevel
    cooldown_minutes: int
    actions: List[str]

class AlertManagerPlugin(BasePlugin):
    """Advanced Alert Manager Plugin"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.notification_callbacks: List[Callable] = []
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.process_alerts)
        
        # Default configuration
        self.config = {
            "enable_notifications": True,
            "alert_threshold": 80.0,
            "notification_sound": False,
            "email_notifications": False,
            "sms_notifications": False,
            "webhook_url": "",
            "alert_retention_days": 30,
            "auto_acknowledge": False
        }
        
        # Initialize default alert rules
        self.initialize_default_rules()
    
    def initialize(self, dashboard: 'ServiceHealthDashboardGUI') -> bool:
        """Initialize the alert manager plugin"""
        try:
            self.dashboard = dashboard
            self.update_timer.start(5000)  # Check every 5 seconds
            
            # Register hooks
            self.register_hook("service_updated", self.on_service_updated)
            self.register_hook("service_status_changed", self.on_service_status_changed)
            
            logger.info("Alert Manager Plugin initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize alert manager plugin: {e}")
            return False
    
    def create_widget(self) -> QWidget:
        """Create the alert manager widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Alert Manager")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #E74C3C;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Alert controls
        acknowledge_btn = QPushButton("Acknowledge Selected")
        acknowledge_btn.clicked.connect(self.acknowledge_selected)
        header_layout.addWidget(acknowledge_btn)
        
        resolve_btn = QPushButton("Resolve Selected")
        resolve_btn.clicked.connect(self.resolve_selected)
        header_layout.addWidget(resolve_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_alerts)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Active alerts tab
        self.setup_active_alerts_tab()
        
        # Alert rules tab
        self.setup_alert_rules_tab()
        
        # Alert history tab
        self.setup_alert_history_tab()
        
        # Configuration tab
        self.setup_configuration_tab()
        
        layout.addWidget(self.tab_widget)
        
        widget.setLayout(layout)
        return widget
    
    def setup_active_alerts_tab(self):
        """Setup active alerts tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Alert summary
        summary_layout = QHBoxLayout()
        
        self.total_alerts_label = QLabel("Total Alerts: 0")
        self.active_alerts_label = QLabel("Active: 0")
        self.acknowledged_alerts_label = QLabel("Acknowledged: 0")
        self.critical_alerts_label = QLabel("Critical: 0")
        
        for label in [self.total_alerts_label, self.active_alerts_label, 
                     self.acknowledged_alerts_label, self.critical_alerts_label]:
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        
        summary_layout.addWidget(self.total_alerts_label)
        summary_layout.addWidget(self.active_alerts_label)
        summary_layout.addWidget(self.acknowledged_alerts_label)
        summary_layout.addWidget(self.critical_alerts_label)
        
        layout.addLayout(summary_layout)
        
        # Active alerts table
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(7)
        self.alerts_table.setHorizontalHeaderLabels([
            "Select", "Time", "Service", "Level", "Title", "Status", "Actions"
        ])
        
        # Set table properties
        self.alerts_table.setAlternatingRowColors(True)
        self.alerts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.alerts_table.horizontalHeader().setStretchLastSection(True)
        self.alerts_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #cccccc;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #E74C3C;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.alerts_table)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Active Alerts")
    
    def setup_alert_rules_tab(self):
        """Setup alert rules tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Rules controls
        controls_layout = QHBoxLayout()
        
        add_rule_btn = QPushButton("Add Rule")
        add_rule_btn.clicked.connect(self.add_alert_rule)
        controls_layout.addWidget(add_rule_btn)
        
        edit_rule_btn = QPushButton("Edit Rule")
        edit_rule_btn.clicked.connect(self.edit_alert_rule)
        controls_layout.addWidget(edit_rule_btn)
        
        delete_rule_btn = QPushButton("Delete Rule")
        delete_rule_btn.clicked.connect(self.delete_alert_rule)
        controls_layout.addWidget(delete_rule_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Alert rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            "Name", "Service Pattern", "Condition", "Threshold", "Level", "Enabled"
        ])
        
        self.rules_table.setAlternatingRowColors(True)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.rules_table)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Alert Rules")
    
    def setup_alert_history_tab(self):
        """Setup alert history tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # History controls
        controls_layout = QHBoxLayout()
        
        export_history_btn = QPushButton("Export History")
        export_history_btn.clicked.connect(self.export_alert_history)
        controls_layout.addWidget(export_history_btn)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_alert_history)
        controls_layout.addWidget(clear_history_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Alert history table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Service", "Level", "Title", "Status", 
            "Acknowledged By", "Acknowledged At", "Resolved At"
        ])
        
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.history_table)
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Alert History")
    
    def setup_configuration_tab(self):
        """Setup configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Configuration form
        config_group = QGroupBox("Alert Configuration")
        config_layout = QFormLayout()
        
        # Enable notifications
        self.enable_notifications_check = QCheckBox()
        self.enable_notifications_check.setChecked(self.config["enable_notifications"])
        config_layout.addRow("Enable Notifications:", self.enable_notifications_check)
        
        # Alert threshold
        self.alert_threshold_spin = QDoubleSpinBox()
        self.alert_threshold_spin.setRange(0.0, 100.0)
        self.alert_threshold_spin.setValue(self.config["alert_threshold"])
        config_layout.addRow("Alert Threshold:", self.alert_threshold_spin)
        
        # Notification sound
        self.notification_sound_check = QCheckBox()
        self.notification_sound_check.setChecked(self.config["notification_sound"])
        config_layout.addRow("Notification Sound:", self.notification_sound_check)
        
        # Email notifications
        self.email_notifications_check = QCheckBox()
        self.email_notifications_check.setChecked(self.config["email_notifications"])
        config_layout.addRow("Email Notifications:", self.email_notifications_check)
        
        # SMS notifications
        self.sms_notifications_check = QCheckBox()
        self.sms_notifications_check.setChecked(self.config["sms_notifications"])
        config_layout.addRow("SMS Notifications:", self.sms_notifications_check)
        
        # Webhook URL
        self.webhook_url_edit = QLineEdit()
        self.webhook_url_edit.setText(self.config["webhook_url"])
        config_layout.addRow("Webhook URL:", self.webhook_url_edit)
        
        # Alert retention days
        self.alert_retention_spin = QSpinBox()
        self.alert_retention_spin.setRange(1, 365)
        self.alert_retention_spin.setValue(self.config["alert_retention_days"])
        config_layout.addRow("Alert Retention (Days):", self.alert_retention_spin)
        
        # Auto acknowledge
        self.auto_acknowledge_check = QCheckBox()
        self.auto_acknowledge_check.setChecked(self.config["auto_acknowledge"])
        config_layout.addRow("Auto Acknowledge:", self.auto_acknowledge_check)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Save configuration button
        save_config_btn = QPushButton("Save Configuration")
        save_config_btn.clicked.connect(self.save_configuration)
        layout.addWidget(save_config_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "Configuration")
    
    def initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                id="health_score_low",
                name="Low Health Score",
                enabled=True,
                service_pattern=".*",
                condition="health_score < threshold",
                threshold=80.0,
                level=AlertLevel.WARNING,
                cooldown_minutes=5,
                actions=["notification", "log"]
            ),
            AlertRule(
                id="response_time_high",
                name="High Response Time",
                enabled=True,
                service_pattern=".*",
                condition="response_time > threshold",
                threshold=5.0,
                level=AlertLevel.ERROR,
                cooldown_minutes=2,
                actions=["notification", "log", "email"]
            ),
            AlertRule(
                id="service_unhealthy",
                name="Service Unhealthy",
                enabled=True,
                service_pattern=".*",
                condition="status == 'unhealthy'",
                threshold=0.0,
                level=AlertLevel.CRITICAL,
                cooldown_minutes=1,
                actions=["notification", "log", "email", "sms"]
            ),
            AlertRule(
                id="retry_count_high",
                name="High Retry Count",
                enabled=True,
                service_pattern=".*",
                condition="retry_count > threshold",
                threshold=3,
                level=AlertLevel.ERROR,
                cooldown_minutes=3,
                actions=["notification", "log"]
            )
        ]
        
        self.alert_rules = default_rules
    
    def update_data(self, service_data: Dict[str, Any]) -> None:
        """Update alert data with service information"""
        try:
            # Process alert rules
            for rule in self.alert_rules:
                if rule.enabled and self._matches_service_pattern(service_data.get('name', ''), rule.service_pattern):
                    if self._evaluate_condition(service_data, rule):
                        self._create_alert(service_data, rule)
            
            # Update alert display
            self.update_alerts_display()
            
        except Exception as e:
            logger.error(f"Error updating alert data: {e}")
    
    def _matches_service_pattern(self, service_name: str, pattern: str) -> bool:
        """Check if service name matches pattern"""
        import re
        try:
            return re.match(pattern, service_name) is not None
        except:
            return service_name == pattern
    
    def _evaluate_condition(self, service_data: Dict[str, Any], rule: AlertRule) -> bool:
        """Evaluate alert condition"""
        try:
            # Replace variables in condition
            condition = rule.condition
            condition = condition.replace("threshold", str(rule.threshold))
            condition = condition.replace("health_score", str(service_data.get('health_score', 0)))
            condition = condition.replace("response_time", str(service_data.get('response_time', 0)))
            condition = condition.replace("status", f"'{service_data.get('status', 'unknown')}'")
            condition = condition.replace("retry_count", str(service_data.get('retry_count', 0)))
            
            # Evaluate condition
            return eval(condition)
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _create_alert(self, service_data: Dict[str, Any], rule: AlertRule):
        """Create a new alert"""
        alert_id = f"{rule.id}_{service_data.get('name', 'unknown')}_{int(time.time())}"
        
        # Check cooldown
        if self._is_in_cooldown(alert_id, rule.cooldown_minutes):
            return
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now(),
            service_name=service_data.get('name', 'unknown'),
            level=rule.level,
            status=AlertStatus.ACTIVE,
            title=rule.name,
            message=f"{rule.name} detected for {service_data.get('name', 'unknown')}",
            source="alert_manager",
            metadata=service_data
        )
        
        self.alerts.append(alert)
        
        # Execute actions
        for action in rule.actions:
            self._execute_action(alert, action)
        
        logger.info(f"Alert created: {alert.title} for {alert.service_name}")
    
    def _is_in_cooldown(self, alert_id: str, cooldown_minutes: int) -> bool:
        """Check if alert is in cooldown period"""
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        for alert in self.alerts:
            if (alert.id.startswith(alert_id.split('_')[0]) and 
                alert.timestamp > cutoff_time and 
                alert.status == AlertStatus.ACTIVE):
                return True
        
        return False
    
    def _execute_action(self, alert: Alert, action: str):
        """Execute alert action"""
        try:
            if action == "notification":
                self._send_notification(alert)
            elif action == "log":
                logger.warning(f"ALERT: {alert.title} - {alert.message}")
            elif action == "email":
                self._send_email(alert)
            elif action == "sms":
                self._send_sms(alert)
            elif action == "webhook":
                self._send_webhook(alert)
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
    
    def _send_notification(self, alert: Alert):
        """Send system notification"""
        if self.config["enable_notifications"]:
            # This would integrate with system notifications
            logger.info(f"NOTIFICATION: {alert.title} - {alert.message}")
    
    def _send_email(self, alert: Alert):
        """Send email notification"""
        if self.config["email_notifications"]:
            # This would integrate with email service
            logger.info(f"EMAIL: {alert.title} - {alert.message}")
    
    def _send_sms(self, alert: Alert):
        """Send SMS notification"""
        if self.config["sms_notifications"]:
            # This would integrate with SMS service
            logger.info(f"SMS: {alert.title} - {alert.message}")
    
    def _send_webhook(self, alert: Alert):
        """Send webhook notification"""
        if self.config["webhook_url"]:
            try:
                payload = {
                    "alert": asdict(alert),
                    "timestamp": datetime.now().isoformat()
                }
                # This would send HTTP request to webhook URL
                logger.info(f"WEBHOOK: {alert.title} - {alert.message}")
            except Exception as e:
                logger.error(f"Error sending webhook: {e}")
    
    def process_alerts(self):
        """Process alerts and update display"""
        self.update_alerts_display()
        self.cleanup_old_alerts()
    
    def update_alerts_display(self):
        """Update alerts display"""
        if not hasattr(self, 'alerts_table'):
            return
        
        # Update summary
        total_alerts = len(self.alerts)
        active_alerts = len([a for a in self.alerts if a.status == AlertStatus.ACTIVE])
        acknowledged_alerts = len([a for a in self.alerts if a.status == AlertStatus.ACKNOWLEDGED])
        critical_alerts = len([a for a in self.alerts if a.level == AlertLevel.CRITICAL])
        
        if hasattr(self, 'total_alerts_label'):
            self.total_alerts_label.setText(f"Total Alerts: {total_alerts}")
        if hasattr(self, 'active_alerts_label'):
            self.active_alerts_label.setText(f"Active: {active_alerts}")
        if hasattr(self, 'acknowledged_alerts_label'):
            self.acknowledged_alerts_label.setText(f"Acknowledged: {acknowledged_alerts}")
        if hasattr(self, 'critical_alerts_label'):
            self.critical_alerts_label.setText(f"Critical: {critical_alerts}")
        
        # Update alerts table
        self.alerts_table.setRowCount(len(self.alerts))
        
        for row, alert in enumerate(self.alerts):
            # Select checkbox
            select_checkbox = QCheckBox()
            self.alerts_table.setCellWidget(row, 0, select_checkbox)
            
            # Time
            self.alerts_table.setItem(row, 1, QTableWidgetItem(alert.timestamp.strftime("%H:%M:%S")))
            
            # Service
            self.alerts_table.setItem(row, 2, QTableWidgetItem(alert.service_name))
            
            # Level
            level_item = QTableWidgetItem(alert.level.value.upper())
            if alert.level == AlertLevel.CRITICAL:
                level_item.setBackground(QColor("#FF6B6B"))
            elif alert.level == AlertLevel.ERROR:
                level_item.setBackground(QColor("#FFB347"))
            elif alert.level == AlertLevel.WARNING:
                level_item.setBackground(QColor("#FFF8DC"))
            else:
                level_item.setBackground(QColor("#E6F3FF"))
            self.alerts_table.setItem(row, 3, level_item)
            
            # Title
            self.alerts_table.setItem(row, 4, QTableWidgetItem(alert.title))
            
            # Status
            status_item = QTableWidgetItem(alert.status.value.upper())
            if alert.status == AlertStatus.ACTIVE:
                status_item.setBackground(QColor("#FF6B6B"))
            elif alert.status == AlertStatus.ACKNOWLEDGED:
                status_item.setBackground(QColor("#FFF8DC"))
            elif alert.status == AlertStatus.RESOLVED:
                status_item.setBackground(QColor("#90EE90"))
            self.alerts_table.setItem(row, 5, status_item)
            
            # Actions
            actions_btn = QPushButton("View")
            actions_btn.clicked.connect(lambda checked, a=alert: self.view_alert_details(a))
            self.alerts_table.setCellWidget(row, 6, actions_btn)
    
    def acknowledge_selected(self):
        """Acknowledge selected alerts"""
        for row in range(self.alerts_table.rowCount()):
            checkbox = self.alerts_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                alert_id = self.alerts[row].id
                self.acknowledge_alert(alert_id)
    
    def resolve_selected(self):
        """Resolve selected alerts"""
        for row in range(self.alerts_table.rowCount()):
            checkbox = self.alerts_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                alert_id = self.alerts[row].id
                self.resolve_alert(alert_id)
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = "User"
                alert.acknowledged_at = datetime.now()
                break
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                # Move to history
                self.alert_history.append(alert)
                self.alerts.remove(alert)
                break
    
    def clear_all_alerts(self):
        """Clear all alerts"""
        reply = QMessageBox.question(
            None, "Clear All Alerts", 
            "Are you sure you want to clear all alerts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Move to history
            self.alert_history.extend(self.alerts)
            self.alerts.clear()
    
    def view_alert_details(self, alert: Alert):
        """View alert details"""
        details = f"""
Alert Details:
ID: {alert.id}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Service: {alert.service_name}
Level: {alert.level.value.upper()}
Status: {alert.status.value.upper()}
Title: {alert.title}
Message: {alert.message}
Source: {alert.source}
"""
        
        QMessageBox.information(None, "Alert Details", details)
    
    def save_configuration(self):
        """Save configuration"""
        self.config["enable_notifications"] = self.enable_notifications_check.isChecked()
        self.config["alert_threshold"] = self.alert_threshold_spin.value()
        self.config["notification_sound"] = self.notification_sound_check.isChecked()
        self.config["email_notifications"] = self.email_notifications_check.isChecked()
        self.config["sms_notifications"] = self.sms_notifications_check.isChecked()
        self.config["webhook_url"] = self.webhook_url_edit.text()
        self.config["alert_retention_days"] = self.alert_retention_spin.value()
        self.config["auto_acknowledge"] = self.auto_acknowledge_check.isChecked()
        
        QMessageBox.information(None, "Configuration Saved", "Alert configuration has been saved.")
    
    def cleanup_old_alerts(self):
        """Cleanup old alerts"""
        retention_days = self.config["alert_retention_days"]
        cutoff_time = datetime.now() - timedelta(days=retention_days)
        
        # Remove old alerts from history
        self.alert_history = [
            alert for alert in self.alert_history 
            if alert.timestamp > cutoff_time
        ]
    
    def export_alert_history(self):
        """Export alert history"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                None, "Export Alert History", "alert_history.json", "JSON Files (*.json)"
            )
            
            if file_path:
                export_data = {
                    "export_timestamp": datetime.now().isoformat(),
                    "alerts": [asdict(alert) for alert in self.alerts],
                    "alert_history": [asdict(alert) for alert in self.alert_history],
                    "alert_rules": [asdict(rule) for rule in self.alert_rules]
                }
                
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                QMessageBox.information(None, "Export Complete", f"Alert history exported to {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting alert history: {e}")
            QMessageBox.critical(None, "Export Error", f"Failed to export alert history: {e}")
    
    def clear_alert_history(self):
        """Clear alert history"""
        reply = QMessageBox.question(
            None, "Clear Alert History", 
            "Are you sure you want to clear all alert history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.alert_history.clear()
    
    def on_service_updated(self, service_name: str, service_data: Dict[str, Any]):
        """Handle service update event"""
        self.update_data(service_data)
    
    def on_service_status_changed(self, service_name: str, new_status: str):
        """Handle service status change event"""
        # This will be handled by the update_data method
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        logger.info("Alert Manager Plugin cleaned up")

# Create plugin instance
def create_plugin():
    """Create alert manager plugin instance"""
    metadata = PluginMetadata(
        name=PLUGIN_NAME,
        version=PLUGIN_VERSION,
        description=PLUGIN_DESCRIPTION,
        author=PLUGIN_AUTHOR,
        category=PLUGIN_CATEGORY,
        dependencies=PLUGIN_DEPENDENCIES,
        config_schema=PLUGIN_CONFIG_SCHEMA
    )
    
    return AlertManagerPlugin(metadata)

if __name__ == "__main__":
    print("VoiceStudio God-Tier Service Alert Manager Plugin")
    print("Advanced Alert Management and Notification System")
    print("Maximum Alert Intelligence and Notification System")
    print("Version: 1.0.0 'Ultimate Alert Manager Plugin'")
