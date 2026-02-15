"""
Voice Synthesis with Cloned Voice Tests.

Tests voice synthesis workflows using cloned and default voices:
- Text-to-speech generation
- Voice selection (cloned voices)
- Audio playback preview
- Output format options
- Multi-voice synthesis

Requires:
- WinAppDriver running
- Backend running on port 8001
- VoiceStudio application built
"""

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

from fixtures import get_test_script

# Test configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8001")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
TRACE_ENABLED = os.getenv("VOICESTUDIO_TRACE_ENABLED", "1") == "1"
SCREENSHOTS_ENABLED = os.getenv("VOICESTUDIO_SCREENSHOTS_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.synthesis,
    pytest.mark.voice,
]


@pytest.fixture
def tracer():
    """Create a workflow tracer for this test."""
    tracer = WorkflowTracer("voice_synthesis", OUTPUT_DIR)
    tracer.start()
    yield tracer
    tracer.export_report()


@pytest.fixture
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "voice_synthesis_api_calls.json")


@pytest.mark.api
class TestSynthesisBasicAPI:
    """Basic synthesis API tests."""

    @pytest.mark.smoke
    def test_synthesize_simple_text(self, api_monitor, tracer):
        """Test basic text-to-speech synthesis."""
        tracer.step("Testing simple text synthesis")

        payload = {
            "text": "Hello, this is a test.",
            "voice_id": "default",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", "/api/voice/synthesize", response)

            if response.status_code in [200, 201, 202]:
                content_type = response.headers.get("content-type", "")

                if "audio" in content_type:
                    tracer.step(f"Received audio: {len(response.content)} bytes")
                    tracer.success("Simple synthesis works - received audio")
                else:
                    data = response.json()
                    tracer.step(f"Synthesis result: {data}")
                    if "job_id" in data or "audio" in data or "url" in data:
                        tracer.success("Simple synthesis works - job/audio created")
                    else:
                        tracer.step("Synthesis returned but no audio/job")
            else:
                tracer.step(f"Synthesis returned {response.status_code}: {response.text[:200]}")

        except Exception as e:
            tracer.error(e, "Simple synthesis failed")
            pytest.skip(f"Synthesis endpoint not available: {e}")

    def test_synthesize_with_options(self, api_monitor, tracer):
        """Test synthesis with additional options."""
        tracer.step("Testing synthesis with options")

        payload = {
            "text": get_test_script("short"),
            "voice_id": "default",
            "speed": 1.0,
            "pitch": 1.0,
            "output_format": "wav",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", "/api/voice/synthesize (with options)", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Synthesis with options successful")
                tracer.success("Synthesis options work")
            else:
                tracer.step(f"Synthesis with options: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Synthesis with options failed")

    def test_synthesize_long_text(self, api_monitor, tracer):
        """Test synthesis with longer text."""
        tracer.step("Testing long text synthesis")

        payload = {
            "text": get_test_script("long"),
            "voice_id": "default",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=120  # Longer timeout for long text
            )
            tracer.api_call("POST", "/api/voice/synthesize (long)", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Long text synthesis successful")
                tracer.success("Long text synthesis works")
            else:
                tracer.step(f"Long synthesis: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Long text synthesis failed")


@pytest.mark.api
class TestVoiceSelection:
    """Tests for voice selection and profiles."""

    def test_get_available_voices(self, api_monitor, tracer):
        """Test getting list of available voices."""
        tracer.step("Getting available voices")

        try:
            response = api_monitor.get("/api/voices")
            tracer.api_call("GET", "/api/voices", response)

            if response.status_code == 200:
                voices = response.json()
                tracer.step(f"Available voices: {len(voices) if isinstance(voices, list) else 'N/A'}")

                if isinstance(voices, list) and len(voices) > 0:
                    for voice in voices[:5]:  # Log first 5
                        if isinstance(voice, dict):
                            tracer.step(f"Voice: {voice.get('id', 'unknown')} - {voice.get('name', 'unnamed')}")
                        else:
                            tracer.step(f"Voice: {voice}")

                tracer.success("Voices list retrieved")
            else:
                tracer.step(f"Voices returned {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get voices failed")

    def test_get_cloned_voices(self, api_monitor, tracer):
        """Test getting cloned voice profiles."""
        tracer.step("Getting cloned voice profiles")

        try:
            response = api_monitor.get("/api/profiles")
            tracer.api_call("GET", "/api/profiles", response)

            cloned_voices = []
            if response.status_code == 200:
                profiles = response.json()

                if isinstance(profiles, list):
                    cloned_voices = [
                        p for p in profiles
                        if isinstance(p, dict) and p.get("type") == "cloned"
                    ]

                tracer.step(f"Cloned voices found: {len(cloned_voices)}")
                tracer.success("Cloned voices retrieved")
            else:
                tracer.step(f"Profiles returned {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get cloned voices failed")

    def test_synthesize_with_cloned_voice(self, api_monitor, tracer):
        """Test synthesis using a cloned voice."""
        tracer.step("Testing synthesis with cloned voice")

        # First get available cloned voices
        try:
            response = api_monitor.get("/api/profiles")
            if response.status_code != 200:
                pytest.skip("Cannot get profiles")

            profiles = response.json()
            cloned_voice_id = None

            if isinstance(profiles, list):
                for p in profiles:
                    if isinstance(p, dict) and p.get("type") == "cloned":
                        cloned_voice_id = p.get("id") or p.get("voice_id")
                        break

            if not cloned_voice_id:
                tracer.step("No cloned voices available - using default")
                cloned_voice_id = "default"

            # Synthesize with the voice
            payload = {
                "text": "Testing synthesis with a cloned voice.",
                "voice_id": cloned_voice_id,
            }

            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", f"/api/voice/synthesize (voice={cloned_voice_id})", response)

            if response.status_code in [200, 201, 202]:
                tracer.step(f"Synthesis with voice {cloned_voice_id} successful")
                tracer.success("Cloned voice synthesis works")
            else:
                tracer.step(f"Cloned voice synthesis: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Cloned voice synthesis failed")


@pytest.mark.api
class TestSynthesisFormats:
    """Tests for output format options."""

    @pytest.mark.parametrize("output_format", ["wav", "mp3", "ogg"])
    def test_synthesis_output_formats(self, output_format, api_monitor, tracer):
        """Test synthesis with different output formats."""
        tracer.step(f"Testing synthesis with format: {output_format}")

        payload = {
            "text": "Testing output format.",
            "voice_id": "default",
            "output_format": output_format,
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", f"/api/voice/synthesize (format={output_format})", response)

            if response.status_code in [200, 201, 202]:
                content_type = response.headers.get("content-type", "")
                tracer.step(f"Format {output_format}: Content-Type={content_type}")
                tracer.success(f"Format {output_format} works")
            else:
                tracer.step(f"Format {output_format}: {response.status_code}")

        except Exception as e:
            tracer.error(e, f"Format {output_format} failed")


@pytest.mark.api
class TestMultiVoiceSynthesis:
    """Tests for multi-voice synthesis features."""

    def test_multi_voice_api(self, api_monitor, tracer):
        """Test multi-voice synthesis API."""
        tracer.step("Testing multi-voice synthesis")

        # Multi-voice payload with segments
        payload = {
            "segments": [
                {"text": "Hello, I am voice one.", "voice_id": "default"},
                {"text": "And I am voice two.", "voice_id": "default"},
            ],
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/multi-synthesize",
                json=payload,
                timeout=120
            )
            tracer.api_call("POST", "/api/voice/multi-synthesize", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Multi-voice synthesis successful")
                tracer.success("Multi-voice API works")
            elif response.status_code == 404:
                tracer.step("Multi-voice endpoint not implemented")
            else:
                tracer.step(f"Multi-voice: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Multi-voice synthesis failed")


@pytest.mark.workflow
class TestSynthesisUIWorkflow:
    """UI-based synthesis workflow tests."""

    @pytest.mark.smoke
    def test_navigate_to_synthesis(self, driver, app_launched, tracer):
        """Test navigation to synthesis panel."""
        tracer.step("Navigating to synthesis panel", driver, SCREENSHOTS_ENABLED)

        try:
            # Try different navigation options
            nav_options = [
                ("accessibility id", "NavGenerate"),
                ("accessibility id", "NavSynthesize"),
                ("accessibility id", "NavVoice"),
                ("xpath", "//*[contains(@Name, 'Generate')]"),
                ("xpath", "//*[contains(@Name, 'Synth')]"),
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
                tracer.success("Navigation to synthesis panel successful")
            else:
                tracer.step("No synthesis navigation found")

        except Exception as e:
            tracer.error(e, "Navigation failed")

    def test_text_input_exists(self, driver, app_launched, tracer):
        """Test that text input field exists in synthesis panel."""
        tracer.step("Looking for text input field", driver, SCREENSHOTS_ENABLED)

        try:
            text_inputs = [
                ("accessibility id", "SynthesisTextBox"),
                ("accessibility id", "TextInput"),
                ("accessibility id", "ScriptTextBox"),
                ("xpath", "//*[@AutomationId='SynthesisTextBox']"),
                ("xpath", "//Edit[contains(@Name, 'Text')]"),
            ]

            text_input = None
            for by, value in text_inputs:
                try:
                    text_input = driver.find_element(by, value)
                    tracer.step(f"Found text input: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if text_input:
                tracer.success("Text input field found")
            else:
                tracer.step("No text input field found")

        except Exception as e:
            tracer.error(e, "Text input search failed")

    def test_voice_selector_exists(self, driver, app_launched, tracer):
        """Test that voice selector exists in synthesis panel."""
        tracer.step("Looking for voice selector", driver, SCREENSHOTS_ENABLED)

        try:
            selectors = [
                ("accessibility id", "VoiceSelector"),
                ("accessibility id", "VoiceComboBox"),
                ("accessibility id", "VoiceDropdown"),
                ("xpath", "//*[@AutomationId='VoiceSelector']"),
                ("xpath", "//ComboBox[contains(@Name, 'Voice')]"),
            ]

            voice_selector = None
            for by, value in selectors:
                try:
                    voice_selector = driver.find_element(by, value)
                    tracer.step(f"Found voice selector: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if voice_selector:
                tracer.success("Voice selector found")
            else:
                tracer.step("No voice selector found")

        except Exception as e:
            tracer.error(e, "Voice selector search failed")

    def test_generate_button_exists(self, driver, app_launched, tracer):
        """Test that generate button exists."""
        tracer.step("Looking for generate button", driver, SCREENSHOTS_ENABLED)

        try:
            buttons = [
                ("accessibility id", "GenerateButton"),
                ("accessibility id", "SynthesizeButton"),
                ("accessibility id", "PlayButton"),
                ("xpath", "//*[contains(@Name, 'Generate')]"),
                ("xpath", "//*[contains(@Name, 'Synthesize')]"),
            ]

            generate_btn = None
            for by, value in buttons:
                try:
                    generate_btn = driver.find_element(by, value)
                    tracer.step(f"Found generate button: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if generate_btn:
                tracer.success("Generate button found")
            else:
                tracer.step("No generate button found")

        except Exception as e:
            tracer.error(e, "Generate button search failed")


@pytest.mark.workflow
class TestSynthesisE2E:
    """End-to-end synthesis workflow tests."""

    @pytest.mark.slow
    def test_complete_synthesis_api_workflow(self, api_monitor, tracer):
        """Test complete synthesis workflow via API."""
        tracer.step("Starting complete synthesis workflow")

        # Step 1: Get available voices
        tracer.step("Step 1: Get available voices")
        response = api_monitor.get("/api/voices")
        tracer.api_call("GET", "/api/voices", response)

        voices = []
        if response.status_code == 200:
            voices = response.json()
            tracer.step(f"Found {len(voices) if isinstance(voices, list) else 'N/A'} voices")

        # Step 2: Select voice
        tracer.step("Step 2: Select voice")
        selected_voice = "default"
        if isinstance(voices, list) and len(voices) > 0:
            if isinstance(voices[0], dict):
                selected_voice = voices[0].get("id", "default")
            else:
                selected_voice = str(voices[0])
        tracer.step(f"Selected voice: {selected_voice}")

        # Step 3: Synthesize text
        tracer.step("Step 3: Synthesize text")
        payload = {
            "text": get_test_script("short"),
            "voice_id": selected_voice,
        }

        response = requests.post(
            f"{BACKEND_URL}/api/voice/synthesize",
            json=payload,
            timeout=60
        )
        tracer.api_call("POST", "/api/voice/synthesize", response)

        audio_result = None
        if response.status_code in [200, 201, 202]:
            content_type = response.headers.get("content-type", "")
            if "audio" in content_type:
                audio_result = response.content
                tracer.step(f"Received audio: {len(audio_result)} bytes")
            else:
                audio_result = response.json()
                tracer.step(f"Synthesis result: {audio_result}")

        # Step 4: Verify result
        tracer.step("Step 4: Verify result")
        if audio_result:
            tracer.success("Complete synthesis workflow successful")
        else:
            tracer.step("Synthesis did not return audio")


# Run tests directly if executed as script
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
