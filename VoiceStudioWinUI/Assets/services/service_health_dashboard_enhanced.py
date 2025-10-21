#!/usr/bin/env python3
"""
VOICESTUDIO GOD-TIER SERVICE HEALTH DASHBOARD ENHANCED
Advanced PyQt6 GUI with Plugin System Integration
Maximum Extensibility and Customization
Version: 3.0.0 "Ultimate Enhanced Dashboard"
"""

import sys
import os
import asyncio
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import requests
from dataclasses import dataclass, asdict
from pathlib import Path

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QProgressBar, QGroupBox, QFrame, QScrollArea,
    QTextEdit, QSplitter, QHeaderView, QMessageBox, QSystemTrayIcon,
    QMenu, QStatusBar, QToolBar, QAction, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QSlider, QRadioButton, QButtonGroup, QListWidget, QListWidgetItem,
    QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QFileDialog,
    QDockWidget, QMdiArea, QMdiSubWindow, QDesktopWidget, QInputDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, QRect, QSize, QPoint, QDateTime, QObject, QEvent
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QPainter, 
    QBrush, QLinearGradient, QPen, QAction, QKeySequence
)

# Import plugin system
from service_health_dashboard_plugins import (
    PluginManager, PluginConfigDialog, PluginManagerDialog, 
    BasePlugin, PluginMetadata
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ServiceHealthMetrics:
    """Enhanced service health metrics"""
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
    custom_metrics: Dict[str, Any] = None
    plugin_data: Dict[str, Any] = None

class ServiceHealthWorker(QThread):
    """Enhanced background worker for service health monitoring"""
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
                "color": "#FF6B6B"
            },
            "assistant": {
                "url": "http://127.0.0.1:5080",
                "health_endpoint": "/health",
                "priority": "high",
                "description": "AI Assistant Service",
                "color": "#4ECDC4"
            },
            "orchestrator": {
                "url": "http://127.0.0.1:5090",
                "health_endpoint": "/health",
                "priority": "medium",
                "description": "Service Orchestrator",
                "color": "#45B7D1"
            },
            "web_interface": {
                "url": "http://127.0.0.1:8080",
                "health_endpoint": "/health",
                "priority": "medium",
                "description": "Web Interface Service",
                "color": "#96CEB4"
            },
            "autofix": {
                "url": "http://127.0.0.1:5081",
                "health_endpoint": "/health",
                "priority": "low",
                "description": "Auto-Fix Service",
                "color": "#FECA57"
            },
            "chatgpt_upgrade_monitor": {
                "url": "http://127.0.0.1:5085",
                "health_endpoint": "/health",
                "priority": "low",
                "description": "ChatGPT Upgrade Monitor",
                "color": "#FF9FF3"
            },
            "advanced_daw": {
                "url": "http://127.0.0.1:5086",
                "health_endpoint": "/health",
                "priority": "high",
                "description": "Advanced DAW System",
                "color": "#54A0FF"
            },
            "trillion_dollar_cloner": {
                "url": "http://127.0.0.1:5087",
                "health_endpoint": "/health",
                "priority": "high",
                "description": "Trillion Dollar Voice Cloner",
                "color": "#5F27CD"
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
                health_score=0.0,
                custom_metrics={},
                plugin_data={}
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
                "last_check": service.last_check.isoformat(),
                "custom_metrics": service.custom_metrics,
                "plugin_data": service.plugin_data
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

class ServiceHealthDashboardEnhancedGUI(QMainWindow):
    """Enhanced PyQt6 Service Health Dashboard GUI with Plugin System"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceStudio God-Tier Service Health Dashboard Enhanced")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1400, 900)
        
        # Initialize service widgets dictionary
        self.service_widgets = {}
        
        # Initialize plugin system
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.plugin_loaded.connect(self.on_plugin_loaded)
        self.plugin_manager.plugin_unloaded.connect(self.on_plugin_unloaded)
        self.plugin_manager.plugin_error.connect(self.on_plugin_error)
        
        # Initialize worker thread
        self.health_worker = ServiceHealthWorker()
        self.health_worker.health_updated.connect(self.update_dashboard)
        self.health_worker.service_status_changed.connect(self.on_service_status_changed)
        
        # Load default plugins
        self.load_default_plugins()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_dock_widgets()
        
        # Start worker thread
        self.health_worker.start()
        
        logger.info("Enhanced Service Health Dashboard GUI initialized")

    def setup_ui(self):
        """Setup the enhanced main UI"""
        # Create central widget with MDI area
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        # Create main dashboard subwindow
        self.dashboard_subwindow = QMdiSubWindow()
        self.dashboard_subwindow.setWindowTitle("Service Dashboard")
        self.dashboard_subwindow.setWindowFlags(Qt.WindowType.Widget)
        
        dashboard_widget = self.create_dashboard_widget()
        self.dashboard_subwindow.setWidget(dashboard_widget)
        self.mdi_area.addSubWindow(self.dashboard_subwindow)
        self.dashboard_subwindow.showMaximized()
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMdiArea {
                background-color: #f5f5f5;
            }
        """)

    def create_dashboard_widget(self) -> QWidget:
        """Create the main dashboard widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self.setup_header(layout)
        
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
        
        # Plugins tab
        self.setup_plugins_tab()
        
        # Logs tab
        self.setup_logs_tab()
        
        layout.addWidget(self.tab_widget)
        widget.setLayout(layout)
        return widget

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
        title_label = QLabel("VoiceStudio God-Tier Service Health Dashboard Enhanced")
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
        self.services_table.setColumnCount(9)
        self.services_table.setHorizontalHeaderLabels([
            "Service", "Status", "Priority", "Response Time", 
            "Health Score", "Retry Count", "Memory", "CPU", "Last Check"
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

    def setup_plugins_tab(self):
        """Setup the plugins tab"""
        plugins_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Plugin controls
        controls_layout = QHBoxLayout()
        
        refresh_plugins_btn = QPushButton("Refresh Plugins")
        refresh_plugins_btn.clicked.connect(self.refresh_plugins)
        controls_layout.addWidget(refresh_plugins_btn)
        
        manage_plugins_btn = QPushButton("Manage Plugins")
        manage_plugins_btn.clicked.connect(self.manage_plugins)
        controls_layout.addWidget(manage_plugins_btn)
        
        load_plugin_btn = QPushButton("Load Plugin")
        load_plugin_btn.clicked.connect(self.load_plugin)
        controls_layout.addWidget(load_plugin_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Plugin widgets area
        self.plugin_widgets_area = QScrollArea()
        self.plugin_widgets_area.setWidgetResizable(True)
        
        self.plugin_widgets_container = QWidget()
        self.plugin_widgets_layout = QVBoxLayout()
        self.plugin_widgets_container.setLayout(self.plugin_widgets_layout)
        
        self.plugin_widgets_area.setWidget(self.plugin_widgets_container)
        layout.addWidget(self.plugin_widgets_area)
        
        plugins_widget.setLayout(layout)
        self.tab_widget.addTab(plugins_widget, "Plugins")

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
        
        # Plugins menu
        plugins_menu = menubar.addMenu('Plugins')
        
        # Manage plugins action
        manage_plugins_action = QAction('Manage Plugins', self)
        manage_plugins_action.triggered.connect(self.manage_plugins)
        plugins_menu.addAction(manage_plugins_action)
        
        # Load plugin action
        load_plugin_action = QAction('Load Plugin', self)
        load_plugin_action.triggered.connect(self.load_plugin)
        plugins_menu.addAction(load_plugin_action)
        
        plugins_menu.addSeparator()
        
        # Plugin submenu
        self.plugin_submenu = plugins_menu.addMenu('Available Plugins')
        
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

    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_dashboard)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Plugin management actions
        manage_plugins_action = QAction("Manage Plugins", self)
        manage_plugins_action.triggered.connect(self.manage_plugins)
        toolbar.addAction(manage_plugins_action)

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

    def setup_dock_widgets(self):
        """Setup dock widgets for plugins"""
        # Plugin dock widget
        self.plugin_dock = QDockWidget("Plugin Panel", self)
        self.plugin_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        plugin_widget = QWidget()
        plugin_layout = QVBoxLayout()
        
        self.plugin_panel_widgets = QWidget()
        self.plugin_panel_layout = QVBoxLayout()
        self.plugin_panel_widgets.setLayout(self.plugin_panel_layout)
        
        plugin_layout.addWidget(self.plugin_panel_widgets)
        plugin_widget.setLayout(plugin_layout)
        
        self.plugin_dock.setWidget(plugin_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.plugin_dock)

    def load_default_plugins(self):
        """Load default plugins"""
        try:
            # Load analytics plugin
            if self.plugin_manager.load_plugin("analytics"):
                logger.info("Analytics plugin loaded successfully")
            
            # Load alert manager plugin
            if self.plugin_manager.load_plugin("alert_manager"):
                logger.info("Alert manager plugin loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading default plugins: {e}")

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
            
            # Notify plugins
            self.notify_plugins("dashboard_updated", dashboard_data)
            
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
            
            # Memory usage
            self.services_table.setItem(row, 6, QTableWidgetItem(f"{service_data.get('memory_usage', 0):.1f}MB"))
            
            # CPU usage
            self.services_table.setItem(row, 7, QTableWidgetItem(f"{service_data.get('cpu_usage', 0):.1f}%"))
            
            # Last check
            last_check = datetime.fromisoformat(service_data['last_check']).strftime("%H:%M:%S")
            self.services_table.setItem(row, 8, QTableWidgetItem(last_check))

    def update_dashboard_widgets(self, services_data: Dict[str, Any]):
        """Update the dashboard widgets"""
        # Clear existing widgets
        for i in reversed(range(self.services_layout.count())):
            child = self.services_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add service widgets (simplified version)
        row = 0
        col = 0
        max_cols = 3
        
        for service_name, service_data in services_data.items():
            # Create simple service widget
            service_widget = self.create_service_widget(service_data)
            self.services_layout.addWidget(service_widget, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_service_widget(self, service_data: Dict[str, Any]) -> QWidget:
        """Create a service widget"""
        widget = QGroupBox(service_data['name'].replace('_', ' ').title())
        layout = QVBoxLayout()
        
        # Status indicator
        status_color = "#4ECDC4" if service_data['status'] == 'healthy' else "#FF6B6B"
        status_label = QLabel(f"Status: {service_data['status'].title()}")
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Health score
        health_label = QLabel(f"Health Score: {service_data['health_score']:.1f}")
        layout.addWidget(health_label)
        
        # Response time
        response_label = QLabel(f"Response Time: {service_data['response_time']:.3f}s")
        layout.addWidget(response_label)
        
        widget.setLayout(layout)
        return widget

    def notify_plugins(self, event: str, data: Any = None):
        """Notify all plugins of an event"""
        for plugin in self.plugin_manager.get_all_plugins().values():
            try:
                plugin.trigger_hook(event, data)
            except Exception as e:
                logger.error(f"Error notifying plugin {plugin.metadata.name}: {e}")

    def on_service_status_changed(self, service_name: str, new_status: str):
        """Handle service status change"""
        self.add_log_entry(f"Service {service_name} status changed to {new_status}")
        
        # Notify plugins
        self.notify_plugins("service_status_changed", {"service_name": service_name, "status": new_status})
        
        # Show notification if service becomes unhealthy
        if new_status == 'unhealthy':
            self.show_notification(f"Service {service_name} is unhealthy")

    def on_plugin_loaded(self, plugin_name: str):
        """Handle plugin loaded event"""
        self.add_log_entry(f"Plugin {plugin_name} loaded successfully")
        
        # Add plugin widget to plugins tab
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin:
            plugin_widget = plugin.create_widget()
            if plugin_widget:
                self.plugin_widgets_layout.addWidget(plugin_widget)
                
                # Add to plugin panel
                panel_widget = plugin.create_widget()
                if panel_widget:
                    self.plugin_panel_layout.addWidget(panel_widget)

    def on_plugin_unloaded(self, plugin_name: str):
        """Handle plugin unloaded event"""
        self.add_log_entry(f"Plugin {plugin_name} unloaded")

    def on_plugin_error(self, plugin_name: str, error: str):
        """Handle plugin error event"""
        self.add_log_entry(f"Plugin {plugin_name} error: {error}")

    def manage_plugins(self):
        """Open plugin manager dialog"""
        dialog = PluginManagerDialog(self.plugin_manager, self)
        dialog.exec()

    def load_plugin(self):
        """Load a plugin"""
        plugin_name, ok = QInputDialog.getText(self, "Load Plugin", "Enter plugin name:")
        if ok and plugin_name:
            self.plugin_manager.load_plugin(plugin_name)

    def refresh_plugins(self):
        """Refresh plugin list"""
        self.plugin_manager.load_plugin_metadata()
        self.add_log_entry("Plugin list refreshed")

    def refresh_dashboard(self):
        """Manually refresh the dashboard"""
        self.add_log_entry("Manual refresh requested")

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
        QMessageBox.information(self, "Service Alert", message)

    def update_time(self):
        """Update the time display in status bar"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
            "VoiceStudio God-Tier Service Health Dashboard Enhanced\n"
            "Version 3.0.0\n\n"
            "Advanced PyQt6 GUI with Plugin System Integration\n"
            "Maximum Extensibility and Customization\n\n"
            "Built with PyQt6 and Advanced Plugin Architecture")

    def closeEvent(self, event):
        """Handle application close"""
        # Stop worker thread
        self.health_worker.stop()
        self.health_worker.wait()
        
        # Cleanup plugins
        for plugin in self.plugin_manager.get_all_plugins().values():
            plugin.cleanup()
        
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceStudio Service Health Dashboard Enhanced")
    app.setApplicationVersion("3.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ServiceHealthDashboardEnhancedGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
