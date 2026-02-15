"""
Voice Browser Page Object for VoiceStudio.

Provides access to the Voice Browser panel for managing voice profiles.
"""

import logging
import time

from tests.e2e.framework.page_objects import BasePage, ElementLocator

logger = logging.getLogger(__name__)


class VoiceBrowserPage(BasePage):
    """
    Page object for the Voice Browser panel.

    This panel displays and manages voice profiles, allowing users to
    browse, preview, edit, and delete voice profiles.
    """

    # ==========================================================================
    # Locators - Root
    # ==========================================================================

    ROOT = ElementLocator.by_automation_id(
        "VoiceBrowserView_Root", "Voice Browser root element"
    )

    # ==========================================================================
    # Locators - Search/Filter
    # ==========================================================================

    SEARCH_INPUT = ElementLocator.by_automation_id(
        "SearchInput", "Voice search input"
    )
    FILTER_DROPDOWN = ElementLocator.by_automation_id(
        "FilterDropdown", "Voice filter dropdown"
    )
    SORT_DROPDOWN = ElementLocator.by_automation_id(
        "SortDropdown", "Voice sort dropdown"
    )

    # ==========================================================================
    # Locators - Voice List
    # ==========================================================================

    VOICE_LIST = ElementLocator.by_automation_id(
        "VoiceList", "Voice profiles list"
    )
    VOICE_LIST_ITEM = ElementLocator.by_automation_id(
        "VoiceListItem", "Voice profile list item"
    )
    VOICE_CARD = ElementLocator.by_automation_id(
        "VoiceCard", "Voice profile card"
    )
    EMPTY_STATE = ElementLocator.by_automation_id(
        "EmptyState", "Empty state message"
    )

    # ==========================================================================
    # Locators - Voice Item Details
    # ==========================================================================

    VOICE_NAME = ElementLocator.by_automation_id(
        "VoiceName", "Voice name text"
    )
    VOICE_ENGINE = ElementLocator.by_automation_id(
        "VoiceEngine", "Voice engine badge"
    )
    VOICE_QUALITY = ElementLocator.by_automation_id(
        "VoiceQuality", "Voice quality indicator"
    )

    # ==========================================================================
    # Locators - Actions
    # ==========================================================================

    PREVIEW_BUTTON = ElementLocator.by_automation_id(
        "PreviewButton", "Preview voice button"
    )
    EDIT_BUTTON = ElementLocator.by_automation_id(
        "EditButton", "Edit voice button"
    )
    DELETE_BUTTON = ElementLocator.by_automation_id(
        "DeleteButton", "Delete voice button"
    )
    USE_BUTTON = ElementLocator.by_automation_id(
        "UseVoiceButton", "Use voice for synthesis button"
    )

    # ==========================================================================
    # Locators - Help
    # ==========================================================================

    HELP_OVERLAY = ElementLocator.by_automation_id(
        "HelpOverlay", "Help overlay"
    )

    # ==========================================================================
    # Validation
    # ==========================================================================

    def _validate_page(self):
        """Validate Voice Browser panel is loaded."""
        try:
            self.wait_for_element(self.ROOT, timeout=10.0)
            logger.info("Voice Browser panel validated")
        except TimeoutError:
            logger.warning("Voice Browser panel not immediately visible")

    # ==========================================================================
    # Search/Filter
    # ==========================================================================

    def search_voices(self, query: str):
        """Search for voices by name or keyword."""
        self.type_text(self.SEARCH_INPUT, query)
        # Wait for search results to update
        time.sleep(0.5)
        logger.info(f"Searched for voices: {query}")

    def clear_search(self):
        """Clear the search input."""
        element = self.wait_for_element(self.SEARCH_INPUT)
        element.clear()
        time.sleep(0.3)

    def filter_by_engine(self, engine: str):
        """Filter voices by engine type."""
        self.click(self.FILTER_DROPDOWN)
        time.sleep(0.3)
        engine_option = ElementLocator.by_name(engine, f"Engine filter: {engine}")
        self.click(engine_option)
        time.sleep(0.5)
        logger.info(f"Filtered by engine: {engine}")

    def sort_by(self, sort_option: str):
        """Sort voices by specified option."""
        self.click(self.SORT_DROPDOWN)
        time.sleep(0.3)
        option = ElementLocator.by_name(sort_option, f"Sort option: {sort_option}")
        self.click(option)
        time.sleep(0.5)
        logger.info(f"Sorted by: {sort_option}")

    # ==========================================================================
    # Voice List
    # ==========================================================================

    def get_voice_count(self) -> int:
        """Get the number of voices in the list."""
        try:
            items = self.find_elements(self.VOICE_LIST_ITEM)
            return len(items)
        except Exception:
            return 0

    def is_empty(self) -> bool:
        """Check if the voice list is empty."""
        return self.is_displayed(self.EMPTY_STATE) or self.get_voice_count() == 0

    def get_voice_names(self) -> list[str]:
        """Get all voice names in the list."""
        names = []
        items = self.find_elements(self.VOICE_LIST_ITEM)
        for item in items:
            try:
                name_element = item.find_element("accessibility id", "VoiceName")
                names.append(name_element.text)
            except Exception:
                continue
        return names

    def find_voice_by_name(self, name: str) -> bool:
        """Check if a voice with the given name exists."""
        self.search_voices(name)
        time.sleep(0.5)
        names = self.get_voice_names()
        return any(name.lower() in n.lower() for n in names)

    def select_voice_by_name(self, name: str):
        """Select a voice by its name."""
        self.search_voices(name)
        time.sleep(0.5)

        items = self.find_elements(self.VOICE_LIST_ITEM)
        for item in items:
            try:
                name_element = item.find_element("accessibility id", "VoiceName")
                if name.lower() in name_element.text.lower():
                    item.click()
                    logger.info(f"Selected voice: {name}")
                    return
            except Exception:
                continue

        raise ValueError(f"Voice not found: {name}")

    def select_voice_by_index(self, index: int):
        """Select a voice by its index in the list."""
        items = self.find_elements(self.VOICE_LIST_ITEM)
        if index >= len(items):
            raise IndexError(f"Voice index {index} out of range (max: {len(items) - 1})")

        items[index].click()
        logger.info(f"Selected voice at index: {index}")

    # ==========================================================================
    # Voice Actions
    # ==========================================================================

    def preview_selected_voice(self):
        """Preview the currently selected voice."""
        self.click(self.PREVIEW_BUTTON)
        logger.info("Started voice preview")

    def edit_selected_voice(self):
        """Open edit dialog for the selected voice."""
        self.click(self.EDIT_BUTTON)
        logger.info("Opened voice edit dialog")

    def delete_selected_voice(self, confirm: bool = True):
        """Delete the currently selected voice."""
        self.click(self.DELETE_BUTTON)

        # Handle confirmation dialog
        if confirm:
            confirm_button = ElementLocator.by_automation_id(
                "ConfirmDeleteButton", "Confirm delete button"
            )
            try:
                self.click(confirm_button)
                logger.info("Deleted selected voice")
            except Exception:
                # Try alternative confirmation button
                ok_button = ElementLocator.by_name("OK", "OK button")
                self.click(ok_button)

    def use_selected_voice(self):
        """Use the selected voice for synthesis."""
        self.click(self.USE_BUTTON)
        logger.info("Selected voice for synthesis")

    # ==========================================================================
    # Wait Helpers
    # ==========================================================================

    def wait_for_voice_to_appear(self, name: str, timeout: float = 30.0) -> bool:
        """Wait for a voice with the given name to appear in the list."""
        start = time.time()
        while time.time() - start < timeout:
            if self.find_voice_by_name(name):
                return True
            time.sleep(1.0)
        return False

    def wait_for_voice_to_disappear(self, name: str, timeout: float = 30.0) -> bool:
        """Wait for a voice to be removed from the list."""
        start = time.time()
        while time.time() - start < timeout:
            if not self.find_voice_by_name(name):
                return True
            time.sleep(1.0)
        return False
