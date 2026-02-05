"""
VoiceStudio E2E Test Framework.

Provides:
- WinAppDriver/FlaUI integration
- Page Object Model base classes
- Element locators and helpers
- Screenshot capture utilities
- Wait and retry mechanisms
"""

from .base import E2ETestBase, E2EConfig
from .page_objects import BasePage, ElementLocator
from .helpers import WaitHelper, ScreenshotHelper, RetryHelper
from .session import SessionManager

__all__ = [
    "E2ETestBase",
    "E2EConfig",
    "BasePage",
    "ElementLocator",
    "WaitHelper",
    "ScreenshotHelper",
    "RetryHelper",
    "SessionManager",
]
