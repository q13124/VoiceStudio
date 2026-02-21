"""
Real-Time Voice Converter Tests.

Tests for the real-time voice conversion workflow:
- Audio device selection (input/output)
- Voice model selection (RVC, etc.)
- Latency settings
- Real-time processing controls
- Audio monitoring

Requires:
- WinAppDriver running
- Backend running on port 8000
- VoiceStudio application built
- Audio devices available
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

# Test configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8000")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
TRACE_ENABLED = os.getenv("VOICESTUDIO_TRACE_ENABLED", "1") == "1"
SCREENSHOTS_ENABLED = os.getenv("VOICESTUDIO_SCREENSHOTS_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.realtime,
    pytest.mark.voice_conversion,
]


@pytest.fixture
def tracer():
    """Create a workflow tracer for this test."""
    tracer = WorkflowTracer("realtime_converter", OUTPUT_DIR)
    tracer.start()
    yield tracer
    tracer.export_report()


@pytest.fixture
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "realtime_converter_api_calls.json")


class TestAudioDevices:
    """Tests for audio device enumeration and selection."""

    @pytest.mark.smoke
    def test_list_audio_devices(self, api_monitor, tracer):
        """Test listing available audio devices."""
        tracer.step("Getting audio devices")

        try:
            response = api_monitor.get("/api/audio/devices")
            tracer.api_call("GET", "/api/audio/devices", response)

            if response.status_code == 200:
                devices = response.json()
                tracer.step(f"Audio devices response: {devices}")

                if isinstance(devices, dict):
                    inputs = devices.get("inputs", devices.get("input", []))
                    outputs = devices.get("outputs", devices.get("output", []))
                    tracer.step(f"Input devices: {len(inputs) if isinstance(inputs, list) else 'N/A'}")
                    tracer.step(f"Output devices: {len(outputs) if isinstance(outputs, list) else 'N/A'}")
                elif isinstance(devices, list):
                    tracer.step(f"Total devices: {len(devices)}")

                tracer.success("Audio devices retrieved")
            else:
                tracer.step(f"Audio devices returned {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get audio devices failed")

    def test_list_input_devices(self, api_monitor, tracer):
        """Test listing input (microphone) devices."""
        tracer.step("Getting input devices")

        try:
            response = api_monitor.get("/api/audio/devices/input")
            tracer.api_call("GET", "/api/audio/devices/input", response)

            if response.status_code == 200:
                devices = response.json()
                tracer.step(f"Input devices: {devices}")
                tracer.success("Input devices retrieved")
            elif response.status_code == 404:
                tracer.step("Input devices endpoint not found")
            else:
                tracer.step(f"Input devices: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get input devices failed")

    def test_list_output_devices(self, api_monitor, tracer):
        """Test listing output (speaker) devices."""
        tracer.step("Getting output devices")

        try:
            response = api_monitor.get("/api/audio/devices/output")
            tracer.api_call("GET", "/api/audio/devices/output", response)

            if response.status_code == 200:
                devices = response.json()
                tracer.step(f"Output devices: {devices}")
                tracer.success("Output devices retrieved")
            elif response.status_code == 404:
                tracer.step("Output devices endpoint not found")
            else:
                tracer.step(f"Output devices: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get output devices failed")


class TestVoiceModels:
    """Tests for voice conversion model selection."""

    def test_list_rvc_models(self, api_monitor, tracer):
        """Test listing available RVC models."""
        tracer.step("Getting RVC models")

        try:
            response = api_monitor.get("/api/rvc/models")
            tracer.api_call("GET", "/api/rvc/models", response)

            if response.status_code == 200:
                models = response.json()
                tracer.step(f"RVC models: {models}")

                if isinstance(models, list) and len(models) > 0:
                    for model in models[:5]:
                        if isinstance(model, dict):
                            tracer.step(f"  - {model.get('name', 'unknown')}")
                        else:
                            tracer.step(f"  - {model}")

                tracer.success("RVC models retrieved")
            elif response.status_code == 404:
                tracer.step("RVC models endpoint not found")
            else:
                tracer.step(f"RVC models: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get RVC models failed")

    def test_list_voice_conversion_engines(self, api_monitor, tracer):
        """Test listing voice conversion engines."""
        tracer.step("Getting voice conversion engines")

        try:
            response = api_monitor.get("/api/engine/list")
            tracer.api_call("GET", "/api/engine/list", response)

            if response.status_code == 200:
                engines = response.json()

                # Filter voice conversion engines
                vc_engines = []
                if isinstance(engines, list):
                    for engine in engines:
                        if isinstance(engine, dict):
                            engine_type = engine.get("type", "")
                            engine_name = engine.get("name", "").lower()
                            if "conversion" in engine_type or "rvc" in engine_name or "vc" in engine_type:
                                vc_engines.append(engine)
                        elif "rvc" in str(engine).lower():
                            vc_engines.append(engine)

                tracer.step(f"Voice conversion engines: {len(vc_engines)}")
                for engine in vc_engines:
                    tracer.step(f"  - {engine}")

                tracer.success("Voice conversion engines retrieved")
            else:
                tracer.step(f"Engine list: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get VC engines failed")


class TestRealtimeProcessing:
    """Tests for real-time processing controls."""

    def test_realtime_status(self, api_monitor, tracer):
        """Test real-time processing status."""
        tracer.step("Getting real-time status")

        try:
            response = api_monitor.get("/api/realtime/status")
            tracer.api_call("GET", "/api/realtime/status", response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Real-time status: {status}")

                # Check for expected status fields
                expected_fields = ["active", "running", "latency", "model"]
                for field in expected_fields:
                    if field in status:
                        tracer.step(f"  {field}: {status[field]}")

                tracer.success("Real-time status retrieved")
            elif response.status_code == 404:
                tracer.step("Real-time status endpoint not found")
            else:
                tracer.step(f"Real-time status: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Get real-time status failed")

    def test_realtime_start_stop(self, api_monitor, tracer):
        """Test starting and stopping real-time processing."""
        tracer.step("Testing real-time start/stop")

        # Try to start real-time processing
        try:
            start_payload = {
                "model": "default",
                "input_device": "default",
                "output_device": "default",
            }

            response = requests.post(
                f"{BACKEND_URL}/api/realtime/start",
                json=start_payload,
                timeout=10
            )
            tracer.api_call("POST", "/api/realtime/start", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Real-time processing started")

                # Wait a moment
                time.sleep(1)

                # Stop it
                response = requests.post(
                    f"{BACKEND_URL}/api/realtime/stop",
                    timeout=10
                )
                tracer.api_call("POST", "/api/realtime/stop", response)

                if response.status_code in [200, 201, 202]:
                    tracer.step("Real-time processing stopped")
                    tracer.success("Real-time start/stop works")
                else:
                    tracer.step(f"Stop failed: {response.status_code}")

            elif response.status_code == 404:
                tracer.step("Real-time endpoints not found")
            elif response.status_code == 422:
                tracer.step(f"Start validation failed: {response.text}")
            else:
                tracer.step(f"Start returned {response.status_code}")

        except Exception as e:
            tracer.error(e, "Real-time start/stop failed")

    def test_latency_settings(self, api_monitor, tracer):
        """Test latency configuration."""
        tracer.step("Testing latency settings")

        try:
            # Get current settings
            response = api_monitor.get("/api/realtime/settings")
            tracer.api_call("GET", "/api/realtime/settings", response)

            if response.status_code == 200:
                settings = response.json()
                tracer.step(f"Current settings: {settings}")

                # Try to update latency
                if "latency" in settings or "buffer_size" in settings:
                    new_settings = {"latency": 50}  # 50ms
                    response = requests.post(
                        f"{BACKEND_URL}/api/realtime/settings",
                        json=new_settings,
                        timeout=10
                    )
                    tracer.api_call("POST", "/api/realtime/settings", response)

                    if response.status_code in [200, 201]:
                        tracer.step("Latency settings updated")
                        tracer.success("Latency configuration works")
                    else:
                        tracer.step(f"Settings update: {response.status_code}")

            elif response.status_code == 404:
                tracer.step("Real-time settings endpoint not found")
            else:
                tracer.step(f"Settings: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Latency settings failed")


class TestRealtimeConverterUI:
    """UI-based real-time converter tests."""

    @pytest.mark.smoke
    def test_navigate_to_realtime(self, driver, app_launched, tracer):
        """Test navigation to real-time converter panel."""
        tracer.step("Navigating to real-time converter", driver, SCREENSHOTS_ENABLED)

        try:
            nav_options = [
                ("accessibility id", "NavRealtime"),
                ("accessibility id", "NavVoiceConverter"),
                ("accessibility id", "NavLive"),
                ("xpath", "//*[contains(@Name, 'Real')]"),
                ("xpath", "//*[contains(@Name, 'Converter')]"),
                ("xpath", "//*[contains(@Name, 'Live')]"),
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
                tracer.success("Navigation to real-time converter successful")
            else:
                tracer.step("No real-time converter navigation found")

        except Exception as e:
            tracer.error(e, "Navigation failed")

    def test_input_device_selector(self, driver, app_launched, tracer):
        """Test input device selector in UI."""
        tracer.step("Looking for input device selector", driver, SCREENSHOTS_ENABLED)

        try:
            selectors = [
                ("accessibility id", "InputDeviceSelector"),
                ("accessibility id", "MicrophoneComboBox"),
                ("accessibility id", "InputDevice"),
                ("xpath", "//ComboBox[contains(@Name, 'Input')]"),
                ("xpath", "//ComboBox[contains(@Name, 'Microphone')]"),
            ]

            input_selector = None
            for by, value in selectors:
                try:
                    input_selector = driver.find_element(by, value)
                    tracer.step(f"Found input selector: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if input_selector:
                tracer.success("Input device selector found")
            else:
                tracer.step("No input device selector found")

        except Exception as e:
            tracer.error(e, "Input selector search failed")

    def test_output_device_selector(self, driver, app_launched, tracer):
        """Test output device selector in UI."""
        tracer.step("Looking for output device selector", driver, SCREENSHOTS_ENABLED)

        try:
            selectors = [
                ("accessibility id", "OutputDeviceSelector"),
                ("accessibility id", "SpeakerComboBox"),
                ("accessibility id", "OutputDevice"),
                ("xpath", "//ComboBox[contains(@Name, 'Output')]"),
                ("xpath", "//ComboBox[contains(@Name, 'Speaker')]"),
            ]

            output_selector = None
            for by, value in selectors:
                try:
                    output_selector = driver.find_element(by, value)
                    tracer.step(f"Found output selector: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if output_selector:
                tracer.success("Output device selector found")
            else:
                tracer.step("No output device selector found")

        except Exception as e:
            tracer.error(e, "Output selector search failed")

    def test_model_selector(self, driver, app_launched, tracer):
        """Test voice model selector in UI."""
        tracer.step("Looking for model selector", driver, SCREENSHOTS_ENABLED)

        try:
            selectors = [
                ("accessibility id", "ModelSelector"),
                ("accessibility id", "VoiceModelComboBox"),
                ("accessibility id", "RVCModelSelector"),
                ("xpath", "//ComboBox[contains(@Name, 'Model')]"),
                ("xpath", "//ComboBox[contains(@Name, 'Voice')]"),
            ]

            model_selector = None
            for by, value in selectors:
                try:
                    model_selector = driver.find_element(by, value)
                    tracer.step(f"Found model selector: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if model_selector:
                tracer.success("Model selector found")
            else:
                tracer.step("No model selector found")

        except Exception as e:
            tracer.error(e, "Model selector search failed")

    def test_start_stop_buttons(self, driver, app_launched, tracer):
        """Test start/stop buttons in UI."""
        tracer.step("Looking for start/stop buttons", driver, SCREENSHOTS_ENABLED)

        try:
            buttons = [
                ("accessibility id", "StartButton"),
                ("accessibility id", "StopButton"),
                ("accessibility id", "ToggleButton"),
                ("xpath", "//*[contains(@Name, 'Start')]"),
                ("xpath", "//*[contains(@Name, 'Stop')]"),
            ]

            found_buttons = []
            for by, value in buttons:
                try:
                    driver.find_element(by, value)
                    found_buttons.append(value)
                    tracer.step(f"Found button: {value}", driver, SCREENSHOTS_ENABLED)
                except Exception:
                    continue

            if found_buttons:
                tracer.success(f"Found {len(found_buttons)} control buttons")
            else:
                tracer.step("No start/stop buttons found")

        except Exception as e:
            tracer.error(e, "Button search failed")

    def test_latency_slider(self, driver, app_launched, tracer):
        """Test latency slider in UI."""
        tracer.step("Looking for latency slider", driver, SCREENSHOTS_ENABLED)

        try:
            sliders = [
                ("accessibility id", "LatencySlider"),
                ("accessibility id", "BufferSlider"),
                ("xpath", "//Slider[contains(@Name, 'Latency')]"),
                ("xpath", "//Slider[contains(@Name, 'Buffer')]"),
            ]

            latency_slider = None
            for by, value in sliders:
                try:
                    latency_slider = driver.find_element(by, value)
                    tracer.step(f"Found latency slider: {value}", driver, SCREENSHOTS_ENABLED)
                    break
                except Exception:
                    continue

            if latency_slider:
                tracer.success("Latency slider found")
            else:
                tracer.step("No latency slider found")

        except Exception as e:
            tracer.error(e, "Latency slider search failed")


class TestRealtimeE2E:
    """End-to-end real-time converter tests."""

    @pytest.mark.slow
    def test_complete_realtime_setup(self, api_monitor, tracer):
        """Test complete real-time converter setup workflow."""
        tracer.step("Starting complete real-time setup workflow")

        # Step 1: Get audio devices
        tracer.step("Step 1: Get audio devices")
        response = api_monitor.get("/api/audio/devices")
        tracer.api_call("GET", "/api/audio/devices", response)

        devices = {}
        if response.status_code == 200:
            devices = response.json()
            tracer.step(f"Devices retrieved: {type(devices)}")

        # Step 2: Get available models
        tracer.step("Step 2: Get voice models")
        response = api_monitor.get("/api/rvc/models")
        tracer.api_call("GET", "/api/rvc/models", response)

        models = []
        if response.status_code == 200:
            models = response.json()
            tracer.step(f"Models: {len(models) if isinstance(models, list) else 'N/A'}")

        # Step 3: Check status
        tracer.step("Step 3: Check real-time status")
        response = api_monitor.get("/api/realtime/status")
        tracer.api_call("GET", "/api/realtime/status", response)

        status = {}
        if response.status_code == 200:
            status = response.json()
            tracer.step(f"Status: {status}")

        tracer.success("Real-time setup workflow complete")

    @pytest.mark.slow
    def test_realtime_session_api(self, api_monitor, tracer):
        """Test real-time session lifecycle via API."""
        tracer.step("Testing real-time session lifecycle")

        # Check if real-time endpoints exist
        response = api_monitor.get("/api/realtime/status")
        if response.status_code == 404:
            pytest.skip("Real-time endpoints not available")

        try:
            # Start session
            tracer.step("Starting real-time session")
            start_payload = {
                "model": "default",
                "input_device": "default",
                "output_device": "default",
                "latency": 50,
            }

            response = requests.post(
                f"{BACKEND_URL}/api/realtime/start",
                json=start_payload,
                timeout=10
            )
            tracer.api_call("POST", "/api/realtime/start", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("Session started")

                # Check status while running
                time.sleep(0.5)
                response = api_monitor.get("/api/realtime/status")
                tracer.api_call("GET", "/api/realtime/status (running)", response)

                if response.status_code == 200:
                    status = response.json()
                    tracer.step(f"Running status: {status}")

                # Stop session
                response = requests.post(
                    f"{BACKEND_URL}/api/realtime/stop",
                    timeout=10
                )
                tracer.api_call("POST", "/api/realtime/stop", response)

                if response.status_code in [200, 201, 202]:
                    tracer.step("Session stopped")
                    tracer.success("Real-time session lifecycle works")
                else:
                    tracer.step(f"Stop failed: {response.status_code}")
            else:
                tracer.step(f"Start failed: {response.status_code}: {response.text[:200]}")

        except Exception as e:
            tracer.error(e, "Real-time session test failed")


# Run tests directly if executed as script
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
