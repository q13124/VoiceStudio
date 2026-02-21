"""
Engine Availability Matrix Tests.

Comprehensive tests for all VoiceStudio engine capabilities:
- TTS engines (XTTS, Piper, Chatterbox, Bark, OpenVoice)
- STT engines (Whisper, WhisperCPP, Vosk)
- Voice conversion engines (RVC)
- Image generation (SDXL, ComfyUI)
- Video generation (SVD, Deforum)

Requires:
- Backend running on port 8000
- Engine binaries/models available
"""

from __future__ import annotations

import os

# Import tracing infrastructure
import sys
from pathlib import Path
from typing import Any

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent))
from tracing.api_monitor import APIMonitor
from tracing.workflow_tracer import WorkflowTracer

# Test configuration
BACKEND_URL = os.getenv("VOICESTUDIO_BACKEND_URL", "http://127.0.0.1:8000")
OUTPUT_DIR = Path(os.getenv("VOICESTUDIO_OUTPUT_DIR", ".buildlogs/validation"))
TRACE_ENABLED = os.getenv("VOICESTUDIO_TRACE_ENABLED", "1") == "1"

# Pytest markers
pytestmark = [
    pytest.mark.engines,
    pytest.mark.api,
]


# Engine matrix definition
ENGINE_MATRIX: dict[str, list[dict[str, Any]]] = {
    "tts": [
        {
            "id": "xtts",
            "name": "XTTS v2",
            "capabilities": ["synthesis", "voice_cloning", "multilingual"],
            "test_endpoint": "/api/engine/xtts/status",
        },
        {
            "id": "piper",
            "name": "Piper",
            "capabilities": ["synthesis", "fast", "lightweight"],
            "test_endpoint": "/api/engine/piper/status",
        },
        {
            "id": "chatterbox",
            "name": "Chatterbox",
            "capabilities": ["synthesis", "emotional"],
            "test_endpoint": "/api/engine/chatterbox/status",
        },
        {
            "id": "bark",
            "name": "Bark",
            "capabilities": ["synthesis", "nonverbal", "music"],
            "test_endpoint": "/api/engine/bark/status",
        },
        {
            "id": "openvoice",
            "name": "OpenVoice",
            "capabilities": ["synthesis", "voice_cloning"],
            "test_endpoint": "/api/engine/openvoice/status",
        },
    ],
    "stt": [
        {
            "id": "whisper",
            "name": "Whisper",
            "capabilities": ["transcription", "multilingual", "timestamps"],
            "test_endpoint": "/api/engine/whisper/status",
        },
        {
            "id": "whisper_cpp",
            "name": "WhisperCPP",
            "capabilities": ["transcription", "fast", "cpu_optimized"],
            "test_endpoint": "/api/engine/whisper_cpp/status",
        },
        {
            "id": "vosk",
            "name": "Vosk",
            "capabilities": ["transcription", "offline", "realtime"],
            "test_endpoint": "/api/engine/vosk/status",
        },
    ],
    "voice_conversion": [
        {
            "id": "rvc",
            "name": "RVC",
            "capabilities": ["voice_conversion", "realtime", "model_training"],
            "test_endpoint": "/api/engine/rvc/status",
        },
    ],
    "image_gen": [
        {
            "id": "sdxl",
            "name": "SDXL",
            "capabilities": ["image_generation", "high_quality"],
            "test_endpoint": "/api/engine/sdxl/status",
        },
        {
            "id": "comfyui",
            "name": "ComfyUI",
            "capabilities": ["image_generation", "workflow", "custom_nodes"],
            "test_endpoint": "/api/engine/comfyui/status",
        },
    ],
    "video_gen": [
        {
            "id": "svd",
            "name": "Stable Video Diffusion",
            "capabilities": ["video_generation", "image_to_video"],
            "test_endpoint": "/api/engine/svd/status",
        },
        {
            "id": "deforum",
            "name": "Deforum",
            "capabilities": ["video_generation", "animation", "interpolation"],
            "test_endpoint": "/api/engine/deforum/status",
        },
    ],
}


@pytest.fixture
def tracer():
    """Create a workflow tracer for this test."""
    tracer = WorkflowTracer("engine_matrix", OUTPUT_DIR)
    tracer.start()
    yield tracer
    tracer.export_report()


@pytest.fixture
def api_monitor():
    """Create an API monitor for tracking backend calls."""
    monitor = APIMonitor(base_url=BACKEND_URL)
    yield monitor
    monitor.export_log(OUTPUT_DIR / "api_coverage" / "engine_matrix_api_calls.json")


class TestEngineList:
    """Tests for engine listing API."""

    @pytest.mark.smoke
    def test_list_all_engines(self, api_monitor, tracer):
        """Test listing all available engines."""
        tracer.step("Getting all engines")

        try:
            response = api_monitor.get("/api/engines/list")
            tracer.api_call("GET", "/api/engines/list", response)

            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

            engines = response.json()
            tracer.step(f"Engines response type: {type(engines)}")

            if isinstance(engines, list):
                tracer.step(f"Total engines: {len(engines)}")

                # Categorize engines
                by_type = {}
                for engine in engines:
                    if isinstance(engine, dict):
                        engine_type = engine.get("type", "unknown")
                        if engine_type not in by_type:
                            by_type[engine_type] = []
                        by_type[engine_type].append(engine.get("id", engine.get("name", "?")))

                for etype, eids in by_type.items():
                    tracer.step(f"  {etype}: {len(eids)} ({', '.join(eids[:3])}...)")
            else:
                tracer.step(f"Engines: {engines}")

            tracer.success("Engine list retrieved")

        except Exception as e:
            tracer.error(e, "Engine list failed")
            raise

    def test_list_engines_by_type(self, api_monitor, tracer):
        """Test listing engines by type."""
        tracer.step("Getting engines by type")

        engine_types = ["tts", "stt", "voice_conversion", "image_gen", "video_gen"]

        for etype in engine_types:
            try:
                response = api_monitor.get(f"/api/engine/list?type={etype}")
                tracer.api_call("GET", f"/api/engine/list?type={etype}", response)

                if response.status_code == 200:
                    engines = response.json()
                    count = len(engines) if isinstance(engines, list) else "N/A"
                    tracer.step(f"  {etype}: {count} engines")
                elif response.status_code == 404:
                    tracer.step(f"  {etype}: endpoint not found")
                else:
                    tracer.step(f"  {etype}: {response.status_code}")

            except Exception as e:
                tracer.step(f"  {etype}: error - {e}")

        tracer.success("Engine type query complete")


class TestTTSEngines:
    """Tests for TTS (Text-to-Speech) engines."""

    @pytest.mark.parametrize("engine", ENGINE_MATRIX["tts"], ids=[e["id"] for e in ENGINE_MATRIX["tts"]])
    def test_tts_engine_status(self, engine, api_monitor, tracer):
        """Test status of each TTS engine."""
        tracer.step(f"Testing TTS engine: {engine['name']}")

        try:
            response = api_monitor.get(engine["test_endpoint"])
            tracer.api_call("GET", engine["test_endpoint"], response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Status: {status}")
                tracer.success(f"{engine['name']} is available")
            elif response.status_code == 404:
                tracer.step(f"{engine['name']}: endpoint not found")
            else:
                tracer.step(f"{engine['name']}: {response.status_code}")

        except Exception as e:
            tracer.error(e, f"{engine['name']} status check failed")

    def test_tts_synthesis_basic(self, api_monitor, tracer):
        """Test basic TTS synthesis."""
        tracer.step("Testing TTS synthesis")

        payload = {
            "text": "Hello, this is a TTS test.",
            "engine": "auto",
        }

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/voice/synthesize",
                json=payload,
                timeout=60
            )
            tracer.api_call("POST", "/api/voice/synthesize", response)

            if response.status_code in [200, 201, 202]:
                tracer.step("TTS synthesis successful")
                tracer.success("TTS synthesis works")
            else:
                tracer.step(f"TTS synthesis: {response.status_code}")

        except Exception as e:
            tracer.error(e, "TTS synthesis failed")


class TestSTTEngines:
    """Tests for STT (Speech-to-Text) engines."""

    @pytest.mark.parametrize("engine", ENGINE_MATRIX["stt"], ids=[e["id"] for e in ENGINE_MATRIX["stt"]])
    def test_stt_engine_status(self, engine, api_monitor, tracer):
        """Test status of each STT engine."""
        tracer.step(f"Testing STT engine: {engine['name']}")

        try:
            response = api_monitor.get(engine["test_endpoint"])
            tracer.api_call("GET", engine["test_endpoint"], response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Status: {status}")
                tracer.success(f"{engine['name']} is available")
            elif response.status_code == 404:
                tracer.step(f"{engine['name']}: endpoint not found")
            else:
                tracer.step(f"{engine['name']}: {response.status_code}")

        except Exception as e:
            tracer.error(e, f"{engine['name']} status check failed")


class TestVoiceConversionEngines:
    """Tests for voice conversion engines."""

    @pytest.mark.parametrize("engine", ENGINE_MATRIX["voice_conversion"],
                           ids=[e["id"] for e in ENGINE_MATRIX["voice_conversion"]])
    def test_vc_engine_status(self, engine, api_monitor, tracer):
        """Test status of each voice conversion engine."""
        tracer.step(f"Testing VC engine: {engine['name']}")

        try:
            response = api_monitor.get(engine["test_endpoint"])
            tracer.api_call("GET", engine["test_endpoint"], response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Status: {status}")
                tracer.success(f"{engine['name']} is available")
            elif response.status_code == 404:
                tracer.step(f"{engine['name']}: endpoint not found")
            else:
                tracer.step(f"{engine['name']}: {response.status_code}")

        except Exception as e:
            tracer.error(e, f"{engine['name']} status check failed")

    def test_rvc_models_list(self, api_monitor, tracer):
        """Test listing RVC models."""
        tracer.step("Getting RVC models")

        try:
            response = api_monitor.get("/api/rvc/models")
            tracer.api_call("GET", "/api/rvc/models", response)

            if response.status_code == 200:
                models = response.json()
                count = len(models) if isinstance(models, list) else "N/A"
                tracer.step(f"RVC models: {count}")
                tracer.success("RVC models retrieved")
            elif response.status_code == 404:
                tracer.step("RVC models endpoint not found")
            else:
                tracer.step(f"RVC models: {response.status_code}")

        except Exception as e:
            tracer.error(e, "RVC models failed")


class TestImageGenEngines:
    """Tests for image generation engines."""

    @pytest.mark.parametrize("engine", ENGINE_MATRIX["image_gen"],
                           ids=[e["id"] for e in ENGINE_MATRIX["image_gen"]])
    def test_image_engine_status(self, engine, api_monitor, tracer):
        """Test status of each image generation engine."""
        tracer.step(f"Testing image engine: {engine['name']}")

        try:
            response = api_monitor.get(engine["test_endpoint"])
            tracer.api_call("GET", engine["test_endpoint"], response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Status: {status}")
                tracer.success(f"{engine['name']} is available")
            elif response.status_code == 404:
                tracer.step(f"{engine['name']}: endpoint not found")
            else:
                tracer.step(f"{engine['name']}: {response.status_code}")

        except Exception as e:
            tracer.error(e, f"{engine['name']} status check failed")


class TestVideoGenEngines:
    """Tests for video generation engines."""

    @pytest.mark.parametrize("engine", ENGINE_MATRIX["video_gen"],
                           ids=[e["id"] for e in ENGINE_MATRIX["video_gen"]])
    def test_video_engine_status(self, engine, api_monitor, tracer):
        """Test status of each video generation engine."""
        tracer.step(f"Testing video engine: {engine['name']}")

        try:
            response = api_monitor.get(engine["test_endpoint"])
            tracer.api_call("GET", engine["test_endpoint"], response)

            if response.status_code == 200:
                status = response.json()
                tracer.step(f"Status: {status}")
                tracer.success(f"{engine['name']} is available")
            elif response.status_code == 404:
                tracer.step(f"{engine['name']}: endpoint not found")
            else:
                tracer.step(f"{engine['name']}: {response.status_code}")

        except Exception as e:
            tracer.error(e, f"{engine['name']} status check failed")


class TestEngineCapabilities:
    """Tests for engine capability queries."""

    def test_get_engine_capabilities(self, api_monitor, tracer):
        """Test getting capabilities for available engines."""
        tracer.step("Testing engine capabilities")

        # First get list of engines
        try:
            response = api_monitor.get("/api/engine/list")
            if response.status_code != 200:
                pytest.skip("Engine list not available")

            engines = response.json()
            if not isinstance(engines, list) or len(engines) == 0:
                pytest.skip("No engines available")

            # Test first 3 engines
            tested = 0
            for engine in engines[:3]:
                engine_id = None
                if isinstance(engine, dict):
                    engine_id = engine.get("id") or engine.get("name")
                else:
                    engine_id = str(engine)

                if engine_id:
                    response = api_monitor.get(f"/api/engine/{engine_id}/capabilities")
                    tracer.api_call("GET", f"/api/engine/{engine_id}/capabilities", response)

                    if response.status_code == 200:
                        caps = response.json()
                        tracer.step(f"{engine_id}: {caps}")
                        tested += 1
                    else:
                        tracer.step(f"{engine_id}: {response.status_code}")

            tracer.step(f"Tested {tested} engine capabilities")
            tracer.success("Engine capabilities tested")

        except Exception as e:
            tracer.error(e, "Engine capabilities failed")


class TestEngineHealth:
    """Tests for engine health checking."""

    @pytest.mark.smoke
    def test_overall_engine_health(self, api_monitor, tracer):
        """Test overall engine health endpoint."""
        tracer.step("Testing engine health")

        try:
            response = api_monitor.get("/api/engine/health")
            tracer.api_call("GET", "/api/engine/health", response)

            if response.status_code == 200:
                health = response.json()
                tracer.step(f"Health status: {health}")
                tracer.success("Engine health check works")
            elif response.status_code == 404:
                tracer.step("Engine health endpoint not found")
            else:
                tracer.step(f"Engine health: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Engine health failed")

    def test_preflight_check(self, api_monitor, tracer):
        """Test engine preflight check."""
        tracer.step("Testing preflight check")

        try:
            response = api_monitor.get("/api/preflight")
            tracer.api_call("GET", "/api/preflight", response)

            if response.status_code == 200:
                preflight = response.json()
                tracer.step(f"Preflight: {preflight}")

                # Check for expected fields
                expected = ["engines", "status", "ready"]
                for field in expected:
                    if field in preflight:
                        tracer.step(f"  {field}: {preflight[field]}")

                tracer.success("Preflight check works")
            elif response.status_code == 404:
                tracer.step("Preflight endpoint not found")
            else:
                tracer.step(f"Preflight: {response.status_code}")

        except Exception as e:
            tracer.error(e, "Preflight check failed")


class TestEngineMatrixReport:
    """Generate engine matrix report."""

    @pytest.mark.smoke
    def test_generate_engine_report(self, api_monitor, tracer):
        """Generate comprehensive engine availability report."""
        tracer.step("Generating engine matrix report")

        report = {
            "available": {},
            "unavailable": {},
            "total_defined": 0,
            "total_available": 0,
        }

        for category, engines in ENGINE_MATRIX.items():
            report["available"][category] = []
            report["unavailable"][category] = []

            for engine in engines:
                report["total_defined"] += 1

                try:
                    response = api_monitor.get(engine["test_endpoint"])

                    if response.status_code == 200:
                        report["available"][category].append(engine["name"])
                        report["total_available"] += 1
                        tracer.step(f"✓ {engine['name']}")
                    else:
                        report["unavailable"][category].append(engine["name"])
                        tracer.step(f"✗ {engine['name']}")

                except Exception:
                    report["unavailable"][category].append(engine["name"])
                    tracer.step(f"✗ {engine['name']} (error)")

        # Summary
        tracer.step("\n=== Engine Matrix Summary ===")
        tracer.step(f"Total engines defined: {report['total_defined']}")
        tracer.step(f"Engines available: {report['total_available']}")
        coverage = (report['total_available'] / report['total_defined'] * 100) if report['total_defined'] > 0 else 0
        tracer.step(f"Coverage: {coverage:.1f}%")

        for category in ENGINE_MATRIX:
            avail = len(report["available"][category])
            total = len(ENGINE_MATRIX[category])
            tracer.step(f"  {category}: {avail}/{total}")

        # Write report
        report_path = OUTPUT_DIR / "engine_matrix_report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("VoiceStudio Engine Matrix Report\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Total engines: {report['total_defined']}\n")
            f.write(f"Available: {report['total_available']}\n")
            f.write(f"Coverage: {coverage:.1f}%\n\n")

            for category in ENGINE_MATRIX:
                f.write(f"\n{category.upper()}\n")
                f.write("-" * 20 + "\n")
                for name in report["available"][category]:
                    f.write(f"  ✓ {name}\n")
                for name in report["unavailable"][category]:
                    f.write(f"  ✗ {name}\n")

        tracer.step(f"Report written to: {report_path}")
        tracer.success("Engine matrix report generated")


# Run tests directly if executed as script
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
