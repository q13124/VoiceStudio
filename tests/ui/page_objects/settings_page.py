"""
Settings Page Object for VoiceStudio UI Tests.

Provides automation for the Settings panel including:
- Settings category navigation
- Configuration changes
- Save operations
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Optional

from .base_page import BasePage

if TYPE_CHECKING:
    from tests.ui.conftest import WinAppDriverElement


class SettingsPage(BasePage):
    """
    Page object for the Settings panel.

    Handles application settings and preferences.
    """

    # Element automation IDs (from automation_ids.py)
    SETTINGS_CATEGORIES = "SettingsView_SettingsCategories"
    SAVE_BUTTON = "SettingsView_SaveButton"

    @property
    def root_automation_id(self) -> str:
        return "SettingsView_Root"

    @property
    def nav_automation_id(self) -> str:
        return "NavSettings"

    # =========================================================================
    # Category Navigation
    # =========================================================================

    def get_settings_categories(self) -> list[WinAppDriverElement]:
        """Get list of settings category elements."""
        try:
            categories = self.find_element(self.SETTINGS_CATEGORIES)
            return categories.find_elements("class name", "ListViewItem")
        except RuntimeError:
            return []

    def select_category(self, category_name: str) -> bool:
        """
        Select a settings category by name.

        Args:
            category_name: Name of the category to select.

        Returns:
            True if category was selected.
        """
        categories = self.get_settings_categories()
        for category in categories:
            try:
                if category_name.lower() in category.text.lower():
                    category.click()
                    time.sleep(0.3)
                    return True
            except RuntimeError:
                continue
        return False

    # =========================================================================
    # Settings Actions
    # =========================================================================

    def save_settings(self) -> bool:
        """Click the save button to persist settings."""
        return self.click_with_retry(self.SAVE_BUTTON)

    def is_save_enabled(self) -> bool:
        """Check if save button is enabled (settings changed)."""
        try:
            button = self.find_element(self.SAVE_BUTTON)
            return button.is_enabled()
        except RuntimeError:
            return False

    # =========================================================================
    # Setting Manipulation
    # =========================================================================

    def set_text_setting(self, setting_id: str, value: str) -> bool:
        """
        Set a text-based setting value.

        Args:
            setting_id: AutomationId of the text input.
            value: Value to set.

        Returns:
            True if successful.
        """
        return self.type_text(setting_id, value)

    def toggle_setting(self, setting_id: str) -> bool:
        """
        Toggle a boolean setting.

        Args:
            setting_id: AutomationId of the toggle.

        Returns:
            True if successful.
        """
        return self.click_with_retry(setting_id)

    def select_dropdown_setting(self, dropdown_id: str, value: str) -> bool:
        """
        Select a value from a dropdown setting.

        Args:
            dropdown_id: AutomationId of the dropdown.
            value: Value to select.

        Returns:
            True if successful.
        """
        return self.select_combobox_item(dropdown_id, value)

    # =========================================================================
    # Workflow Convenience
    # =========================================================================

    def navigate_and_select_category(self, category_name: str) -> bool:
        """
        Navigate to settings and select a category.

        Args:
            category_name: Name of the category.

        Returns:
            True if successful.
        """
        if not self.is_loaded():
            if not self.navigate():
                return False

        return self.select_category(category_name)
