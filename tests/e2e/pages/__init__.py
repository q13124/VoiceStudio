"""
VoiceStudio Page Objects.

This module exports page objects for the VoiceStudio application.
"""

from tests.e2e.pages.main_window import MainWindowPage
from tests.e2e.pages.voice_quick_clone import VoiceQuickClonePage
from tests.e2e.pages.voice_browser import VoiceBrowserPage
from tests.e2e.pages.synthesis import SynthesisPage
from tests.e2e.pages.project import ProjectPage

__all__ = [
    "MainWindowPage",
    "VoiceQuickClonePage",
    "VoiceBrowserPage",
    "SynthesisPage",
    "ProjectPage",
]
