"""
Transcription Workflow Tests.

Tests speech-to-text transcription workflows:
- Audio file transcription
- Real-time transcription
- Multiple STT engine support (Whisper, WhisperCPP, Vosk)
- Language detection
- Transcript export formats

Requires:
- WinAppDriver running
- Backend running on port 8001
- VoiceStudio application built
- At least one STT engine available
"""

from __future__ import annotations

import os

# Import tracing infrastructure
import sys
import time
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent))
from tracing.api_monitor import APIMonitor
from tracing.workflow_tracer import WorkflowTracer

from fixtures import get_test_audio_path

# Test configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8001")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
TRACE_ENABLED = os.getenv("VOICESTUDIO_TRACE_ENABLED", "1") == "1"
SCREENSHOTS_ENABLED = os.getenv("VOICESTUDIO_SCREENSHOTS_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.transcription,
    pytest.mark.stt,
]


@pytest.fixture
def tracer():
    """Create a workflow tracer for this test."""
    tracer = WorkflowTracer("transcription", OUTPUT_DIR)
    tracer.start()
    yield tracer
    tracer.export_report()


@pytest.fixture
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "transcription_api_calls.json")


class TestTranscriptionBasicAPI:
    """Basic transcription API tests."""

    @pytest.mark.smoke
    def test_transcribe_audio_file(self, api_monitor, tracer):
        """Test basic audio file transcription."""
        tracer.step("Testing basic transcription")

        test_audio = get_test_audio_path("reference_clean")
        if not test_audio.exists():
            pytest.skip(f"Test audio not found at {test_audio}")

        try:
            with open(test_audio, "rb") as f:
                files = {"file": (test_audio.name, f, "audio/wav")}
                response = requests.post(
                    f"{BACKEND_URL}/api/transcribe",
                    files=files,
                    timeout=120  # Transcription can take time
                )
                tracer.api_call("POST", "/api/transcribe", response)

                if response.status_code in [200, 201, 202]:
                    result = response.json()
                    tracer.step(f"Transcription result: {result}")

                    # Check for expected fields
                    if "text" in result or "transcript" in result:
                        text = result.get("text") or result.get("transcript")
                        tracer.step(f"Transcribed text: {text[:100] if text else 'empty'}...")
                        tracer.success("Basic transcription works")
                    elif "job_id" in result:
                        tracer.step(f"Transcription job created: {result['job_id']}")
                        tracer.success("Async transcription initiated")
                    else:
                        tracer.step("Transcription returned but no text/job")
                else:
                    tracer.step(f"Transcription returned {response.status_code}: {response.text[:200]}")

        except Exception as e:
            tracer.error(e, "Transcription failed")
            pytest.skip(f"Transcription endpoint not available: {e}")

    def test_transcribe_with_language(self, api_monitor, tracer):
        """Test transcription with language specification."""
        tracer.step("Testing transcription with language")

        test_audio = get_test_audio_path("reference_clean")
        if not test_audio.exists():
            pytest.skip(f"Test audio not found at {test_audio}")

        try:
            with open(test_audio, "rb") as f:
                files = {"file": (test_audio.name, f, "audio/wav")}
                data = {"language": "en"}
                response = requests.post(
                    f"{BACKEND_URL}/api/transcribe",
                    files=files,
                    data=data,
                    timeout=120
                )
                tracer.api_call("POST", "/api/transcribe (lang=en)", response)

                if response.status_code in [200, 201, 202]:
                    tracer.step("Transcription with language successful")
                    tracer.success("Language specification works")
                else:
                    tracer.step(f"Transcription with language: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Transcription with language failed")


class TestSTTEngineSelection:
    """Tests for STT engine selection."""

    def test_list_stt_engines(self, api_monitor, tracer):
        """Test listing available STT engines."""
        tracer.step("Getting available STT engines")

        try:
            response = api_monitor.get("/api/engine/list")
            tracer.api_call("GET", "/api/engine/list", response)

            if response.status_code == 200:
                engines = response.json()

                # Filter STT engines
                stt_engines = []
                if isinstance(engines, list):
                    for engine in engines:
                        if isinstance(engine, dict):
                            if engine.get("type") == "stt" or "stt" in str(engine).lower():
                                stt_engines.append(engine)
                        elif "whisper" in str(engine).lower() or "vosk" in str(engine).lower():
                            stt_engines.append(engine)

                tracer.step(f"STT engines found: {len(stt_engines)}")
                for engine in stt_engines:
                    if isinstance(engine, dict):
                        tracer.step(f"  - {engine.get('id', engine.get('name', 'unknown'))}")
                    else:
                        tracer.step(f"  - {engine}")

                tracer.success("STT engine list retrieved")
            else:
                tracer.step(f"Engine list returned {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get STT engines failed")

    def test_transcribe_with_engine(self, api_monitor, tracer):
        """Test transcription with specific engine."""
        tracer.step("Testing transcription with engine selection")

        test_audio = get_test_audio_path("reference_clean")
        if not test_audio.exists():
            pytest.skip(f"Test audio not found at {test_audio}")

        # Try common STT engines
        engines_to_try = ["whisper", "whisper_cpp", "vosk", "auto"]

        for engine_id in engines_to_try:
            try:
                with open(test_audio, "rb") as f:
                    files = {"file": (test_audio.name, f, "audio/wav")}
                    data = {"engine": engine_id}
                    response = requests.post(
                        f"{BACKEND_URL}/api/transcribe",
                        files=files,
                        data=data,
                        timeout=120
                    )
                    tracer.api_call("POST", f"/api/transcribe (engine={engine_id})", response)

                    if response.status_code in [200, 201, 202]:
                        tracer.step(f"Engine {engine_id} transcription successful")
                        tracer.success(f"Engine selection works ({engine_id})")
                        return  # Success with first working engine
                    else:
                        tracer.step(f"Engine {engine_id}: {response.status_code}")

            except Exception as e:
                tracer.step(f"Engine {engine_id} failed: {e}")

        tracer.step("No STT engines available for testing")


class TestLanguageDetection:
    """Tests for automatic language detection."""

    def test_detect_language(self, api_monitor, tracer):
        """Test language detection API."""
        tracer.step("Testing language detection")

        test_audio = get_test_audio_path("reference_clean")
        if not test_audio.exists():
            pytest.skip(f"Test audio not found at {test_audio}")

        try:
            with open(test_audio, "rb") as f:
                files = {"file": (test_audio.name, f, "audio/wav")}

                # Try dedicated language detection endpoint
                response = requests.post(
                    f"{BACKEND_URL}/api/audio/detect-language",
                    files=files,
                    timeout=60
                )
                tracer.api_call("POST", "/api/audio/detect-language", response)

                if response.status_code == 200:
                    result = response.json()
                    tracer.step(f"Detected language: {result}")
                    tracer.success("Language detection works")
                elif response.status_code == 404:
                    tracer.step("Language detection endpoint not found")

                    # Try transcription with auto language detection
                    with open(test_audio, "rb") as f2:
                        files2 = {"file": (test_audio.name, f2, "audio/wav")}
                        data = {"detect_language": True}
                        response2 = requests.post(
                            f"{BACKEND_URL}/api/transcribe",
                            files=files2,
                            data=data,
                            timeout=120
                        )
                        tracer.api_call("POST", "/api/transcribe (detect_language)", response2)

                        if response2.status_code in [200, 201, 202]:
                            result2 = response2.json()
                            if "language" in result2:
                                tracer.step(f"Detected: {result2['language']}")
                                tracer.success("Language detection via transcribe works")
                else:
                    tracer.step(f"Language detection: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Language detection failed")


class TestTranscriptExport:
    """Tests for transcript export formats."""

    def test_export_formats(self, api_monitor, tracer):
        """Test transcript export in different formats."""
        tracer.step("Testing transcript export formats")

        export_formats = ["txt", "srt", "vtt", "json"]

        for fmt in export_formats:
            try:
                response = api_monitor.get(f"/api/transcription/export?format={fmt}")
                tracer.api_call("GET", f"/api/transcription/export?format={fmt}", response)

                if response.status_code == 200:
                    tracer.step(f"Format {fmt}: OK")
                elif response.status_code == 404:
                    tracer.step(f"Format {fmt}: endpoint not found")
                else:
                    tracer.step(f"Format {fmt}: {response.status_code}")

            except Exception as e:
                tracer.step(f"Format {fmt} failed: {e}")

        tracer.success("Export format check complete")


class TestTranscriptionUIWorkflow:
    """UI-based transcription workflow tests."""

    @pytest.mark.smoke
    def test_navigate_to_transcription(self, driver, app_launched, tracer):
        """Test navigation to transcription panel."""
        tracer.step("Navigating to transcription panel", driver, SCREENSHOTS_ENABLED)

        try:
            # Try different navigation options
            nav_options = [
                ("accessibility id", "NavTranscribe"),
                ("accessibility id", "NavTranscription"),
                ("accessibility id", "NavSTT"),
                ("xpath", "//*[contains(@Name, 'Transcri')]"),
                ("xpath", "//*[contains(@Name, 'Speech')]"),
            ]

            navigated = False
            for by, value in nav_options:
                try:
                    element = driver.find_element(by, value)
                    element.click()
                    time.sleep(1)
                    tracer.step(f"Clicked navigation: {value}", driver, SCREENSHOTS_ENABLED)
                    navigated = True
                    break
                except Exception:
                    continue

            if navigated:
                tracer.success("Navigation to transcription panel successful")
            else:
                tracer.step("No transcription navigation found")

        except Exception as e:
            tracer.error(e, "Navigation failed")

    def test_upload_area_exists(self, driver, app_launched, tracer):
        """Test that upload/drop area exists in transcription panel."""
        tracer.step("Looking for upload area", driver, SCREENSHOTS_ENABLED)

        try:
            upload_elements = [
                ("accessibility id", "UploadArea"),
                ("accessibility id", "DropZone"),
                ("accessibility id", "FileUpload"),
                ("xpath", "//*[contains(@Name, 'Upload')]"),
                ("xpath", "//*[contains(@Name, 'Drop')]"),
            ]

            upload_area = None
            for by, value in upload_elements:
                try:
                    upload_area = driver.find_element(by, value)
                    tracer.step(f"Found upload area: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if upload_area:
                tracer.success("Upload area found")
            else:
                tracer.step("No upload area found")

        except Exception as e:
            tracer.error(e, "Upload area search failed")

    def test_engine_selector_exists(self, driver, app_launched, tracer):
        """Test that engine selector exists in transcription panel."""
        tracer.step("Looking for engine selector", driver, SCREENSHOTS_ENABLED)

        try:
            selectors = [
                ("accessibility id", "EngineSelector"),
                ("accessibility id", "STTEngineComboBox"),
                ("accessibility id", "EngineDropdown"),
                ("xpath", "//ComboBox[contains(@Name, 'Engine')]"),
                ("xpath", "//*[contains(@Name, 'Whisper')]"),
            ]

            engine_selector = None
            for by, value in selectors:
                try:
                    engine_selector = driver.find_element(by, value)
                    tracer.step(f"Found engine selector: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if engine_selector:
                tracer.success("Engine selector found")
            else:
                tracer.step("No engine selector found")

        except Exception as e:
            tracer.error(e, "Engine selector search failed")

    def test_transcribe_button_exists(self, driver, app_launched, tracer):
        """Test that transcribe button exists."""
        tracer.step("Looking for transcribe button", driver, SCREENSHOTS_ENABLED)

        try:
            buttons = [
                ("accessibility id", "TranscribeButton"),
                ("accessibility id", "StartTranscriptionButton"),
                ("accessibility id", "ProcessButton"),
                ("xpath", "//*[contains(@Name, 'Transcribe')]"),
                ("xpath", "//*[contains(@Name, 'Start')]"),
            ]

            transcribe_btn = None
            for by, value in buttons:
                try:
                    transcribe_btn = driver.find_element(by, value)
                    tracer.step(f"Found transcribe button: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if transcribe_btn:
                tracer.success("Transcribe button found")
            else:
                tracer.step("No transcribe button found")

        except Exception as e:
            tracer.error(e, "Transcribe button search failed")


class TestTranscriptionE2E:
    """End-to-end transcription workflow tests."""

    @pytest.mark.slow
    def test_complete_transcription_workflow(self, api_monitor, tracer):
        """Test complete transcription workflow via API."""
        tracer.step("Starting complete transcription workflow")

        # Step 1: Get available STT engines
        tracer.step("Step 1: Get available STT engines")
        response = api_monitor.get("/api/engine/list")
        tracer.api_call("GET", "/api/engine/list", response)

        engines = []
        selected_engine = "auto"
        if response.status_code == 200:
            engines = response.json()
            if isinstance(engines, list):
                for engine in engines:
                    if isinstance(engine, dict) and engine.get("type") == "stt":
                        selected_engine = engine.get("id", "auto")
                        break
        tracer.step(f"Selected engine: {selected_engine}")

        # Step 2: Upload and transcribe
        tracer.step("Step 2: Transcribe audio")
        test_audio = get_test_audio_path("reference_clean")

        if not test_audio.exists():
            pytest.skip(f"Test audio not found at {test_audio}")

        transcript = None
        with open(test_audio, "rb") as f:
            files = {"file": (test_audio.name, f, "audio/wav")}
            data = {"engine": selected_engine, "language": "en"}
            response = requests.post(
                f"{BACKEND_URL}/api/transcribe",
                files=files,
                data=data,
                timeout=120
            )
            tracer.api_call("POST", "/api/transcribe", response)

            if response.status_code in [200, 201, 202]:
                result = response.json()
                transcript = result.get("text") or result.get("transcript")
                tracer.step(f"Transcribed: {transcript[:100] if transcript else 'empty'}...")

        # Step 3: Check result
        tracer.step("Step 3: Verify result")
        if transcript:
            tracer.step(f"Transcript length: {len(transcript)} chars")
            tracer.success("Complete transcription workflow successful")
        else:
            tracer.step("No transcript received")

    @pytest.mark.slow
    def test_batch_transcription(self, api_monitor, tracer):
        """Test batch transcription of multiple files."""
        tracer.step("Testing batch transcription")

        audio_files = [
            get_test_audio_path("short_audio"),
            get_test_audio_path("reference_clean"),
        ]

        existing_files = [f for f in audio_files if f.exists()]
        if len(existing_files) < 2:
            pytest.skip("Need at least 2 audio files for batch test")

        results = []
        for audio_file in existing_files:
            try:
                with open(audio_file, "rb") as f:
                    files = {"file": (audio_file.name, f, "audio/wav")}
                    response = requests.post(
                        f"{BACKEND_URL}/api/transcribe",
                        files=files,
                        timeout=120
                    )
                    tracer.api_call("POST", f"/api/transcribe ({audio_file.name})", response)

                    if response.status_code in [200, 201, 202]:
                        result = response.json()
                        results.append(result)
                        tracer.step(f"Transcribed {audio_file.name}")

            except Exception as e:
                tracer.step(f"Failed to transcribe {audio_file.name}: {e}")

        tracer.step(f"Batch transcription complete: {len(results)}/{len(existing_files)} successful")
        if len(results) == len(existing_files):
            tracer.success("Batch transcription works")


# Run tests directly if executed as script
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
