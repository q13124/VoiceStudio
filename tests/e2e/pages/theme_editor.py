"""
Page object for Theme Editor panel.

Provides methods to interact with the Theme Editor for E2E testing.
"""


from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ThemeEditorPage:
    """Page object for the Theme Editor panel."""

    # AutomationIds
    PANEL_ID = "ThemeEditorView"
    THEME_COMBO_ID = "ThemeEditor.ComboBox.Theme"
    ACCENT_GRID_ID = "ThemeEditor.GridView.Accents"
    DENSITY_COMBO_ID = "ThemeEditor.ComboBox.Density"
    CUSTOM_NAME_INPUT_ID = "ThemeEditor.TextBox.CustomName"
    SAVE_THEME_BUTTON_ID = "ThemeEditor.Button.SaveTheme"
    LOAD_THEME_BUTTON_ID = "ThemeEditor.Button.LoadTheme"
    DELETE_THEME_BUTTON_ID = "ThemeEditor.Button.DeleteTheme"
    RESET_BUTTON_ID = "ThemeEditor.Button.Reset"
    SAVED_THEMES_COMBO_ID = "ThemeEditor.ComboBox.SavedThemes"
    COLOR_PICKER_ID = "ThemeEditor.ColorPicker.Custom"
    APPLY_COLOR_BUTTON_ID = "ThemeEditor.Button.ApplyColor"

    def __init__(self, driver):
        """Initialize the Theme Editor page object."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_displayed(self) -> bool:
        """Check if the Theme Editor panel is displayed."""
        try:
            panel = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.PANEL_ID
            )
            return panel.is_displayed()
        except Exception:
            return False

    def wait_for_load(self, timeout: int = 10):
        """Wait for the Theme Editor panel to load."""
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

    def select_theme(self, theme_name: str):
        """Select a theme by name."""
        combo = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.THEME_COMBO_ID
        )
        combo.click()

        theme_item = self.wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.NAME, theme_name)
            )
        )
        theme_item.click()

    def get_accent_colors(self) -> list[str]:
        """Get available accent color names."""
        try:
            grid = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.ACCENT_GRID_ID
            )
            items = grid.find_elements(AppiumBy.CLASS_NAME, "GridViewItem")
            return [item.get_attribute("Name") for item in items]
        except Exception:
            return []

    def select_accent_by_index(self, index: int):
        """Select an accent color by index."""
        grid = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.ACCENT_GRID_ID
        )
        items = grid.find_elements(AppiumBy.CLASS_NAME, "GridViewItem")
        if 0 <= index < len(items):
            items[index].click()

    def select_accent_by_name(self, name: str):
        """Select an accent color by name."""
        grid = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.ACCENT_GRID_ID
        )
        items = grid.find_elements(AppiumBy.CLASS_NAME, "GridViewItem")
        for item in items:
            if item.get_attribute("Name") == name:
                item.click()
                return
        raise ValueError(f"Accent color '{name}' not found")

    def select_density(self, density_name: str):
        """Select a density option."""
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

    def save_custom_theme(self, name: str):
        """Save current settings as a custom theme."""
        name_input = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.CUSTOM_NAME_INPUT_ID
        )
        name_input.clear()
        name_input.send_keys(name)

        save_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.SAVE_THEME_BUTTON_ID
        )
        save_btn.click()

    def load_saved_theme(self, name: str):
        """Load a saved custom theme."""
        combo = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.SAVED_THEMES_COMBO_ID
        )
        combo.click()

        theme_item = self.wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.NAME, name)
            )
        )
        theme_item.click()

        load_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.LOAD_THEME_BUTTON_ID
        )
        load_btn.click()

    def delete_selected_theme(self):
        """Delete the currently selected saved theme."""
        delete_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.DELETE_THEME_BUTTON_ID
        )
        delete_btn.click()

    def reset_to_defaults(self):
        """Reset all theme settings to defaults."""
        reset_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.RESET_BUTTON_ID
        )
        reset_btn.click()

    def apply_custom_color(self):
        """Apply the custom color from the color picker."""
        apply_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.APPLY_COLOR_BUTTON_ID
        )
        apply_btn.click()
