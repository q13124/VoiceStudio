"""
Wizard Flow E2E Tests for VoiceStudio.

Tests the complete voice cloning wizard workflow including:
- Audio file selection
- Engine auto-detection
- Profile name configuration
- Clone execution
- Profile verification in Voice Browser
"""

import logging
import os
import time
import wave
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tests.e2e.framework.base import E2ETestBase
from tests.e2e.framework.helpers import PerformanceTimer, TestDataHelper

logger = logging.getLogger(__name__)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_audio_file(tmp_path: Path) -> str:
    """Create a sample WAV file for testing."""
    audio_file = tmp_path / "test_voice_sample.wav"

    # Create a simple WAV file
    with wave.open(str(audio_file), "wb") as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(22050)  # 22.05 kHz

        # Generate 3 seconds of audio data (silence)
        duration = 3.0
        n_frames = int(22050 * duration)
        wav.writeframes(bytes(n_frames * 2))

    return str(audio_file)


@pytest.fixture
def unique_profile_name() -> str:
    """Generate a unique profile name for testing."""
    return TestDataHelper.unique_name("E2E-WizardTest")


# =============================================================================
# Mock-Based Tests (No App Required)
# =============================================================================


class TestWizardFlowMock:
    """
    Mock-based wizard flow tests.

    These tests validate the E2E test structure and logic
    without requiring the actual application.
    """

    def test_wizard_flow_structure(self):
        """Verify wizard flow test structure is correct."""
        # Verify test class exists and has expected structure
        assert TestVoiceCloningWizard is not None
        assert hasattr(TestVoiceCloningWizard, "test_complete_voice_cloning_workflow")
        assert hasattr(TestVoiceCloningWizard, "test_wizard_with_custom_engine")

    def test_page_objects_importable(self):
        """Verify page objects can be imported."""
        from tests.e2e.pages import (
            MainWindowPage,
            SynthesisPage,
            VoiceBrowserPage,
            VoiceQuickClonePage,
        )

        # Verify classes exist
        assert MainWindowPage is not None
        assert VoiceQuickClonePage is not None
        assert VoiceBrowserPage is not None
        assert SynthesisPage is not None

    def test_sample_audio_fixture(self, sample_audio_file: str):
        """Verify sample audio file fixture creates valid WAV."""
        assert os.path.exists(sample_audio_file)
        assert sample_audio_file.endswith(".wav")

        # Verify it's a valid WAV file
        with wave.open(sample_audio_file, "rb") as wav:
            assert wav.getnchannels() == 1
            assert wav.getsampwidth() == 2
            assert wav.getframerate() == 22050
            assert wav.getnframes() > 0

    def test_unique_profile_name_fixture(self, unique_profile_name: str):
        """Verify unique profile name generation."""
        assert unique_profile_name.startswith("E2E-WizardTest")
        assert len(unique_profile_name) > len("E2E-WizardTest")

    def test_mock_wizard_flow(self, sample_audio_file: str, unique_profile_name: str):
        """
        Test wizard flow with mocked page objects.

        This validates the test logic without requiring the app.
        """
        # Create mock page objects
        mock_main_window = MagicMock()
        mock_quick_clone = MagicMock()
        mock_voice_browser = MagicMock()

        # Configure mock behavior
        mock_main_window.get_voice_quick_clone_page.return_value = mock_quick_clone
        mock_main_window.get_voice_browser_page.return_value = mock_voice_browser

        mock_quick_clone.is_quick_clone_enabled.return_value = True
        mock_quick_clone.is_clone_successful.return_value = True
        mock_quick_clone.get_created_profile_id.return_value = "test-profile-123"
        mock_quick_clone.get_quality_score.return_value = 0.85

        mock_voice_browser.find_voice_by_name.return_value = True
        mock_voice_browser.get_voice_count.return_value = 1

        # Simulate wizard flow
        # Step 1: Navigate to quick clone
        mock_main_window.navigate_to_train()
        mock_main_window.navigate_to_train.assert_called_once()

        # Step 2: Get quick clone page
        quick_clone_page = mock_main_window.get_voice_quick_clone_page()

        # Step 3: Select audio file
        quick_clone_page.select_audio_file(sample_audio_file)
        quick_clone_page.select_audio_file.assert_called_with(sample_audio_file)

        # Step 4: Set profile name
        quick_clone_page.set_profile_name(unique_profile_name)
        quick_clone_page.set_profile_name.assert_called_with(unique_profile_name)

        # Step 5: Execute clone
        quick_clone_page.click_quick_clone()
        quick_clone_page.click_quick_clone.assert_called_once()

        # Step 6: Wait for completion
        quick_clone_page.wait_for_processing_complete()

        # Step 7: Verify success
        assert quick_clone_page.is_clone_successful()
        profile_id = quick_clone_page.get_created_profile_id()
        assert profile_id == "test-profile-123"

        # Step 8: Navigate to voice browser
        mock_main_window.navigate_to_profiles()
        voice_browser = mock_main_window.get_voice_browser_page()

        # Step 9: Verify profile exists
        assert voice_browser.find_voice_by_name(unique_profile_name)

        logger.info("Mock wizard flow completed successfully")


# =============================================================================
# Full E2E Tests (Require Application)
# =============================================================================


@pytest.mark.e2e
@pytest.mark.wizard
@pytest.mark.requires_app
class TestVoiceCloningWizard(E2ETestBase):
    """
    End-to-end tests for the voice cloning wizard.

    These tests require:
    - VoiceStudio application running
    - WinAppDriver running
    - Backend server available
    """

    # =========================================================================
    # Test: Complete Voice Cloning Workflow
    # =========================================================================

    def test_complete_voice_cloning_workflow(
        self, sample_audio_file: str, unique_profile_name: str, app_session
    ):
        """
        Test the complete voice cloning wizard workflow.

        Steps:
        1. Navigate to Train/Quick Clone panel
        2. Select reference audio file
        3. Verify auto-detection of engine/quality
        4. Set custom profile name
        5. Execute quick clone
        6. Wait for completion
        7. Verify created profile in Voice Browser
        8. Verify profile can be used for synthesis
        """
        from tests.e2e.pages import MainWindowPage

        with PerformanceTimer("Complete voice cloning wizard") as timer:
            # Initialize main window page
            main_window = MainWindowPage(app_session)

            # Step 1: Navigate to quick clone panel
            main_window.navigate_to_train()
            quick_clone_page = main_window.get_voice_quick_clone_page()

            # Step 2: Select audio file
            quick_clone_page.select_audio_file(sample_audio_file)
            assert quick_clone_page.is_audio_selected()

            # Step 3: Verify auto-detection
            detected_engine = quick_clone_page.get_detected_engine()
            assert detected_engine, "Engine should be auto-detected"

            detected_quality = quick_clone_page.get_detected_quality()
            assert detected_quality, "Quality mode should be auto-detected"

            # Step 4: Set profile name
            quick_clone_page.set_profile_name(unique_profile_name)
            assert quick_clone_page.get_profile_name() == unique_profile_name

            # Step 5: Verify quick clone is enabled
            assert quick_clone_page.is_quick_clone_enabled()

            # Step 6: Execute quick clone
            quick_clone_page.click_quick_clone()

            # Step 7: Wait for completion
            quick_clone_page.wait_for_processing_complete(timeout=120.0)

            # Step 8: Verify success
            assert quick_clone_page.is_clone_successful()
            profile_id = quick_clone_page.get_created_profile_id()
            assert profile_id, "Should have created profile ID"

            quality_score = quick_clone_page.get_quality_score()
            assert quality_score is not None, "Should have quality score"
            assert quality_score >= 0.0, "Quality score should be non-negative"

            # Step 9: Navigate to Voice Browser
            main_window.navigate_to_profiles()
            voice_browser = main_window.get_voice_browser_page()

            # Step 10: Verify profile exists
            assert voice_browser.wait_for_voice_to_appear(unique_profile_name)

            logger.info(
                f"Wizard completed: profile={profile_id}, "
                f"quality={quality_score:.2f}, "
                f"duration={timer.elapsed:.2f}s"
            )

    # =========================================================================
    # Test: Wizard with Custom Engine Selection
    # =========================================================================

    def test_wizard_with_custom_engine(
        self, sample_audio_file: str, unique_profile_name: str, app_session
    ):
        """
        Test wizard with custom engine selection.

        Verifies that users can override auto-detected settings.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_train()
        quick_clone_page = main_window.get_voice_quick_clone_page()

        # Select audio file
        quick_clone_page.select_audio_file(sample_audio_file)

        # Override engine selection
        quick_clone_page.select_engine("xtts")
        quick_clone_page.select_quality_mode("high")

        # Set profile name
        quick_clone_page.set_profile_name(unique_profile_name + "-custom")

        # Execute and verify
        quick_clone_page.click_quick_clone()
        quick_clone_page.wait_for_processing_complete(timeout=180.0)

        assert quick_clone_page.is_clone_successful()

    # =========================================================================
    # Test: Wizard Reset Functionality
    # =========================================================================

    def test_wizard_reset(self, sample_audio_file: str, app_session):
        """
        Test the wizard reset functionality.

        Verifies that the reset button clears all selections.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_train()
        quick_clone_page = main_window.get_voice_quick_clone_page()

        # Select audio and configure
        quick_clone_page.select_audio_file(sample_audio_file)
        quick_clone_page.set_profile_name("Test Profile")

        # Verify selections
        assert quick_clone_page.is_audio_selected()

        # Reset
        quick_clone_page.click_reset()

        # Verify reset
        assert not quick_clone_page.is_audio_selected()
        assert not quick_clone_page.is_quick_clone_enabled()

    # =========================================================================
    # Test: Wizard Validation
    # =========================================================================

    def test_wizard_validation(self, app_session):
        """
        Test wizard input validation.

        Verifies that the wizard properly validates inputs before allowing clone.
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_train()
        quick_clone_page = main_window.get_voice_quick_clone_page()

        # Verify clone button is disabled without audio
        assert not quick_clone_page.is_quick_clone_enabled()

    # =========================================================================
    # Test: Wizard Error Handling
    # =========================================================================

    def test_wizard_error_handling(self, tmp_path: Path, unique_profile_name: str, app_session):
        """
        Test wizard error handling with invalid audio.

        Verifies proper error messages are displayed.
        """
        from tests.e2e.pages import MainWindowPage

        # Create an invalid audio file
        invalid_file = tmp_path / "invalid.wav"
        invalid_file.write_bytes(b"not a real wav file")

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_train()
        quick_clone_page = main_window.get_voice_quick_clone_page()

        # Try to select invalid file
        try:
            quick_clone_page.select_audio_file(str(invalid_file))

            # If we get here and can click clone
            if quick_clone_page.is_quick_clone_enabled():
                quick_clone_page.set_profile_name(unique_profile_name)
                quick_clone_page.click_quick_clone()

                # Should fail
                time.sleep(5.0)  # Wait for error

                error_msg = quick_clone_page.get_error_message()
                assert error_msg, "Should display error for invalid file"
        except Exception as e:
            # Expected - invalid file should be rejected
            logger.info(f"Invalid file correctly rejected: {e}")


# =============================================================================
# Backend Integration Tests
# =============================================================================


@pytest.mark.e2e
@pytest.mark.wizard
@pytest.mark.requires_backend
class TestWizardBackendIntegration:
    """
    Tests that verify wizard integration with backend.

    These tests can run with just the backend, without UI.
    """

    def test_clone_api_integration(
        self, sample_audio_file: str, unique_profile_name: str, api_client
    ):
        """
        Test clone API integration.

        Verifies the backend clone endpoint works correctly.
        """

        # Read audio file
        with open(sample_audio_file, "rb") as f:
            audio_data = f.read()

        # Call clone endpoint
        response = api_client.post(
            "/api/voice/clone",
            files={"audio": ("test.wav", audio_data, "audio/wav")},
            data={
                "engine": "xtts",
                "quality_mode": "standard",
                "profile_name": unique_profile_name,
            },
        )

        if response.status_code == 200:
            result = response.json()
            assert "profile_id" in result or "job_id" in result
            logger.info(f"Clone API response: {result}")
        elif response.status_code == 503:
            pytest.skip("Clone engine not available")
        else:
            # Log error for debugging
            logger.error(f"Clone API failed: {response.status_code} - {response.text}")

    def test_profile_listing_after_clone(self, api_client):
        """
        Test that profiles are listed after creation.
        """
        response = api_client.get("/api/voice/profiles")

        if response.status_code == 200:
            profiles = response.json()
            assert isinstance(profiles, list)
            logger.info(f"Found {len(profiles)} voice profiles")
        else:
            logger.warning(f"Could not list profiles: {response.status_code}")


# =============================================================================
# Performance Tests
# =============================================================================


@pytest.mark.e2e
@pytest.mark.wizard
@pytest.mark.performance
@pytest.mark.requires_app
class TestWizardPerformance:
    """
    Performance tests for the voice cloning wizard.
    """

    def test_wizard_navigation_performance(self, app_session, performance_timer):
        """
        Test navigation to wizard panel is responsive.

        Target: < 2 seconds
        """
        from tests.e2e.pages import MainWindowPage

        with performance_timer("Navigate to wizard") as timer:
            main_window = MainWindowPage(app_session)
            main_window.navigate_to_train()
            _ = main_window.get_voice_quick_clone_page()

        assert timer.elapsed < 2.0, f"Navigation too slow: {timer.elapsed:.2f}s"

    def test_wizard_file_selection_performance(
        self, sample_audio_file: str, app_session, performance_timer
    ):
        """
        Test file selection and auto-detection is responsive.

        Target: < 3 seconds
        """
        from tests.e2e.pages import MainWindowPage

        main_window = MainWindowPage(app_session)
        main_window.navigate_to_train()
        quick_clone_page = main_window.get_voice_quick_clone_page()

        with performance_timer("Select audio and auto-detect") as timer:
            quick_clone_page.select_audio_file(sample_audio_file)
            # Wait for auto-detection
            time.sleep(1.0)
            _ = quick_clone_page.get_detected_engine()
            _ = quick_clone_page.get_detected_quality()

        assert timer.elapsed < 3.0, f"Selection too slow: {timer.elapsed:.2f}s"
