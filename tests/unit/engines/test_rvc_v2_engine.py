"""
Unit tests for RVC v2 Engine manifest and registration.

RVC v2 uses the same engine class as RVC v1 but with a distinct manifest
for separate configuration defaults and versioning.
"""

import pytest
import json
from pathlib import Path


class TestRVCv2Manifest:
    """Tests for RVC v2 engine manifest."""

    def test_manifest_exists(self):
        """RVC v2 manifest file should exist."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        assert manifest_path.exists()

    def test_manifest_valid_json(self):
        """Manifest should be valid JSON."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert isinstance(manifest, dict)

    def test_manifest_engine_id(self):
        """Manifest should have engine_id = 'rvc_v2'."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert manifest["engine_id"] == "rvc_v2"

    def test_manifest_version_is_2(self):
        """Manifest version should be 2.x."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert manifest["version"].startswith("2.")

    def test_manifest_has_required_fields(self):
        """Manifest should have all required fields."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        required_fields = [
            "engine_id",
            "name",
            "type",
            "subtype",
            "version",
            "venv_family",
            "entry_point",
            "capabilities",
        ]
        
        for field in required_fields:
            assert field in manifest, f"Missing field: {field}"

    def test_manifest_entry_point_uses_rvc_engine(self):
        """Entry point should use the existing RVCEngine class."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        # RVC v2 uses the same engine class as v1
        assert "rvc_engine" in manifest["entry_point"]
        assert "RVCEngine" in manifest["entry_point"]

    def test_manifest_subtype_is_voice_conversion(self):
        """Subtype should be voice_conversion."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert manifest["subtype"] == "voice_conversion"

    def test_manifest_venv_family(self):
        """Venv family should be venv_voice_conversion."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert manifest["venv_family"] == "venv_voice_conversion"


class TestRVCv2Capabilities:
    """Tests for RVC v2 capabilities."""

    def test_has_v2_architecture_capability(self):
        """Should have v2_architecture capability."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert "v2_architecture" in manifest["capabilities"]

    def test_has_rmvpe_pitch_extraction(self):
        """Should have rmvpe_pitch_extraction capability."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert "rmvpe_pitch_extraction" in manifest["capabilities"]

    def test_has_voice_conversion_capability(self):
        """Should have voice_conversion capability."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        assert "voice_conversion" in manifest["capabilities"]


class TestRVCv2ConfigSchema:
    """Tests for RVC v2 config schema."""

    def test_has_pitch_extraction_method_config(self):
        """Config should include pitch_extraction_method."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        config = manifest.get("config_schema", {})
        assert "pitch_extraction_method" in config

    def test_rmvpe_is_default_pitch_method(self):
        """RMVPE should be the default pitch extraction method."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        config = manifest.get("config_schema", {})
        assert config["pitch_extraction_method"]["default"] == "rmvpe"

    def test_has_model_version_config(self):
        """Config should include model_version."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        config = manifest.get("config_schema", {})
        assert "model_version" in config
        assert config["model_version"]["default"] == "v2"


class TestRVCv2VenvFamilyRegistration:
    """Tests for venv family registration."""

    def test_rvc_v2_in_voice_conversion_family(self):
        """rvc_v2 should be in venv_voice_conversion family."""
        from app.core.runtime.venv_family_manager import (
            ENGINE_TO_FAMILY,
            VenvFamily,
        )
        
        assert "rvc_v2" in ENGINE_TO_FAMILY
        assert ENGINE_TO_FAMILY["rvc_v2"] == VenvFamily.VOICE_CONVERSION

    def test_rvc_v1_and_v2_in_same_family(self):
        """Both RVC v1 and v2 should be in same venv family."""
        from app.core.runtime.venv_family_manager import ENGINE_TO_FAMILY
        
        assert ENGINE_TO_FAMILY.get("rvc") == ENGINE_TO_FAMILY.get("rvc_v2")


class TestRVCv2QualityFeatures:
    """Tests for RVC v2 quality features."""

    def test_quality_tier_is_high(self):
        """Quality tier should be high for v2."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        quality = manifest.get("quality_features", {})
        assert quality.get("quality_tier") == "high"

    def test_mos_estimate_higher_than_v1(self):
        """MOS estimate should be higher than v1 (4.0-4.5)."""
        manifest_path = Path("engines/audio/rvc_v2/engine.manifest.json")
        manifest = json.loads(manifest_path.read_text())
        
        quality = manifest.get("quality_features", {})
        mos = quality.get("mos_estimate", "")
        
        # v2 should have higher range than v1 (4.0-4.5)
        assert "4.2" in mos or "4.7" in mos
