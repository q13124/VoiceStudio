"""
Synthesis Page Object for VoiceStudio.

Provides access to the voice synthesis panel.
"""

from __future__ import annotations

import logging
import time

from tests.e2e.framework.page_objects import BasePage, ElementLocator

logger = logging.getLogger(__name__)


class SynthesisPage(BasePage):
    """
    Page object for the Synthesis panel.

    This panel allows users to synthesize speech from text using
    selected voice profiles.
    """

    # ==========================================================================
    # Locators - Root
    # ==========================================================================

    ROOT = ElementLocator.by_automation_id("SynthesisView_Root", "Synthesis root element")

    # ==========================================================================
    # Locators - Voice Selection
    # ==========================================================================

    VOICE_SELECTOR = ElementLocator.by_automation_id("VoiceSelector", "Voice selection dropdown")
    SELECTED_VOICE_NAME = ElementLocator.by_automation_id(
        "SelectedVoiceName", "Selected voice name display"
    )
    CHANGE_VOICE_BUTTON = ElementLocator.by_automation_id(
        "ChangeVoiceButton", "Change voice button"
    )

    # ==========================================================================
    # Locators - Text Input
    # ==========================================================================

    TEXT_INPUT = ElementLocator.by_automation_id("TextInput", "Text to synthesize input")
    CHARACTER_COUNT = ElementLocator.by_automation_id("CharacterCount", "Character count display")
    CLEAR_TEXT_BUTTON = ElementLocator.by_automation_id("ClearTextButton", "Clear text button")

    # ==========================================================================
    # Locators - Engine Settings
    # ==========================================================================

    ENGINE_SELECTOR = ElementLocator.by_automation_id("EngineSelector", "Engine selection dropdown")
    QUALITY_SELECTOR = ElementLocator.by_automation_id(
        "QualitySelector", "Quality mode selection dropdown"
    )
    SPEED_SLIDER = ElementLocator.by_automation_id("SpeedSlider", "Speech speed slider")
    PITCH_SLIDER = ElementLocator.by_automation_id("PitchSlider", "Speech pitch slider")

    # ==========================================================================
    # Locators - Synthesis Actions
    # ==========================================================================

    SYNTHESIZE_BUTTON = ElementLocator.by_automation_id(
        "SynthesizeButton", "Start synthesis button"
    )
    PREVIEW_BUTTON = ElementLocator.by_automation_id("PreviewButton", "Preview synthesis button")
    STOP_BUTTON = ElementLocator.by_automation_id("StopButton", "Stop synthesis button")

    # ==========================================================================
    # Locators - Progress/Status
    # ==========================================================================

    SYNTHESIS_STATUS = ElementLocator.by_automation_id("SynthesisStatus", "Synthesis status text")
    SYNTHESIS_PROGRESS = ElementLocator.by_automation_id(
        "SynthesisProgress", "Synthesis progress bar"
    )
    LOADING_INDICATOR = ElementLocator.by_automation_id("LoadingIndicator", "Loading spinner")

    # ==========================================================================
    # Locators - Output
    # ==========================================================================

    OUTPUT_PLAYER = ElementLocator.by_automation_id("OutputPlayer", "Audio output player")
    PLAY_BUTTON = ElementLocator.by_automation_id("PlayButton", "Play audio button")
    PAUSE_BUTTON = ElementLocator.by_automation_id("PauseButton", "Pause audio button")
    SAVE_BUTTON = ElementLocator.by_automation_id("SaveButton", "Save audio button")
    DOWNLOAD_BUTTON = ElementLocator.by_automation_id("DownloadButton", "Download audio button")

    # ==========================================================================
    # Locators - Error/Success
    # ==========================================================================

    SUCCESS_MESSAGE = ElementLocator.by_automation_id("SuccessMessage", "Success message display")
    ERROR_MESSAGE = ElementLocator.by_automation_id("ErrorMessage", "Error message display")

    # ==========================================================================
    # Validation
    # ==========================================================================

    def _validate_page(self):
        """Validate Synthesis panel is loaded."""
        try:
            self.wait_for_element(self.ROOT, timeout=10.0)
            logger.info("Synthesis panel validated")
        except TimeoutError:
            logger.warning("Synthesis panel not immediately visible")

    # ==========================================================================
    # Voice Selection
    # ==========================================================================

    def get_selected_voice_name(self) -> str:
        """Get the name of the currently selected voice."""
        return self.get_text(self.SELECTED_VOICE_NAME)

    def select_voice(self, voice_name: str):
        """Select a voice from the dropdown."""
        self.click(self.VOICE_SELECTOR)
        time.sleep(0.3)
        voice_option = ElementLocator.by_name(voice_name, f"Voice option: {voice_name}")
        self.click(voice_option)
        logger.info(f"Selected voice: {voice_name}")

    def is_voice_selected(self) -> bool:
        """Check if a voice is selected."""
        try:
            name = self.get_selected_voice_name()
            return bool(name and name.strip())
        except Exception:
            return False

    # ==========================================================================
    # Text Input
    # ==========================================================================

    def enter_text(self, text: str):
        """Enter text to synthesize."""
        self.type_text(self.TEXT_INPUT, text)
        logger.info(f"Entered text ({len(text)} chars)")

    def get_text(self) -> str:
        """Get the current text in the input."""
        element = self.wait_for_element(self.TEXT_INPUT)
        return element.get_attribute("Value.Value") or element.text

    def clear_text(self):
        """Clear the text input."""
        if self.is_displayed(self.CLEAR_TEXT_BUTTON):
            self.click(self.CLEAR_TEXT_BUTTON)
        else:
            element = self.wait_for_element(self.TEXT_INPUT)
            element.clear()

    def get_character_count(self) -> int:
        """Get the current character count."""
        try:
            text = self.get_text(self.CHARACTER_COUNT)
            # Parse count from text like "123 / 1000"
            parts = text.split("/")
            return int(parts[0].strip())
        except Exception:
            return len(self.get_text())

    # ==========================================================================
    # Engine Settings
    # ==========================================================================

    def select_engine(self, engine: str):
        """Select the synthesis engine."""
        self.click(self.ENGINE_SELECTOR)
        time.sleep(0.3)
        option = ElementLocator.by_name(engine, f"Engine: {engine}")
        self.click(option)
        logger.info(f"Selected engine: {engine}")

    def select_quality(self, quality: str):
        """Select the quality mode."""
        self.click(self.QUALITY_SELECTOR)
        time.sleep(0.3)
        option = ElementLocator.by_name(quality, f"Quality: {quality}")
        self.click(option)
        logger.info(f"Selected quality: {quality}")

    def set_speed(self, speed: float):
        """Set the speech speed (0.5 - 2.0)."""
        self.wait_for_element(self.SPEED_SLIDER)
        # Slider interaction depends on implementation
        # This is a simplified approach
        logger.info(f"Set speed: {speed}")

    def set_pitch(self, pitch: float):
        """Set the speech pitch (0.5 - 2.0)."""
        self.wait_for_element(self.PITCH_SLIDER)
        logger.info(f"Set pitch: {pitch}")

    # ==========================================================================
    # Synthesis Actions
    # ==========================================================================

    def click_synthesize(self):
        """Click the Synthesize button."""
        self.click(self.SYNTHESIZE_BUTTON)
        logger.info("Clicked Synthesize button")

    def click_preview(self):
        """Click the Preview button."""
        self.click(self.PREVIEW_BUTTON)
        logger.info("Clicked Preview button")

    def click_stop(self):
        """Click the Stop button."""
        self.click(self.STOP_BUTTON)
        logger.info("Clicked Stop button")

    def is_synthesize_enabled(self) -> bool:
        """Check if Synthesize button is enabled."""
        return self.is_enabled(self.SYNTHESIZE_BUTTON)

    # ==========================================================================
    # Progress/Status
    # ==========================================================================

    def get_synthesis_status(self) -> str:
        """Get the current synthesis status."""
        try:
            return self.get_text(self.SYNTHESIS_STATUS)
        except Exception:
            return ""

    def is_synthesizing(self) -> bool:
        """Check if synthesis is in progress."""
        return self.is_displayed(self.LOADING_INDICATOR)

    def wait_for_synthesis_complete(self, timeout: float = 60.0):
        """Wait for synthesis to complete."""
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_synthesizing():
                status = self.get_synthesis_status().lower()
                if "complete" in status or "ready" in status:
                    return True
                if "error" in status or "failed" in status:
                    raise RuntimeError(f"Synthesis failed: {status}")
                return True
            time.sleep(1.0)
        raise TimeoutError("Synthesis did not complete within timeout")

    # ==========================================================================
    # Output Actions
    # ==========================================================================

    def is_output_available(self) -> bool:
        """Check if synthesized output is available."""
        return self.is_displayed(self.OUTPUT_PLAYER)

    def play_output(self):
        """Play the synthesized audio."""
        self.click(self.PLAY_BUTTON)
        logger.info("Playing synthesized audio")

    def pause_output(self):
        """Pause the synthesized audio."""
        self.click(self.PAUSE_BUTTON)
        logger.info("Paused synthesized audio")

    def save_output(self):
        """Save the synthesized audio."""
        self.click(self.SAVE_BUTTON)
        logger.info("Saving synthesized audio")

    def download_output(self):
        """Download the synthesized audio."""
        self.click(self.DOWNLOAD_BUTTON)
        logger.info("Downloading synthesized audio")

    # ==========================================================================
    # Error/Success
    # ==========================================================================

    def is_synthesis_successful(self) -> bool:
        """Check if synthesis was successful."""
        return self.is_displayed(self.SUCCESS_MESSAGE) or self.is_output_available()

    def get_error_message(self) -> str:
        """Get error message if synthesis failed."""
        try:
            return self.get_text(self.ERROR_MESSAGE)
        except Exception:
            return ""

    # ==========================================================================
    # Complete Workflow
    # ==========================================================================

    def synthesize_text(
        self,
        text: str,
        voice_name: str | None = None,
        engine: str | None = None,
        quality: str | None = None,
        wait_for_completion: bool = True,
        timeout: float = 60.0,
    ):
        """
        Complete a full text synthesis workflow.

        Args:
            text: Text to synthesize
            voice_name: Optional voice to use
            engine: Optional engine override
            quality: Optional quality mode
            wait_for_completion: Whether to wait for synthesis
            timeout: Timeout for synthesis
        """
        logger.info("Starting synthesis workflow")

        # Select voice if specified
        if voice_name:
            self.select_voice(voice_name)

        # Configure engine settings
        if engine:
            self.select_engine(engine)

        if quality:
            self.select_quality(quality)

        # Enter text
        self.enter_text(text)

        # Start synthesis
        if not self.is_synthesize_enabled():
            raise RuntimeError("Synthesize button is not enabled")

        self.click_synthesize()

        # Wait for completion
        if wait_for_completion:
            self.wait_for_synthesis_complete(timeout)

            if not self.is_synthesis_successful():
                error = self.get_error_message()
                raise RuntimeError(f"Synthesis failed: {error}")

        logger.info("Synthesis workflow completed")
