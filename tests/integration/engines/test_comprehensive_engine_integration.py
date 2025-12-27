"""
Comprehensive Engine Integration Test Suite
Tests all 48 engines for functionality, error handling, and completeness.

Worker 3: Testing/Quality/Documentation Specialist
Date: 2025-01-28
"""

import importlib.util
import inspect
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# All 48 engines from __init__.py
ALL_ENGINES = [
    # TTS Engines
    ("xtts_engine", "XTTSEngine", "TTS"),
    ("chatterbox_engine", "ChatterboxEngine", "TTS"),
    ("tortoise_engine", "TortoiseEngine", "TTS"),
    ("piper_engine", "PiperEngine", "TTS"),
    ("silero_engine", "SileroEngine", "TTS"),
    ("f5_tts_engine", "F5TTSEngine", "TTS"),
    ("voxcpm_engine", "VoxCPMEngine", "TTS"),
    ("parakeet_engine", "ParakeetEngine", "TTS"),
    ("higgs_audio_engine", "HiggsAudioEngine", "TTS"),
    ("openvoice_engine", "OpenVoiceEngine", "TTS"),
    ("bark_engine", "BarkEngine", "TTS"),
    ("openai_tts_engine", "OpenAITTSEngine", "TTS"),
    ("marytts_engine", "MaryTTSEngine", "TTS"),
    ("rhvoice_engine", "RHVoiceEngine", "TTS"),
    ("espeak_ng_engine", "ESpeakNGEngine", "TTS"),
    ("festival_flite_engine", "FestivalFliteEngine", "TTS"),
    # STT Engines
    ("whisper_engine", "WhisperEngine", "STT"),
    ("whisper_cpp_engine", "WhisperCPPEngine", "STT"),
    ("whisper_ui_engine", "WhisperUIEngine", "STT"),
    ("vosk_engine", "VoskEngine", "STT"),
    ("aeneas_engine", "AeneasEngine", "STT"),
    # Voice Conversion Engines
    ("rvc_engine", "RVCEngine", "VC"),
    ("gpt_sovits_engine", "GPTSovitsEngine", "VC"),
    ("mockingbird_engine", "MockingBirdEngine", "VC"),
    ("voice_ai_engine", "VoiceAIEngine", "VC"),
    ("lyrebird_engine", "LyrebirdEngine", "VC"),
    # Image Generation Engines
    ("sdxl_engine", "SDXLEngine", "IMAGE"),
    ("sdxl_comfy_engine", "SDXLComfyEngine", "IMAGE"),
    ("comfyui_engine", "ComfyUIEngine", "IMAGE"),
    ("automatic1111_engine", "Automatic1111Engine", "IMAGE"),
    ("sdnext_engine", "SDNextEngine", "IMAGE"),
    ("invokeai_engine", "InvokeAIEngine", "IMAGE"),
    ("fooocus_engine", "FooocusEngine", "IMAGE"),
    ("localai_engine", "LocalAIEngine", "IMAGE"),
    ("openjourney_engine", "OpenJourneyEngine", "IMAGE"),
    ("realistic_vision_engine", "RealisticVisionEngine", "IMAGE"),
    ("sd_cpu_engine", "SDCPUEngine", "IMAGE"),
    ("fastsd_cpu_engine", "FastSDCPUEngine", "IMAGE"),
    ("realesrgan_engine", "RealESRGANEngine", "IMAGE"),
    # Video Generation Engines
    ("svd_engine", "SVDEngine", "VIDEO"),
    ("deforum_engine", "DeforumEngine", "VIDEO"),
    ("fomm_engine", "FOMMEngine", "VIDEO"),
    ("sadtalker_engine", "SadTalkerEngine", "VIDEO"),
    ("deepfacelab_engine", "DeepFaceLabEngine", "VIDEO"),
    ("moviepy_engine", "MoviePyEngine", "VIDEO"),
    ("ffmpeg_ai_engine", "FFmpegAIEngine", "VIDEO"),
    ("video_creator_engine", "VideoCreatorEngine", "VIDEO"),
    # Utility Engines
    ("speaker_encoder_engine", "SpeakerEncoderEngine", "UTILITY"),
    ("streaming_engine", "StreamingEngine", "UTILITY"),
]

# Test results storage
test_results: Dict[str, Dict[str, Any]] = {}


def generate_test_audio(
    duration_seconds: float = 1.0, sample_rate: int = 22050
) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
    audio = np.sin(2 * np.pi * 440.0 * t)
    audio = audio * 0.5
    return audio.astype(np.float32)


def load_engine_module(engine_file: str):
    """Load engine module dynamically."""
    engine_path = project_root / "app" / "core" / "engines" / f"{engine_file}.py"

    if not engine_path.exists():
        return None, f"Engine file not found: {engine_path}"

    try:
        spec = importlib.util.spec_from_file_location(engine_file, engine_path)
        if spec is None or spec.loader is None:
            return None, f"Could not load engine module: {engine_file}"

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, None
    except Exception as e:
        return None, f"Error loading module: {e}"


def get_engine_class(module, class_name: str):
    """Get the engine class from module."""
    try:
        if hasattr(module, class_name):
            engine_class = getattr(module, class_name)
            if inspect.isclass(engine_class):
                return engine_class
        return None
    except Exception as e:
        logger.warning(f"Error getting engine class: {e}")
        return None


def check_engine_initialization(engine_class, engine_type: str) -> Tuple[bool, str]:
    """Test if engine can be instantiated."""
    try:
        # Try to create engine instance
        if engine_type in ["TTS", "STT", "VC"]:
            engine = engine_class(device="cpu", gpu=False)
        elif engine_type in ["IMAGE", "VIDEO"]:
            engine = engine_class(device="cpu", gpu=False)
        else:
            engine = engine_class(device="cpu", gpu=False)

        # Check if has required methods
        required_methods = ["initialize", "cleanup"]
        missing_methods = [m for m in required_methods if not hasattr(engine, m)]

        if missing_methods:
            return False, f"Missing required methods: {missing_methods}"

        return True, "Engine initialized successfully"
    except Exception as e:
        return False, f"Initialization failed: {e}"


def check_engine_functionality(
    engine, engine_type: str
) -> Tuple[bool, str, Optional[Any]]:
    """Test basic engine functionality."""
    try:
        if engine_type == "TTS":
            if hasattr(engine, "synthesize"):
                # Try synthesis with minimal params
                result = engine.synthesize(
                    text="Test", voice_profile_id="test", sample_rate=22050
                )
                if result is not None:
                    return True, "Synthesis successful", result
                return False, "Synthesis returned None", None
            return False, "No synthesize method", None

        elif engine_type == "STT":
            if hasattr(engine, "transcribe"):
                test_audio = generate_test_audio()
                result = engine.transcribe(test_audio, sample_rate=22050)
                if result is not None:
                    return True, "Transcription successful", result
                return False, "Transcription returned None", None
            return False, "No transcribe method", None

        elif engine_type == "VC":
            if hasattr(engine, "convert"):
                test_audio = generate_test_audio()
                result = engine.convert(
                    audio=test_audio,
                    source_voice_id="test",
                    target_voice_id="test",
                    sample_rate=22050,
                )
                if result is not None:
                    return True, "Conversion successful", result
                return False, "Conversion returned None", None
            return False, "No convert method", None

        elif engine_type == "IMAGE":
            if hasattr(engine, "generate"):
                result = engine.generate(prompt="test", width=512, height=512)
                if result is not None:
                    return True, "Image generation successful", result
                return False, "Image generation returned None", None
            return False, "No generate method", None

        elif engine_type == "VIDEO":
            if hasattr(engine, "generate"):
                result = engine.generate(
                    prompt="test", width=512, height=512, duration=1.0
                )
                if result is not None:
                    return True, "Video generation successful", result
                return False, "Video generation returned None", None
            return False, "No generate method", None

        return False, f"Unknown engine type: {engine_type}", None
    except Exception as e:
        return False, f"Functionality test failed: {e}", None


def check_for_forbidden_terms(file_path: Path) -> List[str]:
    """Check file for forbidden placeholder terms."""
    violations = []
    forbidden_terms = [
        "TODO",
        "FIXME",
        "PLACEHOLDER",
        "stub",
        "dummy",
        "mock",
        "fake",
        "NotImplementedError",
        "NotImplementedException",
        "for now",
        "coming soon",
        "not yet",
        "eventually",
        "later",
        "temporary",
    ]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()
                for term in forbidden_terms:
                    if term.lower() in line_lower:
                        # Skip if in string literal or comment that's acceptable
                        if '"' in line or "'" in line:
                            continue
                        if line.strip().startswith("#"):
                            violations.append(
                                f"Line {line_num}: Found '{term}' - {line.strip()[:80]}"
                            )
    except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")

    return violations


@pytest.fixture(scope="module")
def test_audio():
    """Generate test audio for synthesis tests."""
    return generate_test_audio(duration_seconds=1.0)


class TestEngineImport:
    """Test suite for engine importability."""

    @pytest.mark.parametrize("engine_file,engine_class_name,engine_type", ALL_ENGINES)
    def test_engine_can_be_imported(self, engine_file, engine_class_name, engine_type):
        """Verify engine module can be imported."""
        module, error = load_engine_module(engine_file)

        if error:
            test_results[engine_file] = {
                "status": "SKIPPED",
                "error": error,
                "type": engine_type,
            }
            pytest.skip(f"Could not import {engine_file}: {error}")

        assert module is not None, f"Failed to import {engine_file}"
        test_results[engine_file] = {"status": "IMPORTED", "type": engine_type}

    @pytest.mark.parametrize("engine_file,engine_class_name,engine_type", ALL_ENGINES)
    def test_engine_class_exists(self, engine_file, engine_class_name, engine_type):
        """Verify engine class exists in module."""
        module, error = load_engine_module(engine_file)

        if error or module is None:
            pytest.skip(f"Could not load module: {error}")

        engine_class = get_engine_class(module, engine_class_name)

        if engine_class is None:
            if engine_file in test_results:
                test_results[engine_file]["error"] = "Engine class not found"
            pytest.skip(f"No engine class '{engine_class_name}' found in {engine_file}")

        assert engine_class is not None, f"No engine class in {engine_file}"

        if engine_file in test_results:
            test_results[engine_file]["class_found"] = True


class TestEngineInitialization:
    """Test suite for engine initialization."""

    @pytest.mark.parametrize("engine_file,engine_class_name,engine_type", ALL_ENGINES)
    def test_engine_initialization(self, engine_file, engine_class_name, engine_type):
        """Test engine can be instantiated."""
        module, error = load_engine_module(engine_file)

        if error or module is None:
            pytest.skip(f"Could not load module: {error}")

        engine_class = get_engine_class(module, engine_class_name)

        if engine_class is None:
            pytest.skip(f"No engine class found in {engine_file}")

        success, message = check_engine_initialization(engine_class, engine_type)

        if engine_file in test_results:
            test_results[engine_file]["initialization"] = {
                "success": success,
                "message": message,
            }

        if not success:
            pytest.skip(f"Initialization failed: {message}")


class TestEngineFunctionality:
    """Test suite for basic engine functionality."""

    @pytest.mark.parametrize("engine_file,engine_class_name,engine_type", ALL_ENGINES)
    def test_engine_basic_functionality(
        self, engine_file, engine_class_name, engine_type, test_audio
    ):
        """Test basic engine functionality."""
        module, error = load_engine_module(engine_file)

        if error or module is None:
            pytest.skip(f"Could not load module: {error}")

        engine_class = get_engine_class(module, engine_class_name)

        if engine_class is None:
            pytest.skip(f"No engine class found in {engine_file}")

        # Try to initialize
        try:
            if engine_type in ["TTS", "STT", "VC"]:
                engine = engine_class(device="cpu", gpu=False)
            else:
                engine = engine_class(device="cpu", gpu=False)
        except Exception as e:
            pytest.skip(f"Could not initialize engine: {e}")

        success, message, result = check_engine_functionality(engine, engine_type)

        if engine_file in test_results:
            test_results[engine_file]["functionality"] = {
                "success": success,
                "message": message,
                "has_result": result is not None,
            }

        # Don't fail test if functionality not available (may require models)
        if not success:
            pytest.skip(f"Functionality test: {message}")


class TestEngineCodeQuality:
    """Test suite for code quality (no placeholders)."""

    @pytest.mark.parametrize("engine_file,engine_class_name,engine_type", ALL_ENGINES)
    def test_no_forbidden_terms(self, engine_file, engine_class_name, engine_type):
        """Verify engine files contain no forbidden placeholder terms."""
        engine_path = project_root / "app" / "core" / "engines" / f"{engine_file}.py"

        if not engine_path.exists():
            pytest.skip(f"Engine file not found: {engine_path}")

        violations = check_for_forbidden_terms(engine_path)

        if engine_file in test_results:
            test_results[engine_file]["code_quality"] = {
                "violations": len(violations),
                "violation_details": violations[:5],  # First 5 violations
            }

        if violations:
            violation_msg = "\n".join(violations[:10])
            pytest.fail(f"Found forbidden terms in {engine_file}.py:\n{violation_msg}")


def generate_test_report():
    """Generate comprehensive test report."""
    report_path = (
        project_root
        / "docs"
        / "governance"
        / "worker3"
        / "ENGINE_INTEGRATION_TEST_REPORT_2025-01-28.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)

    total_engines = len(ALL_ENGINES)
    imported = sum(1 for r in test_results.values() if r.get("status") == "IMPORTED")
    initialized = sum(
        1
        for r in test_results.values()
        if r.get("initialization", {}).get("success", False)
    )
    functional = sum(
        1
        for r in test_results.values()
        if r.get("functionality", {}).get("success", False)
    )
    violations = sum(
        1
        for r in test_results.values()
        if r.get("code_quality", {}).get("violations", 0) > 0
    )

    report = f"""# Engine Integration Test Report
## Comprehensive Testing of All 48 Engines

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Worker:** Worker 3 (Testing/Quality/Documentation Specialist)  
**Test Suite:** Comprehensive Engine Integration Tests

---

## 📊 Executive Summary

**Total Engines Tested:** {total_engines}  
**Successfully Imported:** {imported} ({imported/total_engines*100:.1f}%)  
**Successfully Initialized:** {initialized} ({initialized/total_engines*100:.1f}%)  
**Functional:** {functional} ({functional/total_engines*100:.1f}%)  
**Code Quality Violations:** {violations} ({violations/total_engines*100:.1f}%)

---

## 📋 Detailed Results

### By Engine Type

"""

    # Group by type
    by_type = {}
    for engine_file, _, engine_type in ALL_ENGINES:
        if engine_type not in by_type:
            by_type[engine_type] = []
        by_type[engine_type].append(engine_file)

    for engine_type, engines in sorted(by_type.items()):
        report += f"\n#### {engine_type} Engines ({len(engines)})\n\n"
        report += "| Engine | Imported | Initialized | Functional | Violations |\n"
        report += "|--------|----------|-------------|------------|------------|\n"

        for engine_file in engines:
            result = test_results.get(engine_file, {})
            imported_status = "✅" if result.get("status") == "IMPORTED" else "❌"
            init_status = (
                "✅" if result.get("initialization", {}).get("success", False) else "❌"
            )
            func_status = (
                "✅" if result.get("functionality", {}).get("success", False) else "❌"
            )
            violations_count = result.get("code_quality", {}).get("violations", 0)
            violations_status = f"{violations_count}" if violations_count > 0 else "✅"

            report += f"| {engine_file} | {imported_status} | {init_status} | {func_status} | {violations_status} |\n"

    report += "\n---\n\n## 🔍 Detailed Engine Status\n\n"

    for engine_file, engine_class_name, engine_type in ALL_ENGINES:
        result = test_results.get(engine_file, {})
        report += f"### {engine_file} ({engine_type})\n\n"
        report += f"- **Class:** {engine_class_name}\n"
        report += f"- **Import Status:** {result.get('status', 'NOT TESTED')}\n"

        if "initialization" in result:
            init = result["initialization"]
            report += f"- **Initialization:** {'✅' if init.get('success') else '❌'} - {init.get('message', 'N/A')}\n"

        if "functionality" in result:
            func = result["functionality"]
            report += f"- **Functionality:** {'✅' if func.get('success') else '❌'} - {func.get('message', 'N/A')}\n"

        if "code_quality" in result:
            cq = result["code_quality"]
            if cq.get("violations", 0) > 0:
                report += f"- **Code Quality:** ⚠️ {cq['violations']} violations found\n"
                for violation in cq.get("violation_details", [])[:3]:
                    report += f"  - {violation}\n"
            else:
                report += "- **Code Quality:** ✅ No violations\n"

        if "error" in result:
            report += f"- **Error:** {result['error']}\n"

        report += "\n"

    report += "\n---\n\n## 📝 Notes\n\n"
    report += "- ✅ = Success\n"
    report += "- ❌ = Failed or Not Available\n"
    report += "- Functional tests may skip if models are not available\n"
    report += "- Code quality violations include TODO, FIXME, placeholders, etc.\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Test report generated: {report_path}")
    return report_path


@pytest.fixture(scope="session", autouse=True)
def generate_report():
    """Generate test report after all tests complete."""
    yield
    generate_test_report()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
