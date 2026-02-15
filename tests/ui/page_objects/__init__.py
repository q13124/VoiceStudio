"""
VoiceStudio Page Object Model.

This module provides Page Object implementations for UI automation testing.
Each page object encapsulates the structure and behavior of a UI component.
"""

from .analyzer_page import AnalyzerPage
from .base_page import BasePage
from .clone_page import ClonePage
from .effects_page import EffectsPage
from .library_page import LibraryPage
from .studio_page import StudioPage

__all__ = [
    "AnalyzerPage",
    "BasePage",
    "ClonePage",
    "EffectsPage",
    "LibraryPage",
    "StudioPage",
]
