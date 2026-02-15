"""
VoiceStudio E2E Test Framework.

Provides:
- WinAppDriver/FlaUI integration
- Page Object Model base classes
- Element locators and helpers
- Screenshot capture utilities
- Wait and retry mechanisms
"""

from .base import E2EConfig, E2ETestBase
from .helpers import RetryHelper, ScreenshotHelper, WaitHelper
from .page_objects import BasePage, ElementLocator
from .session import SessionManager

__all__ = [
    "BasePage",
    "E2EConfig",
    "E2ETestBase",
    "ElementLocator",
    "RetryHelper",
    "ScreenshotHelper",
    "SessionManager",
    "WaitHelper",
]
