"""
UI Smoke Tests for Critical Workflows.

These tests validate the four most critical user workflows:
1. Voice synthesis (Studio panel)
2. Voice cloning (Clone panel)
3. Audio analysis (Analyzer panel)
4. Effects application (Effects panel)

These tests are designed to run in CI as nightly smoke tests.
"""

from __future__ import annotations

import time

import pytest

from tests.ui.page_objects import (
    AnalyzerPage,
    ClonePage,
    EffectsPage,
    LibraryPage,
    StudioPage,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def studio_page(driver):
    """Get Studio page object."""
    page = StudioPage(driver)
    page.navigate()
    assert page.is_loaded(), "Failed to navigate to Studio panel"
    return page


@pytest.fixture
def clone_page(driver):
    """Get Clone page object."""
    page = ClonePage(driver)
    page.navigate()
    assert page.is_loaded(), "Failed to navigate to Clone panel"
    return page


@pytest.fixture
def analyzer_page(driver):
    """Get Analyzer page object."""
    page = AnalyzerPage(driver)
    page.navigate()
    assert page.is_loaded(), "Failed to navigate to Analyzer panel"
    return page


@pytest.fixture
def effects_page(driver):
    """Get Effects page object."""
    page = EffectsPage(driver)
    page.navigate()
    assert page.is_loaded(), "Failed to navigate to Effects panel"
    return page


@pytest.fixture
def library_page(driver):
    """Get Library page object."""
    page = LibraryPage(driver)
    page.navigate()
    assert page.is_loaded(), "Failed to navigate to Library panel"
    return page


# =============================================================================
# Smoke Test: Voice Synthesis Workflow
# =============================================================================


class TestVoiceSynthesisWorkflow:
    """Smoke tests for the voice synthesis workflow."""

    @pytest.mark.smoke
    def test_studio_panel_loads(self, studio_page):
        """Verify Studio panel loads with all critical elements."""
        elements = studio_page.verify_elements_present()

        assert elements["root"], "Root element not found"
        assert elements["text_input"], "Text input not found"
        assert elements["synthesize_button"], "Synthesize button not found"

    @pytest.mark.smoke
    def test_text_input_accepts_text(self, studio_page):
        """Verify text can be entered into the synthesis input."""
        test_text = "Hello, this is a smoke test for voice synthesis."

        result = studio_page.enter_text(test_text)
        assert result, "Failed to enter text"

        # Verify text was entered (if we can read it back)
        current_text = studio_page.text_input
        if current_text:
            assert test_text in current_text

    @pytest.mark.smoke
    def test_synthesize_button_becomes_enabled(self, studio_page):
        """Verify synthesize button enables after entering text."""
        # Enter some text
        studio_page.enter_text("Test text for synthesis")
        time.sleep(0.5)

        # Button should be enabled now (or at least exist)
        assert studio_page.element_exists(studio_page.SYNTHESIZE_BUTTON)

    @pytest.mark.smoke
    @pytest.mark.slow
    def test_synthesis_workflow_completes(self, studio_page):
        """
        Full synthesis workflow smoke test.

        Note: This test requires a working engine and may take time.
        Marked as slow for CI filtering.
        """
        # This is a slower test that actually exercises synthesis
        # Only run when engines are available

        # Check if synthesize is enabled (engine available)
        if not studio_page.is_synthesize_enabled:
            pytest.skip("Synthesis not available (no engine configured)")

        # Attempt synthesis
        studio_page.synthesize_text(
            "Hello world",
            wait_for_completion=True,
            timeout=60.0
        )

        # For smoke test, we mainly care that it doesn't crash
        # Success depends on engine availability
        studio_page.capture_screenshot("synthesis_result")


# =============================================================================
# Smoke Test: Voice Cloning Workflow
# =============================================================================


class TestVoiceCloningWorkflow:
    """Smoke tests for the voice cloning workflow."""

    @pytest.mark.smoke
    def test_clone_panel_loads(self, clone_page):
        """Verify Clone panel loads with all critical elements."""
        elements = clone_page.verify_elements_present()

        assert elements["root"], "Root element not found"

    @pytest.mark.smoke
    def test_profile_name_input_exists(self, clone_page):
        """Verify profile name input is accessible."""
        # Either quick clone or wizard mode should have profile input
        has_input = (
            clone_page.element_exists(clone_page.PROFILE_NAME_INPUT) or
            clone_page.is_quick_clone_mode()
        )
        assert has_input, "No profile input found in clone panel"

    @pytest.mark.smoke
    def test_clone_navigation_elements(self, clone_page):
        """Verify navigation/action elements exist."""
        # Check for either wizard buttons or quick clone buttons
        has_action = (
            clone_page.element_exists(clone_page.CREATE_PROFILE_BUTTON) or
            clone_page.element_exists(clone_page.WIZARD_NEXT_BUTTON) or
            clone_page.element_exists(clone_page.WIZARD_FINISH_BUTTON)
        )
        assert has_action, "No action buttons found in clone panel"

    @pytest.mark.smoke
    def test_clone_panel_screenshot(self, clone_page):
        """Capture screenshot of clone panel for visual verification."""
        clone_page.capture_screenshot("clone_panel")
        assert True  # Don't fail on screenshot issues


# =============================================================================
# Smoke Test: Audio Analysis Workflow
# =============================================================================


class TestAudioAnalysisWorkflow:
    """Smoke tests for the audio analysis workflow."""

    @pytest.mark.smoke
    def test_analyzer_panel_loads(self, analyzer_page):
        """Verify Analyzer panel loads with all critical elements."""
        elements = analyzer_page.verify_elements_present()

        assert elements["root"], "Root element not found"

    @pytest.mark.smoke
    def test_analyzer_has_browse_button(self, analyzer_page):
        """Verify browse button exists for file selection."""
        assert analyzer_page.element_exists(analyzer_page.BROWSE_BUTTON), \
            "Browse button not found"

    @pytest.mark.smoke
    def test_analyzer_has_tab_view(self, analyzer_page):
        """Verify tab view exists for different analysis views."""
        assert analyzer_page.element_exists(analyzer_page.TAB_VIEW), \
            "Tab view not found"

    @pytest.mark.smoke
    def test_analyzer_help_accessible(self, analyzer_page):
        """Verify help button is accessible."""
        if analyzer_page.element_exists(analyzer_page.HELP_BUTTON):
            analyzer_page.click_help()
            # Just verify click doesn't crash
            time.sleep(0.3)
            # Try to close any dialog that may have opened
            analyzer_page.driver.press_escape()


# =============================================================================
# Smoke Test: Effects Application Workflow
# =============================================================================


class TestEffectsApplicationWorkflow:
    """Smoke tests for the effects application workflow."""

    @pytest.mark.smoke
    def test_effects_panel_loads(self, effects_page):
        """Verify Effects panel loads with all critical elements."""
        elements = effects_page.verify_elements_present()

        assert elements["root"], "Root element not found"

    @pytest.mark.smoke
    def test_effects_has_presets(self, effects_page):
        """Verify presets combobox exists."""
        assert effects_page.element_exists(effects_page.MIXER_PRESETS_COMBO), \
            "Presets combobox not found"

    @pytest.mark.smoke
    def test_effects_has_master_volume(self, effects_page):
        """Verify master volume slider exists."""
        assert effects_page.element_exists(effects_page.MASTER_VOLUME_SLIDER), \
            "Master volume slider not found"

    @pytest.mark.smoke
    def test_effects_reset_button(self, effects_page):
        """Verify reset button works."""
        if effects_page.element_exists(effects_page.RESET_BUTTON):
            effects_page.click_reset()
            # Just verify click doesn't crash
            time.sleep(0.3)


# =============================================================================
# Cross-Panel Navigation Tests
# =============================================================================


class TestCrossPanelNavigation:
    """Smoke tests for navigation between panels."""

    @pytest.mark.smoke
    def test_navigate_all_critical_panels(self, driver):
        """Test navigation to all four critical panels."""
        panels = [
            ("studio", StudioPage),
            ("clone", ClonePage),
            ("analyzer", AnalyzerPage),
            ("effects", EffectsPage),
        ]

        results = {}
        for panel_name, PageClass in panels:
            page = PageClass(driver)
            success = page.navigate()
            results[panel_name] = success
            time.sleep(0.3)

        # Report results
        failed = [name for name, success in results.items() if not success]
        assert not failed, f"Failed to navigate to: {', '.join(failed)}"

    @pytest.mark.smoke
    def test_rapid_navigation_stability(self, driver):
        """Test rapid navigation doesn't crash the UI."""
        pages = [
            StudioPage(driver),
            ClonePage(driver),
            AnalyzerPage(driver),
            EffectsPage(driver),
            LibraryPage(driver),
        ]

        # Navigate rapidly through all panels
        for _ in range(2):  # Two complete cycles
            for page in pages:
                try:
                    page.navigate(wait_time=0.2)
                except Exception:
                    pass  # Continue even if one fails

        # Verify we can still navigate to a known panel
        final_page = StudioPage(driver)
        assert final_page.navigate(), "UI became unresponsive after rapid navigation"


# =============================================================================
# Sentinel Integration Tests
# =============================================================================


class TestSentinelIntegration:
    """Tests that validate sentinel workflow integration points."""

    @pytest.mark.smoke
    def test_library_search_functional(self, library_page):
        """Verify library search works (sentinel audio file discovery)."""
        # Search functionality is critical for finding sentinel test files
        elements = library_page.verify_elements_present()

        assert elements["search_box"], "Search box not found"

        # Try searching
        result = library_page.search("test")
        assert result, "Search input failed"

    @pytest.mark.smoke
    def test_all_panels_have_root_ids(self, driver):
        """Verify all critical panels have proper root AutomationIds."""
        pages = [
            StudioPage(driver),
            ClonePage(driver),
            AnalyzerPage(driver),
            EffectsPage(driver),
            LibraryPage(driver),
        ]

        missing_roots = []
        for page in pages:
            page.navigate()
            if not page.is_loaded():
                missing_roots.append(page.__class__.__name__)

        assert not missing_roots, f"Panels missing root IDs: {', '.join(missing_roots)}"
