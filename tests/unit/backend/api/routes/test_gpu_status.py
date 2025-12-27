"""
Unit Tests for GPU Status API Route
Tests GPU status and monitoring endpoints comprehensively.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the route module
try:
    from backend.api.routes import gpu_status
except ImportError:
    pytest.skip(
        "Could not import gpu_status route module", allow_module_level=True
    )


class TestGPUStatusRouteImports:
    """Test GPU status route module can be imported."""

    def test_gpu_status_module_imports(self):
        """Test gpu_status module can be imported."""
        assert (
            gpu_status is not None
        ), "Failed to import gpu_status module"
        assert hasattr(
            gpu_status, "router"
        ), "gpu_status module missing router"

    def test_router_exists(self):
        """Test router exists and is configured."""
        assert gpu_status.router is not None, "Router should exist"
        if hasattr(gpu_status.router, "prefix"):
            assert (
                "/api/gpu-status" in gpu_status.router.prefix
            ), "Router prefix should include /api/gpu-status"

    def test_router_has_routes(self):
        """Test router has registered routes."""
        if hasattr(gpu_status.router, "routes"):
            routes = [route.path for route in gpu_status.router.routes]
            assert len(routes) > 0, "Router should have routes registered"


class TestGPUStatusEndpoints:
    """Test GPU status endpoints."""

    def test_get_gpu_status_success(self):
        """Test successful GPU status retrieval."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                "0, NVIDIA GeForce RTX 3080, 10240, 5120, 45.5, 65.0, 250.0, "
                "470.63.01\n"
            )
            mock_run.return_value = mock_result

            response = client.get("/api/gpu-status")
            assert response.status_code == 200
            data = response.json()
            assert "devices" in data
            assert "total_devices" in data
            assert "available_devices" in data

    def test_get_gpu_status_no_gpu(self):
        """Test GPU status when no GPU available."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("nvidia-smi not found")

            response = client.get("/api/gpu-status")
            assert response.status_code == 200
            data = response.json()
            assert data["total_devices"] == 0
            assert len(data["devices"]) == 0

    def test_get_gpu_status_multiple_devices(self):
        """Test GPU status with multiple devices."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                "0, NVIDIA GeForce RTX 3080, 10240, 5120, 45.5, 65.0, 250.0, "
                "470.63.01\n"
                "1, NVIDIA GeForce RTX 3090, 24576, 12288, 30.0, 70.0, 350.0, "
                "470.63.01\n"
            )
            mock_run.return_value = mock_result

            response = client.get("/api/gpu-status")
            assert response.status_code == 200
            data = response.json()
            assert data["total_devices"] == 2
            assert len(data["devices"]) == 2

    def test_get_gpu_status_timeout(self):
        """Test GPU status with timeout."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        import subprocess

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("nvidia-smi", 5)

            response = client.get("/api/gpu-status")
            assert response.status_code == 200
            data = response.json()
            assert data["total_devices"] == 0

    def test_list_gpu_devices_success(self):
        """Test successful GPU devices listing."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                "0, NVIDIA GeForce RTX 3080, 10240, 5120, 45.5, 65.0, 250.0, "
                "470.63.01\n"
            )
            mock_run.return_value = mock_result

            response = client.get("/api/gpu-status/devices")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_list_gpu_devices_empty(self):
        """Test listing devices when no GPU available."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("nvidia-smi not found")

            response = client.get("/api/gpu-status/devices")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_get_gpu_device_success(self):
        """Test successful GPU device retrieval."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                "0, NVIDIA GeForce RTX 3080, 10240, 5120, 45.5, 65.0, 250.0, "
                "470.63.01\n"
            )
            mock_run.return_value = mock_result

            response = client.get("/api/gpu-status/devices/nvidia-0")
            assert response.status_code == 200
            data = response.json()
            assert data["device_id"] == "nvidia-0"
            assert data["vendor"] == "NVIDIA"

    def test_get_gpu_device_not_found(self):
        """Test getting non-existent GPU device."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = (
                "0, NVIDIA GeForce RTX 3080, 10240, 5120, 45.5, 65.0, 250.0, "
                "470.63.01\n"
            )
            mock_run.return_value = mock_result

            response = client.get("/api/gpu-status/devices/nonexistent")
            assert response.status_code == 404

    def test_get_gpu_device_no_devices(self):
        """Test getting device when no GPUs available."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("nvidia-smi not found")

            response = client.get("/api/gpu-status/devices/nvidia-0")
            assert response.status_code == 404

    def test_get_gpu_status_invalid_nvidia_smi_output(self):
        """Test handling invalid nvidia-smi output."""
        app = FastAPI()
        app.include_router(gpu_status.router)
        client = TestClient(app)

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "invalid,output,format\n"
            mock_run.return_value = mock_result

            response = client.get("/api/gpu-status")
            assert response.status_code == 200
            data = response.json()
            # Should handle gracefully and return empty or partial data
            assert "devices" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
