"""Debug test mode detection."""

import os
import sys
from pathlib import Path

# Force test mode BEFORE any imports
os.environ["VOICESTUDIO_TEST_MODE"] = "1"

# This should already be set
print(f"VOICESTUDIO_TEST_MODE at module load: {os.environ.get('VOICESTUDIO_TEST_MODE', 'NOT SET')}")

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.routes.eval_abx import _is_test_mode

print(f"_is_test_mode() result: {_is_test_mode()}")

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app


class TestDebugMode:
    """Debug test to verify test mode is working."""

    @pytest.fixture
    def client(self):
        # Force test mode in app state for reliable detection
        app.state.test_mode = True
        with TestClient(app) as client:
            yield client
        # Clean up
        app.state.test_mode = False

    def test_abx_start_in_test_mode(self, client: TestClient):
        """Test ABX start endpoint in test mode."""
        print(f"\n_is_test_mode() in test: {_is_test_mode()}")
        print(f"os.environ in test: {os.environ.get('VOICESTUDIO_TEST_MODE', 'NOT SET')}")
        print(f"app.state.test_mode: {getattr(app.state, 'test_mode', 'NOT SET')}")
        
        response = client.post(
            "/api/eval/abx/start",
            json={"items": ["a", "b", "c"]},
        )
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
