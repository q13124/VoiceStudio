"""
Page object for Profile Editor/Profiles panel.

Provides methods to interact with voice profiles for E2E testing.
"""

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ProfileEditorPage:
    """Page object for the Profiles panel and profile editing."""

    # AutomationIds
    PANEL_ID = "ProfilesView"
    PROFILE_LIST_ID = "Profiles.ListView.ProfileList"
    NEW_PROFILE_BUTTON_ID = "Profiles.Button.New"
    EDIT_PROFILE_BUTTON_ID = "Profiles.Button.Edit"
    DELETE_PROFILE_BUTTON_ID = "Profiles.Button.Delete"
    CLONE_PROFILE_BUTTON_ID = "Profiles.Button.Clone"
    SEARCH_INPUT_ID = "Profiles.TextBox.Search"

    # Profile Editor Dialog
    EDITOR_DIALOG_ID = "ProfileEditor.Dialog"
    NAME_INPUT_ID = "ProfileEditor.TextBox.Name"
    DESCRIPTION_INPUT_ID = "ProfileEditor.TextBox.Description"
    ENGINE_COMBO_ID = "ProfileEditor.ComboBox.Engine"
    VOICE_COMBO_ID = "ProfileEditor.ComboBox.Voice"
    SAVE_BUTTON_ID = "ProfileEditor.Button.Save"
    CANCEL_BUTTON_ID = "ProfileEditor.Button.Cancel"

    # Audio Upload
    AUDIO_UPLOAD_BUTTON_ID = "ProfileEditor.Button.UploadAudio"
    AUDIO_RECORD_BUTTON_ID = "ProfileEditor.Button.RecordAudio"

    def __init__(self, driver):
        """Initialize the Profile Editor page object."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def is_displayed(self) -> bool:
        """Check if the Profiles panel is displayed."""
        try:
            panel = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.PANEL_ID
            )
            return panel.is_displayed()
        except Exception:
            return False

    def wait_for_load(self, timeout: int = 10):
        """Wait for the Profiles panel to load."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, self.PANEL_ID)
            )
        )

    def get_profile_names(self) -> list[str]:
        """Get list of profile names."""
        try:
            list_view = self.driver.find_element(
                AppiumBy.ACCESSIBILITY_ID, self.PROFILE_LIST_ID
            )
            items = list_view.find_elements(AppiumBy.CLASS_NAME, "ListViewItem")
            return [item.get_attribute("Name") for item in items]
        except Exception:
            return []

    def select_profile(self, name: str):
        """Select a profile by name."""
        list_view = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.PROFILE_LIST_ID
        )
        items = list_view.find_elements(AppiumBy.CLASS_NAME, "ListViewItem")
        for item in items:
            if item.get_attribute("Name") == name:
                item.click()
                return
        raise ValueError(f"Profile '{name}' not found")

    def search_profiles(self, query: str):
        """Search for profiles by name."""
        search_input = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.SEARCH_INPUT_ID
        )
        search_input.clear()
        search_input.send_keys(query)

    def click_new_profile(self):
        """Click the New Profile button."""
        new_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.NEW_PROFILE_BUTTON_ID
        )
        new_btn.click()
        # Wait for editor dialog
        self.wait.until(
            EC.presence_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, self.EDITOR_DIALOG_ID)
            )
        )

    def click_edit_profile(self):
        """Click the Edit Profile button."""
        edit_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.EDIT_PROFILE_BUTTON_ID
        )
        edit_btn.click()
        # Wait for editor dialog
        self.wait.until(
            EC.presence_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, self.EDITOR_DIALOG_ID)
            )
        )

    def click_delete_profile(self):
        """Click the Delete Profile button."""
        delete_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.DELETE_PROFILE_BUTTON_ID
        )
        delete_btn.click()

    def click_clone_profile(self):
        """Click the Clone Profile button."""
        clone_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.CLONE_PROFILE_BUTTON_ID
        )
        clone_btn.click()

    # Editor dialog methods
    def set_profile_name(self, name: str):
        """Set the profile name in the editor."""
        name_input = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.NAME_INPUT_ID
        )
        name_input.clear()
        name_input.send_keys(name)

    def set_profile_description(self, description: str):
        """Set the profile description in the editor."""
        desc_input = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.DESCRIPTION_INPUT_ID
        )
        desc_input.clear()
        desc_input.send_keys(description)

    def select_engine(self, engine_name: str):
        """Select an engine in the editor."""
        combo = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.ENGINE_COMBO_ID
        )
        combo.click()

        engine_item = self.wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.NAME, engine_name)
            )
        )
        engine_item.click()

    def select_voice(self, voice_name: str):
        """Select a voice in the editor."""
        combo = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.VOICE_COMBO_ID
        )
        combo.click()

        voice_item = self.wait.until(
            EC.element_to_be_clickable(
                (AppiumBy.NAME, voice_name)
            )
        )
        voice_item.click()

    def save_profile(self):
        """Click Save in the editor dialog."""
        save_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.SAVE_BUTTON_ID
        )
        save_btn.click()
        # Wait for dialog to close
        self.wait.until(
            EC.invisibility_of_element_located(
                (AppiumBy.ACCESSIBILITY_ID, self.EDITOR_DIALOG_ID)
            )
        )

    def cancel_edit(self):
        """Click Cancel in the editor dialog."""
        cancel_btn = self.driver.find_element(
            AppiumBy.ACCESSIBILITY_ID, self.CANCEL_BUTTON_ID
        )
        cancel_btn.click()

    def create_profile(self, name: str, engine: str, voice: str, description: str = ""):
        """Create a new profile with the given parameters."""
        self.click_new_profile()
        self.set_profile_name(name)
        if description:
            self.set_profile_description(description)
        self.select_engine(engine)
        self.select_voice(voice)
        self.save_profile()
