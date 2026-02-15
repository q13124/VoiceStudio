"""
Voice Quick Clone Page Object for VoiceStudio.

Provides access to the Quick Voice Clone wizard panel.
"""

import logging
import os
import time

from tests.e2e.framework.page_objects import BasePage, ElementLocator

logger = logging.getLogger(__name__)


class VoiceQuickClonePage(BasePage):
    """
    Page object for the Voice Quick Clone panel.

    This panel provides a streamlined, wizard-like interface for
    quickly cloning a voice from a reference audio file.
    """

    # ==========================================================================
    # Locators - Root
    # ==========================================================================

    ROOT = ElementLocator.by_automation_id(
        "VoiceQuickCloneView_Root", "Voice Quick Clone root element"
    )

    # ==========================================================================
    # Locators - Audio Selection
    # ==========================================================================

    BROWSE_AUDIO_BUTTON = ElementLocator.by_automation_id(
        "BrowseAudioButton", "Browse for audio file button"
    )
    AUDIO_FILE_NAME = ElementLocator.by_automation_id(
        "AudioFileName", "Selected audio file name display"
    )
    DROP_ZONE = ElementLocator.by_automation_id(
        "AudioDropZone", "Audio file drop zone"
    )

    # ==========================================================================
    # Locators - Auto-Detection
    # ==========================================================================

    DETECTED_ENGINE = ElementLocator.by_automation_id(
        "DetectedEngine", "Auto-detected engine display"
    )
    DETECTED_QUALITY = ElementLocator.by_automation_id(
        "DetectedQualityMode", "Auto-detected quality mode display"
    )
    ENGINE_SELECTOR = ElementLocator.by_automation_id(
        "EngineSelector", "Engine selection dropdown"
    )
    QUALITY_SELECTOR = ElementLocator.by_automation_id(
        "QualitySelector", "Quality mode selection dropdown"
    )

    # ==========================================================================
    # Locators - Profile Configuration
    # ==========================================================================

    PROFILE_NAME_INPUT = ElementLocator.by_automation_id(
        "ProfileNameInput", "Profile name input field"
    )

    # ==========================================================================
    # Locators - Actions
    # ==========================================================================

    QUICK_CLONE_BUTTON = ElementLocator.by_automation_id(
        "QuickCloneButton", "Start quick clone button"
    )
    RESET_BUTTON = ElementLocator.by_automation_id(
        "ResetButton", "Reset form button"
    )

    # ==========================================================================
    # Locators - Progress/Status
    # ==========================================================================

    PROCESSING_STATUS = ElementLocator.by_automation_id(
        "ProcessingStatus", "Processing status text"
    )
    PROCESSING_PROGRESS = ElementLocator.by_automation_id(
        "ProcessingProgress", "Processing progress bar"
    )
    LOADING_INDICATOR = ElementLocator.by_automation_id(
        "LoadingIndicator", "Loading spinner"
    )

    # ==========================================================================
    # Locators - Results
    # ==========================================================================

    CREATED_PROFILE_ID = ElementLocator.by_automation_id(
        "CreatedProfileId", "Created profile ID display"
    )
    QUALITY_SCORE = ElementLocator.by_automation_id(
        "QualityScore", "Voice quality score display"
    )
    SUCCESS_MESSAGE = ElementLocator.by_automation_id(
        "SuccessMessage", "Success message display"
    )
    ERROR_MESSAGE = ElementLocator.by_automation_id(
        "ErrorMessage", "Error message display"
    )

    # ==========================================================================
    # Locators - Help
    # ==========================================================================

    HELP_OVERLAY = ElementLocator.by_automation_id(
        "HelpOverlay", "Help overlay"
    )
    HELP_BUTTON = ElementLocator.by_automation_id(
        "HelpButton", "Help button"
    )

    # ==========================================================================
    # Validation
    # ==========================================================================

    def _validate_page(self):
        """Validate Voice Quick Clone panel is loaded."""
        try:
            self.wait_for_element(self.ROOT, timeout=10.0)
            logger.info("Voice Quick Clone panel validated")
        except TimeoutError:
            logger.warning("Voice Quick Clone panel not immediately visible")

    # ==========================================================================
    # Audio Selection
    # ==========================================================================

    def click_browse_audio(self):
        """Click the browse audio button to open file picker."""
        self.click(self.BROWSE_AUDIO_BUTTON)
        logger.info("Clicked browse audio button")

    def get_selected_file_name(self) -> str:
        """Get the currently selected audio file name."""
        return self.get_text(self.AUDIO_FILE_NAME)

    def is_audio_selected(self) -> bool:
        """Check if an audio file has been selected."""
        try:
            file_name = self.get_selected_file_name()
            return bool(file_name and file_name.strip())
        except Exception:
            return False

    def select_audio_file(self, file_path: str):
        """
        Select an audio file using the file picker.

        Note: This is a complex operation that requires handling
        the Windows file picker dialog.

        Args:
            file_path: Absolute path to the audio file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Click browse button to open file picker
        self.click_browse_audio()

        # Handle Windows file picker dialog
        # Wait for the file dialog to appear
        time.sleep(1.0)

        # The file picker is a separate window - need to use Windows automation
        # This is typically handled by typing the path in the filename field

        # Find the Open dialog window
        file_dialog = ElementLocator.by_name("Open", "File picker dialog")
        try:
            self.wait_for_element(file_dialog, timeout=5.0)
        except TimeoutError:
            logger.warning("File dialog not found, may need different approach")
            return

        # Type the file path in the filename field
        filename_field = ElementLocator.by_automation_id(
            "1148", "File name input"  # Standard Windows file dialog ID
        )
        self.type_text(filename_field, file_path)

        # Click Open button
        open_button = ElementLocator.by_name("Open", "Open button")
        self.click(open_button)

        # Wait for dialog to close and file to be selected
        time.sleep(0.5)
        logger.info(f"Selected audio file: {file_path}")

    # ==========================================================================
    # Engine/Quality Selection
    # ==========================================================================

    def get_detected_engine(self) -> str:
        """Get the auto-detected engine name."""
        return self.get_text(self.DETECTED_ENGINE)

    def get_detected_quality(self) -> str:
        """Get the auto-detected quality mode."""
        return self.get_text(self.DETECTED_QUALITY)

    def select_engine(self, engine_name: str):
        """Select a specific engine from the dropdown."""
        self.click(self.ENGINE_SELECTOR)
        time.sleep(0.3)
        engine_option = ElementLocator.by_name(engine_name, f"Engine option: {engine_name}")
        self.click(engine_option)
        logger.info(f"Selected engine: {engine_name}")

    def select_quality_mode(self, quality_mode: str):
        """Select a specific quality mode from the dropdown."""
        self.click(self.QUALITY_SELECTOR)
        time.sleep(0.3)
        quality_option = ElementLocator.by_name(
            quality_mode, f"Quality option: {quality_mode}"
        )
        self.click(quality_option)
        logger.info(f"Selected quality mode: {quality_mode}")

    # ==========================================================================
    # Profile Configuration
    # ==========================================================================

    def set_profile_name(self, name: str):
        """Set the profile name."""
        self.type_text(self.PROFILE_NAME_INPUT, name)
        logger.info(f"Set profile name: {name}")

    def get_profile_name(self) -> str:
        """Get the current profile name."""
        element = self.wait_for_element(self.PROFILE_NAME_INPUT)
        return element.get_attribute("Value.Value") or element.text

    # ==========================================================================
    # Clone Actions
    # ==========================================================================

    def click_quick_clone(self):
        """Click the Quick Clone button to start cloning."""
        self.click(self.QUICK_CLONE_BUTTON)
        logger.info("Clicked Quick Clone button")

    def is_quick_clone_enabled(self) -> bool:
        """Check if Quick Clone button is enabled."""
        return self.is_enabled(self.QUICK_CLONE_BUTTON)

    def click_reset(self):
        """Click the Reset button to clear the form."""
        self.click(self.RESET_BUTTON)
        logger.info("Clicked Reset button")

    # ==========================================================================
    # Progress/Status
    # ==========================================================================

    def get_processing_status(self) -> str:
        """Get the current processing status text."""
        try:
            return self.get_text(self.PROCESSING_STATUS)
        except Exception:
            return ""

    def is_processing(self) -> bool:
        """Check if cloning is in progress."""
        return self.is_displayed(self.LOADING_INDICATOR)

    def wait_for_processing_complete(self, timeout: float = 120.0):
        """Wait for the cloning process to complete."""
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_processing():
                status = self.get_processing_status().lower()
                if "complete" in status or "success" in status:
                    return True
                if "failed" in status or "error" in status:
                    raise RuntimeError(f"Clone failed: {status}")
                # If not processing and status is empty/done, consider complete
                if not self.is_processing():
                    return True
            time.sleep(1.0)
        raise TimeoutError("Clone process did not complete within timeout")

    # ==========================================================================
    # Results
    # ==========================================================================

    def get_created_profile_id(self) -> str:
        """Get the ID of the created voice profile."""
        return self.get_text(self.CREATED_PROFILE_ID)

    def get_quality_score(self) -> float | None:
        """Get the quality score of the cloned voice."""
        try:
            text = self.get_text(self.QUALITY_SCORE)
            # Parse score from text like "0.85" or "85%"
            text = text.replace("%", "").strip()
            score = float(text)
            return score if score <= 1.0 else score / 100.0
        except Exception:
            return None

    def is_clone_successful(self) -> bool:
        """Check if the clone operation was successful."""
        try:
            if self.is_displayed(self.ERROR_MESSAGE):
                return False
            if self.is_displayed(self.SUCCESS_MESSAGE):
                return True
            # Check for created profile ID as success indicator
            profile_id = self.get_created_profile_id()
            return bool(profile_id and profile_id.strip())
        except Exception:
            return False

    def get_error_message(self) -> str:
        """Get the error message if clone failed."""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except Exception:
            return ""

    # ==========================================================================
    # Help
    # ==========================================================================

    def show_help(self):
        """Show the help overlay."""
        if self.is_displayed(self.HELP_BUTTON):
            self.click(self.HELP_BUTTON)

    def is_help_visible(self) -> bool:
        """Check if help overlay is visible."""
        return self.is_displayed(self.HELP_OVERLAY)

    # ==========================================================================
    # Complete Workflow
    # ==========================================================================

    def complete_quick_clone_wizard(
        self,
        audio_file: str,
        profile_name: str | None = None,
        engine: str | None = None,
        quality_mode: str | None = None,
        wait_for_completion: bool = True,
        timeout: float = 120.0
    ) -> str:
        """
        Complete the entire quick clone workflow.

        Args:
            audio_file: Path to the reference audio file
            profile_name: Optional custom profile name
            engine: Optional engine override (uses auto-detect if not set)
            quality_mode: Optional quality mode override
            wait_for_completion: Whether to wait for cloning to complete
            timeout: Timeout for the clone operation

        Returns:
            Created profile ID
        """
        logger.info(f"Starting quick clone wizard with audio: {audio_file}")

        # Step 1: Select audio file
        self.select_audio_file(audio_file)

        # Wait for auto-detection
        time.sleep(1.0)

        # Step 2: Optionally override engine
        if engine:
            self.select_engine(engine)

        # Step 3: Optionally override quality mode
        if quality_mode:
            self.select_quality_mode(quality_mode)

        # Step 4: Set profile name if provided
        if profile_name:
            self.set_profile_name(profile_name)

        # Step 5: Start cloning
        if not self.is_quick_clone_enabled():
            raise RuntimeError("Quick Clone button is not enabled")

        self.click_quick_clone()

        # Step 6: Wait for completion if requested
        if wait_for_completion:
            self.wait_for_processing_complete(timeout)

            if not self.is_clone_successful():
                error = self.get_error_message()
                raise RuntimeError(f"Clone failed: {error}")

        profile_id = self.get_created_profile_id()
        logger.info(f"Quick clone completed, profile ID: {profile_id}")
        return profile_id
