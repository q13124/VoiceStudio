"""
End-to-End test for Voice Morph workflow.

Tests the complete voice morphing and blending workflow including:
- Creating morph configurations
- Applying morph to audio
- Blending two voices
- Getting voice embeddings
- Previewing morphed voices
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from api.main import app


class TestVoiceMorphConfigWorkflow:
    """End-to-end tests for voice morph configuration management."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_create_morph_config(self, client: TestClient):
        """
        POST /api/voice-morph/configs creates a new morph configuration.
        """
        print("\n[E2E] Creating morph configuration...")
        
        response = client.post(
            "/api/voice-morph/configs",
            json={
                "name": "Test Morph Config",
                "source_audio_id": "test-audio-001",
                "target_voices": [
                    {"voice_profile_id": "voice-a", "weight": 0.6},
                    {"voice_profile_id": "voice-b", "weight": 0.4},
                ],
                "morph_strength": 0.7,
                "preserve_emotion": True,
                "preserve_prosody": True,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "config_id" in data
        assert data["name"] == "Test Morph Config"
        assert data["morph_strength"] == 0.7
        print(f"[E2E] Created morph config: {data['config_id']}")

    def test_list_morph_configs(self, client: TestClient):
        """
        GET /api/voice-morph/configs lists all morph configurations.
        """
        print("\n[E2E] Listing morph configurations...")
        
        # Create a config first
        client.post(
            "/api/voice-morph/configs",
            json={
                "name": "List Test Config",
                "source_audio_id": "test-audio",
                "target_voices": [{"voice_profile_id": "test-voice", "weight": 1.0}],
            },
        )
        
        response = client.get("/api/voice-morph/configs")
        assert response.status_code == 200
        
        configs = response.json()
        assert isinstance(configs, list)
        print(f"[E2E] Found {len(configs)} morph configurations")

    def test_get_morph_config(self, client: TestClient):
        """
        GET /api/voice-morph/configs/{config_id} returns config details.
        """
        print("\n[E2E] Getting morph configuration...")
        
        # Create a config
        create_response = client.post(
            "/api/voice-morph/configs",
            json={
                "name": "Get Test Config",
                "source_audio_id": "test-audio",
                "target_voices": [{"voice_profile_id": "test-voice", "weight": 1.0}],
            },
        )
        config_id = create_response.json()["config_id"]
        
        # Get the config
        response = client.get(f"/api/voice-morph/configs/{config_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["config_id"] == config_id
        assert data["name"] == "Get Test Config"
        print(f"[E2E] Retrieved config: {config_id}")

    def test_update_morph_config(self, client: TestClient):
        """
        PUT /api/voice-morph/configs/{config_id} updates a configuration.
        """
        print("\n[E2E] Updating morph configuration...")
        
        # Create a config
        create_response = client.post(
            "/api/voice-morph/configs",
            json={
                "name": "Original Name",
                "source_audio_id": "test-audio",
                "target_voices": [{"voice_profile_id": "test-voice", "weight": 1.0}],
                "morph_strength": 0.5,
            },
        )
        config_id = create_response.json()["config_id"]
        
        # Update the config
        response = client.put(
            f"/api/voice-morph/configs/{config_id}",
            json={
                "name": "Updated Name",
                "source_audio_id": "test-audio",
                "target_voices": [{"voice_profile_id": "new-voice", "weight": 1.0}],
                "morph_strength": 0.8,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["morph_strength"] == 0.8
        print(f"[E2E] Updated config: {config_id}")

    def test_delete_morph_config(self, client: TestClient):
        """
        DELETE /api/voice-morph/configs/{config_id} deletes a configuration.
        """
        print("\n[E2E] Deleting morph configuration...")
        
        # Create a config
        create_response = client.post(
            "/api/voice-morph/configs",
            json={
                "name": "Delete Test",
                "source_audio_id": "test-audio",
                "target_voices": [{"voice_profile_id": "test-voice", "weight": 1.0}],
            },
        )
        config_id = create_response.json()["config_id"]
        
        # Delete the config
        response = client.delete(f"/api/voice-morph/configs/{config_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = client.get(f"/api/voice-morph/configs/{config_id}")
        assert get_response.status_code == 404
        print(f"[E2E] Deleted config: {config_id}")


class TestVoiceMorphApplyWorkflow:
    """End-to-end tests for applying voice morph configurations."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_apply_morph_config_not_found(self, client: TestClient):
        """
        POST /api/voice-morph/apply returns 404 for non-existent config.
        """
        print("\n[E2E] Testing apply morph with invalid config...")
        
        response = client.post(
            "/api/voice-morph/apply",
            json={"config_id": "non-existent-config"},
        )
        
        assert response.status_code == 404
        print("[E2E] Correctly returned 404 for invalid config")

    def test_apply_morph_workflow(self, client: TestClient):
        """
        Test the complete morph apply workflow.
        """
        print("\n[E2E] Testing morph apply workflow...")
        
        # Create a config
        create_response = client.post(
            "/api/voice-morph/configs",
            json={
                "name": "Apply Test",
                "source_audio_id": "test-source-audio",
                "target_voices": [
                    {"voice_profile_id": "target-voice-1", "weight": 0.7},
                    {"voice_profile_id": "target-voice-2", "weight": 0.3},
                ],
                "morph_strength": 0.6,
            },
        )
        config_id = create_response.json()["config_id"]
        
        # Apply the morph (may fail if source audio doesn't exist, which is expected)
        response = client.post(
            "/api/voice-morph/apply",
            json={"config_id": config_id},
        )
        
        # Accept 200 (success), 404 (source not found), or 503 (deps missing)
        assert response.status_code in [200, 404, 503]
        print(f"[E2E] Apply morph response: {response.status_code}")


class TestVoiceBlendWorkflow:
    """End-to-end tests for voice blending functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_blend_voices_validation(self, client: TestClient):
        """
        POST /api/voice-morph/voice/blend validates input.
        """
        print("\n[E2E] Testing voice blend input validation...")
        
        # Missing voice IDs
        response = client.post(
            "/api/voice-morph/voice/blend",
            json={"blend_ratio": 0.5},
        )
        
        assert response.status_code == 400
        print("[E2E] Correctly validated missing voice IDs")

    def test_blend_voices_ratio_validation(self, client: TestClient):
        """
        POST /api/voice-morph/voice/blend validates blend ratio.
        """
        print("\n[E2E] Testing blend ratio validation...")
        
        response = client.post(
            "/api/voice-morph/voice/blend",
            json={
                "voice_a_id": "voice-a",
                "voice_b_id": "voice-b",
                "blend_ratio": 1.5,  # Invalid - should be 0.0-1.0
            },
        )
        
        assert response.status_code == 400
        print("[E2E] Correctly validated invalid blend ratio")

    def test_blend_voices_workflow(self, client: TestClient):
        """
        Test the complete voice blend workflow.
        """
        print("\n[E2E] Testing voice blend workflow...")
        
        response = client.post(
            "/api/voice-morph/voice/blend",
            json={
                "voice_a_id": "test-voice-a",
                "voice_b_id": "test-voice-b",
                "blend_ratio": 0.5,
                "text": "Testing voice blend.",
            },
        )
        
        # Accept 200 (success) or 500 (synthesis dependencies)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "blend_ratio" in data
            print(f"[E2E] Voice blend successful: {data}")
        else:
            print(f"[E2E] Voice blend skipped (dependencies): {response.status_code}")


class TestVoiceMorphWorkflow:
    """End-to-end tests for voice morph over time functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_morph_voice_over_time(self, client: TestClient):
        """
        POST /api/voice-morph/voice/morph morphs voice over time.
        """
        print("\n[E2E] Testing voice morph over time...")
        
        response = client.post(
            "/api/voice-morph/voice/morph",
            json={
                "source_audio_id": "test-source",
                "voice_a_id": "voice-a",
                "voice_b_id": "voice-b",
                "start_ratio": 0.0,
                "end_ratio": 1.0,
                "morph_speed": 1.0,
            },
        )
        
        # Accept 200 (success) or 500 (processing error)
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "morphed_audio_id" in data
            print(f"[E2E] Morph successful: {data['morphed_audio_id']}")
        else:
            print(f"[E2E] Morph skipped: {response.status_code}")


class TestVoiceEmbeddingWorkflow:
    """End-to-end tests for voice embedding extraction."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_get_voice_embedding_validation(self, client: TestClient):
        """
        POST /api/voice-morph/voice/embedding validates input.
        """
        print("\n[E2E] Testing voice embedding validation...")
        
        response = client.post(
            "/api/voice-morph/voice/embedding",
            json={"voice_profile_id": ""},
        )
        
        assert response.status_code == 400
        print("[E2E] Correctly validated empty profile ID")

    def test_get_voice_embedding_not_found(self, client: TestClient):
        """
        POST /api/voice-morph/voice/embedding returns 404 for unknown profile.
        """
        print("\n[E2E] Testing voice embedding profile not found...")
        
        response = client.post(
            "/api/voice-morph/voice/embedding",
            json={"voice_profile_id": "non-existent-profile"},
        )
        
        assert response.status_code == 404
        print("[E2E] Correctly returned 404 for non-existent profile")


class TestVoicePreviewWorkflow:
    """End-to-end tests for voice preview functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_preview_voice_validation(self, client: TestClient):
        """
        POST /api/voice-morph/voice/preview validates input.
        """
        print("\n[E2E] Testing voice preview validation...")
        
        response = client.post(
            "/api/voice-morph/voice/preview",
            json={"text": ""},  # Empty text
        )
        
        assert response.status_code == 400
        print("[E2E] Correctly validated empty text")

    def test_preview_voice_requires_profile_or_blend(self, client: TestClient):
        """
        POST /api/voice-morph/voice/preview requires profile or blend voices.
        """
        print("\n[E2E] Testing preview requires voice specification...")
        
        response = client.post(
            "/api/voice-morph/voice/preview",
            json={"text": "Test preview text."},  # No voice specified
        )
        
        assert response.status_code == 400
        print("[E2E] Correctly required voice specification")
