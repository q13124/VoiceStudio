"""
E2E Tests: Audio Effects Workflow.

Tests complete audio effects pipelines:
- Effect chain configuration
- Real-time preview
- Batch effect processing
- Effect presets
- Export with effects
"""

from datetime import datetime

import pytest

# Pytest markers
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.workflow,
    pytest.mark.effects,
]


# Common audio effects in VoiceStudio
AUDIO_EFFECTS = [
    "equalizer",
    "compressor",
    "limiter",
    "noise_gate",
    "reverb",
    "delay",
    "chorus",
    "pitch_shift",
    "time_stretch",
    "normalization",
    "de_esser",
    "de_noise",
    "de_click",
    "de_hum",
    "gain",
    "pan",
    "stereo_widener",
    "bass_boost",
    "treble_boost",
    "distortion",
]


class TestEffectsAvailability:
    """Tests for effects availability."""

    def test_list_available_effects(self, api_client, backend_available):
        """Test listing all available effects."""
        response = api_client.get("/api/effects", timeout=10)

        if response.status_code == 200:
            effects = response.json()
            print(f"Available effects: {effects}")
            return effects
        elif response.status_code == 404:
            pytest.skip("Effects API not available")

    def test_effects_categories(self, api_client, backend_available):
        """Test effects categories."""
        response = api_client.get("/api/effects/categories", timeout=10)

        if response.status_code == 200:
            categories = response.json()
            print(f"Effect categories: {categories}")
        elif response.status_code == 404:
            pytest.skip("Effects categories API not available")

    @pytest.mark.parametrize("effect_name", AUDIO_EFFECTS[:10])  # Test first 10
    def test_effect_parameters(self, effect_name, api_client, backend_available):
        """Test getting parameters for specific effects."""
        response = api_client.get(f"/api/effects/{effect_name}/parameters", timeout=10)

        if response.status_code == 200:
            params = response.json()
            print(f"{effect_name} parameters: {params}")
        elif response.status_code == 404:
            print(f"Effect {effect_name} not available")


class TestEffectPresets:
    """Tests for effect presets."""

    def test_list_presets(self, api_client, backend_available):
        """Test listing effect presets."""
        response = api_client.get("/api/effects/presets", timeout=10)

        if response.status_code == 200:
            presets = response.json()
            print(f"Effect presets: {len(presets) if isinstance(presets, list) else presets}")
        elif response.status_code == 404:
            pytest.skip("Effect presets API not available")

    def test_create_preset(self, api_client, backend_available):
        """Test creating an effect preset."""
        preset_config = {
            "name": f"E2E Test Preset {datetime.now().strftime('%H%M%S')}",
            "effects": [
                {"type": "equalizer", "params": {"low": 0, "mid": 0, "high": 0}},
                {"type": "compressor", "params": {"threshold": -20, "ratio": 4}},
            ],
        }

        response = api_client.post("/api/effects/presets/create", json=preset_config, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Preset created: {result}")
        elif response.status_code == 404:
            pytest.skip("Preset creation API not available")

    def test_factory_presets(self, api_client, backend_available):
        """Test factory/default presets."""
        response = api_client.get("/api/effects/presets/factory", timeout=10)

        if response.status_code == 200:
            factory_presets = response.json()
            print(f"Factory presets: {factory_presets}")
        elif response.status_code == 404:
            pytest.skip("Factory presets API not available")


class TestEffectChain:
    """Tests for effect chain operations."""

    def test_get_current_chain(self, api_client, backend_available):
        """Test getting current effect chain."""
        response = api_client.get("/api/effects/chain", timeout=10)

        if response.status_code == 200:
            chain = response.json()
            print(f"Current effect chain: {chain}")
        elif response.status_code == 404:
            pytest.skip("Effect chain API not available")

    def test_add_effect_to_chain(self, api_client, backend_available):
        """Test adding effect to chain."""
        effect_config = {
            "type": "equalizer",
            "params": {"low": 2, "mid": 0, "high": -1},
            "enabled": True,
        }

        response = api_client.post("/api/effects/chain/add", json=effect_config, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Effect added: {result}")
        elif response.status_code == 404:
            pytest.skip("Effect chain add API not available")

    def test_clear_effect_chain(self, api_client, backend_available):
        """Test clearing effect chain."""
        response = api_client.post("/api/effects/chain/clear", timeout=10)

        if response.status_code == 200:
            print("Effect chain cleared")
        elif response.status_code == 404:
            pytest.skip("Effect chain clear API not available")

    def test_effect_chain_ordering(self, api_client, backend_available):
        """Test reordering effects in chain."""
        order_config = {
            "order": [1, 0, 2],  # New order by index
        }

        response = api_client.post("/api/effects/chain/reorder", json=order_config, timeout=10)

        if response.status_code == 200:
            print("Chain reordered")
        elif response.status_code == 404:
            pytest.skip("Effect chain reorder API not available")


class TestEffectProcessing:
    """Tests for effect processing."""

    def test_apply_effect_to_audio(self, api_client, backend_available, test_audio_file):
        """Test applying effect to audio file."""
        if not test_audio_file.exists():
            pytest.skip("Test audio file not available")

        # First upload the audio
        with open(test_audio_file, "rb") as f:
            files = {"file": (test_audio_file.name, f, "audio/wav")}
            upload_resp = api_client.post("/api/audio/upload", files=files, timeout=30)

        if upload_resp.status_code != 200:
            pytest.skip("Audio upload not available")

        upload_result = upload_resp.json()
        file_id = upload_result.get("file_id") or upload_result.get("id")

        if not file_id:
            pytest.skip("Could not get uploaded file ID")

        # Apply effect
        effect_request = {
            "file_id": file_id,
            "effects": [
                {"type": "normalization", "params": {"target_db": -3}},
            ],
        }

        process_resp = api_client.post("/api/effects/process", json=effect_request, timeout=60)

        if process_resp.status_code == 200:
            result = process_resp.json()
            print(f"Effect processing result: {result}")
        elif process_resp.status_code == 404:
            pytest.skip("Effect processing API not available")

    def test_preview_effect(self, api_client, backend_available):
        """Test effect preview (real-time)."""
        preview_config = {
            "effect": "reverb",
            "params": {"room_size": 0.5, "damping": 0.5},
            "preview_duration": 2.0,
        }

        response = api_client.post("/api/effects/preview", json=preview_config, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Preview started: {result}")
        elif response.status_code == 404:
            pytest.skip("Effect preview API not available")


class TestNoiseReduction:
    """Tests for noise reduction effects."""

    def test_noise_profile(self, api_client, backend_available):
        """Test noise profile analysis."""
        response = api_client.get("/api/effects/noise/profile", timeout=10)

        if response.status_code == 200:
            profile = response.json()
            print(f"Noise profile: {profile}")
        elif response.status_code == 404:
            pytest.skip("Noise profile API not available")

    def test_denoise_settings(self, api_client, backend_available):
        """Test denoise settings."""
        response = api_client.get("/api/effects/denoise/settings", timeout=10)

        if response.status_code == 200:
            settings = response.json()
            print(f"Denoise settings: {settings}")
        elif response.status_code == 404:
            pytest.skip("Denoise settings API not available")

    def test_denoise_preview(self, api_client, backend_available):
        """Test denoise preview."""
        denoise_config = {
            "strength": 0.5,
            "preserve_voice": True,
        }

        response = api_client.post("/api/effects/denoise/preview", json=denoise_config, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"Denoise preview: {result}")
        elif response.status_code == 404:
            pytest.skip("Denoise preview API not available")


class TestPitchAndTempo:
    """Tests for pitch and tempo effects."""

    def test_pitch_shift_range(self, api_client, backend_available):
        """Test pitch shift parameter range."""
        response = api_client.get("/api/effects/pitch_shift/range", timeout=10)

        if response.status_code == 200:
            range_info = response.json()
            print(f"Pitch shift range: {range_info}")
        elif response.status_code == 404:
            pytest.skip("Pitch shift range API not available")

    def test_time_stretch_range(self, api_client, backend_available):
        """Test time stretch parameter range."""
        response = api_client.get("/api/effects/time_stretch/range", timeout=10)

        if response.status_code == 200:
            range_info = response.json()
            print(f"Time stretch range: {range_info}")
        elif response.status_code == 404:
            pytest.skip("Time stretch range API not available")

    def test_formant_preservation(self, api_client, backend_available):
        """Test formant preservation settings."""
        response = api_client.get("/api/effects/pitch_shift/formant", timeout=10)

        if response.status_code == 200:
            formant_info = response.json()
            print(f"Formant preservation: {formant_info}")
        elif response.status_code == 404:
            pytest.skip("Formant preservation API not available")


class TestFullEffectsWorkflow:
    """Complete effects workflow test."""

    def test_complete_effects_workflow_api(self, api_client, backend_available, workflow_state):
        """Test complete effects workflow via API."""
        state = workflow_state

        # Step 1: List available effects
        effects_resp = api_client.get("/api/effects", timeout=10)
        if effects_resp.status_code == 200:
            effects = effects_resp.json()
            effect_count = len(effects) if isinstance(effects, list) else "N/A"
            state["record_step"]("Listed effects", data={"count": effect_count})
        else:
            state["record_step"]("Effects list not available", success=False)

        # Step 2: Get effect presets
        presets_resp = api_client.get("/api/effects/presets", timeout=10)
        if presets_resp.status_code == 200:
            presets = presets_resp.json()
            preset_count = len(presets) if isinstance(presets, list) else "N/A"
            state["record_step"]("Listed presets", data={"count": preset_count})
        else:
            state["record_step"]("Presets not available")

        # Step 3: Get current effect chain
        chain_resp = api_client.get("/api/effects/chain", timeout=10)
        if chain_resp.status_code == 200:
            state["record_step"]("Got effect chain", data=chain_resp.json())
        else:
            state["record_step"]("Effect chain not available")

        # Step 4: Clear effect chain
        clear_resp = api_client.post("/api/effects/chain/clear", timeout=10)
        if clear_resp.status_code == 200:
            state["record_step"]("Cleared effect chain")
        else:
            state["record_step"]("Could not clear chain")

        # Step 5: Add effects to chain
        effects_to_add = [
            {"type": "equalizer", "params": {"low": 0, "mid": 2, "high": 1}},
            {"type": "compressor", "params": {"threshold": -18, "ratio": 3}},
            {"type": "normalization", "params": {"target_db": -3}},
        ]

        added_count = 0
        for effect in effects_to_add:
            add_resp = api_client.post("/api/effects/chain/add", json=effect, timeout=10)
            if add_resp.status_code == 200:
                added_count += 1

        state["record_step"](
            "Added effects to chain", data={"added": added_count, "total": len(effects_to_add)}
        )

        # Report
        success_count = sum(1 for s in state["steps"] if s["success"])
        total_count = len(state["steps"])
        print(f"\nEffects workflow: {success_count}/{total_count} steps successful")
        for step in state["steps"]:
            status = "✓" if step["success"] else "✗"
            data_str = f" - {step['data']}" if step.get("data") else ""
            print(f"  {status} {step['name']}{data_str}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
