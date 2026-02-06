"""
UI Test Helper Utilities.

Common operations and utilities for WinAppDriver UI tests.
"""

import time
from typing import List, Optional, Tuple
from dataclasses import dataclass

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =============================================================================
# Panel Configuration
# =============================================================================

@dataclass
class PanelConfig:
    """Configuration for a panel."""
    name: str
    nav_button_id: str
    view_root_id: str
    load_timeout: int = 10


# Core panels with their automation IDs
CORE_PANELS = [
    PanelConfig("Profiles", "NavRail_ProfilesButton", "ProfilesView_Root"),
    PanelConfig("Timeline", "NavRail_TimelineButton", "TimelineView_Root"),
    PanelConfig("EffectsMixer", "NavRail_EffectsMixerButton", "EffectsMixerView_Root"),
    PanelConfig("Analyzer", "NavRail_AnalyzerButton", "AnalyzerView_Root"),
    PanelConfig("Settings", "NavRail_SettingsButton", "SettingsView_Root"),
    PanelConfig("VoiceSynthesis", "NavRail_VoiceSynthesisButton", "VoiceSynthesisView_Root"),
]

# Extended panels
EXTENDED_PANELS = [
    PanelConfig("VoiceCloning", "NavRail_VoiceCloningButton", "VoiceCloningWizardView_Root"),
    PanelConfig("Transcription", "NavRail_TranscriptionButton", "TranscriptionView_Root"),
    PanelConfig("BatchProcessing", "NavRail_BatchProcessingButton", "BatchProcessingView_Root"),
    PanelConfig("QualityControl", "NavRail_QualityControlButton", "QualityControlView_Root"),
    PanelConfig("PluginManagement", "NavRail_PluginManagementButton", "PluginManagementView_Root"),
]

ALL_PANELS = CORE_PANELS + EXTENDED_PANELS


# =============================================================================
# Element Helpers
# =============================================================================

class ElementHelper:
    """Helper class for element operations."""
    
    def __init__(self, driver):
        self.driver = driver
    
    def find_by_id(self, automation_id: str, timeout: int = 10):
        """Find element by AutomationId."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(
                EC.presence_of_element_located(("accessibility id", automation_id))
            )
        except TimeoutException:
            return None
    
    def click_button(self, automation_id: str, wait_after: float = 0.5) -> bool:
        """Click a button by AutomationId."""
        element = self.find_by_id(automation_id)
        if element:
            element.click()
            time.sleep(wait_after)
            return True
        return False
    
    def get_text(self, automation_id: str) -> Optional[str]:
        """Get text content of an element."""
        element = self.find_by_id(automation_id)
        return element.text if element else None
    
    def is_visible(self, automation_id: str, timeout: int = 5) -> bool:
        """Check if element is visible."""
        try:
            element = self.find_by_id(automation_id, timeout)
            return element is not None and element.is_displayed()
        except Exception:
            return False
    
    def wait_for_condition(self, condition_fn, timeout: int = 10, 
                           poll_interval: float = 0.5) -> bool:
        """Wait for a custom condition to be true."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                if condition_fn():
                    return True
            # ALLOWED: bare except - Polling for condition, retrying is expected
            except Exception:
                pass
            time.sleep(poll_interval)
        return False
    
    def get_children(self, parent_id: str) -> List:
        """Get child elements of a parent."""
        parent = self.find_by_id(parent_id)
        if parent:
            return parent.find_elements("xpath", ".//*")
        return []


# =============================================================================
# Navigation Helpers
# =============================================================================

class NavigationHelper:
    """Helper class for navigation operations."""
    
    def __init__(self, driver):
        self.driver = driver
        self.element = ElementHelper(driver)
    
    def navigate_to_panel(self, panel: PanelConfig) -> bool:
        """Navigate to a specific panel."""
        if not self.element.click_button(panel.nav_button_id):
            return False
        return self.element.is_visible(panel.view_root_id, panel.load_timeout)
    
    def navigate_to_panel_by_name(self, name: str) -> bool:
        """Navigate to a panel by its name."""
        panel = next((p for p in ALL_PANELS if p.name == name), None)
        if panel:
            return self.navigate_to_panel(panel)
        return False
    
    def get_current_panel(self) -> Optional[str]:
        """Get the currently active panel."""
        for panel in ALL_PANELS:
            if self.element.is_visible(panel.view_root_id, timeout=1):
                return panel.name
        return None
    
    def cycle_all_panels(self) -> List[Tuple[str, bool]]:
        """Navigate through all panels and return results."""
        results = []
        for panel in ALL_PANELS:
            success = self.navigate_to_panel(panel)
            results.append((panel.name, success))
        return results


# =============================================================================
# Form Helpers
# =============================================================================

class FormHelper:
    """Helper class for form interactions."""
    
    def __init__(self, driver):
        self.driver = driver
        self.element = ElementHelper(driver)
    
    def fill_text_field(self, automation_id: str, text: str, 
                        clear_first: bool = True) -> bool:
        """Fill a text field."""
        element = self.element.find_by_id(automation_id)
        if element:
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        return False
    
    def toggle_checkbox(self, automation_id: str) -> bool:
        """Toggle a checkbox."""
        return self.element.click_button(automation_id)
    
    def select_dropdown_item(self, dropdown_id: str, item_id: str) -> bool:
        """Select an item from a dropdown."""
        if not self.element.click_button(dropdown_id):
            return False
        time.sleep(0.3)  # Wait for dropdown to open
        return self.element.click_button(item_id)
    
    def submit_form(self, submit_button_id: str) -> bool:
        """Submit a form by clicking submit button."""
        return self.element.click_button(submit_button_id)


# =============================================================================
# Assertion Helpers
# =============================================================================

def assert_element_visible(driver, automation_id: str, message: str = None):
    """Assert that an element is visible."""
    helper = ElementHelper(driver)
    assert helper.is_visible(automation_id), \
        message or f"Element '{automation_id}' should be visible"


def assert_element_not_visible(driver, automation_id: str, message: str = None):
    """Assert that an element is not visible."""
    helper = ElementHelper(driver)
    assert not helper.is_visible(automation_id, timeout=2), \
        message or f"Element '{automation_id}' should not be visible"


def assert_text_equals(driver, automation_id: str, expected: str, message: str = None):
    """Assert that element text equals expected value."""
    helper = ElementHelper(driver)
    actual = helper.get_text(automation_id)
    assert actual == expected, \
        message or f"Expected text '{expected}' but got '{actual}'"


def assert_panel_loaded(driver, panel: PanelConfig, message: str = None):
    """Assert that a panel has loaded."""
    assert_element_visible(driver, panel.view_root_id, 
        message or f"Panel '{panel.name}' should be loaded")


# =============================================================================
# Test Data Generators
# =============================================================================

def generate_test_profile_name() -> str:
    """Generate a unique test profile name."""
    timestamp = int(time.time())
    return f"TestProfile_{timestamp}"


def generate_test_text() -> str:
    """Generate sample text for TTS testing."""
    return "This is a test of the voice synthesis system. Hello, world!"
