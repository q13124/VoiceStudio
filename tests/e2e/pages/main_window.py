"""
Main Window Page Object for VoiceStudio.

Provides access to the main application window, navigation,
and common UI components.
"""

import logging
import time
from typing import TYPE_CHECKING

from tests.e2e.framework.page_objects import BasePage, ElementLocator

if TYPE_CHECKING:
    from tests.e2e.pages.voice_quick_clone import VoiceQuickClonePage
    from tests.e2e.pages.voice_browser import VoiceBrowserPage
    from tests.e2e.pages.synthesis import SynthesisPage

logger = logging.getLogger(__name__)


class MainWindowPage(BasePage):
    """
    Page object for the VoiceStudio main window.
    
    Provides navigation and access to all main panels and components.
    """
    
    # ==========================================================================
    # Locators - Navigation Rail
    # ==========================================================================
    
    NAV_STUDIO = ElementLocator.by_automation_id(
        "NavStudio", "Studio navigation button"
    )
    NAV_PROFILES = ElementLocator.by_automation_id(
        "NavProfiles", "Profiles navigation button"
    )
    NAV_LIBRARY = ElementLocator.by_automation_id(
        "NavLibrary", "Library navigation button"
    )
    NAV_EFFECTS = ElementLocator.by_automation_id(
        "NavEffects", "Effects navigation button"
    )
    NAV_TRAIN = ElementLocator.by_automation_id(
        "NavTrain", "Train navigation button"
    )
    NAV_ANALYZE = ElementLocator.by_automation_id(
        "NavAnalyze", "Analyze navigation button"
    )
    NAV_SETTINGS = ElementLocator.by_automation_id(
        "NavSettings", "Settings navigation button"
    )
    NAV_LOGS = ElementLocator.by_automation_id(
        "NavLogs", "Logs navigation button"
    )
    
    # ==========================================================================
    # Locators - Panel Hosts
    # ==========================================================================
    
    LEFT_PANEL_HOST = ElementLocator.by_automation_id(
        "LeftPanelHost", "Left panel container"
    )
    CENTER_PANEL_HOST = ElementLocator.by_automation_id(
        "CenterPanelHost", "Center panel container"
    )
    RIGHT_PANEL_HOST = ElementLocator.by_automation_id(
        "RightPanelHost", "Right panel container"
    )
    BOTTOM_PANEL_HOST = ElementLocator.by_automation_id(
        "BottomPanelHost", "Bottom panel container"
    )
    
    # ==========================================================================
    # Locators - Toolbar
    # ==========================================================================
    
    COMMAND_TOOLBAR = ElementLocator.by_automation_id(
        "CommandToolbar", "Main command toolbar"
    )
    
    # ==========================================================================
    # Locators - Status Bar
    # ==========================================================================
    
    STATUS_TEXT = ElementLocator.by_automation_id(
        "StatusText", "Status bar text"
    )
    PROCESSING_INDICATOR = ElementLocator.by_automation_id(
        "ProcessingIndicator", "Processing status indicator"
    )
    NETWORK_INDICATOR = ElementLocator.by_automation_id(
        "NetworkIndicator", "Network status indicator"
    )
    ENGINE_INDICATOR = ElementLocator.by_automation_id(
        "EngineIndicator", "Engine status indicator"
    )
    JOB_STATUS_TEXT = ElementLocator.by_automation_id(
        "JobStatusText", "Job status text"
    )
    JOB_PROGRESS_BAR = ElementLocator.by_automation_id(
        "JobProgressBar", "Job progress bar"
    )
    
    # ==========================================================================
    # Locators - Panel Views
    # ==========================================================================
    
    VOICE_QUICK_CLONE_VIEW = ElementLocator.by_automation_id(
        "VoiceQuickCloneView_Root", "Voice Quick Clone panel"
    )
    VOICE_BROWSER_VIEW = ElementLocator.by_automation_id(
        "VoiceBrowserView_Root", "Voice Browser panel"
    )
    
    # ==========================================================================
    # Locators - Overlays
    # ==========================================================================
    
    TOAST_CONTAINER = ElementLocator.by_automation_id(
        "ToastContainer", "Toast notification container"
    )
    GLOBAL_SEARCH_OVERLAY = ElementLocator.by_automation_id(
        "GlobalSearchOverlay", "Global search overlay"
    )
    GLOBAL_SEARCH_VIEW = ElementLocator.by_automation_id(
        "GlobalSearchView", "Global search view"
    )
    
    # ==========================================================================
    # Validation
    # ==========================================================================
    
    def _validate_page(self):
        """Validate main window is loaded."""
        # Wait for navigation rail to be visible
        try:
            self.wait_for_element(self.NAV_STUDIO, timeout=30.0)
            logger.info("Main window validated - navigation rail visible")
        except TimeoutError:
            logger.error("Main window validation failed - navigation not found")
            raise
    
    # ==========================================================================
    # Navigation Methods
    # ==========================================================================
    
    def navigate_to_studio(self):
        """Navigate to Studio view."""
        self.click(self.NAV_STUDIO)
        self.wait_for_loading()
        logger.info("Navigated to Studio")
    
    def navigate_to_profiles(self):
        """Navigate to Profiles view."""
        self.click(self.NAV_PROFILES)
        self.wait_for_loading()
        logger.info("Navigated to Profiles")
    
    def navigate_to_library(self):
        """Navigate to Library view."""
        self.click(self.NAV_LIBRARY)
        self.wait_for_loading()
        logger.info("Navigated to Library")
    
    def navigate_to_effects(self):
        """Navigate to Effects view."""
        self.click(self.NAV_EFFECTS)
        self.wait_for_loading()
        logger.info("Navigated to Effects")
    
    def navigate_to_train(self):
        """Navigate to Train view (Voice Cloning)."""
        self.click(self.NAV_TRAIN)
        self.wait_for_loading()
        logger.info("Navigated to Train")
    
    def navigate_to_analyze(self):
        """Navigate to Analyze view."""
        self.click(self.NAV_ANALYZE)
        self.wait_for_loading()
        logger.info("Navigated to Analyze")
    
    def navigate_to_settings(self):
        """Navigate to Settings view."""
        self.click(self.NAV_SETTINGS)
        self.wait_for_loading()
        logger.info("Navigated to Settings")
    
    def navigate_to_logs(self):
        """Navigate to Logs view."""
        self.click(self.NAV_LOGS)
        self.wait_for_loading()
        logger.info("Navigated to Logs")
    
    # ==========================================================================
    # Panel Access Methods
    # ==========================================================================
    
    def get_voice_quick_clone_page(self) -> "VoiceQuickClonePage":
        """Get Voice Quick Clone page object."""
        from tests.e2e.pages.voice_quick_clone import VoiceQuickClonePage
        self.wait_for_element(self.VOICE_QUICK_CLONE_VIEW)
        return VoiceQuickClonePage(self.driver, self.timeout)
    
    def get_voice_browser_page(self) -> "VoiceBrowserPage":
        """Get Voice Browser page object."""
        from tests.e2e.pages.voice_browser import VoiceBrowserPage
        self.wait_for_element(self.VOICE_BROWSER_VIEW)
        return VoiceBrowserPage(self.driver, self.timeout)
    
    def get_synthesis_page(self) -> "SynthesisPage":
        """Get Synthesis page object."""
        from tests.e2e.pages.synthesis import SynthesisPage
        return SynthesisPage(self.driver, self.timeout)
    
    # ==========================================================================
    # Status Methods
    # ==========================================================================
    
    def get_status_text(self) -> str:
        """Get current status bar text."""
        return self.get_text(self.STATUS_TEXT)
    
    def get_job_status(self) -> str:
        """Get current job status text."""
        return self.get_text(self.JOB_STATUS_TEXT)
    
    def is_processing(self) -> bool:
        """Check if application is currently processing."""
        job_status = self.get_job_status().lower()
        return job_status not in ["idle", "ready", ""]
    
    def wait_for_ready(self, timeout: float = 30.0):
        """Wait for application to be ready (not processing)."""
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_processing():
                return True
            time.sleep(0.5)
        raise TimeoutError("Application did not become ready")
    
    def wait_for_job_complete(self, timeout: float = 120.0):
        """Wait for current job to complete."""
        start = time.time()
        while time.time() - start < timeout:
            job_status = self.get_job_status().lower()
            if job_status in ["idle", "complete", "done", ""]:
                return True
            if "error" in job_status or "failed" in job_status:
                raise RuntimeError(f"Job failed: {job_status}")
            time.sleep(1.0)
        raise TimeoutError("Job did not complete within timeout")
    
    # ==========================================================================
    # Toast/Notification Methods
    # ==========================================================================
    
    def wait_for_toast(self, timeout: float = 10.0) -> str:
        """Wait for toast notification and return text."""
        start = time.time()
        while time.time() - start < timeout:
            if self.is_displayed(self.TOAST_CONTAINER):
                # Look for toast message text
                toast_message = ElementLocator.by_xpath(
                    "//*[@AutomationId='ToastContainer']//*[contains(@AutomationId, 'Message')]"
                )
                try:
                    return self.get_text(toast_message)
                except Exception:
                    # Toast visible but message not found, return container text
                    return self.find_element(self.TOAST_CONTAINER).text
            time.sleep(0.5)
        raise TimeoutError("Toast notification not displayed")
    
    def dismiss_toast(self):
        """Dismiss any visible toast notification."""
        toast_close = ElementLocator.by_xpath(
            "//*[@AutomationId='ToastContainer']//*[@AutomationId='CloseButton']"
        )
        if self.is_displayed(toast_close):
            self.click(toast_close)
    
    # ==========================================================================
    # Search Methods
    # ==========================================================================
    
    def open_global_search(self):
        """Open the global search overlay (Ctrl+K)."""
        from selenium.webdriver.common.keys import Keys
        self.driver.find_element("tag name", "Window").send_keys(Keys.CONTROL + "k")
        self.wait_for_element(self.GLOBAL_SEARCH_VIEW)
    
    def close_global_search(self):
        """Close the global search overlay."""
        from selenium.webdriver.common.keys import Keys
        if self.is_displayed(self.GLOBAL_SEARCH_OVERLAY):
            self.driver.find_element("tag name", "Window").send_keys(Keys.ESCAPE)
