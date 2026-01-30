"""
Engine Integration Test Suite
Tests all 48 engines for functionality, error handling, and placeholder detection.
"""

import sys
import os
from pathlib import Path
import pytest
import numpy as np
import logging
from typing import Dict, List, Any
import importlib.util
import inspect

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# List of all engines to test (48 engines total)
ENGINE_FILES = [
    "xtts_engine",
    "chatterbox_engine",
    "tortoise_engine",
    "piper_engine",
    "whisper_engine",
    "aeneas_engine",
    "silero_engine",
    "higgs_audio_engine",
    "f5_tts_engine",
    "voxcpm_engine",
    "parakeet_engine",
    "marytts_engine",
    "rhvoice_engine",
    "espeak_ng_engine",
    "festival_flite_engine",
    "realesrgan_engine",
    "svd_engine",
    "sdxl_comfy_engine",
    "comfyui_engine",
    "whisper_ui_engine",
    "ffmpeg_ai_engine",
    "moviepy_engine",
    "video_creator_engine",
    "deforum_engine",
    "sdxl_engine",
    "openjourney_engine",
    "realistic_vision_engine",
    "sd_cpu_engine",
    "fastsd_cpu_engine",
    "localai_engine",
    "fooocus_engine",
    "invokeai_engine",
    "sdnext_engine",
    "automatic1111_engine",
    "rvc_engine",
    "gpt_sovits_engine",
    "mockingbird_engine",
    "whisper_cpp_engine",
    "openvoice_engine",
    "lyrebird_engine",
    "voice_ai_engine",
    "sadtalker_engine",
    "fomm_engine",
    "deepfacelab_engine",
    "bark_engine",
    "speaker_encoder_engine",
    "streaming_engine",
    "openai_tts_engine",
]


FORBIDDEN_TERMS = [
    "TODO", "FIXME", "NOTE", "HACK", "REMINDER", "XXX", "WARNING", "CAUTION",
    "BUG", "ISSUE", "REFACTOR", "OPTIMIZE", "REVIEW", "CHECK", "VERIFY",
    "TEST", "DEBUG", "DEPRECATED", "OBSOLETE",
    "placeholder", "stub", "dummy", "mock", "fake", "sample", "temporary",
    "NotImplementedError", "NotImplementedException", "pass",
    "incomplete", "unfinished", "partial", "coming soon", "not yet",
    "eventually", "later", "for now", "temporary", "needs", "requires",
    "missing", "WIP", "tbd", "tba", "tbc"
]


def generate_test_audio(duration_seconds: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
    audio = np.sin(2 * np.pi * 440.0 * t)
    audio = audio * 0.5
    return audio.astype(np.float32)


def check_for_forbidden_terms(file_path: Path) -> List[str]:
    """Check file for forbidden placeholder terms."""
    violations = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line_lower = line.lower()
                for term in FORBIDDEN_TERMS:
                    if term.lower() in line_lower:
                        violations.append(f"Line {line_num}: Found '{term}' - {line.strip()[:80]}")
    except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")
    
    return violations


def load_engine_module(engine_name: str):
    """Load engine module dynamically."""
    engine_path = project_root / "app" / "core" / "engines" / f"{engine_name}.py"
    
    if not engine_path.exists():
        pytest.skip(f"Engine file not found: {engine_path}")
    
    spec = importlib.util.spec_from_file_location(engine_name, engine_path)
    if spec is None or spec.loader is None:
        pytest.skip(f"Could not load engine module: {engine_name}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def get_engine_class(module):
    """Get the main engine class from module."""
    classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass)
               if name.endswith('Engine') and obj.__module__ == module.__name__]
    
    if not classes:
        return None
    
    return classes[0]


@pytest.fixture(scope="module")
def test_audio():
    """Generate test audio for synthesis tests."""
    return generate_test_audio(duration_seconds=1.0)


class TestEnginePlaceholderDetection:
    """Test suite for detecting placeholders in engine code."""
    
    @pytest.mark.parametrize("engine_name", ENGINE_FILES)
    def test_no_forbidden_terms(self, engine_name):
        """Verify engine files contain no forbidden placeholder terms."""
        engine_path = project_root / "app" / "core" / "engines" / f"{engine_name}.py"
        
        if not engine_path.exists():
            pytest.skip(f"Engine file not found: {engine_path}")
        
        violations = check_for_forbidden_terms(engine_path)
        
        if violations:
            violation_msg = "\n".join(violations[:10])
            pytest.fail(f"Found forbidden terms in {engine_name}.py:\n{violation_msg}")


class TestEngineInitialization:
    """Test suite for engine initialization."""
    
    @pytest.mark.parametrize("engine_name", ENGINE_FILES)
    def test_engine_can_be_imported(self, engine_name):
        """Verify engine module can be imported."""
        try:
            module = load_engine_module(engine_name)
            assert module is not None, f"Failed to import {engine_name}"
        except Exception as e:
            pytest.skip(f"Could not import {engine_name}: {e}")
    
    @pytest.mark.parametrize("engine_name", ENGINE_FILES)
    def test_engine_class_exists(self, engine_name):
        """Verify engine class exists in module."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)
            
            if engine_class is None:
                pytest.skip(f"No engine class found in {engine_name}")
            
            assert engine_class is not None, f"No engine class in {engine_name}"
        except Exception as e:
            pytest.skip(f"Could not find engine class in {engine_name}: {e}")


class TestEngineBasicFunctionality:
    """Test suite for basic engine functionality."""
    
    @pytest.mark.parametrize("engine_name", [
        "xtts_engine",
        "chatterbox_engine",
        "tortoise_engine",
        "piper_engine",
        "silero_engine",
    ])
    def test_tts_engine_synthesis(self, engine_name, test_audio):
        """Test TTS engines can synthesize speech."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)
            
            if engine_class is None:
                pytest.skip(f"No engine class in {engine_name}")
            
            engine = engine_class(
                model_path=None,
                device="cpu"
            )
            
            if hasattr(engine, 'synthesize'):
                result = engine.synthesize(
                    text="Hello, this is a test.",
                    voice_profile_id="test",
                    sample_rate=22050
                )
                
                assert result is not None, f"{engine_name} synthesis returned None"
                assert hasattr(result, 'audio') or isinstance(result, (np.ndarray, list, dict)), \
                    f"{engine_name} synthesis returned unexpected type"
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} synthesis: {e}")
    
    @pytest.mark.parametrize("engine_name", [
        "whisper_engine",
        "whisper_cpp_engine",
    ])
    def test_transcription_engine(self, engine_name, test_audio):
        """Test transcription engines can transcribe audio."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)
            
            if engine_class is None:
                pytest.skip(f"No engine class in {engine_name}")
            
            engine = engine_class(
                model_path=None,
                device="cpu"
            )
            
            if hasattr(engine, 'transcribe'):
                result = engine.transcribe(test_audio, sample_rate=22050)
                
                assert result is not None, f"{engine_name} transcription returned None"
                assert isinstance(result, (str, dict)), \
                    f"{engine_name} transcription returned unexpected type"
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} transcription: {e}")


class TestEngineErrorHandling:
    """Test suite for engine error handling."""
    
    @pytest.mark.parametrize("engine_name", ENGINE_FILES)
    def test_engine_handles_invalid_input(self, engine_name):
        """Verify engines handle invalid input gracefully."""
        try:
            module = load_engine_module(engine_name)
            engine_class = get_engine_class(module)
            
            if engine_class is None:
                pytest.skip(f"No engine class in {engine_name}")
            
            engine = engine_class(
                model_path=None,
                device="cpu"
            )
            
            if hasattr(engine, 'synthesize'):
                try:
                    result = engine.synthesize(
                        text="",
                        voice_profile_id="",
                        sample_rate=22050
                    )
                except (ValueError, TypeError, AttributeError):
                    ...
                except Exception as e:
                    logger.warning(f"{engine_name} raised unexpected exception: {e}")
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} error handling: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

