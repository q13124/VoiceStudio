"""
Page object for Settings panel.

Provides methods to interact with the Settings view for E2E testing.
"""


from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class SettingsPage:
    """Page object for the Settings panel."""

    # AutomationIds
    PANEL_ID = "SettingsView"
    THEME_COMBO_ID = "Settings.ComboBox.Theme"
    DENSITY_COMBO_ID = "Settings.ComboBox.Density"
    LANGUAGE_COMBO_ID = "Settings.ComboBox.Language"
    SAVE_BUTTON_ID = "Settings.Button.Save"
    RESET_BUTTON_ID = "Settings.Button.Reset"
    BACKEND_URL_INPUT_ID = "Settings.TextBox.BackendUrl"
    AUTO_SAVE_TOGGLE_ID = "Settings.Toggle.AutoSave"

    def __init__(self, driver):
        """Initialize the Settings page object."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_displayed(self) -> bool:
        """Check if the Settings panel is currently displayed."""
        try:
            panel = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.PANEL_ID
            )
            return panel.is_displayed()
        except Exception:
            return False

    def wait_for_load(self, timeout: int = 10):
        """Wait for the Settings panel to load."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, self.PANEL_ID)
            )
        )

    def get_current_theme(self) -> str | None:
        """Get the currently selected theme."""
        try:
            combo = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.THEME_COMBO_ID
            )
            return combo.get_attribute("Value.Value")
        except Exception:
            return None

    def set_theme(self, theme_name: str):
        """Select a theme by name."""
        combo = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.THEME_COMBO_ID
        )
        combo.click()

        # Find and click the theme item
        theme_item = self.wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.NAME, theme_name)
            )
        )
        theme_item.click()

    def get_current_density(self) -> str | None:
        """Get the currently selected density."""
        try:
            combo = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.DENSITY_COMBO_ID
            )
            return combo.get_attribute("Value.Value")
        except Exception:
            return None

    def set_density(self, density_name: str):
        """Select a density by name."""
        combo = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.DENSITY_COMBO_ID
        )
        combo.click()

        density_item = self.wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.NAME, density_name)
            )
        )
        density_item.click()

    def get_backend_url(self) -> str | None:
        """Get the current backend URL."""
        try:
            textbox = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.BACKEND_URL_INPUT_ID
            )
            return textbox.text
        except Exception:
            return None

    def set_backend_url(self, url: str):
        """Set the backend URL."""
        textbox = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.BACKEND_URL_INPUT_ID
        )
        textbox.clear()
        textbox.send_keys(url)

    def is_auto_save_enabled(self) -> bool:
        """Check if auto-save is enabled."""
        try:
            toggle = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.AUTO_SAVE_TOGGLE_ID
            )
            return toggle.get_attribute("Toggle.ToggleState") == "1"
        except Exception:
            return False

    def toggle_auto_save(self):
        """Toggle the auto-save setting."""
        toggle = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.AUTO_SAVE_TOGGLE_ID
        )
        toggle.click()

    def click_save(self):
        """Click the Save button."""
        save_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.SAVE_BUTTON_ID
        )
        save_btn.click()

    def click_reset(self):
        """Click the Reset to Defaults button."""
        reset_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.RESET_BUTTON_ID
        )
        reset_btn.click()
