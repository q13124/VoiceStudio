#!/usr/bin/env python3
"""
VoiceStudio Advanced MIDI Editor
Professional MIDI editing with piano roll, step sequencer, and advanced tools.
"""

import sys
import os
import time
import logging
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QGridLayout, QLabel, QPushButton, QSlider, QComboBox,
                            QCheckBox, QGroupBox, QFrame, QScrollArea, QSpinBox,
                            QDoubleSpinBox, QLineEdit, QListWidget, QListWidgetItem,
                            QMenu, QAction, QFileDialog, QMessageBox, QSplitter)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QBrush
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MIDINote:
    """MIDI note representation"""
    def __init__(self, note: int, velocity: int, start_time: float, duration: float, channel: int = 0):
        self.note = note
        self.velocity = velocity
        self.start_time = start_time
        self.duration = duration
        self.channel = channel
        self.selected = False

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "note": self.note,
            "velocity": self.velocity,
            "start_time": self.start_time,
            "duration": self.duration,
            "channel": self.channel
        }

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        note = cls(data["note"], data["velocity"], data["start_time"], data["duration"], data["channel"])
        return note

class PianoRollWidget(QWidget):
    """Professional piano roll widget"""

    note_selected = pyqtSignal(object)
    note_moved = pyqtSignal(object, float, float)
    note_resized = pyqtSignal(object, float)

    def __init__(self):
        super().__init__()
        self.notes = []
        self.selected_notes = []
        self.zoom_x = 1.0
        self.zoom_y = 1.0
        self.scroll_x = 0.0
        self.scroll_y = 0.0
        self.grid_size = 0.25  # Quarter note grid
        self.snap_to_grid = True
        self.tempo = 120.0
        self.time_signature = (4, 4)

        # Piano keys
        self.piano_keys = self._generate_piano_keys()

        # Mouse interaction
        self.dragging = False
        self.drag_start = QPoint()
        self.drag_note = None
        self.resize_handle = None

        self.setup_ui()

    def setup_ui(self):
        """Setup piano roll UI"""
        self.setMinimumSize(800, 400)
        self.setMouseTracking(True)

    def _generate_piano_keys(self) -> List[Dict[str, Any]]:
        """Generate piano key information"""
        keys = []
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        for octave in range(11):  # C0 to B10
            for note_idx, note_name in enumerate(note_names):
                midi_note = octave * 12 + note_idx
                is_black = note_name.endswith('#')

                keys.append({
                    'midi_note': midi_note,
                    'name': f"{note_name}{octave}",
                    'is_black': is_black,
                    'rect': QRect()  # Will be set in paintEvent
                })

        return keys

    def add_note(self, note: MIDINote):
        """Add note to piano roll"""
        self.notes.append(note)
        self.update()

    def remove_note(self, note: MIDINote):
        """Remove note from piano roll"""
        if note in self.notes:
            self.notes.remove(note)
        if note in self.selected_notes:
            self.selected_notes.remove(note)
        self.update()

    def clear_notes(self):
        """Clear all notes"""
        self.notes.clear()
        self.selected_notes.clear()
        self.update()

    def set_notes(self, notes: List[MIDINote]):
        """Set notes list"""
        self.notes = notes.copy()
        self.selected_notes.clear()
        self.update()

    def paintEvent(self, event):
        """Paint piano roll"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Calculate key height
        key_height = 20
        visible_keys = height // key_height

        # Paint background
        painter.fillRect(0, 0, width, height, QColor(40, 40, 40))

        # Paint piano keys
        self._paint_piano_keys(painter, key_height, visible_keys)

        # Paint grid
        self._paint_grid(painter, width, height, key_height, visible_keys)

        # Paint notes
        self._paint_notes(painter, width, height, key_height, visible_keys)

        # Paint selection rectangle
        if self.dragging and self.drag_start:
            self._paint_selection_rectangle(painter)

    def _paint_piano_keys(self, painter: QPainter, key_height: int, visible_keys: int):
        """Paint piano keys"""
        # Calculate which keys are visible
        start_key = max(0, int(self.scroll_y // key_height))
        end_key = min(len(self.piano_keys), start_key + visible_keys)

        for i in range(start_key, end_key):
            key = self.piano_keys[i]
            y = i * key_height - self.scroll_y

            if y + key_height > 0 and y < self.height():
                # Set key color
                if key['is_black']:
                    color = QColor(60, 60, 60)
                else:
                    color = QColor(220, 220, 220)

                painter.fillRect(0, y, 60, key_height, color)

                # Draw key border
                painter.setPen(QPen(QColor(100, 100, 100), 1))
                painter.drawRect(0, y, 60, key_height)

                # Draw note name
                painter.setPen(QPen(QColor(0, 0, 0) if not key['is_black'] else QColor(255, 255, 255), 1))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(5, y + key_height - 5, key['name'])

                # Store key rect for hit testing
                key['rect'] = QRect(0, y, 60, key_height)

    def _paint_grid(self, painter: QPainter, width: int, height: int, key_height: int, visible_keys: int):
        """Paint grid lines"""
        painter.setPen(QPen(QColor(80, 80, 80), 1))

        # Vertical grid lines
        pixels_per_beat = 100 * self.zoom_x
        beat_width = pixels_per_beat

        start_x = int(self.scroll_x // beat_width) * beat_width - self.scroll_x
        for x in range(start_x, width, int(beat_width)):
            if x >= 60:  # Don't draw over piano keys
                painter.drawLine(x, 0, x, height)

        # Horizontal grid lines (between keys)
        for i in range(visible_keys + 1):
            y = i * key_height - self.scroll_y
            if y >= 0 and y <= height:
                painter.drawLine(60, y, width, y)

    def _paint_notes(self, painter: QPainter, width: int, height: int, key_height: int, visible_keys: int):
        """Paint MIDI notes"""
        pixels_per_beat = 100 * self.zoom_x

        for note in self.notes:
            # Calculate note position
            note_x = 60 + note.start_time * pixels_per_beat - self.scroll_x
            note_width = note.duration * pixels_per_beat

            # Find key index for this note
            key_index = None
            for i, key in enumerate(self.piano_keys):
                if key['midi_note'] == note.note:
                    key_index = i
                    break

            if key_index is None:
                continue

            note_y = key_index * key_height - self.scroll_y

            # Check if note is visible
            if note_x + note_width < 60 or note_x > width or note_y + key_height < 0 or note_y > height:
                continue

            # Set note color based on velocity and selection
            if note in self.selected_notes:
                color = QColor(255, 200, 0)  # Orange for selected
            else:
                # Color based on velocity
                velocity_factor = note.velocity / 127.0
                color = QColor(int(100 + velocity_factor * 155),
                             int(100 + velocity_factor * 155),
                             255)

            # Draw note rectangle
            painter.fillRect(note_x, note_y, note_width, key_height - 1, color)

            # Draw note border
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawRect(note_x, note_y, note_width, key_height - 1)

            # Draw velocity indicator
            if note_width > 20:
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.setFont(QFont("Arial", 8))
                painter.drawText(note_x + 2, note_y + key_height - 5, str(note.velocity))

    def _paint_selection_rectangle(self, painter: QPainter):
        """Paint selection rectangle"""
        if not self.dragging:
            return

        current_pos = self.mapFromGlobal(self.cursor().pos())
        rect = QRect(self.drag_start, current_pos).normalized()

        painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.DashLine))
        painter.setBrush(QBrush(QColor(255, 255, 255, 50)))
        painter.drawRect(rect)

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()

            # Check if clicking on a note
            clicked_note = self._get_note_at_position(event.pos())

            if clicked_note:
                if not (event.modifiers() & Qt.ControlModifier):
                    self.selected_notes.clear()
                self.selected_notes.append(clicked_note)
                clicked_note.selected = True
                self.drag_note = clicked_note
                self.note_selected.emit(clicked_note)
            else:
                # Start selection rectangle
                if not (event.modifiers() & Qt.ControlModifier):
                    self.selected_notes.clear()
                    for note in self.notes:
                        note.selected = False

            self.update()

    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.dragging:
            if self.drag_note:
                # Move note
                self._move_note(self.drag_note, event.pos())
            else:
                # Update selection rectangle
                self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

            if self.drag_note:
                self.drag_note = None
            else:
                # Finalize selection
                self._finalize_selection(event.pos())

            self.update()

    def _get_note_at_position(self, pos: QPoint) -> Optional[MIDINote]:
        """Get note at mouse position"""
        pixels_per_beat = 100 * self.zoom_x
        key_height = 20

        for note in self.notes:
            note_x = 60 + note.start_time * pixels_per_beat - self.scroll_x
            note_width = note.duration * pixels_per_beat

            # Find key index
            key_index = None
            for i, key in enumerate(self.piano_keys):
                if key['midi_note'] == note.note:
                    key_index = i
                    break

            if key_index is None:
                continue

            note_y = key_index * key_height - self.scroll_y

            # Check if position is within note
            if (note_x <= pos.x() <= note_x + note_width and
                note_y <= pos.y() <= note_y + key_height):
                return note

        return None

    def _move_note(self, note: MIDINote, pos: QPoint):
        """Move note to new position"""
        pixels_per_beat = 100 * self.zoom_x
        key_height = 20

        # Calculate new time
        new_time = (pos.x() - 60 + self.scroll_x) / pixels_per_beat

        # Snap to grid
        if self.snap_to_grid:
            new_time = round(new_time / self.grid_size) * self.grid_size

        # Calculate new note number
        key_index = int((pos.y() + self.scroll_y) // key_height)
        if 0 <= key_index < len(self.piano_keys):
            new_note = self.piano_keys[key_index]['midi_note']

            # Update note
            old_time = note.start_time
            old_note = note.note

            note.start_time = max(0, new_time)
            note.note = new_note

            self.note_moved.emit(note, old_time, old_note)

    def _finalize_selection(self, pos: QPoint):
        """Finalize selection rectangle"""
        rect = QRect(self.drag_start, pos).normalized()
        pixels_per_beat = 100 * self.zoom_x
        key_height = 20

        # Select notes within rectangle
        for note in self.notes:
            note_x = 60 + note.start_time * pixels_per_beat - self.scroll_x
            note_width = note.duration * pixels_per_beat

            # Find key index
            key_index = None
            for i, key in enumerate(self.piano_keys):
                if key['midi_note'] == note.note:
                    key_index = i
                    break

            if key_index is None:
                continue

            note_y = key_index * key_height - self.scroll_y

            # Check if note is within selection rectangle
            note_rect = QRect(note_x, note_y, note_width, key_height)
            if rect.intersects(note_rect):
                if note not in self.selected_notes:
                    self.selected_notes.append(note)
                    note.selected = True

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            delta = event.angleDelta().y()
            zoom_factor = 1.1 if delta > 0 else 0.9

            self.zoom_x *= zoom_factor
            self.zoom_x = max(0.1, min(10.0, self.zoom_x))

            self.update()
        else:
            # Scroll
            delta = event.angleDelta().y()
            self.scroll_y -= delta * 0.1
            self.scroll_y = max(0, self.scroll_y)

            self.update()

    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == Qt.Key_Delete:
            # Delete selected notes
            for note in self.selected_notes:
                self.remove_note(note)
        elif event.key() == Qt.Key_A and event.modifiers() & Qt.ControlModifier:
            # Select all notes
            self.selected_notes = self.notes.copy()
            for note in self.notes:
                note.selected = True
            self.update()
        elif event.key() == Qt.Key_D and event.modifiers() & Qt.ControlModifier:
            # Deselect all notes
            self.selected_notes.clear()
            for note in self.notes:
                note.selected = False
            self.update()

class StepSequencerWidget(QWidget):
    """Step sequencer widget"""

    def __init__(self):
        super().__init__()
        self.steps = 16
        self.step_data = {}  # step -> note -> velocity
        self.current_step = 0
        self.is_playing = False
        self.tempo = 120.0

        self.setup_ui()

    def setup_ui(self):
        """Setup step sequencer UI"""
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶")
        self.play_button.setCheckable(True)
        self.play_button.setMaximumSize(40, 40)
        self.play_button.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:checked {
                background: #45a049;
            }
        """)
        self.play_button.toggled.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("⏹")
        self.stop_button.setMaximumSize(40, 40)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background: #F44336;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #D32F2F;
            }
        """)
        self.stop_button.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_button)

        controls_layout.addStretch()

        # Tempo control
        tempo_layout = QHBoxLayout()
        tempo_layout.addWidget(QLabel("Tempo:"))
        self.tempo_spinbox = QSpinBox()
        self.tempo_spinbox.setRange(60, 200)
        self.tempo_spinbox.setValue(int(self.tempo))
        self.tempo_spinbox.valueChanged.connect(self.update_tempo)
        tempo_layout.addWidget(self.tempo_spinbox)
        controls_layout.addLayout(tempo_layout)

        layout.addLayout(controls_layout)

        # Step grid
        self.step_grid = QWidget()
        self.step_layout = QGridLayout(self.step_grid)

        # Create step buttons
        self.step_buttons = []
        for step in range(self.steps):
            step_button = QPushButton(str(step + 1))
            step_button.setCheckable(True)
            step_button.setMaximumSize(30, 30)
            step_button.setStyleSheet("""
                QPushButton {
                    background: #333;
                    border: 1px solid #555;
                    border-radius: 3px;
                    color: white;
                }
                QPushButton:checked {
                    background: #4CAF50;
                }
            """)
            step_button.toggled.connect(lambda checked, s=step: self.toggle_step(s))
            self.step_buttons.append(step_button)
            self.step_layout.addWidget(step_button, 0, step)

        layout.addWidget(self.step_grid)

        # Playback timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.advance_step)

    def toggle_playback(self, playing):
        """Toggle playback"""
        self.is_playing = playing
        if playing:
            self.playback_timer.start(int(60000 / (self.tempo * 4)))  # 16th notes
        else:
            self.playback_timer.stop()

    def stop_playback(self):
        """Stop playback"""
        self.is_playing = False
        self.playback_timer.stop()
        self.current_step = 0
        self.update_step_indicators()

    def update_tempo(self, tempo):
        """Update tempo"""
        self.tempo = tempo
        if self.is_playing:
            self.playback_timer.start(int(60000 / (self.tempo * 4)))

    def advance_step(self):
        """Advance to next step"""
        self.current_step = (self.current_step + 1) % self.steps
        self.update_step_indicators()

    def update_step_indicators(self):
        """Update step indicators"""
        for i, button in enumerate(self.step_buttons):
            if i == self.current_step and self.is_playing:
                button.setStyleSheet("""
                    QPushButton {
                        background: #FF9800;
                        border: 1px solid #555;
                        border-radius: 3px;
                        color: white;
                    }
                """)
            elif button.isChecked():
                button.setStyleSheet("""
                    QPushButton {
                        background: #4CAF50;
                        border: 1px solid #555;
                        border-radius: 3px;
                        color: white;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background: #333;
                        border: 1px solid #555;
                        border-radius: 3px;
                        color: white;
                    }
                """)

    def toggle_step(self, step):
        """Toggle step on/off"""
        if step not in self.step_data:
            self.step_data[step] = {}

        # For now, just toggle a default note
        if 60 in self.step_data[step]:
            del self.step_data[step][60]
        else:
            self.step_data[step][60] = 80  # Default velocity

class MIDIEditorWidget(QWidget):
    """Main MIDI editor widget"""

    def __init__(self):
        super().__init__()
        self.notes = []
        self.setup_ui()

    def setup_ui(self):
        """Setup MIDI editor UI"""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        # Tools
        self.select_tool_button = QPushButton("Select")
        self.select_tool_button.setCheckable(True)
        self.select_tool_button.setChecked(True)
        toolbar_layout.addWidget(self.select_tool_button)

        self.draw_tool_button = QPushButton("Draw")
        self.draw_tool_button.setCheckable(True)
        toolbar_layout.addWidget(self.draw_tool_button)

        self.erase_tool_button = QPushButton("Erase")
        self.erase_tool_button.setCheckable(True)
        toolbar_layout.addWidget(self.erase_tool_button)

        toolbar_layout.addStretch()

        # Grid controls
        grid_layout = QHBoxLayout()
        grid_layout.addWidget(QLabel("Grid:"))

        self.grid_combo = QComboBox()
        self.grid_combo.addItems(["1/1", "1/2", "1/4", "1/8", "1/16", "1/32"])
        self.grid_combo.setCurrentText("1/16")
        self.grid_combo.currentTextChanged.connect(self.update_grid)
        grid_layout.addWidget(self.grid_combo)

        self.snap_checkbox = QCheckBox("Snap")
        self.snap_checkbox.setChecked(True)
        grid_layout.addWidget(self.snap_checkbox)

        toolbar_layout.addLayout(grid_layout)

        layout.addLayout(toolbar_layout)

        # Main editor area
        splitter = QSplitter(Qt.Horizontal)

        # Piano roll
        self.piano_roll = PianoRollWidget()
        self.piano_roll.note_selected.connect(self.on_note_selected)
        self.piano_roll.note_moved.connect(self.on_note_moved)
        splitter.addWidget(self.piano_roll)

        # Step sequencer
        self.step_sequencer = StepSequencerWidget()
        splitter.addWidget(self.step_sequencer)

        splitter.setSizes([600, 200])
        layout.addWidget(splitter)

        # Properties panel
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)

        # Note properties
        properties_group = QGroupBox("Note Properties")
        properties_layout = QVBoxLayout(properties_group)

        # Note number
        note_layout = QHBoxLayout()
        note_layout.addWidget(QLabel("Note:"))
        self.note_spinbox = QSpinBox()
        self.note_spinbox.setRange(0, 127)
        self.note_spinbox.valueChanged.connect(self.update_selected_note)
        note_layout.addWidget(self.note_spinbox)
        properties_layout.addLayout(note_layout)

        # Velocity
        velocity_layout = QHBoxLayout()
        velocity_layout.addWidget(QLabel("Velocity:"))
        self.velocity_spinbox = QSpinBox()
        self.velocity_spinbox.setRange(1, 127)
        self.velocity_spinbox.valueChanged.connect(self.update_selected_note)
        velocity_layout.addWidget(self.velocity_spinbox)
        properties_layout.addLayout(velocity_layout)

        # Start time
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start:"))
        self.start_spinbox = QDoubleSpinBox()
        self.start_spinbox.setRange(0, 1000)
        self.start_spinbox.setDecimals(3)
        self.start_spinbox.valueChanged.connect(self.update_selected_note)
        start_layout.addWidget(self.start_spinbox)
        properties_layout.addLayout(start_layout)

        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))
        self.duration_spinbox = QDoubleSpinBox()
        self.duration_spinbox.setRange(0.001, 100)
        self.duration_spinbox.setDecimals(3)
        self.duration_spinbox.valueChanged.connect(self.update_selected_note)
        duration_layout.addWidget(self.duration_spinbox)
        properties_layout.addLayout(duration_layout)

        self.properties_layout.addWidget(properties_group)

        layout.addWidget(self.properties_widget)

    def update_grid(self, grid_text):
        """Update grid size"""
        grid_map = {
            "1/1": 1.0,
            "1/2": 0.5,
            "1/4": 0.25,
            "1/8": 0.125,
            "1/16": 0.0625,
            "1/32": 0.03125
        }

        self.piano_roll.grid_size = grid_map.get(grid_text, 0.25)
        self.piano_roll.snap_to_grid = self.snap_checkbox.isChecked()

    def on_note_selected(self, note):
        """Handle note selection"""
        self.note_spinbox.setValue(note.note)
        self.velocity_spinbox.setValue(note.velocity)
        self.start_spinbox.setValue(note.start_time)
        self.duration_spinbox.setValue(note.duration)

    def on_note_moved(self, note, old_time, old_note):
        """Handle note movement"""
        self.on_note_selected(note)

    def update_selected_note(self):
        """Update selected note properties"""
        if self.piano_roll.selected_notes:
            note = self.piano_roll.selected_notes[0]
            note.note = self.note_spinbox.value()
            note.velocity = self.velocity_spinbox.value()
            note.start_time = self.start_spinbox.value()
            note.duration = self.duration_spinbox.value()

            self.piano_roll.update()

    def add_note(self, note: MIDINote):
        """Add note to editor"""
        self.notes.append(note)
        self.piano_roll.add_note(note)

    def remove_note(self, note: MIDINote):
        """Remove note from editor"""
        if note in self.notes:
            self.notes.remove(note)
        self.piano_roll.remove_note(note)

    def clear_notes(self):
        """Clear all notes"""
        self.notes.clear()
        self.piano_roll.clear_notes()

    def get_notes(self) -> List[MIDINote]:
        """Get all notes"""
        return self.notes.copy()

class AdvancedMIDIEditor(QWidget):
    """Advanced MIDI editor main window"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styling()

    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("VoiceStudio Advanced MIDI Editor")
        self.setGeometry(100, 100, 1200, 800)

        layout = QVBoxLayout(self)

        # Menu bar
        menubar_layout = QHBoxLayout()

        # File operations
        file_layout = QHBoxLayout()

        new_button = QPushButton("New")
        new_button.clicked.connect(self.new_project)
        file_layout.addWidget(new_button)

        open_button = QPushButton("Open")
        open_button.clicked.connect(self.open_project)
        file_layout.addWidget(open_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_project)
        file_layout.addWidget(save_button)

        menubar_layout.addLayout(file_layout)
        menubar_layout.addStretch()

        # Tools
        tools_layout = QHBoxLayout()

        quantize_button = QPushButton("Quantize")
        quantize_button.clicked.connect(self.quantize_notes)
        tools_layout.addWidget(quantize_button)

        humanize_button = QPushButton("Humanize")
        humanize_button.clicked.connect(self.humanize_notes)
        tools_layout.addWidget(humanize_button)

        transpose_button = QPushButton("Transpose")
        transpose_button.clicked.connect(self.transpose_notes)
        tools_layout.addWidget(transpose_button)

        menubar_layout.addLayout(tools_layout)

        layout.addLayout(menubar_layout)

        # Main editor
        self.midi_editor = MIDIEditorWidget()
        layout.addWidget(self.midi_editor)

    def setup_styling(self):
        """Setup styling"""
        self.setStyleSheet("""
            QWidget {
                background: #2d2d2d;
                color: #ffffff;
            }
            QPushButton {
                background: #4CAF50;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSpinBox, QDoubleSpinBox {
                background: #333;
                border: 1px solid #555;
                border-radius: 3px;
                color: white;
                padding: 2px;
            }
            QComboBox {
                background: #333;
                border: 1px solid #555;
                border-radius: 3px;
                color: white;
                padding: 2px;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background: #333;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background: #4CAF50;
                border: 1px solid #555;
                border-radius: 3px;
            }
        """)

    def new_project(self):
        """Create new project"""
        self.midi_editor.clear_notes()

    def open_project(self):
        """Open project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open MIDI Project", "", "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                notes = [MIDINote.from_dict(note_data) for note_data in data.get('notes', [])]

                self.midi_editor.clear_notes()
                for note in notes:
                    self.midi_editor.add_note(note)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project: {e}")

    def save_project(self):
        """Save project"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save MIDI Project", "", "JSON Files (*.json)"
        )

        if file_path:
            try:
                notes_data = [note.to_dict() for note in self.midi_editor.get_notes()]
                data = {
                    'notes': notes_data,
                    'created_at': datetime.now().isoformat()
                }

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {e}")

    def quantize_notes(self):
        """Quantize selected notes"""
        # Simple quantization implementation
        for note in self.midi_editor.piano_roll.selected_notes:
            note.start_time = round(note.start_time / 0.25) * 0.25

        self.midi_editor.piano_roll.update()

    def humanize_notes(self):
        """Humanize selected notes"""
        import random

        for note in self.midi_editor.piano_roll.selected_notes:
            # Add small timing variations
            timing_variation = random.uniform(-0.01, 0.01)
            note.start_time += timing_variation

            # Add velocity variations
            velocity_variation = random.randint(-5, 5)
            note.velocity = max(1, min(127, note.velocity + velocity_variation))

        self.midi_editor.piano_roll.update()

    def transpose_notes(self):
        """Transpose selected notes"""
        transpose_amount, ok = QInputDialog.getInt(
            self, "Transpose", "Semitones:", 0, -12, 12
        )

        if ok:
            for note in self.midi_editor.piano_roll.selected_notes:
                note.note = max(0, min(127, note.note + transpose_amount))

            self.midi_editor.piano_roll.update()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("VoiceStudio Advanced MIDI Editor")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("VoiceStudio")

    # Create and show main window
    window = AdvancedMIDIEditor()
    window.show()

    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
