"""
Page Object Model for VoiceStudio E2E Tests.

Provides page object base classes and common element locators
for structured UI testing.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Element Locator
# =============================================================================


@dataclass
class ElementLocator:
    """Represents a UI element locator."""

    value: str
    by: str = "automation_id"
    description: str = ""

    def __str__(self) -> str:
        return f"{self.by}={self.value}"

    @classmethod
    def by_automation_id(cls, automation_id: str, description: str = "") -> ElementLocator:
        """Create locator by automation ID."""
        return cls(value=automation_id, by="automation_id", description=description)

    @classmethod
    def by_name(cls, name: str, description: str = "") -> ElementLocator:
        """Create locator by name."""
        return cls(value=name, by="name", description=description)

    @classmethod
    def by_class(cls, class_name: str, description: str = "") -> ElementLocator:
        """Create locator by class name."""
        return cls(value=class_name, by="class_name", description=description)

    @classmethod
    def by_xpath(cls, xpath: str, description: str = "") -> ElementLocator:
        """Create locator by XPath."""
        return cls(value=xpath, by="xpath", description=description)


# =============================================================================
# Base Page Object
# =============================================================================


class BasePage:
    """
    Base class for Page Objects.

    Implements the Page Object Model pattern for structured UI testing.
    Each page or panel in the application should have a corresponding
    page object class.

    Usage:
        class MainWindow(BasePage):
            # Locators
            NAVIGATION_PANEL = ElementLocator.by_automation_id("NavigationPanel")
            VOICE_BROWSER = ElementLocator.by_automation_id("VoiceBrowserView")

            def navigate_to_voice_browser(self):
                self.click(self.VOICE_BROWSER)
                return VoiceBrowserPage(self.driver)
    """

    def __init__(self, driver, timeout: float = 10.0):
        """
        Initialize page object.

        Args:
            driver: WebDriver instance
            timeout: Default timeout for element waits
        """
        self.driver = driver
        self.timeout = timeout
        self._validate_page()

    def _validate_page(self):
        """
        Validate page is loaded correctly.
        Override in subclasses to add specific validation.
        """
        pass

    # -------------------------------------------------------------------------
    # Element Interaction
    # -------------------------------------------------------------------------

    def find_element(self, locator: ElementLocator) -> Any:
        """Find element by locator."""
        by_mapping = {
            "automation_id": "accessibility id",
            "name": "name",
            "class_name": "class name",
            "xpath": "xpath",
        }
        actual_by = by_mapping.get(locator.by, locator.by)
        return self.driver.find_element(actual_by, locator.value)

    def find_elements(self, locator: ElementLocator) -> list[Any]:
        """Find multiple elements by locator."""
        by_mapping = {
            "automation_id": "accessibility id",
            "name": "name",
            "class_name": "class name",
            "xpath": "xpath",
        }
        actual_by = by_mapping.get(locator.by, locator.by)
        return self.driver.find_elements(actual_by, locator.value)

    def wait_for_element(self, locator: ElementLocator, timeout: float | None = None) -> Any:
        """Wait for element to be present and visible."""
        timeout = timeout or self.timeout
        start = time.time()

        while time.time() - start < timeout:
            try:
                element = self.find_element(locator)
                if element is not None and element.is_displayed():
                    return element
            # ALLOWED: bare except - Polling for element, retrying is expected
            except Exception:
                pass
            time.sleep(0.5)

        raise TimeoutError(f"Element not found: {locator} " f"(description: {locator.description})")

    def wait_for_element_clickable(
        self, locator: ElementLocator, timeout: float | None = None
    ) -> Any:
        """Wait for element to be clickable."""
        timeout = timeout or self.timeout
        start = time.time()

        while time.time() - start < timeout:
            try:
                element = self.find_element(locator)
                if element is not None and element.is_displayed() and element.is_enabled():
                    return element
            # ALLOWED: bare except - Polling for element, retrying is expected
            except Exception:
                pass
            time.sleep(0.5)

        raise TimeoutError(
            f"Element not clickable: {locator} " f"(description: {locator.description})"
        )

    def click(self, locator: ElementLocator, wait: bool = True):
        """Click on element."""
        element = self.wait_for_element_clickable(locator) if wait else self.find_element(locator)
        element.click()
        logger.debug(f"Clicked: {locator.description or locator.value}")

    def double_click(self, locator: ElementLocator):
        """Double-click on element."""
        element = self.wait_for_element_clickable(locator)
        # WinAppDriver ActionChains equivalent
        from selenium.webdriver import ActionChains

        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        logger.debug(f"Double-clicked: {locator.description or locator.value}")

    def type_text(self, locator: ElementLocator, text: str, clear_first: bool = True):
        """Type text into element."""
        element = self.wait_for_element_clickable(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug(f"Typed '{text}' into: {locator.description or locator.value}")

    def get_text(self, locator: ElementLocator) -> str:
        """Get text from element."""
        element = self.wait_for_element(locator)
        return element.text

    def get_attribute(self, locator: ElementLocator, attribute: str) -> str:
        """Get attribute from element."""
        element = self.wait_for_element(locator)
        return element.get_attribute(attribute)

    def is_displayed(self, locator: ElementLocator) -> bool:
        """Check if element is displayed."""
        try:
            element = self.find_element(locator)
            return element is not None and element.is_displayed()
        except Exception:
            return False

    def is_enabled(self, locator: ElementLocator) -> bool:
        """Check if element is enabled."""
        try:
            element = self.find_element(locator)
            return element is not None and element.is_enabled()
        except Exception:
            return False

    # -------------------------------------------------------------------------
    # Selection Helpers
    # -------------------------------------------------------------------------

    def select_item_by_text(self, locator: ElementLocator, text: str):
        """Select item from list/dropdown by text."""
        element = self.wait_for_element_clickable(locator)
        element.click()
        time.sleep(0.5)

        # Find and click the item with matching text
        items = self.find_elements(ElementLocator.by_xpath(f"//*[contains(@Name, '{text}')]"))
        for item in items:
            if text in item.text:
                item.click()
                return

        raise ValueError(f"Item not found: {text}")

    def select_item_by_index(self, locator: ElementLocator, index: int):
        """Select item from list/dropdown by index."""
        element = self.wait_for_element_clickable(locator)
        element.click()
        time.sleep(0.5)

        # Get all items and select by index
        items = self.find_elements(ElementLocator.by_class("ListViewItem"))
        if index < len(items):
            items[index].click()
        else:
            raise IndexError(f"Index {index} out of range (max: {len(items) - 1})")

    # -------------------------------------------------------------------------
    # Wait Helpers
    # -------------------------------------------------------------------------

    def wait_for_condition(
        self,
        condition: Callable[[], bool],
        timeout: float | None = None,
        message: str = "Condition not met",
    ):
        """Wait for a custom condition to be true."""
        timeout = timeout or self.timeout
        start = time.time()

        while time.time() - start < timeout:
            if condition():
                return True
            time.sleep(0.5)

        raise TimeoutError(message)

    def wait_for_loading(self, timeout: float | None = None):
        """Wait for loading indicators to disappear."""
        loading_locators = [
            ElementLocator.by_automation_id("LoadingIndicator"),
            ElementLocator.by_automation_id("ProgressRing"),
            ElementLocator.by_automation_id("BusyIndicator"),
        ]

        timeout = timeout or self.timeout
        start = time.time()

        while time.time() - start < timeout:
            loading_visible = False
            for locator in loading_locators:
                if self.is_displayed(locator):
                    loading_visible = True
                    break

            if not loading_visible:
                return True
            time.sleep(0.5)

        logger.warning("Loading indicator still visible after timeout")
        return False


# =============================================================================
# Common Page Components
# =============================================================================


class NavigationComponent(BasePage):
    """Component for main navigation."""

    # Locators
    NAVIGATION_PANEL = ElementLocator.by_automation_id("NavigationPanel")
    VOICE_BROWSER = ElementLocator.by_automation_id("VoiceBrowserNavItem")
    VOICE_CLONING = ElementLocator.by_automation_id("VoiceCloningNavItem")
    SYNTHESIS = ElementLocator.by_automation_id("SynthesisNavItem")
    PROJECTS = ElementLocator.by_automation_id("ProjectsNavItem")
    SETTINGS = ElementLocator.by_automation_id("SettingsNavItem")

    def navigate_to_voice_browser(self):
        """Navigate to Voice Browser panel."""
        self.click(self.VOICE_BROWSER)
        self.wait_for_loading()

    def navigate_to_voice_cloning(self):
        """Navigate to Voice Cloning panel."""
        self.click(self.VOICE_CLONING)
        self.wait_for_loading()

    def navigate_to_synthesis(self):
        """Navigate to Synthesis panel."""
        self.click(self.SYNTHESIS)
        self.wait_for_loading()

    def navigate_to_projects(self):
        """Navigate to Projects panel."""
        self.click(self.PROJECTS)
        self.wait_for_loading()

    def navigate_to_settings(self):
        """Navigate to Settings panel."""
        self.click(self.SETTINGS)
        self.wait_for_loading()


class DialogComponent(BasePage):
    """Component for handling dialogs."""

    # Common dialog locators
    DIALOG_OVERLAY = ElementLocator.by_automation_id("ContentDialogOverlay")
    DIALOG_TITLE = ElementLocator.by_automation_id("DialogTitle")
    OK_BUTTON = ElementLocator.by_automation_id("PrimaryButton")
    CANCEL_BUTTON = ElementLocator.by_automation_id("SecondaryButton")
    CLOSE_BUTTON = ElementLocator.by_automation_id("CloseButton")

    def is_dialog_visible(self) -> bool:
        """Check if a dialog is currently visible."""
        return self.is_displayed(self.DIALOG_OVERLAY)

    def get_dialog_title(self) -> str:
        """Get the dialog title text."""
        return self.get_text(self.DIALOG_TITLE)

    def click_ok(self):
        """Click the OK/Primary button."""
        self.click(self.OK_BUTTON)

    def click_cancel(self):
        """Click the Cancel/Secondary button."""
        self.click(self.CANCEL_BUTTON)

    def close_dialog(self):
        """Close the dialog using close button."""
        if self.is_displayed(self.CLOSE_BUTTON):
            self.click(self.CLOSE_BUTTON)
        elif self.is_displayed(self.CANCEL_BUTTON):
            self.click(self.CANCEL_BUTTON)


class NotificationComponent(BasePage):
    """Component for handling notifications."""

    # Notification locators
    NOTIFICATION_AREA = ElementLocator.by_automation_id("NotificationArea")
    NOTIFICATION_MESSAGE = ElementLocator.by_automation_id("NotificationMessage")
    NOTIFICATION_DISMISS = ElementLocator.by_automation_id("NotificationDismiss")

    def wait_for_notification(self, timeout: float | None = None) -> str:
        """Wait for notification and return message."""
        timeout = timeout or 10.0
        element = self.wait_for_element(self.NOTIFICATION_MESSAGE, timeout)
        return element.text

    def dismiss_notification(self):
        """Dismiss current notification."""
        if self.is_displayed(self.NOTIFICATION_DISMISS):
            self.click(self.NOTIFICATION_DISMISS)

    def wait_for_success_notification(self, timeout: float | None = None):
        """Wait for a success notification."""
        message = self.wait_for_notification(timeout)
        # Look for success indicators
        success_keywords = ["success", "completed", "saved", "created"]
        if not any(kw in message.lower() for kw in success_keywords):
            raise AssertionError(f"Expected success notification, got: {message}")
        return message
