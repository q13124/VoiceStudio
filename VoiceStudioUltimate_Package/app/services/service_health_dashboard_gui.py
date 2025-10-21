#!/usr/bin/env python3
"""
VOICESTUDIO GOD-TIER SERVICE HEALTH DASHBOARD - PyQt6 GUI
Real-time Service Health Monitoring and Status Display with Modern GUI
Maximum Performance Tracking and Service Management
Version: 2.0.0 "Ultimate PyQt6 Health Dashboard"
"""

import sys
import asyncio
import time
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import requests
from dataclasses import dataclass, asdict

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QProgressBar, QGroupBox, QFrame, QScrollArea,
    QTextEdit, QSplitter, QHeaderView, QMessageBox, QSystemTrayIcon,
    QMenu, QStatusBar, QToolBar, QAction, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QPoint, QDateTime
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QPainter,
    QBrush, QLinearGradient, QPen, QAction
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ServiceHealthMetrics:
    """Service health metrics"""
    name: str
    url: str
    status: str
    response_time: float
    uptime: float
    memory_usage: float
    cpu_usage: float
    last_check: datetime
    retry_count: int
    health_score: float

class ServiceHealthWorker(QThread):
    """Background worker for service health monitoring"""
    health_updated = pyqtSignal(dict)
    service_status_changed = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.update_interval = 5  # seconds
        self.services = {}

        # Service configurations
        self.service_configs = {
            "voice_cloning": {
                "url": "http://127.0.0.1:5083",
                "health_endpoint": "/health",
                "priority": "high",
                "description": "Voice Cloning Service",
                "color": "#FF6B6B"  # Red
            },
            "assistant": {
                "url": "http://127.0.0.1:5080",
                "health_endpoint": "/health",
                "priority": "high",
                "description": "AI Assistant Service",
                "color": "#4ECDC4"  # Teal
            },
            "orchestrator": {
                "url": "http://127.0.0.1:5090",
                "health_endpoint": "/health",
                "priority": "medium",
                "description": "Service Orchestrator",
                "color": "#45B7D1"  # Blue
            },
            "web_interface": {
                "url": "http://127.0.0.1:8080",
                "health_endpoint": "/health",
                "priority": "medium",
                "description": "Web Interface Service",
                "color": "#96CEB4"  # Green
            },
            "autofix": {
                "url": "http://127.0.0.1:5081",
                "health_endpoint": "/health",
                "priority": "low",
                "description": "Auto-Fix Service",
                "color": "#FECA57"  # Yellow
            },
            "chatgpt_upgrade_monitor": {
                "url": "http://127.0.0.1:5085",
                "health_endpoint": "/health",
                "priority": "low",
                "description": "ChatGPT Upgrade Monitor",
                "color": "#FF9FF3"  # Pink
            },
            "advanced_daw": {
                "url": "http://127.0.0.1:5086",
                "health_endpoint": "/health",
                "priority": "medium",
                "description": "Advanced DAW System",
                "color": "#54A0FF"  # Light Blue
            },
            "trillion_dollar_cloner": {
                "url": "http://127.0.0.1:5087",
                "health_endpoint": "/health",
                "priority": "high",
                "description": "Trillion Dollar Voice Cloner",
                "color": "#5F27CD"  # Purple
            }
        }

        self._initialize_services()

    def _initialize_services(self):
        """Initialize service health metrics"""
        for service_name, config in self.service_configs.items():
            self.services[service_name] = ServiceHealthMetrics(
                name=service_name,
                url=config["url"],
                status="unknown",
                response_time=0.0,
                uptime=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                last_check=datetime.now(),
                retry_count=0,
                health_score=0.0
            )

    async def check_service_health(self, service_name: str) -> bool:
        """Check health of a specific service"""
        if service_name not in self.services:
            return False

        service = self.services[service_name]
        config = self.service_configs[service_name]

        try:
            start_time = time.time()
            response = requests.get(
                f"{service.url}{config['health_endpoint']}",
                timeout=3
            )
            response_time = time.time() - start_time

            old_status = service.status

            if response.status_code == 200:
                service.status = "healthy"
                service.response_time = response_time
                service.retry_count = 0
                service.health_score = max(0, 100 - (response_time * 100))
            else:
                service.status = "unhealthy"
                service.retry_count += 1
                service.health_score = 0

            service.last_check = datetime.now()

            # Emit status change signal if status changed
            if old_status != service.status:
                self.service_status_changed.emit(service_name, service.status)

            return service.status == "healthy"

        except Exception as e:
            old_status = service.status
            service.status = "unhealthy"
            service.retry_count += 1
            service.health_score = 0
            service.last_check = datetime.now()

            if old_status != service.status:
                self.service_status_changed.emit(service_name, service.status)

            logger.debug(f"Health check failed for {service_name}: {e}")
            return False

    async def update_all_services(self):
        """Update health status of all services"""
        tasks = []
        for service_name in self.services.keys():
            task = asyncio.create_task(self.check_service_health(service_name))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        services_data = {}
        for service_name in self.services.keys():
            service = self.services[service_name]
            config = self.service_configs[service_name]

            services_data[service_name] = {
                "name": service.name,
                "description": config["description"],
                "url": service.url,
                "status": service.status,
                "priority": config["priority"],
                "color": config["color"],
                "response_time": service.response_time,
                "uptime": service.uptime,
                "health_score": service.health_score,
                "retry_count": service.retry_count,
                "last_check": service.last_check.isoformat()
            }

        # Calculate summary statistics
        total_services = len(self.services)
        healthy_services = sum(1 for s in self.services.values() if s.status == "healthy")
        unhealthy_services = sum(1 for s in self.services.values() if s.status == "unhealthy")
        avg_response_time = sum(s.response_time for s in self.services.values()) / max(total_services, 1)
        avg_health_score = sum(s.health_score for s in self.services.values()) / max(total_services, 1)

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "unhealthy_services": unhealthy_services,
                "health_percentage": (healthy_services / max(total_services, 1)) * 100,
                "average_response_time": avg_response_time,
                "average_health_score": avg_health_score
            },
            "services": services_data
        }

    def run(self):
        """Main worker thread loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.running:
            try:
                loop.run_until_complete(self.update_all_services())
                dashboard_data = self.get_dashboard_data()
                self.health_updated.emit(dashboard_data)
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Worker thread error: {e}")
                time.sleep(5)

        loop.close()

    def stop(self):
        """Stop the worker thread"""
        self.running = False

class ServiceStatusWidget(QWidget):
    """Individual service status widget"""

    def __init__(self, service_data: Dict[str, Any]):
        super().__init__()
        self.service_data = service_data
        self.setup_ui()

    def setup_ui(self):
        """Setup the service status widget UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Service header
        header_layout = QHBoxLayout()

        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(20, 20)
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                border-radius: 10px;
                background-color: {self.service_data['color']};
                border: 2px solid #ffffff;
            }}
        """)

        # Service name
        self.name_label = QLabel(self.service_data['name'].replace('_', ' ').title())
        self.name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Priority badge
        priority_colors = {"high": "#FF6B6B", "medium": "#FECA57", "low": "#96CEB4"}
        self.priority_label = QLabel(self.service_data['priority'].upper())
        self.priority_label.setStyleSheet(f"""
            QLabel {{
                background-color: {priority_colors[self.service_data['priority']]};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)

        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.priority_label)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.service_data['description'])
        desc_label.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(desc_label)

        # Status
        self.status_label = QLabel(f"Status: {self.service_data['status'].title()}")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.status_label)

        # Metrics layout
        metrics_layout = QGridLayout()

        # Response time
        metrics_layout.addWidget(QLabel("Response Time:"), 0, 0)
        self.response_time_label = QLabel(f"{self.service_data['response_time']:.3f}s")
        metrics_layout.addWidget(self.response_time_label, 0, 1)

        # Health score
        metrics_layout.addWidget(QLabel("Health Score:"), 1, 0)
        self.health_score_progress = QProgressBar()
        self.health_score_progress.setRange(0, 100)
        self.health_score_progress.setValue(int(self.service_data['health_score']))
        self.health_score_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4ECDC4;
                border-radius: 5px;
            }
        """)
        metrics_layout.addWidget(self.health_score_progress, 1, 1)

        # Retry count
        metrics_layout.addWidget(QLabel("Retry Count:"), 2, 0)
        self.retry_count_label = QLabel(str(self.service_data['retry_count']))
        metrics_layout.addWidget(self.retry_count_label, 2, 1)

        layout.addLayout(metrics_layout)

        # URL
        url_label = QLabel(f"URL: {self.service_data['url']}")
        url_label.setStyleSheet("color: #888888; font-size: 10px;")
        url_label.setWordWrap(True)
        layout.addWidget(url_label)

        self.setLayout(layout)

        # Set widget style
        self.setStyleSheet("""
            ServiceStatusWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                margin: 5px;
            }
            ServiceStatusWidget:hover {
                border-color: #4ECDC4;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)

        self.update_status()

    def update_status(self):
        """Update the widget with new service data"""
        # Update status indicator color based on status
        if self.service_data['status'] == 'healthy':
            color = "#4ECDC4"  # Green
        elif self.service_data['status'] == 'unhealthy':
            color = "#FF6B6B"  # Red
        else:
            color = "#FECA57"  # Yellow

        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                border-radius: 10px;
                background-color: {color};
                border: 2px solid #ffffff;
            }}
        """)

        # Update status label
        self.status_label.setText(f"Status: {self.service_data['status'].title()}")

        # Update metrics
        self.response_time_label.setText(f"{self.service_data['response_time']:.3f}s")
        self.health_score_progress.setValue(int(self.service_data['health_score']))
        self.retry_count_label.setText(str(self.service_data['retry_count']))

    def update_service_data(self, service_data: Dict[str, Any]):
        """Update service data and refresh display"""
        self.service_data = service_data
        self.update_status()

class ServiceHealthDashboardGUI(QMainWindow):
    """Main PyQt6 Service Health Dashboard GUI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceStudio God-Tier Service Health Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # Initialize service widgets dictionary
        self.service_widgets = {}

        # Initialize worker thread
        self.health_worker = ServiceHealthWorker()
        self.health_worker.health_updated.connect(self.update_dashboard)
        self.health_worker.service_status_changed.connect(self.on_service_status_changed)

        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()

        # Start worker thread
        self.health_worker.start()

        logger.info("Service Health Dashboard GUI initialized")

    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        self.setup_header(main_layout)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #4ECDC4;
                color: white;
            }
        """)

        # Dashboard tab
        self.setup_dashboard_tab()

        # Services tab
        self.setup_services_tab()

        # Logs tab
        self.setup_logs_tab()

        main_layout.addWidget(self.tab_widget)
        central_widget.setLayout(main_layout)

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)

    def setup_header(self, layout):
        """Setup the dashboard header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4ECDC4, stop:1 #45B7D1);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_frame.setFixedHeight(120)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("VoiceStudio God-Tier Service Health Dashboard")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Summary stats
        self.summary_layout = QHBoxLayout()

        # Total services
        self.total_services_label = QLabel("Total: 0")
        self.total_services_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        self.summary_layout.addWidget(self.total_services_label)

        # Healthy services
        self.healthy_services_label = QLabel("Healthy: 0")
        self.healthy_services_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        self.summary_layout.addWidget(self.healthy_services_label)

        # Unhealthy services
        self.unhealthy_services_label = QLabel("Unhealthy: 0")
        self.unhealthy_services_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        self.summary_layout.addWidget(self.unhealthy_services_label)

        # Health percentage
        self.health_percentage_label = QLabel("Health: 0%")
        self.health_percentage_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 12px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)
        self.summary_layout.addWidget(self.health_percentage_label)

        header_layout.addLayout(self.summary_layout)

        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

    def setup_dashboard_tab(self):
        """Setup the dashboard tab"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Services grid
        self.services_scroll = QScrollArea()
        self.services_scroll.setWidgetResizable(True)
        self.services_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.services_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.services_widget = QWidget()
        self.services_layout = QGridLayout()
        self.services_layout.setSpacing(10)
        self.services_widget.setLayout(self.services_layout)

        self.services_scroll.setWidget(self.services_widget)
        layout.addWidget(self.services_scroll)

        dashboard_widget.setLayout(layout)
        self.tab_widget.addTab(dashboard_widget, "Dashboard")

    def setup_services_tab(self):
        """Setup the services tab with table view"""
        services_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(8)
        self.services_table.setHorizontalHeaderLabels([
            "Service", "Status", "Priority", "Response Time",
            "Health Score", "Retry Count", "URL", "Last Check"
        ])

        # Set table properties
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.services_table.horizontalHeader().setStretchLastSection(True)
        self.services_table.setStyleSheet("""
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

        layout.addWidget(self.services_table)
        services_widget.setLayout(layout)
        self.tab_widget.addTab(services_widget, "Services")

    def setup_logs_tab(self):
        """Setup the logs tab"""
        logs_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Logs text area
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                border: 1px solid #333333;
                border-radius: 5px;
            }
        """)

        layout.addWidget(self.logs_text)
        logs_widget.setLayout(layout)
        self.tab_widget.addTab(logs_widget, "Logs")

    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        # Refresh action
        refresh_action = QAction('Refresh', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_dashboard)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('View')

        # Auto-refresh toggle
        self.auto_refresh_action = QAction('Auto Refresh', self)
        self.auto_refresh_action.setCheckable(True)
        self.auto_refresh_action.setChecked(True)
        view_menu.addAction(self.auto_refresh_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        # About action
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)

        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()

    def update_time(self):
        """Update the time display in status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)

    def update_dashboard(self, dashboard_data: Dict[str, Any]):
        """Update the dashboard with new data"""
        try:
            # Update summary stats
            summary = dashboard_data['summary']
            self.total_services_label.setText(f"Total: {summary['total_services']}")
            self.healthy_services_label.setText(f"Healthy: {summary['healthy_services']}")
            self.unhealthy_services_label.setText(f"Unhealthy: {summary['unhealthy_services']}")
            self.health_percentage_label.setText(f"Health: {summary['health_percentage']:.1f}%")

            # Update services table
            self.update_services_table(dashboard_data['services'])

            # Update dashboard widgets
            self.update_dashboard_widgets(dashboard_data['services'])

            # Add log entry
            self.add_log_entry(f"Dashboard updated at {dashboard_data['timestamp']}")

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")
            self.add_log_entry(f"Error updating dashboard: {e}")

    def update_services_table(self, services_data: Dict[str, Any]):
        """Update the services table"""
        self.services_table.setRowCount(len(services_data))

        for row, (service_name, service_data) in enumerate(services_data.items()):
            # Service name
            self.services_table.setItem(row, 0, QTableWidgetItem(service_name.replace('_', ' ').title()))

            # Status
            status_item = QTableWidgetItem(service_data['status'].title())
            if service_data['status'] == 'healthy':
                status_item.setBackground(QColor("#4ECDC4"))
            elif service_data['status'] == 'unhealthy':
                status_item.setBackground(QColor("#FF6B6B"))
            else:
                status_item.setBackground(QColor("#FECA57"))
            self.services_table.setItem(row, 1, status_item)

            # Priority
            self.services_table.setItem(row, 2, QTableWidgetItem(service_data['priority'].title()))

            # Response time
            self.services_table.setItem(row, 3, QTableWidgetItem(f"{service_data['response_time']:.3f}s"))

            # Health score
            self.services_table.setItem(row, 4, QTableWidgetItem(f"{service_data['health_score']:.1f}"))

            # Retry count
            self.services_table.setItem(row, 5, QTableWidgetItem(str(service_data['retry_count'])))

            # URL
            self.services_table.setItem(row, 6, QTableWidgetItem(service_data['url']))

            # Last check
            last_check = datetime.fromisoformat(service_data['last_check']).strftime("%H:%M:%S")
            self.services_table.setItem(row, 7, QTableWidgetItem(last_check))

    def update_dashboard_widgets(self, services_data: Dict[str, Any]):
        """Update the dashboard widgets"""
        # Clear existing widgets
        for i in reversed(range(self.services_layout.count())):
            child = self.services_layout.itemAt(i).widget()
            if child:
                child.deleteLater()

        # Add service widgets
        row = 0
        col = 0
        max_cols = 3

        for service_name, service_data in services_data.items():
            if service_name in self.service_widgets:
                # Update existing widget
                self.service_widgets[service_name].update_service_data(service_data)
            else:
                # Create new widget
                service_widget = ServiceStatusWidget(service_data)
                self.service_widgets[service_name] = service_widget
                self.services_layout.addWidget(service_widget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def on_service_status_changed(self, service_name: str, new_status: str):
        """Handle service status change"""
        self.add_log_entry(f"Service {service_name} status changed to {new_status}")

        # Show notification if service becomes unhealthy
        if new_status == 'unhealthy':
            self.show_notification(f"Service {service_name} is unhealthy")

    def add_log_entry(self, message: str):
        """Add entry to logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs_text.append(log_entry)

        # Auto-scroll to bottom
        cursor = self.logs_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.logs_text.setTextCursor(cursor)

    def show_notification(self, message: str):
        """Show system notification"""
        if hasattr(self, 'system_tray'):
            self.system_tray.showMessage("Service Alert", message, QSystemTrayIcon.MessageIcon.Warning)

    def refresh_dashboard(self):
        """Manually refresh the dashboard"""
        self.add_log_entry("Manual refresh requested")
        # The worker thread will automatically update

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About",
            "VoiceStudio God-Tier Service Health Dashboard\n"
            "Version 2.0.0\n\n"
            "Real-time service health monitoring and status display\n"
            "Maximum performance tracking and service management\n\n"
            "Built with PyQt6")

    def closeEvent(self, event):
        """Handle application close"""
        self.health_worker.stop()
        self.health_worker.wait()
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceStudio Service Health Dashboard")
    app.setApplicationVersion("2.0.0")

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = ServiceHealthDashboardGUI()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
