#!/usr/bin/env python3
"""
VoiceStudio Real-Time Audio Visualization System
High-performance audio visualization using PyQtGraph with modern UI/UX design.
Integrated with VoiceStudio's voice cloning and audio processing capabilities.
"""

import sys
import numpy as np
import pyqtgraph as pg
import sounddevice as sd
import librosa
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QGridLayout, QLabel, QPushButton,
                            QSlider, QComboBox, QCheckBox, QGroupBox, QFrame,
                            QProgressBar, QTextEdit, QTabWidget, QSplitter)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from typing import Dict, List, Optional, Tuple
import json
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor(QThread):
    """Audio processing thread for real-time analysis"""

    # Signals for different audio features
    waveform_updated = pyqtSignal(np.ndarray)
    spectrum_updated = pyqtSignal(np.ndarray, np.ndarray)  # frequencies, magnitudes
    spectrogram_updated = pyqtSignal(np.ndarray)
    pitch_updated = pyqtSignal(float)
    volume_updated = pyqtSignal(float)

    def __init__(self, sample_rate=44100, chunk_size=1024):
        super().__init__()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.running = False
        self.audio_buffer = np.array([])
        self.spectrogram_buffer = []
        self.max_spectrogram_frames = 100

        # Audio processing parameters
        self.window_size = 2048
        self.hop_length = 512

    def start_processing(self):
        """Start audio processing"""
        self.running = True
        self.start()

    def stop_processing(self):
        """Stop audio processing"""
        self.running = False
        self.wait()

    def run(self):
        """Main processing loop"""
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")

            # Convert to mono if stereo
            if indata.shape[1] > 1:
                audio_data = np.mean(indata, axis=1)
            else:
                audio_data = indata.flatten()

            # Update audio buffer
            self.audio_buffer = np.concatenate([self.audio_buffer, audio_data])
            if len(self.audio_buffer) > self.sample_rate * 2:  # Keep 2 seconds
                self.audio_buffer = self.audio_buffer[-self.sample_rate * 2:]

            # Process audio features
            self._process_audio_features(audio_data)

        # Start audio stream
        try:
            with sd.InputStream(callback=audio_callback,
                              channels=1,
                              samplerate=self.sample_rate,
                              blocksize=self.chunk_size):
                while self.running:
                    time.sleep(0.01)  # Small delay to prevent excessive CPU usage
        except Exception as e:
            logger.error(f"Audio processing error: {e}")

    def _process_audio_features(self, audio_data):
        """Process audio data and extract features"""
        try:
            # Waveform
            self.waveform_updated.emit(audio_data)

            # Volume/RMS
            rms = np.sqrt(np.mean(audio_data**2))
            self.volume_updated.emit(rms)

            # Frequency spectrum
            if len(audio_data) >= self.window_size:
                # Apply window function
                windowed = audio_data[:self.window_size] * np.hanning(self.window_size)

                # FFT
                fft = np.fft.fft(windowed)
                freqs = np.fft.fftfreq(self.window_size, 1/self.sample_rate)
                magnitudes = np.abs(fft[:self.window_size//2])
                freqs = freqs[:self.window_size//2]

                self.spectrum_updated.emit(freqs, magnitudes)

                # Pitch estimation (simplified)
                pitch = self._estimate_pitch(audio_data)
                if pitch > 0:
                    self.pitch_updated.emit(pitch)

            # Spectrogram
            if len(self.audio_buffer) >= self.window_size:
                spectrogram_frame = self._compute_spectrogram_frame()
                if spectrogram_frame is not None:
                    self.spectrogram_buffer.append(spectrogram_frame)
                    if len(self.spectrogram_buffer) > self.max_spectrogram_frames:
                        self.spectrogram_buffer.pop(0)

                    spectrogram = np.array(self.spectrogram_buffer).T
                    self.spectrogram_updated.emit(spectrogram)

        except Exception as e:
            logger.error(f"Feature processing error: {e}")

    def _estimate_pitch(self, audio_data):
        """Estimate fundamental frequency"""
        try:
            # Simple autocorrelation-based pitch estimation
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]

            # Find peaks
            peaks = []
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append(i)

            if peaks:
                # Find the first significant peak (fundamental frequency)
                for peak in peaks[1:]:  # Skip DC component
                    if peak > 20 and peak < len(autocorr) // 4:  # Reasonable frequency range
                        return self.sample_rate / peak

            return 0
        except:
            return 0

    def _compute_spectrogram_frame(self):
        """Compute a single spectrogram frame"""
        try:
            if len(self.audio_buffer) < self.window_size:
                return None

            # Take the most recent window
            window = self.audio_buffer[-self.window_size:]
            windowed = window * np.hanning(self.window_size)

            # FFT
            fft = np.fft.fft(windowed)
            magnitudes = np.abs(fft[:self.window_size//2])

            return magnitudes
        except:
            return None

class ModernAudioVisualizer(QMainWindow):
    """Modern audio visualizer with PyQtGraph and contemporary UI design"""

    def __init__(self):
        super().__init__()
        self.audio_processor = AudioProcessor()
        self.setup_ui()
        self.setup_connections()
        self.setup_styling()

        # Visualization data
        self.waveform_data = np.array([])
        self.spectrum_data = (np.array([]), np.array([]))
        self.spectrogram_data = np.array([])
        self.pitch_history = []
        self.volume_history = []

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_visualizations)
        self.update_timer.start(50)  # 20 FPS

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("VoiceStudio - Real-Time Audio Visualizer")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Controls
        self.setup_control_panel(splitter)

        # Right panel - Visualizations
        self.setup_visualization_panel(splitter)

        # Set splitter proportions
        splitter.setSizes([300, 1100])

    def setup_control_panel(self, parent):
        """Setup control panel"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # Audio controls group
        audio_group = QGroupBox("Audio Controls")
        audio_layout = QVBoxLayout(audio_group)

        # Start/Stop button
        self.start_button = QPushButton("🎤 Start Recording")
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45a049, stop:1 #3d8b40);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d8b40, stop:1 #357a38);
            }
        """)
        audio_layout.addWidget(self.start_button)

        # Sample rate selection
        sample_rate_layout = QHBoxLayout()
        sample_rate_layout.addWidget(QLabel("Sample Rate:"))
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["22050", "44100", "48000"])
        self.sample_rate_combo.setCurrentText("44100")
        sample_rate_layout.addWidget(self.sample_rate_combo)
        audio_layout.addLayout(sample_rate_layout)

        # Chunk size selection
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size:"))
        self.chunk_size_combo = QComboBox()
        self.chunk_size_combo.addItems(["512", "1024", "2048", "4096"])
        self.chunk_size_combo.setCurrentText("1024")
        chunk_layout.addWidget(self.chunk_size_combo)
        audio_layout.addLayout(chunk_layout)

        control_layout.addWidget(audio_group)

        # Visualization controls group
        viz_group = QGroupBox("Visualization Controls")
        viz_layout = QVBoxLayout(viz_group)

        # Visualization type
        viz_type_layout = QHBoxLayout()
        viz_type_layout.addWidget(QLabel("Type:"))
        self.viz_type_combo = QComboBox()
        self.viz_type_combo.addItems(["Waveform", "Spectrum", "Spectrogram", "All"])
        self.viz_type_combo.setCurrentText("All")
        viz_type_layout.addWidget(self.viz_type_combo)
        viz_layout.addLayout(viz_type_layout)

        # Color scheme
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Colors:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Rainbow", "Fire", "Ocean", "Neon", "Classic"])
        self.color_combo.setCurrentText("Rainbow")
        color_layout.addWidget(self.color_combo)
        viz_layout.addLayout(color_layout)

        # Smoothing
        smooth_layout = QHBoxLayout()
        smooth_layout.addWidget(QLabel("Smoothing:"))
        self.smoothing_slider = QSlider(Qt.Horizontal)
        self.smoothing_slider.setRange(0, 10)
        self.smoothing_slider.setValue(3)
        smooth_layout.addWidget(self.smoothing_slider)
        viz_layout.addLayout(smooth_layout)

        control_layout.addWidget(viz_group)

        # Audio analysis group
        analysis_group = QGroupBox("Audio Analysis")
        analysis_layout = QVBoxLayout(analysis_group)

        # Real-time metrics
        self.pitch_label = QLabel("Pitch: -- Hz")
        self.pitch_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        analysis_layout.addWidget(self.pitch_label)

        self.volume_label = QLabel("Volume: -- dB")
        self.volume_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF9800;")
        analysis_layout.addWidget(self.volume_label)

        # Volume meter
        self.volume_meter = QProgressBar()
        self.volume_meter.setRange(0, 100)
        self.volume_meter.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                text-align: center;
                background: #222;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.7 #FFC107, stop:1 #F44336);
                border-radius: 3px;
            }
        """)
        analysis_layout.addWidget(self.volume_meter)

        control_layout.addWidget(analysis_group)

        # Voice cloning integration group
        cloning_group = QGroupBox("Voice Cloning Integration")
        cloning_layout = QVBoxLayout(cloning_group)

        self.record_clone_button = QPushButton("🎯 Record for Cloning")
        self.record_clone_button.setMinimumHeight(40)
        self.record_clone_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9C27B0, stop:1 #7B1FA2);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7B1FA2, stop:1 #6A1B9A);
            }
        """)
        cloning_layout.addWidget(self.record_clone_button)

        self.analyze_button = QPushButton("🔍 Analyze Voice Profile")
        self.analyze_button.setMinimumHeight(40)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF5722, stop:1 #E64A19);
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E64A19, stop:1 #D84315);
            }
        """)
        cloning_layout.addWidget(self.analyze_button)

        control_layout.addWidget(cloning_group)

        # Status and info
        status_group = QGroupBox("Status & Info")
        status_layout = QVBoxLayout(status_group)

        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.status_text)

        control_layout.addWidget(status_group)

        # Add stretch to push everything to top
        control_layout.addStretch()

        parent.addWidget(control_widget)

    def setup_visualization_panel(self, parent):
        """Setup visualization panel"""
        viz_widget = QWidget()
        viz_layout = QVBoxLayout(viz_widget)

        # Create tab widget for different visualization modes
        self.viz_tabs = QTabWidget()
        viz_layout.addWidget(self.viz_tabs)

        # Waveform tab
        self.setup_waveform_tab()

        # Spectrum tab
        self.setup_spectrum_tab()

        # Spectrogram tab
        self.setup_spectrogram_tab()

        # Combined tab
        self.setup_combined_tab()

        parent.addWidget(viz_widget)

    def setup_waveform_tab(self):
        """Setup waveform visualization tab"""
        waveform_widget = QWidget()
        layout = QVBoxLayout(waveform_widget)

        # Create PyQtGraph widget
        self.waveform_plot = pg.PlotWidget()
        self.waveform_plot.setLabel('left', 'Amplitude')
        self.waveform_plot.setLabel('bottom', 'Time', units='s')
        self.waveform_plot.setTitle('Real-Time Waveform')
        self.waveform_plot.showGrid(x=True, y=True)

        # Set up waveform curve
        self.waveform_curve = self.waveform_plot.plot(pen=pg.mkPen('cyan', width=2))

        layout.addWidget(self.waveform_plot)
        self.viz_tabs.addTab(waveform_widget, "🌊 Waveform")

    def setup_spectrum_tab(self):
        """Setup spectrum visualization tab"""
        spectrum_widget = QWidget()
        layout = QVBoxLayout(spectrum_widget)

        # Create PyQtGraph widget
        self.spectrum_plot = pg.PlotWidget()
        self.spectrum_plot.setLabel('left', 'Magnitude', units='dB')
        self.spectrum_plot.setLabel('bottom', 'Frequency', units='Hz')
        self.spectrum_plot.setTitle('Frequency Spectrum')
        self.spectrum_plot.showGrid(x=True, y=True)
        self.spectrum_plot.setLogMode(x=True, y=False)

        # Set up spectrum curve
        self.spectrum_curve = self.spectrum_plot.plot(pen=pg.mkPen('yellow', width=2))

        layout.addWidget(self.spectrum_plot)
        self.viz_tabs.addTab(spectrum_widget, "📊 Spectrum")

    def setup_spectrogram_tab(self):
        """Setup spectrogram visualization tab"""
        spectrogram_widget = QWidget()
        layout = QVBoxLayout(spectrogram_widget)

        # Create PyQtGraph ImageView for spectrogram
        self.spectrogram_view = pg.ImageView()
        self.spectrogram_view.setTitle('Real-Time Spectrogram')

        layout.addWidget(self.spectrogram_view)
        self.viz_tabs.addTab(spectrogram_widget, "🎵 Spectrogram")

    def setup_combined_tab(self):
        """Setup combined visualization tab"""
        combined_widget = QWidget()
        layout = QGridLayout(combined_widget)

        # Waveform (top)
        self.combined_waveform = pg.PlotWidget()
        self.combined_waveform.setLabel('left', 'Amplitude')
        self.combined_waveform.setLabel('bottom', 'Time', units='s')
        self.combined_waveform.setTitle('Waveform')
        self.combined_waveform.showGrid(x=True, y=True)
        self.combined_waveform_curve = self.combined_waveform.plot(pen=pg.mkPen('cyan', width=1))
        layout.addWidget(self.combined_waveform, 0, 0)

        # Spectrum (top right)
        self.combined_spectrum = pg.PlotWidget()
        self.combined_spectrum.setLabel('left', 'Magnitude', units='dB')
        self.combined_spectrum.setLabel('bottom', 'Frequency', units='Hz')
        self.combined_spectrum.setTitle('Spectrum')
        self.combined_spectrum.showGrid(x=True, y=True)
        self.combined_spectrum.setLogMode(x=True, y=False)
        self.combined_spectrum_curve = self.combined_spectrum.plot(pen=pg.mkPen('yellow', width=1))
        layout.addWidget(self.combined_spectrum, 0, 1)

        # Spectrogram (bottom, spanning both columns)
        self.combined_spectrogram = pg.ImageView()
        self.combined_spectrogram.setTitle('Spectrogram')
        layout.addWidget(self.combined_spectrogram, 1, 0, 1, 2)

        self.viz_tabs.addTab(combined_widget, "🎯 Combined")

    def setup_connections(self):
        """Setup signal connections"""
        # Audio processor signals
        self.audio_processor.waveform_updated.connect(self.update_waveform)
        self.audio_processor.spectrum_updated.connect(self.update_spectrum)
        self.audio_processor.spectrogram_updated.connect(self.update_spectrogram)
        self.audio_processor.pitch_updated.connect(self.update_pitch)
        self.audio_processor.volume_updated.connect(self.update_volume)

        # UI controls
        self.start_button.clicked.connect(self.toggle_recording)
        self.record_clone_button.clicked.connect(self.start_voice_cloning_recording)
        self.analyze_button.clicked.connect(self.analyze_voice_profile)

    def setup_styling(self):
        """Setup modern styling"""
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: rgba(255, 255, 255, 0.05);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox {
                background: #333;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #555;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2a2a2a;
            }
            QTabBar::tab {
                background: #333;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
            }
        """)

        # Configure PyQtGraph styling
        pg.setConfigOptions(antialias=True, background='#1a1a1a', foreground='#ffffff')

    def toggle_recording(self):
        """Toggle audio recording"""
        if not self.audio_processor.running:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start audio recording"""
        try:
            # Update sample rate and chunk size
            self.audio_processor.sample_rate = int(self.sample_rate_combo.currentText())
            self.audio_processor.chunk_size = int(self.chunk_size_combo.currentText())

            # Start processing
            self.audio_processor.start_processing()

            # Update UI
            self.start_button.setText("⏹️ Stop Recording")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #F44336, stop:1 #D32F2F);
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #D32F2F, stop:1 #B71C1C);
                }
            """)

            self.log_status("🎤 Recording started")

        except Exception as e:
            self.log_status(f"❌ Failed to start recording: {e}")

    def stop_recording(self):
        """Stop audio recording"""
        try:
            self.audio_processor.stop_processing()

            # Update UI
            self.start_button.setText("🎤 Start Recording")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #3d8b40);
                }
            """)

            self.log_status("⏹️ Recording stopped")

        except Exception as e:
            self.log_status(f"❌ Failed to stop recording: {e}")

    def start_voice_cloning_recording(self):
        """Start recording for voice cloning"""
        self.log_status("🎯 Starting voice cloning recording...")
        # This would integrate with the voice cloning service
        # For now, just log the action

    def analyze_voice_profile(self):
        """Analyze voice profile"""
        self.log_status("🔍 Analyzing voice profile...")
        # This would integrate with the voice cloning service
        # For now, just log the action

    def update_waveform(self, data):
        """Update waveform visualization"""
        self.waveform_data = data

    def update_spectrum(self, freqs, magnitudes):
        """Update spectrum visualization"""
        self.spectrum_data = (freqs, magnitudes)

    def update_spectrogram(self, spectrogram):
        """Update spectrogram visualization"""
        self.spectrogram_data = spectrogram

    def update_pitch(self, pitch):
        """Update pitch display"""
        self.pitch_label.setText(f"Pitch: {pitch:.1f} Hz")
        self.pitch_history.append(pitch)
        if len(self.pitch_history) > 100:
            self.pitch_history.pop(0)

    def update_volume(self, volume):
        """Update volume display"""
        volume_db = 20 * np.log10(volume + 1e-10)  # Convert to dB
        self.volume_label.setText(f"Volume: {volume_db:.1f} dB")

        # Update volume meter
        volume_percent = min(100, max(0, volume_db + 60))  # Scale to 0-100
        self.volume_meter.setValue(int(volume_percent))

        self.volume_history.append(volume_db)
        if len(self.volume_history) > 100:
            self.volume_history.pop(0)

    def update_visualizations(self):
        """Update all visualizations"""
        try:
            # Update waveform
            if len(self.waveform_data) > 0:
                time_axis = np.linspace(0, len(self.waveform_data) / self.audio_processor.sample_rate,
                                      len(self.waveform_data))
                self.waveform_curve.setData(time_axis, self.waveform_data)
                self.combined_waveform_curve.setData(time_axis, self.waveform_data)

            # Update spectrum
            if len(self.spectrum_data[0]) > 0:
                freqs, magnitudes = self.spectrum_data
                # Convert to dB
                magnitudes_db = 20 * np.log10(magnitudes + 1e-10)
                self.spectrum_curve.setData(freqs, magnitudes_db)
                self.combined_spectrum_curve.setData(freqs, magnitudes_db)

            # Update spectrogram
            if len(self.spectrogram_data) > 0:
                # Apply colormap based on selection
                colormap = self.get_colormap()
                self.spectrogram_view.setImage(self.spectrogram_data,
                                             colormap=colormap)
                self.combined_spectrogram.setImage(self.spectrogram_data,
                                                 colormap=colormap)

        except Exception as e:
            logger.error(f"Visualization update error: {e}")

    def get_colormap(self):
        """Get colormap based on user selection"""
        color_scheme = self.color_combo.currentText()

        if color_scheme == "Rainbow":
            return pg.colormap.get('viridis')
        elif color_scheme == "Fire":
            return pg.colormap.get('hot')
        elif color_scheme == "Ocean":
            return pg.colormap.get('plasma')
        elif color_scheme == "Neon":
            return pg.colormap.get('inferno')
        else:  # Classic
            return pg.colormap.get('gray')

    def log_status(self, message):
        """Log status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Handle application close"""
        self.audio_processor.stop_processing()
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("VoiceStudio Audio Visualizer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("VoiceStudio")

    # Create and show main window
    window = ModernAudioVisualizer()
    window.show()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
