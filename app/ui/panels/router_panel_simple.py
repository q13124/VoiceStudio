"""
VoiceStudio — PySide6 Router Panel (Desktop Parity)

A lightweight desktop panel that talks to the Voice Engine Router:
  • GET  /health, /engines
  • POST /tts          (sync)
  • POST /tts_async    (async)
  • GET  /jobs/{id}    (polling)

Notes
-----
- Uses ThreadPoolExecutor to keep UI responsive.
- Saves returned WAV to a temp file and plays it via QMediaPlayer.
- WebSocket streaming is optional; for now we poll /jobs/:id every 500ms.
- Requires: PySide6, requests

Usage
-----
from PySide6.QtWidgets import QApplication
from app.ui.panels.router_panel import RouterPanel

app = QApplication([])
w = RouterPanel(base_url="http://127.0.0.1:5090")
w.show()
app.exec()
"""
from __future__ import annotations

import base64
import os
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import requests
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget  # imported to ensure multimedia backend loads on some systems
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass
class JobStatus:
    id: str
    status: str
    progress: float
    engine: Optional[str]
    result_b64_wav: Optional[str]
    error: Optional[str]


class RouterPanel(QWidget):
    toast = Signal(str)

    def __init__(self, base_url: str = "http://127.0.0.1:5090", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.base_url = base_url.rstrip("/")
        self.pool = ThreadPoolExecutor(max_workers=4)
        self.player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_out)
        self.temp_wav: Optional[Path] = None

        self._build_ui()
        self.toast.connect(self._on_toast)

        # periodic health refresh
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_health)
        self.timer.start(5000)
        self.refresh_health()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        self.setWindowTitle("VoiceStudio — Router Panel")
        root = QVBoxLayout(self)

        # Base URL + Refresh
        url_box = QHBoxLayout()
        self.url_edit = QLineEdit(self.base_url)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_health)
        url_box.addWidget(QLabel("Router URL:"))
        url_box.addWidget(self.url_edit)
        url_box.addWidget(self.btn_refresh)
        root.addLayout(url_box)

        # Engines table
        self.tbl = QTableWidget(0, 4)
        self.tbl.setHorizontalHeaderLabels(["Engine", "Healthy", "Load", "Languages"])
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        root.addWidget(self.tbl)

        # TTS form
        form = QGroupBox("Quick TTS")
        f = QGridLayout(form)
        self.txt_text = QTextEdit("Hello from VoiceStudio Router")
        self.txt_text.setMinimumHeight(96)
        self.cmb_lang = QLineEdit("en")
        self.cmb_quality = QComboBox(); self.cmb_quality.addItems(["fast", "balanced", "quality"]) ; self.cmb_quality.setCurrentText("balanced")
        self.btn_sync = QPushButton("Generate (sync)")
        self.btn_async = QPushButton("Generate (async)")
        self.btn_sync.clicked.connect(self._click_sync)
        self.btn_async.clicked.connect(self._click_async)
        self.lbl_status = QLabel("Idle")
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.setValue(0)

        f.addWidget(QLabel("Text"), 0, 0)
        f.addWidget(self.txt_text, 0, 1, 1, 3)
        f.addWidget(QLabel("Language"), 1, 0)
        f.addWidget(self.cmb_lang, 1, 1)
        f.addWidget(QLabel("Quality"), 1, 2)
        f.addWidget(self.cmb_quality, 1, 3)
        f.addWidget(self.btn_sync, 2, 1)
        f.addWidget(self.btn_async, 2, 2)
        f.addWidget(self.lbl_status, 3, 0, 1, 2)
        f.addWidget(self.progress, 3, 2, 1, 2)

        root.addWidget(form)

        # Audio controls (volume only; play auto on new result)
        vol_box = QHBoxLayout()
        vol_box.addWidget(QLabel("Volume"))
        self.audio_out.setVolume(0.8)
        root.addLayout(vol_box)

        root.addItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Expanding))

    # ---------------- Helpers ----------------
    def _on_toast(self, msg: str) -> None:
        QMessageBox.information(self, "Router", msg)

    def _save_wav(self, b64: str) -> Path:
        raw = base64.b64decode(b64)
        tmp = Path(tempfile.gettempdir()) / f"voicestudio_{int(time.time()*1000)}.wav"
        with open(tmp, "wb") as f:
            f.write(raw)
        self.temp_wav = tmp
        return tmp

    def _play_wav(self, wav_path: Path) -> None:
        from PySide6.QtCore import QUrl
        self.player.setSource(QUrl.fromLocalFile(str(wav_path)))
        self.player.play()

    def _set_busy(self, busy: bool) -> None:
        self.btn_sync.setEnabled(not busy)
        self.btn_async.setEnabled(not busy)

    # ---------------- Networking (threaded) ----------------
    def refresh_health(self) -> None:
        self.base_url = self.url_edit.text().strip().rstrip("/")
        def work():
            r = requests.get(f"{self.base_url}/health", timeout=10)
            r.raise_for_status()
            return r.json()
        def done(fut):
            try:
                js = fut.result()
            except Exception as e:
                self.lbl_status.setText(f"Health error: {e}")
                return
            engines: Dict[str, dict] = js.get("engines", {})
            self.tbl.setRowCount(0)
            for i, (name, info) in enumerate(engines.items()):
                self.tbl.insertRow(i)
                self.tbl.setItem(i, 0, QTableWidgetItem(name))
                self.tbl.setItem(i, 1, QTableWidgetItem("Yes" if info.get("healthy") else "No"))
                self.tbl.setItem(i, 2, QTableWidgetItem(f"{info.get('load',0)*100:.0f}%"))
                self.tbl.setItem(i, 3, QTableWidgetItem(", ".join(info.get("languages", [])[:12])))
            self.lbl_status.setText("Healthy")
        self.pool.submit(work).add_done_callback(lambda f: QApplication.instance().postEvent(self, _CallableEvent(lambda: done(f))))

    def _click_sync(self) -> None:
        text = self.txt_text.toPlainText().strip()
        language = self.cmb_lang.text().strip() or "en"
        quality = self.cmb_quality.currentText()
        self._set_busy(True)
        self.progress.setValue(0)
        self.lbl_status.setText("Generating (sync)…")

        def work():
            r = requests.post(
                f"{self.base_url}/tts",
                json={"text": text, "language": language, "quality": quality, "mode": "sync", "voice_profile": {}, "params": {"sample_rate": 22050}},
                timeout=120,
            )
            r.raise_for_status()
            return r.json()
        def done(fut):
            self._set_busy(False)
            try:
                js = fut.result()
                b64 = js.get("result_b64_wav")
                if b64:
                    p = self._save_wav(b64)
                    self._play_wav(p)
                    self.lbl_status.setText(f"Engine: {js.get('engine')} (sync)")
                else:
                    self.lbl_status.setText("No audio returned")
            except Exception as e:
                self.lbl_status.setText(f"Sync error: {e}")
        self.pool.submit(work).add_done_callback(lambda f: QApplication.instance().postEvent(self, _CallableEvent(lambda: done(f))))

    def _click_async(self) -> None:
        text = self.txt_text.toPlainText().strip()
        language = self.cmb_lang.text().strip() or "en"
        quality = self.cmb_quality.currentText()
        self._set_busy(True)
        self.progress.setValue(0)
        self.lbl_status.setText("Submitting async…")

        def submit_work():
            r = requests.post(
                f"{self.base_url}/tts_async",
                json={"text": text, "language": language, "quality": quality, "voice_profile": {}, "params": {"sample_rate": 22050}},
                timeout=30,
            )
            r.raise_for_status()
            return r.json()

        def after_submit(fut):
            try:
                js = fut.result(); job_id = js.get("job_id")
            except Exception as e:
                self._set_busy(False)
                self.lbl_status.setText(f"Submit error: {e}")
                return
            self.lbl_status.setText(f"Job {job_id}: queued")
            # start polling
            self._poll_job(job_id)

        self.pool.submit(submit_work).add_done_callback(lambda f: QApplication.instance().postEvent(self, _CallableEvent(lambda: after_submit(f))))

    def _poll_job(self, job_id: str) -> None:
        def poll_once():
            try:
                r = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=10)
                r.raise_for_status()
                return r.json()
            except Exception as e:
                return {"status": "error", "error": str(e)}

        def handle(js):
            st = js.get("status", "error")
            if st == "running":
                prog = float(js.get("progress", 0))
                self.progress.setValue(int(prog * 100))
                self.lbl_status.setText(f"Job {job_id}: running {int(prog*100)}%")
            elif st == "queued":
                self.lbl_status.setText(f"Job {job_id}: queued")
            elif st == "done":
                self.progress.setValue(100)
                self._set_busy(False)
                b64 = js.get("result_b64_wav")
                if b64:
                    p = self._save_wav(b64)
                    self._play_wav(p)
                    self.lbl_status.setText(f"Job {job_id}: done (engine {js.get('engine')})")
                else:
                    self.lbl_status.setText(f"Job {job_id}: done (no audio)")
                return True
            else:  # error
                self._set_busy(False)
                self.lbl_status.setText(f"Job {job_id}: error — {js.get('error')}")
                return True
            return False

        def loop():
            # poll until finished
            while True:
                js = poll_once()
                finished = [False]
                def _apply():
                    finished[0] = handle(js)
                QApplication.instance().postEvent(self, _CallableEvent(_apply))
                if finished[0]:
                    break
                time.sleep(0.5)

        threading.Thread(target=loop, daemon=True).start()


# ---- Qt helper to marshal thread callbacks back to UI thread ----
from PySide6.QtCore import QEvent, QObject
class _CallableEvent(QEvent):
    _TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, cb):
        super().__init__(self._TYPE)
        self.cb = cb
class _EventSink(QObject):
    def event(self, e):
        if isinstance(e, _CallableEvent):
            try:
                e.cb()
            except Exception:
                pass
            return True
        return super().event(e)

# Ensure a sink is installed for postEvent above
_s = _EventSink()
