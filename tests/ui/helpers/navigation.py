"""
Navigation Helper for UI Tests.

Provides reusable navigation utilities for WinAppDriver-based UI testing.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.ui.conftest import WinAppDriverSession


# =============================================================================
# Navigation Constants
# =============================================================================


# Main navigation buttons with their automation IDs
NAV_BUTTONS = {
    "studio": "NavStudio",
    "profiles": "NavProfiles",
    "library": "NavLibrary",
    "effects": "NavEffects",
    "train": "NavTrain",
    "analyze": "NavAnalyze",
    "settings": "NavSettings",
    "logs": "NavLogs",
    "diagnostics": "NavLogs",  # Alias
}

# Panel root automation IDs (when available)
PANEL_ROOTS = {
    # Main navigation panels
    "studio": "VoiceSynthesisView_Root",
    "profiles": "ProfilesView_Root",
    "library": "LibraryView_Root",
    "effects": "EffectsMixerView_Root",
    "train": "TrainingView_Root",
    "analyze": "AnalyzeView_Root",
    "settings": "SettingsView_Root",
    "logs": "DiagnosticsView_Root",
    "diagnostics": "DiagnosticsView_Root",  # Alias
}

# Extended panel elements for specific testing
PANEL_ELEMENTS = {
    # Training panel elements
    "training": {
        "root": "TrainingView_Root",
        "datasets_list": "TrainingView_DatasetsListView",
        "dataset_name": "TrainingView_DatasetNameTextBox",
        "dataset_description": "TrainingView_DatasetDescriptionTextBox",
        "audio_files": "TrainingView_AudioFilesTextBox",
        "create_button": "TrainingView_CreateDatasetButton",
        "status_filter": "TrainingView_StatusFilterComboBox",
        "refresh_button": "TrainingView_RefreshButton",
        "jobs_list": "TrainingView_JobsListView",
    },
    # Settings panel elements
    "settings": {
        "root": "SettingsView_Root",
        "save_button": "SettingsView_SaveButton",
        "reset_button": "SettingsView_ResetButton",
        "general_category": "SettingsView_GeneralCategoryButton",
        "engine_category": "SettingsView_EngineCategoryButton",
        "privacy_category": "SettingsView_PrivacyCategoryButton",
        "theme_combo": "SettingsView_ThemeComboBox",
        "language_combo": "SettingsView_LanguageComboBox",
        "autosave_toggle": "SettingsView_AutoSaveToggle",
        "telemetry_toggle": "SettingsView_TelemetryToggle",
    },
    # Library panel elements
    "library": {
        "root": "LibraryView_Root",
        "folders_list": "LibraryView_FoldersListView",
        "drag_drop_canvas": "LibraryView_DragDropCanvas",
        "search_box": "LibraryView_SearchBox",
        "filter_combo": "LibraryView_FilterComboBox",
    },
    # Diagnostics panel elements
    "diagnostics": {
        "root": "DiagnosticsView_Root",
        "tab_view": "DiagnosticsView_TabView",
        "log_level_filter": "DiagnosticsView_LogLevelFilter",
        "log_search_box": "DiagnosticsView_LogSearchBox",
        "logs_list": "DiagnosticsView_LogsListView",
        "refresh_jobs_button": "DiagnosticsView_RefreshJobsButton",
        "active_jobs_list": "DiagnosticsView_ActiveJobsListView",
        "test_connection_button": "DiagnosticsView_TestConnectionButton",
        "refresh_engines_button": "DiagnosticsView_RefreshEnginesButton",
    },
    # Profiles panel elements
    "profiles": {
        "root": "ProfilesView_Root",
        "create_button": "ProfilesView_CreateButton",
        "profile_list": "ProfilesView_ProfileList",
        "filter_combo": "ProfilesView_FilterComboBox",
        "search_box": "ProfilesView_SearchBox",
    },
    # Effects panel elements
    "effects": {
        "root": "EffectsMixerView_Root",
        "master_volume_slider": "EffectsMixerView_MasterVolumeSlider",
        "reset_mixer_button": "EffectsMixerView_ResetMixerButton",
    },
    # Command palette elements
    "command_palette": {
        "root": "CommandPalette_Root",
        "search_box": "CommandPalette_SearchBox",
        "results_list": "CommandPalette_ResultsList",
    },
    # Error dialog elements
    "error_dialog": {
        "root": "ErrorDialog_Root",
        "content": "ErrorDialog_Content",
        "message_text": "ErrorDialog_MessageText",
        "details_text": "ErrorDialog_DetailsText",
        "technical_details_text": "ErrorDialog_TechnicalDetailsText",
    },
    # Loading overlay elements
    "loading_overlay": {
        "root": "LoadingOverlay_Root",
        "progress_ring": "LoadingOverlay_ProgressRing",
    },
    # Status bar elements
    "status_bar": {
        "processing_indicator": "StatusBar_ProcessingIndicator",
        "status_text": "StatusBar_StatusText",
        "job_status_text": "StatusBar_JobStatusText",
        "job_progress_bar": "StatusBar_JobProgressBar",
    },
}


# =============================================================================
# Navigation Helper Class
# =============================================================================


class NavigationHelper:
    """Helper class for navigation operations in UI tests."""

    def __init__(self, driver: WinAppDriverSession):
        """
        Initialize navigation helper.

        Args:
            driver: WinAppDriverSession instance.
        """
        self.driver = driver

    def navigate_to(self, panel_name: str, wait_time: float = 0.5) -> bool:
        """
        Navigate to a panel by name.

        Args:
            panel_name: Panel name (e.g., "studio", "profiles", "settings").
            wait_time: Time to wait after clicking (seconds).

        Returns:
            True if navigation succeeded, False otherwise.
        """
        panel_name_lower = panel_name.lower()
        nav_id = NAV_BUTTONS.get(panel_name_lower)

        if not nav_id:
            raise ValueError(
                f"Unknown panel: {panel_name}. " f"Valid panels: {list(NAV_BUTTONS.keys())}"
            )

        try:
            button = self.driver.find_element("accessibility id", nav_id)
            button.click()
            time.sleep(wait_time)
            return True
        except RuntimeError:
            return False

    def navigate_to_all(self, wait_between: float = 0.2) -> int:
        """
        Navigate through all panels sequentially.

        Args:
            wait_between: Time to wait between navigations (seconds).

        Returns:
            Number of successful navigations.
        """
        successful = 0
        for panel_name in NAV_BUTTONS:
            if panel_name == "diagnostics":
                continue  # Skip alias
            if self.navigate_to(panel_name, wait_between):
                successful += 1
        return successful

    def get_nav_button(self, panel_name: str):
        """
        Get a navigation button element.

        Args:
            panel_name: Panel name.

        Returns:
            WinAppDriverElement for the navigation button.

        Raises:
            ValueError: If panel name is unknown.
            RuntimeError: If button not found.
        """
        panel_name_lower = panel_name.lower()
        nav_id = NAV_BUTTONS.get(panel_name_lower)

        if not nav_id:
            raise ValueError(f"Unknown panel: {panel_name}")

        return self.driver.find_element("accessibility id", nav_id)

    def is_panel_loaded(self, panel_name: str) -> bool:
        """
        Check if a panel root element exists.

        Args:
            panel_name: Panel name.

        Returns:
            True if panel root element is found, False otherwise.
        """
        panel_name_lower = panel_name.lower()
        root_id = PANEL_ROOTS.get(panel_name_lower)

        if not root_id:
            return False

        try:
            self.driver.find_element("accessibility id", root_id)
            return True
        except RuntimeError:
            return False

    def get_all_nav_ids(self) -> list[str]:
        """
        Get list of all navigation automation IDs.

        Returns:
            List of automation ID strings.
        """
        return list(set(NAV_BUTTONS.values()))

    def verify_all_nav_buttons_exist(self) -> tuple[int, list[str]]:
        """
        Verify all navigation buttons exist.

        Returns:
            Tuple of (count found, list of missing button IDs).
        """
        found = 0
        missing = []

        for nav_id in set(NAV_BUTTONS.values()):
            try:
                self.driver.find_element("accessibility id", nav_id)
                found += 1
            except RuntimeError:
                missing.append(nav_id)

        return found, missing


# =============================================================================
# Convenience Functions
# =============================================================================


def navigate_to_panel(
    driver: WinAppDriverSession, panel_name: str, wait_time: float = 0.5
) -> bool:
    """
    Convenience function to navigate to a panel.

    Args:
        driver: WinAppDriverSession instance.
        panel_name: Panel name.
        wait_time: Wait time after navigation.

    Returns:
        True if successful.
    """
    helper = NavigationHelper(driver)
    return helper.navigate_to(panel_name, wait_time)


def get_nav_automation_id(panel_name: str) -> str | None:
    """
    Get the automation ID for a panel's navigation button.

    Args:
        panel_name: Panel name (e.g., "profiles").

    Returns:
        Automation ID string or None if unknown.
    """
    return NAV_BUTTONS.get(panel_name.lower())


def get_panel_root_id(panel_name: str) -> str | None:
    """
    Get the automation ID for a panel's root element.

    Args:
        panel_name: Panel name.

    Returns:
        Automation ID string or None if unknown.
    """
    return PANEL_ROOTS.get(panel_name.lower())


def get_panel_element_id(panel_name: str, element_name: str) -> str | None:
    """
    Get a specific element's automation ID within a panel.

    Args:
        panel_name: Panel name (e.g., "training", "settings").
        element_name: Element name (e.g., "save_button", "search_box").

    Returns:
        Automation ID string or None if unknown.
    """
    panel_elements = PANEL_ELEMENTS.get(panel_name.lower(), {})
    return panel_elements.get(element_name.lower())


def get_all_panel_elements(panel_name: str) -> dict[str, str]:
    """
    Get all known element IDs for a panel.

    Args:
        panel_name: Panel name.

    Returns:
        Dictionary of element names to automation IDs.
    """
    return PANEL_ELEMENTS.get(panel_name.lower(), {})
