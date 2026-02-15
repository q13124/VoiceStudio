"""
Voice Cloning Wizard Page Object.

Provides methods for interacting with the voice cloning panel.
"""

import time
from typing import TYPE_CHECKING

from .base_page import BasePage

if TYPE_CHECKING:
    pass


class ClonePage(BasePage):
    """Page object for the Voice Cloning Wizard panel."""

    # =========================================================================
    # Automation IDs
    # =========================================================================

    @property
    def root_automation_id(self) -> str:
        return "VoiceCloningWizardView_Root"

    @property
    def nav_automation_id(self) -> str:
        return "NavClone"

    # Quick Clone section
    QUICK_CLONE_ROOT = "QuickCloneView_Root"
    AUDIO_DROP_ZONE = "QuickClone_AudioDropZone"
    REFERENCE_FILES_LIST = "QuickClone_ReferenceFilesList"
    PROFILE_NAME_INPUT = "QuickClone_ProfileNameInput"
    CREATE_PROFILE_BUTTON = "QuickClone_CreateProfileButton"
    CLEAR_FILES_BUTTON = "QuickClone_ClearFilesButton"

    # Wizard steps
    WIZARD_STEP_1 = "CloneWizard_Step1"
    WIZARD_STEP_2 = "CloneWizard_Step2"
    WIZARD_STEP_3 = "CloneWizard_Step3"
    WIZARD_NEXT_BUTTON = "CloneWizard_NextButton"
    WIZARD_BACK_BUTTON = "CloneWizard_BackButton"
    WIZARD_FINISH_BUTTON = "CloneWizard_FinishButton"

    # Status indicators
    STATUS_TEXT = "CloneWizard_StatusText"
    PROGRESS_RING = "CloneWizard_ProgressRing"

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def profile_name(self) -> str | None:
        """Get the current profile name input value."""
        return self.get_text(self.PROFILE_NAME_INPUT)

    @property
    def status_text(self) -> str | None:
        """Get the current status text."""
        return self.get_text(self.STATUS_TEXT)

    @property
    def is_create_enabled(self) -> bool:
        """Check if the create button is enabled."""
        try:
            element = self.find_element(self.CREATE_PROFILE_BUTTON, timeout=2)
            return element.is_enabled()
        except RuntimeError:
            return False

    @property
    def is_processing(self) -> bool:
        """Check if cloning is in progress."""
        return self.element_exists(self.PROGRESS_RING)

    # =========================================================================
    # Actions
    # =========================================================================

    def enter_profile_name(self, name: str) -> bool:
        """
        Enter a profile name.

        Args:
            name: The profile name.

        Returns:
            True if successful.
        """
        return self.type_text(self.PROFILE_NAME_INPUT, name)

    def click_create_profile(self) -> bool:
        """
        Click the create profile button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.CREATE_PROFILE_BUTTON)

    def click_clear_files(self) -> bool:
        """
        Click the clear files button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.CLEAR_FILES_BUTTON)

    def click_wizard_next(self) -> bool:
        """
        Click the wizard next button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.WIZARD_NEXT_BUTTON)

    def click_wizard_back(self) -> bool:
        """
        Click the wizard back button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.WIZARD_BACK_BUTTON)

    def click_wizard_finish(self) -> bool:
        """
        Click the wizard finish button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.WIZARD_FINISH_BUTTON)

    # =========================================================================
    # Workflows
    # =========================================================================

    def wait_for_processing_complete(self, timeout: float = 60.0) -> bool:
        """
        Wait for cloning process to complete.

        Args:
            timeout: Maximum time to wait.

        Returns:
            True if processing completed within timeout.
        """
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_processing:
                return True
            time.sleep(0.5)
        return False

    def get_current_wizard_step(self) -> int:
        """
        Get the current wizard step number.

        Returns:
            Step number (1, 2, 3) or 0 if unknown.
        """
        if self.element_exists(self.WIZARD_STEP_3):
            return 3
        elif self.element_exists(self.WIZARD_STEP_2):
            return 2
        elif self.element_exists(self.WIZARD_STEP_1):
            return 1
        return 0

    def verify_elements_present(self) -> dict:
        """
        Verify all critical elements are present.

        Returns:
            Dictionary with element names and their presence status.
        """
        elements = {
            "root": self.root_automation_id,
            "audio_drop_zone": self.AUDIO_DROP_ZONE,
            "profile_name_input": self.PROFILE_NAME_INPUT,
            "create_button": self.CREATE_PROFILE_BUTTON,
        }

        return {
            name: self.element_exists(auto_id)
            for name, auto_id in elements.items()
        }

    def is_quick_clone_mode(self) -> bool:
        """
        Check if in quick clone mode (vs wizard mode).

        Returns:
            True if quick clone interface is visible.
        """
        return self.element_exists(self.QUICK_CLONE_ROOT)
