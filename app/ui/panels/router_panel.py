"""
PySide6 Desktop Router Panel for VoiceStudio
"""

from __future__ import annotations
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QGroupBox,
    QGridLayout,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QFrame,
)
from PySide6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PySide6.QtGui import QFont, QPalette, QColor
import requests
import websocket
import threading


class WebSocketClient(QThread):
    message_received = pyqtSignal(dict)
    connection_changed = pyqtSignal(bool)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.ws = None
        self.running = False

    def run(self):
        self.running = True
        try:
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_close=self.on_close,
                on_error=self.on_error,
            )
            self.ws.run_forever()
        except Exception as e:
            print(f"WebSocket error: {e}")

    def on_open(self, ws):
        self.connection_changed.emit(True)

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.message_received.emit(data)
        except Exception as e:
            print(f"Message parsing error: {e}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connection_changed.emit(False)

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        self.connection_changed.emit(False)

    def stop(self):
        self.running = False
        if self.ws:
            self.ws.close()


class RouterPanel(QMainWindow):
    def __init__(self, base_url: str = "http://127.0.0.1:5090"):
        super().__init__()
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws") + "/ws"
        self.engines: Dict = {}
        self.jobs: Dict[str, Dict] = {}

        self.setWindowTitle("VoiceStudio Router Panel")
        self.setGeometry(100, 100, 1200, 800)

        # Setup UI
        self.setup_ui()
        self.setup_websocket()
        self.setup_timers()

        # Initial data fetch
        self.fetch_health()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_layout = QHBoxLayout()
        self.title_label = QLabel("VoiceStudio Router Panel")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))

        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.fetch_health)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(header_layout)

        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Engines tab
        self.setup_engines_tab()

        # TTS tab
        self.setup_tts_tab()

        # Jobs tab
        self.setup_jobs_tab()

        # Tools tab
        self.setup_tools_tab()

    def setup_engines_tab(self):
        engines_widget = QWidget()
        layout = QVBoxLayout(engines_widget)

        # Engine status table
        self.engines_table = QTableWidget()
        self.engines_table.setColumnCount(5)
        self.engines_table.setHorizontalHeaderLabels(
            ["Engine", "Status", "Load", "Languages", "Quality"]
        )

        layout.addWidget(QLabel("Engine Status"))
        layout.addWidget(self.engines_table)

        self.tab_widget.addTab(engines_widget, "Engines")

    def setup_tts_tab(self):
        tts_widget = QWidget()
        layout = QVBoxLayout(tts_widget)

        # TTS form
        form_group = QGroupBox("Text-to-Speech Request")
        form_layout = QGridLayout(form_group)

        # Text input
        form_layout.addWidget(QLabel("Text:"), 0, 0)
        self.text_input = QTextEdit()
        self.text_input.setMaximumHeight(100)
        self.text_input.setText("Hello, this is a test of the VoiceStudio router!")
        form_layout.addWidget(self.text_input, 0, 1)

        # Language selection
        form_layout.addWidget(QLabel("Language:"), 1, 0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["en", "es", "fr", "de", "it", "pt", "zh", "ja"])
        form_layout.addWidget(self.language_combo, 1, 1)

        # Quality selection
        form_layout.addWidget(QLabel("Quality:"), 2, 0)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["fast", "balanced", "quality"])
        form_layout.addWidget(self.quality_combo, 2, 1)

        # Mode selection
        form_layout.addWidget(QLabel("Mode:"), 3, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["sync", "async"])
        form_layout.addWidget(self.mode_combo, 3, 1)

        # Sample rate
        form_layout.addWidget(QLabel("Sample Rate:"), 4, 0)
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 48000)
        self.sample_rate_spin.setValue(22050)
        form_layout.addWidget(self.sample_rate_spin, 4, 1)

        # Generate button
        self.generate_btn = QPushButton("Generate Speech")
        self.generate_btn.clicked.connect(self.generate_speech)
        form_layout.addWidget(self.generate_btn, 5, 0, 1, 2)

        layout.addWidget(form_group)

        # Response area
        response_group = QGroupBox("Response")
        response_layout = QVBoxLayout(response_group)

        self.response_text = QTextEdit()
        self.response_text.setMaximumHeight(150)
        self.response_text.setReadOnly(True)
        response_layout.addWidget(self.response_text)

        layout.addWidget(response_group)

        self.tab_widget.addTab(tts_widget, "TTS")

    def setup_jobs_tab(self):
        jobs_widget = QWidget()
        layout = QVBoxLayout(jobs_widget)

        # Jobs table
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(6)
        self.jobs_table.setHorizontalHeaderLabels(
            ["Job ID", "Status", "Progress", "Engine", "Started", "Error"]
        )

        layout.addWidget(QLabel("Active Jobs"))
        layout.addWidget(self.jobs_table)

        self.tab_widget.addTab(jobs_widget, "Jobs")

    def setup_tools_tab(self):
        tools_widget = QWidget()
        layout = QVBoxLayout(tools_widget)

        # Diagnostics
        diag_group = QGroupBox("Diagnostics")
        diag_layout = QVBoxLayout(diag_group)

        self.download_diag_btn = QPushButton("Download Diagnostics Bundle")
        self.download_diag_btn.clicked.connect(self.download_diagnostics)
        diag_layout.addWidget(self.download_diag_btn)

        layout.addWidget(diag_group)

        # Settings
        settings_group = QGroupBox("Settings")
        settings_layout = QGridLayout(settings_group)

        settings_layout.addWidget(QLabel("Base URL:"), 0, 0)
        self.url_input = QLineEdit(self.base_url)
        settings_layout.addWidget(self.url_input, 0, 1)

        self.apply_url_btn = QPushButton("Apply URL")
        self.apply_url_btn.clicked.connect(self.apply_url)
        settings_layout.addWidget(self.apply_url_btn, 0, 2)

        layout.addWidget(settings_group)

        self.tab_widget.addTab(tools_widget, "Tools")

    def setup_websocket(self):
        self.ws_client = WebSocketClient(self.ws_url)
        self.ws_client.message_received.connect(self.handle_websocket_message)
        self.ws_client.connection_changed.connect(self.update_connection_status)
        self.ws_client.start()

    def setup_timers(self):
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.fetch_health)
        self.refresh_timer.start(5000)  # 5 seconds

    def update_connection_status(self, connected: bool):
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def handle_websocket_message(self, data: dict):
        if data.get("type") == "job":
            self.update_job_status(data)

    def update_job_status(self, data: dict):
        job_id = data.get("id")
        phase = data.get("phase")

        if phase == "start":
            self.jobs[job_id] = {
                "id": job_id,
                "status": "running",
                "progress": 0,
                "started": time.time(),
            }
        elif phase == "progress":
            if job_id in self.jobs:
                self.jobs[job_id]["progress"] = data.get("progress", 0)
        elif phase == "done":
            if job_id in self.jobs:
                self.jobs[job_id].update(
                    {
                        "status": "done",
                        "progress": 1,
                        "engine": data.get("engine"),
                        "finished": time.time(),
                    }
                )
        elif phase == "error":
            if job_id in self.jobs:
                self.jobs[job_id].update(
                    {
                        "status": "error",
                        "error": data.get("error"),
                        "finished": time.time(),
                    }
                )

        self.update_jobs_table()

    def fetch_health(self):
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.engines = data.get("engines", {})
                self.update_engines_table()
                self.status_label.setText("API Healthy")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.status_label.setText("API Error")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception as e:
            self.status_label.setText("API Unreachable")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            print(f"Health check failed: {e}")

    def update_engines_table(self):
        self.engines_table.setRowCount(len(self.engines))

        for row, (engine_id, engine_data) in enumerate(self.engines.items()):
            self.engines_table.setItem(row, 0, QTableWidgetItem(engine_id.upper()))

            status = "Healthy" if engine_data.get("healthy", False) else "Unhealthy"
            status_item = QTableWidgetItem(status)
            if engine_data.get("healthy", False):
                status_item.setBackground(QColor(200, 255, 200))
            else:
                status_item.setBackground(QColor(255, 200, 200))
            self.engines_table.setItem(row, 1, status_item)

            load = engine_data.get("load", 0)
            self.engines_table.setItem(row, 2, QTableWidgetItem(f"{load:.1%}"))

            languages = ", ".join(engine_data.get("languages", []))
            self.engines_table.setItem(row, 3, QTableWidgetItem(languages))

            quality = ", ".join(engine_data.get("quality", []))
            self.engines_table.setItem(row, 4, QTableWidgetItem(quality))

        self.engines_table.resizeColumnsToContents()

    def update_jobs_table(self):
        self.jobs_table.setRowCount(len(self.jobs))

        for row, (job_id, job_data) in enumerate(self.jobs.items()):
            self.jobs_table.setItem(row, 0, QTableWidgetItem(job_id))
            self.jobs_table.setItem(
                row, 1, QTableWidgetItem(job_data.get("status", "unknown"))
            )

            progress = job_data.get("progress", 0)
            self.jobs_table.setItem(row, 2, QTableWidgetItem(f"{progress:.1%}"))

            engine = job_data.get("engine", "")
            self.jobs_table.setItem(row, 3, QTableWidgetItem(engine))

            started = job_data.get("started", 0)
            started_str = (
                time.strftime("%H:%M:%S", time.localtime(started)) if started else ""
            )
            self.jobs_table.setItem(row, 4, QTableWidgetItem(started_str))

            error = job_data.get("error", "")
            self.jobs_table.setItem(row, 5, QTableWidgetItem(error))

        self.jobs_table.resizeColumnsToContents()

    def generate_speech(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter text to convert")
            return

        request_data = {
            "text": text,
            "language": self.language_combo.currentText(),
            "quality": self.quality_combo.currentText(),
            "voice_profile": {},
            "params": {"sample_rate": self.sample_rate_spin.value()},
            "mode": self.mode_combo.currentText(),
        }

        try:
            response = requests.post(
                f"{self.base_url}/tts", json=request_data, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                response_text = f"Engine: {data.get('engine')}\n"
                response_text += (
                    f"Tried Order: {' → '.join(data.get('tried_order', []))}\n"
                )
                if data.get("job_id"):
                    response_text += f"Job ID: {data.get('job_id')}\n"
                if data.get("result_b64_wav"):
                    response_text += "Audio generated successfully!"

                self.response_text.setText(response_text)
            else:
                QMessageBox.critical(
                    self, "Error", f"TTS request failed: {response.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"TTS request failed: {e}")

    def download_diagnostics(self):
        try:
            # Create diagnostics bundle
            response = requests.post(f"{self.base_url}/diagnostics/bundle", timeout=30)
            if response.status_code == 200:
                data = response.json()
                filename = data.get("file")

                # Download the bundle
                download_response = requests.get(
                    f"{self.base_url}/diagnostics/download?file={filename}"
                )
                if download_response.status_code == 200:
                    # Save file
                    file_path, _ = QFileDialog.getSaveFileName(
                        self, "Save Diagnostics Bundle", filename, "ZIP Files (*.zip)"
                    )
                    if file_path:
                        with open(file_path, "wb") as f:
                            f.write(download_response.content)
                        QMessageBox.information(
                            self, "Success", f"Diagnostics bundle saved to {file_path}"
                        )
                else:
                    QMessageBox.critical(
                        self, "Error", "Failed to download diagnostics bundle"
                    )
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to create diagnostics bundle"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Diagnostics download failed: {e}")

    def apply_url(self):
        new_url = self.url_input.text().strip()
        if new_url:
            self.base_url = new_url
            self.ws_url = new_url.replace("http", "ws") + "/ws"

            # Restart WebSocket connection
            self.ws_client.stop()
            self.ws_client = WebSocketClient(self.ws_url)
            self.ws_client.message_received.connect(self.handle_websocket_message)
            self.ws_client.connection_changed.connect(self.update_connection_status)
            self.ws_client.start()

            QMessageBox.information(self, "Success", f"URL updated to {new_url}")

    def closeEvent(self, event):
        self.ws_client.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = RouterPanel()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
