"""
Integration tests for Chatterbox TTS engine.

Tests TASK-0010: Piper/Chatterbox Integration
Verifies Chatterbox can synthesize via venv_advanced_tts family.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestChatterboxVenvFamily:
    """Test Chatterbox integration with venv families."""

    def test_chatterbox_in_advanced_tts_family(self):
        """Test that Chatterbox is assigned to venv_advanced_tts family."""
        from app.core.runtime.venv_family_manager import (
            ENGINE_TO_FAMILY,
            VenvFamily,
        )

        assert "chatterbox" in ENGINE_TO_FAMILY
        assert ENGINE_TO_FAMILY["chatterbox"] == VenvFamily.ADVANCED_TTS

    def test_venv_advanced_tts_exists(self):
        """Test that venv_advanced_tts venv exists."""
        from app.core.runtime.venv_family_manager import (
            VenvFamily,
            get_venv_manager,
        )

        manager = get_venv_manager()
        assert manager.is_venv_created(VenvFamily.ADVANCED_TTS), \
            "venv_advanced_tts should be created"

    def test_venv_advanced_tts_has_chatterbox(self):
        """Test that Chatterbox is installed in venv_advanced_tts."""
        from app.core.runtime.venv_family_manager import (
            VenvFamily,
            get_venv_manager,
        )

        manager = get_venv_manager()

        if not manager.is_venv_created(VenvFamily.ADVANCED_TTS):
            pytest.skip("venv_advanced_tts not created")

        # Run a test import in the venv
        python_exe = manager.get_python_executable(VenvFamily.ADVANCED_TTS)
        if not python_exe.exists():
            pytest.skip("Python executable not found")

        import subprocess
        result = subprocess.run(
            [str(python_exe), "-c", "from chatterbox.tts import ChatterboxTTS; print('OK')"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Chatterbox import failed: {result.stderr}"
        assert "OK" in result.stdout


class TestChatterboxEngineLifecycle:
    """Test Chatterbox engine lifecycle with venv families."""

    def test_engine_lifecycle_has_venv_support(self):
        """Test that engine lifecycle manager has venv family support."""
        from app.core.runtime.engine_lifecycle import (
            HAS_VENV_FAMILIES,
        )

        assert HAS_VENV_FAMILIES, "Venv families should be available"

    def test_lifecycle_detects_chatterbox_family(self):
        """Test that lifecycle manager detects Chatterbox venv family."""
        from app.core.runtime.engine_lifecycle import EngineLifecycleManager
        from app.core.runtime.venv_family_manager import VenvFamily

        manager = EngineLifecycleManager()

        # Create a mock engine instance with Chatterbox manifest
        from app.core.runtime.engine_lifecycle import EngineInstance
        engine = EngineInstance(
            engine_id="chatterbox",
            manifest={
                "engine_id": "chatterbox",
                "venv_family": "venv_advanced_tts",
            },
        )

        family = manager._get_venv_family(engine)
        assert family == VenvFamily.ADVANCED_TTS


class TestChatterboxEngineImport:
    """Test Chatterbox engine module."""

    def test_chatterbox_engine_module_imports(self):
        """Test that chatterbox_engine module imports without error."""
        from app.core.engines import chatterbox_engine

        assert chatterbox_engine is not None

    def test_chatterbox_engine_class_exists(self):
        """Test that ChatterboxEngine class exists."""
        from app.core.engines.chatterbox_engine import ChatterboxEngine

        assert ChatterboxEngine is not None

    def test_enhance_voice_cloning_quality_imported(self):
        """Test that enhance_voice_cloning_quality is imported (TASK-0010 fix)."""
        from app.core.engines import chatterbox_engine

        # Check the module has the import (may be None if audio_utils not available)
        assert hasattr(chatterbox_engine, "enhance_voice_cloning_quality")


class TestChatterboxManifest:
    """Test Chatterbox engine manifest."""

    def test_chatterbox_manifest_has_venv_family(self):
        """Test that Chatterbox manifest has venv_family field."""
        import json

        manifest_path = project_root / "engines" / "audio" / "chatterbox" / "engine.manifest.json"
        assert manifest_path.exists(), f"Manifest not found: {manifest_path}"

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "venv_family" in manifest, "Manifest should have venv_family field"
        assert manifest["venv_family"] == "venv_advanced_tts"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
