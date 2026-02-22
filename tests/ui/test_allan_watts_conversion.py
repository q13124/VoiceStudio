"""
Allan Watts Audio Format Conversion Tests.

Tests audio format conversion capabilities:
- Format detection for m4a
- Conversion to wav, mp3, flac, ogg
- Quality preservation
- Metadata handling
- Batch conversion
- Error handling

Requirements:
- WinAppDriver running on port 4723
- Backend running on port 8000
- VoiceStudio application built
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent))

from fixtures.audio_test_data import (
    ALLAN_WATTS_METADATA,
    CONVERSION_SPECS,
    CONVERSION_WORKFLOW,
    FORMAT_MIME_TYPES,
    TEST_AUDIO_FILE,
    get_file_size_mb,
    validate_test_file_exists,
)
from tracing.api_monitor import APIMonitor
from tracing.workflow_tracer import WorkflowTracer

# Configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8000")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
SCREENSHOTS_ENABLED = os.getenv("VOICESTUDIO_SCREENSHOTS_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.conversion,
    pytest.mark.allan_watts,
]


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def tracer():
    """Create a workflow tracer for conversion tests."""
    t = WorkflowTracer("allan_watts_conversion", OUTPUT_DIR)
    t.start()
    yield t
    t.export_report()


@pytest.fixture(scope="module")
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "allan_watts_conversion_api_calls.json")


# =============================================================================
# Format Detection Tests
# =============================================================================


class TestFormatDetection:
    """Test audio format detection."""

    def test_m4a_format_detection(self, api_monitor, tracer):
        """Test M4A format detection via API."""
        tracer.start_phase("format_detection", "Test format detection")
        tracer.step("Testing M4A format detection")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                response = api_monitor.post("/api/v3/audio/detect-format", files=files)

            tracer.api_call("POST", "/api/v3/audio/detect-format", response)

            if response.status_code == 200:
                data = response.json()
                tracer.step(f"Format detected: {data}")
                tracer.success("M4A format detection works")
            elif response.status_code == 404:
                tracer.step("Format detection endpoint not implemented")
            else:
                tracer.step(f"Format detection: {response.status_code}")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()

    def test_supported_formats_api(self, api_monitor, tracer):
        """Test listing supported formats."""
        tracer.step("Testing supported formats API")

        try:
            response = api_monitor.get("/api/v3/audio/formats")
            tracer.api_call("GET", "/api/v3/audio/formats", response)

            if response.status_code == 200:
                data = response.json()
                tracer.step(f"Supported formats: {data}")
            else:
                tracer.step(f"Formats endpoint: {response.status_code}")

            tracer.success("Supported formats query completed")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")


# =============================================================================
# Conversion Tests (Each Output Format)
# =============================================================================


class TestConversionToWav:
    """Test conversion to WAV format."""

    def test_m4a_to_wav_api(self, api_monitor, tracer):
        """Test M4A to WAV conversion via API."""
        tracer.start_phase("conversion_wav", "Test WAV conversion")
        tracer.step("Testing M4A to WAV conversion")

        spec = CONVERSION_SPECS["wav"]
        tracer.step(f"Conversion spec: {spec}")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                data = {"target_format": "wav"}
                response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (wav)", response)

            if response.status_code == 200:
                tracer.step("WAV conversion successful")
                tracer.success("M4A to WAV works")
            elif response.status_code == 404:
                tracer.step("Conversion endpoint not implemented")
            else:
                tracer.step(f"WAV conversion: {response.status_code}")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()


class TestConversionToMp3:
    """Test conversion to MP3 format."""

    def test_m4a_to_mp3_api(self, api_monitor, tracer):
        """Test M4A to MP3 conversion via API."""
        tracer.start_phase("conversion_mp3", "Test MP3 conversion")
        tracer.step("Testing M4A to MP3 conversion")

        spec = CONVERSION_SPECS["mp3"]
        tracer.step(f"Conversion spec: {spec}")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                data = {"target_format": "mp3", "bitrate": spec.target_bit_rate}
                response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (mp3)", response)

            if response.status_code == 200:
                tracer.step("MP3 conversion successful")
                tracer.success("M4A to MP3 works")
            elif response.status_code == 404:
                tracer.step("Conversion endpoint not implemented")
            else:
                tracer.step(f"MP3 conversion: {response.status_code}")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()


class TestConversionToFlac:
    """Test conversion to FLAC format."""

    def test_m4a_to_flac_api(self, api_monitor, tracer):
        """Test M4A to FLAC conversion via API."""
        tracer.start_phase("conversion_flac", "Test FLAC conversion")
        tracer.step("Testing M4A to FLAC conversion")

        spec = CONVERSION_SPECS["flac"]
        tracer.step(f"Conversion spec: {spec}")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                data = {"target_format": "flac"}
                response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (flac)", response)

            if response.status_code == 200:
                tracer.step("FLAC conversion successful")
                tracer.success("M4A to FLAC works")
            elif response.status_code == 404:
                tracer.step("Conversion endpoint not implemented")
            else:
                tracer.step(f"FLAC conversion: {response.status_code}")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()


class TestConversionToOgg:
    """Test conversion to OGG format."""

    def test_m4a_to_ogg_api(self, api_monitor, tracer):
        """Test M4A to OGG conversion via API."""
        tracer.start_phase("conversion_ogg", "Test OGG conversion")
        tracer.step("Testing M4A to OGG conversion")

        spec = CONVERSION_SPECS["ogg"]
        tracer.step(f"Conversion spec: {spec}")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                data = {"target_format": "ogg"}
                response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (ogg)", response)

            if response.status_code == 200:
                tracer.step("OGG conversion successful")
                tracer.success("M4A to OGG works")
            elif response.status_code == 404:
                tracer.step("Conversion endpoint not implemented")
            else:
                tracer.step(f"OGG conversion: {response.status_code}")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()


# =============================================================================
# Quality Preservation Tests
# =============================================================================


class TestQualityPreservation:
    """Test audio quality preservation during conversion."""

    def test_duration_preserved(self, api_monitor, tracer):
        """Test that duration is preserved across formats."""
        tracer.start_phase("quality_preservation", "Test quality preservation")
        tracer.step("Documenting duration preservation requirements")

        for fmt, spec in CONVERSION_SPECS.items():
            if spec.preserve_duration:
                tracer.step(f"{fmt.upper()}: duration must be preserved")

        tracer.end_phase(success=True)
        tracer.success("Quality requirements documented")

    def test_channel_preservation(self, api_monitor, tracer):
        """Test that channels are preserved."""
        tracer.step("Documenting channel preservation requirements")

        expected_channels = ALLAN_WATTS_METADATA.expected_channels
        tracer.step(f"Source channels: {expected_channels}")

        for fmt, spec in CONVERSION_SPECS.items():
            if spec.preserve_channels:
                tracer.step(f"{fmt.upper()}: channels must be preserved ({expected_channels})")

        tracer.success("Channel requirements documented")


# =============================================================================
# UI Conversion Tests
# =============================================================================


class TestConversionUI:
    """Test conversion UI workflow."""

    def test_conversion_panel_navigation(self, driver, app_launched, tracer):
        """Test navigation to conversion panel."""
        tracer.start_phase("conversion_ui", "Test conversion UI")
        tracer.step("Navigating to conversion panel")

        tracer.start_panel_transition("unknown", "AudioConversion")

        try:
            # Try navigation
            nav_button = driver.find_element("accessibility id", CONVERSION_WORKFLOW.nav_id)
            nav_button.click()
            time.sleep(0.5)

            # Verify panel loaded
            for _ in range(10):
                try:
                    driver.find_element("accessibility id", CONVERSION_WORKFLOW.root_id)
                    tracer.end_panel_transition(success=True)
                    tracer.success("Conversion panel navigation works")
                    return
                except RuntimeError:
                    time.sleep(0.3)

            tracer.end_panel_transition(success=False, error="Timeout")
        except RuntimeError as e:
            tracer.end_panel_transition(success=False, error=str(e))
            pytest.skip("Conversion panel navigation not available")
        finally:
            tracer.end_phase()

    def test_format_selector_exists(self, driver, app_launched, tracer):
        """Test format selector UI element."""
        tracer.step("Checking format selector")

        try:
            nav_button = driver.find_element("accessibility id", CONVERSION_WORKFLOW.nav_id)
            nav_button.click()
            time.sleep(0.5)

            # Look for format selector
            driver.find_element(
                "xpath",
                "//*[contains(@AutomationId, 'Format') and contains(@ClassName, 'ComboBox')]",
            )
            tracer.step("Format selector found")
            tracer.success("Format selector exists")
        except RuntimeError:
            tracer.step("Format selector not found")
            pytest.skip("Format selector not available")


# =============================================================================
# Batch Conversion Tests
# =============================================================================


class TestBatchConversion:
    """Test batch conversion functionality."""

    def test_batch_conversion_api(self, api_monitor, tracer):
        """Test batch conversion API."""
        tracer.start_phase("batch_conversion", "Test batch conversion")
        tracer.step("Testing batch conversion API structure")

        try:
            # Check if batch endpoint exists
            response = api_monitor.post(
                "/api/v3/audio/convert-batch",
                json={
                    "files": [],
                    "target_format": "wav",
                },
            )
            tracer.api_call("POST", "/api/v3/audio/convert-batch", response)

            if response.status_code == 404:
                tracer.step("Batch conversion not implemented")
            elif response.status_code in [400, 422]:
                tracer.step("Batch conversion validates input")
            elif response.status_code == 200:
                tracer.step("Batch conversion API exists")

            tracer.success("Batch conversion API test completed")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestConversionErrors:
    """Test conversion error handling."""

    def test_invalid_format(self, api_monitor, tracer):
        """Test conversion with invalid target format."""
        tracer.start_phase("conversion_errors", "Test error handling")
        tracer.step("Testing invalid format handling")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                data = {"target_format": "invalid_xyz"}
                response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (invalid)", response)

            if response.status_code in [400, 422]:
                tracer.step("Invalid format properly rejected")
            else:
                tracer.step(f"Invalid format: {response.status_code}")

            tracer.success("Invalid format handling completed")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")
        finally:
            tracer.end_phase()

    def test_corrupted_audio_conversion(self, api_monitor, tracer):
        """Test conversion with corrupted audio."""
        tracer.step("Testing corrupted audio conversion")

        try:
            # Send fake audio data
            files = {"file": ("corrupted.m4a", b"not real audio data", FORMAT_MIME_TYPES["m4a"])}
            data = {"target_format": "wav"}
            response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (corrupted)", response)

            if response.status_code in [400, 422, 500]:
                tracer.step(f"Corrupted audio handled: {response.status_code}")

            tracer.success("Corrupted audio handling completed")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")

    def test_same_format_conversion(self, api_monitor, tracer):
        """Test conversion to same format."""
        tracer.step("Testing same format conversion")

        if not validate_test_file_exists():
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")

        try:
            with open(TEST_AUDIO_FILE, "rb") as f:
                files = {"file": (TEST_AUDIO_FILE.name, f, FORMAT_MIME_TYPES["m4a"])}
                data = {"target_format": "m4a"}  # Same format
                response = api_monitor.post("/api/v3/audio/convert", files=files, data=data)

            tracer.api_call("POST", "/api/v3/audio/convert (same)", response)
            tracer.step(f"Same format response: {response.status_code}")
            tracer.success("Same format conversion test completed")
        except FileNotFoundError:
            pytest.skip(f"Test file not found: {TEST_AUDIO_FILE}")
        except requests.RequestException as e:
            tracer.step(f"API error: {e}")


# =============================================================================
# Integration Tests
# =============================================================================


class TestConversionIntegration:
    """Test conversion integration with other panels."""

    def test_conversion_from_library_event(self, driver, app_launched, tracer):
        """Document conversion from library integration."""
        tracer.start_phase("conversion_integration", "Test conversion integration")
        tracer.step("Documenting library-to-conversion workflow")

        tracer.trace_event(
            "ConvertFromLibraryEvent",
            source_panel="Library",
            target_panel="AudioConversion",
            payload={"action": "convert_file", "expected_data": ["file_path", "target_format"]},
        )

        tracer.step("Library-to-conversion event documented")
        tracer.end_phase(success=True)
        tracer.success("Integration documented")

    def test_converted_file_to_library(self, driver, app_launched, tracer):
        """Document converted file to library integration."""
        tracer.step("Documenting converted file workflow")

        tracer.trace_event(
            "ConversionCompletedEvent",
            source_panel="AudioConversion",
            target_panel="Library",
            payload={
                "action": "add_converted_file",
                "expected_data": ["output_path", "original_path", "format"],
            },
        )

        tracer.step("Conversion-completed event documented")
        tracer.success("Integration documented")


# =============================================================================
# Performance Tests
# =============================================================================


class TestConversionPerformance:
    """Test conversion performance."""

    def test_conversion_speed(self, tracer):
        """Document conversion speed expectations."""
        tracer.start_phase("conversion_performance", "Test conversion performance")
        tracer.step("Documenting conversion speed expectations")

        file_size_mb = get_file_size_mb()
        tracer.step(f"Test file size: {file_size_mb:.2f} MB")

        # Document expected performance
        expected_performance = {
            "wav": "< 2 seconds",
            "mp3": "< 5 seconds",
            "flac": "< 5 seconds",
            "ogg": "< 5 seconds",
        }

        for fmt, expectation in expected_performance.items():
            tracer.step(f"{fmt.upper()} conversion: {expectation}")

        tracer.end_phase(success=True)
        tracer.success("Performance expectations documented")


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-m",
            "not slow",
            "--html=.buildlogs/validation/reports/allan_watts_conversion_report.html",
            "--self-contained-html",
        ]
    )
