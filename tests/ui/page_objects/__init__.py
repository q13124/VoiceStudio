"""
VoiceStudio Page Object Model.

This module provides Page Object implementations for UI automation testing.
Each page object encapsulates the structure and behavior of a UI component.
"""

from __future__ import annotations

from .analyzer_page import AnalyzerPage
from .base_page import BasePage
from .clone_page import ClonePage
from .diagnostics_page import DiagnosticsPage
from .effects_page import EffectsPage
from .library_page import LibraryPage
from .profiles_page import ProfilesPage
from .settings_page import SettingsPage
from .studio_page import StudioPage
from .timeline_page import TimelinePage
from .training_page import TrainingPage
from .transcribe_page import TranscribePage

__all__ = [
    "AnalyzerPage",
    "BasePage",
    "ClonePage",
    "DiagnosticsPage",
    "EffectsPage",
    "LibraryPage",
    "ProfilesPage",
    "SettingsPage",
    "StudioPage",
    "TimelinePage",
    "TrainingPage",
    "TranscribePage",
]
