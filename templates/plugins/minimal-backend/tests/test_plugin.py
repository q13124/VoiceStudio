"""
Unit tests for {{DISPLAY_NAME}} Plugin
"""

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def mock_app():
    """Create a test FastAPI application."""
    return FastAPI()


@pytest.fixture
def plugin_dir():
    """Get the plugin directory path."""
    return Path(__file__).parent.parent


def test_plugin_initialization(mock_app, plugin_dir):
    """Test that plugin initializes correctly."""
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        
        assert plugin is not None
        assert plugin.name == "{{PLUGIN_NAME}}"
        assert plugin.version == "{{VERSION}}"
        assert plugin.author == "{{AUTHOR}}"
        assert plugin.is_initialized()
    except ImportError as e:
        pytest.skip(f"Could not import plugin module: {e}")


def test_status_endpoint(mock_app, plugin_dir):
    """Test the GET /status endpoint."""
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        client = TestClient(mock_app)
        
        response = client.get("/api/plugin/{{PLUGIN_NAME}}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["active", "inactive"]
        assert data["plugin_name"] == "{{PLUGIN_NAME}}"
        assert data["version"] == "{{VERSION}}"
    except ImportError as e:
        pytest.skip(f"Could not import plugin module: {e}")


def test_message_endpoint(mock_app, plugin_dir):
    """Test the POST /message endpoint."""
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        client = TestClient(mock_app)
        
        response = client.post(
            "/api/plugin/{{PLUGIN_NAME}}/message",
            json={"message": "hello world"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Received:" in data["message"]
        assert "processed_at" in data
    except ImportError as e:
        pytest.skip(f"Could not import plugin module: {e}")


def test_message_validation(mock_app, plugin_dir):
    """Test request validation for message endpoint."""
    try:
        from plugin import register
        
        plugin = register(mock_app, plugin_dir)
        client = TestClient(mock_app)
        
        # Missing required field
        response = client.post(
            "/api/plugin/{{PLUGIN_NAME}}/message",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    except ImportError as e:
        pytest.skip(f"Could not import plugin module: {e}")
