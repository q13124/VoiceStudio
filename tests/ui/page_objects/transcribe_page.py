"""
Transcribe Page Object for VoiceStudio UI Tests.

Provides automation for the Transcription panel including:
- Audio selection for transcription
- Engine and language configuration
- Transcription execution
- Results inspection
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Optional

from .base_page import BasePage

if TYPE_CHECKING:
    from tests.ui.conftest import WinAppDriverElement


class TranscribePage(BasePage):
    """
    Page object for the Transcribe panel.

    Handles speech-to-text transcription workflow.
    """

    # Element automation IDs (from automation_ids.py)
    AUDIO_ID_INPUT = "TranscribeView_AudioIdInput"
    PROJECT_ID_INPUT = "TranscribeView_ProjectIdInput"
    ENGINE_COMBOBOX = "TranscribeView_EngineComboBox"
    LANGUAGE_COMBOBOX = "TranscribeView_LanguageComboBox"
    TRANSCRIBE_BUTTON = "TranscribeView_TranscribeButton"
    WORD_TIMESTAMPS_TOGGLE = "TranscribeView_WordTimestampsToggle"
    DIARIZATION_TOGGLE = "TranscribeView_DiarizationToggle"
    VAD_TOGGLE = "TranscribeView_VadToggle"
    TRANSCRIPTION_LIST = "TranscribeView_TranscriptionList"
    TEXT_DISPLAY = "TranscribeView_TextDisplay"

    @property
    def root_automation_id(self) -> str:
        return "TranscribeView_Root"

    @property
    def nav_automation_id(self) -> str:
        return "NavTranscribe"

    # =========================================================================
    # Transcription Configuration
    # =========================================================================

    def set_audio_id(self, audio_id: str) -> bool:
        """Set the audio ID for transcription."""
        return self.type_text(self.AUDIO_ID_INPUT, audio_id)

    def set_project_id(self, project_id: str) -> bool:
        """Set the project ID for transcription."""
        return self.type_text(self.PROJECT_ID_INPUT, project_id)

    def select_engine(self, engine_name: str) -> bool:
        """Select transcription engine."""
        return self.select_combobox_item(self.ENGINE_COMBOBOX, engine_name)

    def select_language(self, language: str) -> bool:
        """Select transcription language."""
        return self.select_combobox_item(self.LANGUAGE_COMBOBOX, language)

    def toggle_word_timestamps(self) -> bool:
        """Toggle word timestamps option."""
        return self.click_with_retry(self.WORD_TIMESTAMPS_TOGGLE)

    def toggle_diarization(self) -> bool:
        """Toggle speaker diarization option."""
        return self.click_with_retry(self.DIARIZATION_TOGGLE)

    def toggle_vad(self) -> bool:
        """Toggle voice activity detection option."""
        return self.click_with_retry(self.VAD_TOGGLE)

    # =========================================================================
    # Transcription Actions
    # =========================================================================

    def start_transcription(self) -> bool:
        """Click the transcribe button to start transcription."""
        return self.click_with_retry(self.TRANSCRIBE_BUTTON)

    def wait_for_transcription_complete(self, timeout: float = 120.0) -> bool:
        """
        Wait for transcription to complete.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            True if transcription completed.
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.get_transcription_text():
                return True
            time.sleep(1.0)
        return False

    # =========================================================================
    # Results
    # =========================================================================

    def get_transcription_text(self) -> Optional[str]:
        """Get the transcribed text from the display."""
        return self.get_text(self.TEXT_DISPLAY)

    def get_transcription_list_items(self) -> list[WinAppDriverElement]:
        """Get list of transcription items."""
        try:
            list_view = self.find_element(self.TRANSCRIPTION_LIST)
            return list_view.find_elements("class name", "ListViewItem")
        except RuntimeError:
            return []

    # =========================================================================
    # Workflow Convenience
    # =========================================================================

    def transcribe_audio(
        self,
        audio_id: str,
        engine: str = "Whisper",
        language: str = "English",
        wait_complete: bool = True,
        timeout: float = 120.0,
    ) -> Optional[str]:
        """
        Full transcription workflow.

        Args:
            audio_id: ID of audio to transcribe.
            engine: Transcription engine name.
            language: Target language.
            wait_complete: Whether to wait for completion.
            timeout: Maximum wait time.

        Returns:
            Transcribed text if successful, None otherwise.
        """
        if not self.is_loaded():
            if not self.navigate():
                return None

        self.set_audio_id(audio_id)
        self.select_engine(engine)
        self.select_language(language)

        if not self.start_transcription():
            return None

        if wait_complete:
            if self.wait_for_transcription_complete(timeout):
                return self.get_transcription_text()

        return None
