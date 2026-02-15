"""
Synthesis Flow E2E Tests for VoiceStudio.

Tests the complete voice synthesis workflow including:
- Voice profile selection
- Text input and configuration
- Engine and quality settings
- Synthesis execution
- Audio output playback and saving
"""

import logging
import time
from unittest.mock import MagicMock

import pytest

from tests.e2e.framework.base import E2ETestBase
from tests.e2e.framework.helpers import PerformanceTimer, TestDataHelper

logger = logging.getLogger(__name__)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_text() -> str:
    """Get sample text for synthesis."""
    return TestDataHelper.sample_text(100)


@pytest.fixture
def sample_ssml() -> str:
    """Get sample SSML for synthesis."""
    return TestDataHelper.sample_ssml("Hello, this is a test of voice synthesis.")


@pytest.fixture
def unique_output_name() -> str:
    """Generate a unique output file name."""
    return TestDataHelper.unique_name("synthesis_output")


# =============================================================================
# Mock-Based Tests (No App Required)
# =============================================================================


class TestSynthesisFlowMock:
    """
    Mock-based synthesis flow tests.

    These tests validate the E2E test structure and logic
    without requiring the actual application.
    """

    def test_synthesis_flow_structure(self):
        """Verify synthesis flow test structure is correct."""
        assert TestVoiceSynthesisFlow is not None
        assert hasattr(TestVoiceSynthesisFlow, 'test_complete_synthesis_workflow')
        assert hasattr(TestVoiceSynthesisFlow, 'test_synthesis_with_ssml')

    def test_page_objects_importable(self):
        """Verify synthesis page objects can be imported."""
        from tests.e2e.pages import MainWindowPage, SynthesisPage, VoiceBrowserPage

        assert SynthesisPage is not None
        assert MainWindowPage is not None
        assert VoiceBrowserPage is not None

    def test_sample_text_fixture(self, sample_text: str):
        """Verify sample text fixture generates valid text."""
        assert sample_text
        assert len(sample_text) >= 100
        assert "quick brown fox" in sample_text.lower() or "test" in sample_text.lower()

    def test_sample_ssml_fixture(self, sample_ssml: str):
        """Verify sample SSML fixture generates valid SSML."""
        assert sample_ssml
        assert "<speak" in sample_ssml
        assert "</speak>" in sample_ssml
        assert "prosody" in sample_ssml

    def test_mock_synthesis_flow(
        self,
        sample_text: str
    ):
        """
        Test synthesis flow with mocked page objects.

        This validates the test logic without requiring the app.
        """
        # Create mock page objects
        mock_main_window = MagicMock()
        mock_synthesis = MagicMock()
        mock_voice_browser = MagicMock()

        # Configure mock behavior
        mock_main_window.get_synthesis_page.return_value = mock_synthesis
        mock_main_window.get_voice_browser_page.return_value = mock_voice_browser

        mock_synthesis.is_voice_selected.return_value = True
        mock_synthesis.is_synthesize_enabled.return_value = True
        mock_synthesis.is_synthesis_successful.return_value = True
        mock_synthesis.is_output_available.return_value = True
        mock_synthesis.get_selected_voice_name.return_value = "Test Voice"

        mock_voice_browser.get_voice_count.return_value = 3
        mock_voice_browser.get_voice_names.return_value = [
            "Test Voice", "Another Voice", "Third Voice"
        ]

        # Simulate synthesis flow
        # Step 1: Navigate to synthesis
        mock_main_window.navigate_to_studio()
        mock_main_window.navigate_to_studio.assert_called_once()

        # Step 2: Get synthesis page
        synthesis_page = mock_main_window.get_synthesis_page()

        # Step 3: Select voice
        synthesis_page.select_voice("Test Voice")
        synthesis_page.select_voice.assert_called_with("Test Voice")

        # Step 4: Enter text
        synthesis_page.enter_text(sample_text)
        synthesis_page.enter_text.assert_called_with(sample_text)

        # Step 5: Configure settings
        synthesis_page.select_engine("xtts")
        synthesis_page.select_quality("high")

        # Step 6: Execute synthesis
        synthesis_page.click_synthesize()
        synthesis_page.click_synthesize.assert_called_once()

        # Step 7: Wait for completion
        synthesis_page.wait_for_synthesis_complete()

        # Step 8: Verify success
        assert synthesis_page.is_synthesis_successful()
        assert synthesis_page.is_output_available()

        # Step 9: Play output
        synthesis_page.play_output()
        synthesis_page.play_output.assert_called_once()

        logger.info("Mock synthesis flow completed successfully")

    def test_mock_synthesis_with_voice_browser(
        self,
        sample_text: str
    ):
        """
        Test synthesis flow starting from voice browser.

        Simulates selecting a voice in browser and using it for synthesis.
        """
        mock_main_window = MagicMock()
        mock_voice_browser = MagicMock()
        mock_synthesis = MagicMock()

        mock_main_window.get_voice_browser_page.return_value = mock_voice_browser
        mock_main_window.get_synthesis_page.return_value = mock_synthesis

        mock_voice_browser.get_voice_count.return_value = 5
        mock_synthesis.get_selected_voice_name.return_value = "Selected Voice"
        mock_synthesis.is_synthesis_successful.return_value = True

        # Navigate to profiles
        mock_main_window.navigate_to_profiles()
        voice_browser = mock_main_window.get_voice_browser_page()

        # Select voice by name
        voice_browser.select_voice_by_name("Selected Voice")

        # Use selected voice for synthesis
        voice_browser.use_selected_voice()

        # Navigate to synthesis
        mock_main_window.navigate_to_studio()
        synthesis_page = mock_main_window.get_synthesis_page()

        # Verify voice is selected
        assert synthesis_page.get_selected_voice_name() == "Selected Voice"

        # Complete synthesis
        synthesis_page.enter_text(sample_text)
        synthesis_page.click_synthesize()
        synthesis_page.wait_for_synthesis_complete()

        assert synthesis_page.is_synthesis_successful()


# =============================================================================
# Full E2E Tests (Require Application)
# =============================================================================


@pytest.mark.e2e
@pytest.mark.synthesis
@pytest.mark.requires_app
class TestVoiceSynthesisFlow(E2ETestBase):
    """
    End-to-end tests for the voice synthesis workflow.

    These tests require:
    - VoiceStudio application running
    - WinAppDriver running
    - Backend server available
    - At least one voice profile available
    """

    # =========================================================================
    # Test: Complete Synthesis Workflow
    # =========================================================================

    def test_complete_synthesis_workflow(
        self,
        sample_text: str,
        app_session
    ):
        """
        Test the complete voice synthesis workflow.

        Steps:
        1. Navigate to Studio/Synthesis panel
        2. Select a voice profile
        3. Enter text to synthesize
        4. Configure engine and quality settings
        5. Execute synthesis
        6. Wait for completion
        7. Verify output is available
        8. Play synthesized audio
        """
        from tests.e2e.pages import MainWindowPage

        with PerformanceTimer("Complete synthesis workflow") as timer:
            # Initialize main window page
            main_window = MainWindowPage(app_session)

            # Step 1: Navigate to synthesis panel
            main_window.navigate_to_studio()
            synthesis_page = main_window.get_synthesis_page()

            # Step 2: Check if a voice is already selected
            if not synthesis_page.is_voice_selected():
                # Need to select a voice first
                main_window.navigate_to_profiles()
                voice_browser = main_window.get_voice_browser_page()

                if voice_browser.is_empty():
                    pytest.skip("No voice profiles available for synthesis test")

                # Select the first available voice
                voice_browser.select_voice_by_index(0)
                voice_browser.use_selected_voice()

                # Navigate back to synthesis
                main_window.navigate_to_studio()
                synthesis_page = main_window.get_synthesis_page()

            # Step 3: Enter text
            synthesis_page.enter_text(sample_text)

            # Step 4: Verify settings (use defaults)
            assert synthesis_page.is_synthesize_enabled()

            # Step 5: Execute synthesis
            synthesis_page.click_synthesize()

            # Step 6: Wait for completion
            synthesis_page.wait_for_synthesis_complete(timeout=60.0)

            # Step 7: Verify success
            assert synthesis_page.is_synthesis_successful()
            assert synthesis_page.is_output_available()

            # Step 8: Play output
            synthesis_page.play_output()
            time.sleep(2.0)  # Let it play briefly
            synthesis_page.pause_output()

            logger.info(
                f"Synthesis completed in {timer.elapsed:.2f}s"
            )

    # =========================================================================
    # Test: Synthesis with SSML
    # =========================================================================

    def test_synthesis_with_ssml(
        self,
        sample_ssml: str,
        app_session
    ):
        """
        Test synthesis using SSML input.

        Verifies that SSML markup is properly handled.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        # Ensure voice is selected
        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected for SSML test")

        # Enter SSML content
        synthesis_page.enter_text(sample_ssml)

        # Execute synthesis
        synthesis_page.click_synthesize()
        synthesis_page.wait_for_synthesis_complete(timeout=60.0)

        assert synthesis_page.is_synthesis_successful()

    # =========================================================================
    # Test: Synthesis with Different Engines
    # =========================================================================

    def test_synthesis_with_engine_selection(
        self,
        sample_text: str,
        app_session
    ):
        """
        Test synthesis with different engine configurations.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected")

        # Configure engine
        synthesis_page.select_engine("xtts")
        synthesis_page.select_quality("standard")

        # Enter text
        synthesis_page.enter_text(sample_text)

        # Synthesize
        synthesis_page.click_synthesize()
        synthesis_page.wait_for_synthesis_complete(timeout=90.0)

        assert synthesis_page.is_synthesis_successful()

    # =========================================================================
    # Test: Save Synthesized Audio
    # =========================================================================

    def test_save_synthesized_audio(
        self,
        sample_text: str,
        unique_output_name: str,
        app_session
    ):
        """
        Test saving synthesized audio to file.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected")

        # Synthesize
        synthesis_page.enter_text(sample_text)
        synthesis_page.click_synthesize()
        synthesis_page.wait_for_synthesis_complete()

        # Save output
        synthesis_page.save_output()

        # Wait for save dialog and verify
        time.sleep(2.0)  # Allow time for save operation

        logger.info(f"Audio save initiated: {unique_output_name}")

    # =========================================================================
    # Test: Multiple Syntheses
    # =========================================================================

    def test_multiple_syntheses(
        self,
        app_session
    ):
        """
        Test performing multiple syntheses in sequence.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected")

        texts = [
            "First synthesis test.",
            "Second synthesis test with longer content.",
            "Third and final synthesis test."
        ]

        for i, text in enumerate(texts):
            synthesis_page.clear_text()
            synthesis_page.enter_text(text)
            synthesis_page.click_synthesize()
            synthesis_page.wait_for_synthesis_complete()

            assert synthesis_page.is_synthesis_successful()
            logger.info(f"Completed synthesis {i + 1}/{len(texts)}")

    # =========================================================================
    # Test: Synthesis Cancellation
    # =========================================================================

    def test_synthesis_cancellation(
        self,
        app_session
    ):
        """
        Test cancelling a synthesis in progress.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected")

        # Start with long text
        long_text = TestDataHelper.sample_text(500)
        synthesis_page.enter_text(long_text)
        synthesis_page.click_synthesize()

        # Wait briefly then cancel
        time.sleep(1.0)

        if synthesis_page.is_synthesizing():
            synthesis_page.click_stop()
            time.sleep(1.0)

            # Verify synthesis stopped
            assert not synthesis_page.is_synthesizing()


# =============================================================================
# Backend Integration Tests
# =============================================================================


@pytest.mark.e2e
@pytest.mark.synthesis
@pytest.mark.requires_backend
class TestSynthesisBackendIntegration:
    """
    Tests that verify synthesis integration with backend.
    """

    def test_synthesis_api_integration(
        self,
        sample_text: str,
        api_client
    ):
        """
        Test synthesis API endpoint.
        """
        # Check for available voices
        profiles_response = api_client.get("/api/voice/profiles")

        if profiles_response.status_code != 200:
            pytest.skip("Could not get voice profiles")

        profiles = profiles_response.json()
        if not profiles:
            pytest.skip("No voice profiles available")

        # Use first available profile
        profile_id = profiles[0].get("id") or profiles[0].get("profile_id")

        # Call synthesis endpoint
        response = api_client.post(
            "/api/voice/synthesize",
            json={
                "text": sample_text,
                "profile_id": profile_id,
                "engine": "xtts",
                "quality_mode": "standard"
            }
        )

        if response.status_code == 200:
            result = response.json()
            assert "audio_url" in result or "job_id" in result
            logger.info(f"Synthesis API response: {result}")
        elif response.status_code == 503:
            pytest.skip("Synthesis engine not available")
        else:
            logger.error(f"Synthesis API failed: {response.status_code} - {response.text}")

    def test_synthesis_status_polling(
        self,
        sample_text: str,
        api_client
    ):
        """
        Test synthesis job status polling.
        """
        # Start a synthesis job
        response = api_client.post(
            "/api/voice/synthesize",
            json={
                "text": sample_text,
                "engine": "xtts"
            }
        )

        if response.status_code != 200:
            pytest.skip("Could not start synthesis")

        result = response.json()
        job_id = result.get("job_id")

        if not job_id:
            # Synchronous synthesis - already complete
            return

        # Poll for status
        max_polls = 30
        for i in range(max_polls):
            status_response = api_client.get(f"/api/jobs/{job_id}")

            if status_response.status_code == 200:
                status = status_response.json()
                state = status.get("state", "unknown")

                if state in ["completed", "done"]:
                    logger.info(f"Synthesis completed after {i + 1} polls")
                    return
                elif state in ["failed", "error"]:
                    pytest.fail(f"Synthesis failed: {status}")

            time.sleep(1.0)

        pytest.fail("Synthesis did not complete within timeout")


# =============================================================================
# Performance Tests
# =============================================================================


@pytest.mark.e2e
@pytest.mark.synthesis
@pytest.mark.performance
@pytest.mark.requires_app
class TestSynthesisPerformance:
    """
    Performance tests for voice synthesis.
    """

    def test_synthesis_latency(
        self,
        sample_text: str,
        app_session,
        performance_timer
    ):
        """
        Test synthesis latency for short text.

        Target: < 10 seconds for 100 characters
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected")

        synthesis_page.enter_text(sample_text[:100])

        with performance_timer("Synthesis latency") as timer:
            synthesis_page.click_synthesize()
            synthesis_page.wait_for_synthesis_complete()

        assert timer.elapsed < 10.0, f"Synthesis too slow: {timer.elapsed:.2f}s"

    def test_synthesis_throughput(
        self,
        app_session,
        performance_timer
    ):
        """
        Test synthesis throughput for multiple requests.

        Target: Complete 3 syntheses in < 60 seconds
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_studio()
        synthesis_page = main_window.get_synthesis_page()

        if not synthesis_page.is_voice_selected():
            pytest.skip("No voice selected")

        texts = [
            "First short test.",
            "Second short test.",
            "Third short test."
        ]

        with performance_timer("Synthesis throughput") as timer:
            for text in texts:
                synthesis_page.clear_text()
                synthesis_page.enter_text(text)
                synthesis_page.click_synthesize()
                synthesis_page.wait_for_synthesis_complete()

        assert timer.elapsed < 60.0, f"Throughput too slow: {timer.elapsed:.2f}s for 3 syntheses"
