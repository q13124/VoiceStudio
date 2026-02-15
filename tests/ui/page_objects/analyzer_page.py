"""
Analyzer Page Object.

Provides methods for interacting with the audio analysis panel.
"""

import time
from typing import TYPE_CHECKING

from .base_page import BasePage

if TYPE_CHECKING:
    pass


class AnalyzerPage(BasePage):
    """Page object for the Analyzer panel."""

    # =========================================================================
    # Automation IDs
    # =========================================================================

    @property
    def root_automation_id(self) -> str:
        return "AnalyzerView_Root"

    @property
    def nav_automation_id(self) -> str:
        return "NavAnalyze"

    # Main elements
    TAB_VIEW = "Analyzer_TabView"
    HELP_BUTTON = "Analyzer_HelpButton"

    # File selection
    FILE_PATH_INPUT = "Analyzer_FilePathInput"
    BROWSE_BUTTON = "Analyzer_BrowseButton"
    DROP_ZONE = "Analyzer_DropZone"

    # Analysis controls
    ANALYZE_BUTTON = "Analyzer_AnalyzeButton"
    COMPARE_BUTTON = "Analyzer_CompareButton"
    EXPORT_BUTTON = "Analyzer_ExportButton"

    # Results area
    RESULTS_PANEL = "Analyzer_ResultsPanel"
    WAVEFORM_DISPLAY = "Analyzer_WaveformDisplay"
    SPECTRUM_DISPLAY = "Analyzer_SpectrumDisplay"
    METRICS_PANEL = "Analyzer_MetricsPanel"

    # Status
    STATUS_TEXT = "Analyzer_StatusText"
    PROGRESS_RING = "Analyzer_ProgressRing"

    # Tabs
    TAB_WAVEFORM = "Analyzer_Tab_Waveform"
    TAB_SPECTRUM = "Analyzer_Tab_Spectrum"
    TAB_METRICS = "Analyzer_Tab_Metrics"
    TAB_COMPARISON = "Analyzer_Tab_Comparison"

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def file_path(self) -> str | None:
        """Get the current file path input value."""
        return self.get_text(self.FILE_PATH_INPUT)

    @property
    def status_text(self) -> str | None:
        """Get the current status text."""
        return self.get_text(self.STATUS_TEXT)

    @property
    def is_analyze_enabled(self) -> bool:
        """Check if the analyze button is enabled."""
        try:
            element = self.find_element(self.ANALYZE_BUTTON, timeout=2)
            return element.is_enabled()
        except RuntimeError:
            return False

    @property
    def is_analyzing(self) -> bool:
        """Check if analysis is in progress."""
        return self.element_exists(self.PROGRESS_RING)

    # =========================================================================
    # Actions
    # =========================================================================

    def enter_file_path(self, path: str) -> bool:
        """
        Enter a file path for analysis.

        Args:
            path: The file path to analyze.

        Returns:
            True if successful.
        """
        return self.type_text(self.FILE_PATH_INPUT, path)

    def click_browse(self) -> bool:
        """
        Click the browse button to open file dialog.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.BROWSE_BUTTON)

    def click_analyze(self) -> bool:
        """
        Click the analyze button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.ANALYZE_BUTTON)

    def click_compare(self) -> bool:
        """
        Click the compare button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.COMPARE_BUTTON)

    def click_export(self) -> bool:
        """
        Click the export button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.EXPORT_BUTTON)

    def click_help(self) -> bool:
        """
        Click the help button.

        Returns:
            True if successful.
        """
        return self.click_with_retry(self.HELP_BUTTON)

    def select_tab(self, tab_name: str) -> bool:
        """
        Select an analysis tab.

        Args:
            tab_name: Tab name (waveform, spectrum, metrics, comparison).

        Returns:
            True if successful.
        """
        tab_ids = {
            "waveform": self.TAB_WAVEFORM,
            "spectrum": self.TAB_SPECTRUM,
            "metrics": self.TAB_METRICS,
            "comparison": self.TAB_COMPARISON,
        }

        tab_id = tab_ids.get(tab_name.lower())
        if not tab_id:
            return False

        return self.click_with_retry(tab_id)

    # =========================================================================
    # Workflows
    # =========================================================================

    def analyze_file(
        self,
        file_path: str,
        wait_for_completion: bool = True,
        timeout: float = 30.0
    ) -> bool:
        """
        Complete workflow to analyze a file.

        Args:
            file_path: Path to the audio file.
            wait_for_completion: Whether to wait for analysis to complete.
            timeout: Maximum time to wait for completion.

        Returns:
            True if analysis started (and completed if wait_for_completion).
        """
        # Enter file path
        if not self.enter_file_path(file_path):
            return False

        time.sleep(0.3)

        # Click analyze
        if not self.click_analyze():
            return False

        if wait_for_completion:
            return self.wait_for_analysis_complete(timeout)

        return True

    def wait_for_analysis_complete(self, timeout: float = 30.0) -> bool:
        """
        Wait for analysis to complete.

        Args:
            timeout: Maximum time to wait.

        Returns:
            True if analysis completed within timeout.
        """
        start = time.time()
        while time.time() - start < timeout:
            if not self.is_analyzing:
                # Verify results are visible
                if self.element_exists(self.RESULTS_PANEL):
                    return True
            time.sleep(0.5)
        return False

    def verify_elements_present(self) -> dict:
        """
        Verify all critical elements are present.

        Returns:
            Dictionary with element names and their presence status.
        """
        elements = {
            "root": self.root_automation_id,
            "tab_view": self.TAB_VIEW,
            "browse_button": self.BROWSE_BUTTON,
            "analyze_button": self.ANALYZE_BUTTON,
        }

        return {
            name: self.element_exists(auto_id)
            for name, auto_id in elements.items()
        }

    def get_active_tab(self) -> str | None:
        """
        Get the name of the currently active tab.

        Returns:
            Tab name or None if cannot determine.
        """
        tab_checks = [
            ("waveform", self.TAB_WAVEFORM),
            ("spectrum", self.TAB_SPECTRUM),
            ("metrics", self.TAB_METRICS),
            ("comparison", self.TAB_COMPARISON),
        ]

        for tab_name, tab_id in tab_checks:
            try:
                element = self.find_element(tab_id, timeout=1)
                # Check if tab is selected (implementation depends on UI)
                if "selected" in element.get_attribute("SelectionItem.IsSelected"):
                    return tab_name
            except (RuntimeError, AttributeError):
                continue

        return None
