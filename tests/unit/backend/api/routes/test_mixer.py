"""
Unit Tests for Mixer API Route
Tests mixer endpoints comprehensively.
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import mixer
except ImportError:
    pytest.skip("Could not import mixer route module", allow_module_level=True)


class TestMixerRouteImports:
    """Test mixer route module can be imported."""

    def test_mixer_module_imports(self):
        """Test mixer module can be imported."""
        assert mixer is not None, "Failed to import mixer module"
        assert hasattr(mixer, "router"), "mixer module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert mixer.router is not None, "Router should exist"
        if hasattr(mixer.router, "prefix"):
            assert (
                "/api/mixer" in mixer.router.prefix
            ), "Router prefix should include /api/mixer"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(mixer.router, "routes"):
            routes = [route.path for route in mixer.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestMixerStateEndpoints:
    """Test mixer state management endpoints."""

    def test_get_mixer_state_success(self):
        """Test successful mixer state retrieval."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        response = client.get("/api/mixer/state/test_project")
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "channels" in data

    def test_get_mixer_state_creates_default(self):
        """Test getting state creates default if not exists."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        response = client.get("/api/mixer/state/new_project")
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "new_project"

    def test_update_mixer_state_success(self):
        """Test successful mixer state update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        now = datetime.utcnow().isoformat()
        state_data = {
            "id": "state1",
            "project_id": "test_project",
            "channels": [],
            "channel_routing": [],
            "sends": [],
            "returns": [],
            "sub_groups": [],
            "master": {"id": "master", "volume": 0.8},
            "created": now,
            "modified": now,
        }

        response = client.put("/api/mixer/state/test_project", json=state_data)
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == "test_project"

    def test_reset_mixer_state_success(self):
        """Test successful mixer state reset."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        response = client.post("/api/mixer/state/test_project/reset")
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data


class TestMixerSendsEndpoints:
    """Test mixer sends endpoints."""

    def test_create_send_success(self):
        """Test successful send creation."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        send_data = {
            "id": str(uuid.uuid4()),
            "name": "Reverb Send",
            "bus_number": 1,
            "volume": 0.5,
            "is_enabled": True,
        }

        response = client.post("/api/mixer/state/test_project/sends", json=send_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Reverb Send"

    def test_update_send_success(self):
        """Test successful send update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        # Create a send first
        send_id = str(uuid.uuid4())
        create_data = {
            "id": send_id,
            "name": "Original Send",
            "bus_number": 1,
            "volume": 0.5,
        }
        client.post("/api/mixer/state/test_project/sends", json=create_data)

        update_data = {
            "id": send_id,
            "name": "Updated Send",
            "bus_number": 1,
            "volume": 0.7,
        }

        response = client.put(
            f"/api/mixer/state/test_project/sends/{send_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Send"

    def test_delete_send_success(self):
        """Test successful send deletion."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        # Create a send first
        send_id = str(uuid.uuid4())
        create_data = {
            "id": send_id,
            "name": "To Delete",
            "bus_number": 1,
            "volume": 0.5,
        }
        client.post("/api/mixer/state/test_project/sends", json=create_data)

        response = client.delete(f"/api/mixer/state/test_project/sends/{send_id}")
        assert response.status_code == 200


class TestMixerReturnsEndpoints:
    """Test mixer returns endpoints."""

    def test_create_return_success(self):
        """Test successful return creation."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        return_data = {
            "id": str(uuid.uuid4()),
            "name": "Reverb Return",
            "bus_number": 1,
            "volume": 0.8,
            "pan": 0.0,
            "is_enabled": True,
        }

        response = client.post(
            "/api/mixer/state/test_project/returns", json=return_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Reverb Return"

    def test_update_return_success(self):
        """Test successful return update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        # Create a return first
        return_id = str(uuid.uuid4())
        create_data = {
            "id": return_id,
            "name": "Original Return",
            "bus_number": 1,
            "volume": 0.5,
        }
        client.post("/api/mixer/state/test_project/returns", json=create_data)

        update_data = {
            "id": return_id,
            "name": "Updated Return",
            "bus_number": 1,
            "volume": 0.7,
        }

        response = client.put(
            f"/api/mixer/state/test_project/returns/{return_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Return"

    def test_delete_return_success(self):
        """Test successful return deletion."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        # Create a return first
        return_id = str(uuid.uuid4())
        create_data = {
            "id": return_id,
            "name": "To Delete",
            "bus_number": 1,
            "volume": 0.5,
        }
        client.post("/api/mixer/state/test_project/returns", json=create_data)

        response = client.delete(f"/api/mixer/state/test_project/returns/{return_id}")
        assert response.status_code == 200


class TestMixerSubGroupsEndpoints:
    """Test mixer subgroups endpoints."""

    def test_create_subgroup_success(self):
        """Test successful subgroup creation."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        subgroup_data = {
            "id": str(uuid.uuid4()),
            "name": "Drums Subgroup",
            "bus_number": 1,
            "volume": 0.9,
            "pan": 0.0,
            "is_muted": False,
            "is_soloed": False,
            "channel_ids": [],
        }

        response = client.post(
            "/api/mixer/state/test_project/subgroups", json=subgroup_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Drums Subgroup"

    def test_update_subgroup_success(self):
        """Test successful subgroup update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        # Create a subgroup first
        subgroup_id = str(uuid.uuid4())
        create_data = {
            "id": subgroup_id,
            "name": "Original Subgroup",
            "bus_number": 1,
            "volume": 0.5,
        }
        client.post("/api/mixer/state/test_project/subgroups", json=create_data)

        update_data = {
            "id": subgroup_id,
            "name": "Updated Subgroup",
            "bus_number": 1,
            "volume": 0.7,
        }

        response = client.put(
            f"/api/mixer/state/test_project/subgroups/{subgroup_id}",
            json=update_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Subgroup"

    def test_delete_subgroup_success(self):
        """Test successful subgroup deletion."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        # Create a subgroup first
        subgroup_id = str(uuid.uuid4())
        create_data = {
            "id": subgroup_id,
            "name": "To Delete",
            "bus_number": 1,
            "volume": 0.5,
        }
        client.post("/api/mixer/state/test_project/subgroups", json=create_data)

        response = client.delete(
            f"/api/mixer/state/test_project/subgroups/{subgroup_id}"
        )
        assert response.status_code == 200


class TestMixerMasterEndpoint:
    """Test mixer master endpoint."""

    def test_update_master_success(self):
        """Test successful master update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        master_data = {
            "id": "master",
            "volume": 0.85,
            "pan": 0.0,
            "is_muted": False,
        }

        response = client.put("/api/mixer/state/test_project/master", json=master_data)
        assert response.status_code == 200
        data = response.json()
        assert data["volume"] == 0.85


class TestMixerChannelRoutingEndpoint:
    """Test mixer channel routing endpoint."""

    def test_update_channel_routing_success(self):
        """Test successful channel routing update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        routing_data = {
            "channel_id": "channel1",
            "main_destination": "Master",
            "sub_group_id": None,
            "send_levels": {},
            "send_enabled": {},
        }

        response = client.put(
            "/api/mixer/state/test_project/channels/channel1/routing",
            json=routing_data,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == "channel1"


class TestMixerPresetsEndpoints:
    """Test mixer presets endpoints."""

    def test_list_presets_success(self):
        """Test successful presets listing."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()

        response = client.get("/api/mixer/presets/test_project")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_preset_success(self):
        """Test successful preset retrieval."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()

        # Create a preset first
        preset_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        preset_data = {
            "id": preset_id,
            "name": "Test Preset",
            "description": "A test preset",
            "project_id": "test_project",
            "state": {
                "id": "state1",
                "project_id": "test_project",
                "channels": [],
                "channel_routing": [],
                "sends": [],
                "returns": [],
                "sub_groups": [],
                "master": {"id": "master", "volume": 1.0},
                "created": now,
                "modified": now,
            },
            "created": now,
            "modified": now,
        }
        mixer._mixer_presets[preset_id] = preset_data

        response = client.get(f"/api/mixer/presets/test_project/{preset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == preset_id

    def test_get_preset_not_found(self):
        """Test getting non-existent preset."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()

        response = client.get("/api/mixer/presets/test_project/nonexistent")
        assert response.status_code == 404

    def test_create_preset_success(self):
        """Test successful preset creation."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()

        now = datetime.utcnow().isoformat()
        preset_data = {
            "id": str(uuid.uuid4()),
            "name": "New Preset",
            "description": "A new preset",
            "project_id": "test_project",
            "state": {
                "id": "state1",
                "project_id": "test_project",
                "channels": [],
                "channel_routing": [],
                "sends": [],
                "returns": [],
                "sub_groups": [],
                "master": {"id": "master", "volume": 1.0},
                "created": now,
                "modified": now,
            },
            "created": now,
            "modified": now,
        }

        response = client.post("/api/mixer/presets/test_project", json=preset_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Preset"

    def test_update_preset_success(self):
        """Test successful preset update."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()

        # Create a preset first
        preset_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        create_data = {
            "id": preset_id,
            "name": "Original Preset",
            "project_id": "test_project",
            "state": {
                "id": "state1",
                "project_id": "test_project",
                "channels": [],
                "channel_routing": [],
                "sends": [],
                "returns": [],
                "sub_groups": [],
                "master": {"id": "master", "volume": 1.0},
                "created": now,
                "modified": now,
            },
            "created": now,
            "modified": now,
        }
        mixer._mixer_presets[preset_id] = create_data

        update_data = {
            "id": preset_id,
            "name": "Updated Preset",
            "project_id": "test_project",
            "state": create_data["state"],
            "created": now,
            "modified": now,
        }

        response = client.put(
            f"/api/mixer/presets/test_project/{preset_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Preset"

    def test_delete_preset_success(self):
        """Test successful preset deletion."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()

        # Create a preset first
        preset_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        preset_data = {
            "id": preset_id,
            "name": "To Delete",
            "project_id": "test_project",
            "state": {
                "id": "state1",
                "project_id": "test_project",
                "channels": [],
                "channel_routing": [],
                "sends": [],
                "returns": [],
                "sub_groups": [],
                "master": {"id": "master", "volume": 1.0},
                "created": now,
                "modified": now,
            },
            "created": now,
            "modified": now,
        }
        mixer._mixer_presets[preset_id] = preset_data

        response = client.delete(f"/api/mixer/presets/test_project/{preset_id}")
        assert response.status_code == 200

    def test_apply_preset_success(self):
        """Test successful preset application."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_presets.clear()
        mixer._mixer_states.clear()

        # Create a preset first
        preset_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        preset_data = {
            "id": preset_id,
            "name": "Test Preset",
            "project_id": "test_project",
            "state": {
                "id": "state1",
                "project_id": "test_project",
                "channels": [],
                "channel_routing": [],
                "sends": [],
                "returns": [],
                "sub_groups": [],
                "master": {"id": "master", "volume": 0.8},
                "created": now,
                "modified": now,
            },
            "created": now,
            "modified": now,
        }
        mixer._mixer_presets[preset_id] = preset_data

        response = client.post(f"/api/mixer/presets/test_project/{preset_id}/apply")
        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data


class TestMixerMetersEndpoints:
    """Test mixer meters endpoints."""

    def test_get_mixer_meters_success(self):
        """Test successful mixer meters retrieval."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        response = client.get("/api/mixer/meters/test_project")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_simulate_meter_updates_success(self):
        """Test successful meter simulation."""
        app = FastAPI()
        app.include_router(mixer.router)
        client = TestClient(app)

        mixer._mixer_states.clear()

        response = client.post("/api/mixer/meters/test_project/simulate?duration=1")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "success" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
