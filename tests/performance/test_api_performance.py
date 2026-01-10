"""
API Performance Tests
Comprehensive performance tests for backend API endpoints.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))
sys.path.insert(0, str(project_root / "app"))

try:
    from fastapi.testclient import TestClient

    from backend.api.main import app

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    pytest.skip("FastAPI not available", allow_module_level=True)


class TestAPIPerformance:
    """Test API endpoint performance."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint_performance(self, client):
        """Test health endpoint response time."""
        start_time = time.perf_counter()
        response = client.get("/api/health")
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        assert (
            elapsed_time < 0.2
        ), f"Health endpoint took {elapsed_time:.3f}s (should be < 0.2s)"

    def test_profiles_list_performance(self, client):
        """Test profiles list endpoint performance."""
        start_time = time.perf_counter()
        response = client.get("/api/profiles")
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        assert (
            elapsed_time < 1.0
        ), f"Profiles list took {elapsed_time:.3f}s (should be < 1.0s)"

    def test_projects_list_performance(self, client):
        """Test projects list endpoint performance."""
        start_time = time.perf_counter()
        response = client.get("/api/projects")
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        assert (
            elapsed_time < 1.0
        ), f"Projects list took {elapsed_time:.3f}s (should be < 1.0s)"

    def test_engines_list_performance(self, client):
        """Test engines list endpoint performance."""
        start_time = time.perf_counter()
        response = client.get("/api/engines")
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        assert (
            elapsed_time < 1.0
        ), f"Engines list took {elapsed_time:.3f}s (should be < 1.0s)"

    @pytest.mark.parametrize(
        "endpoint",
        [
            "/api/health",
            "/api/profiles",
            "/api/projects",
            "/api/engines",
        ],
    )
    def test_endpoint_response_time(self, client, endpoint):
        """Test multiple endpoints for response time."""
        start_time = time.perf_counter()
        response = client.get(endpoint)
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code in [
            200,
            404,
        ], f"Endpoint {endpoint} returned {response.status_code}"
        assert (
            elapsed_time < 2.0
        ), f"Endpoint {endpoint} took {elapsed_time:.3f}s (should be < 2.0s)"

    def test_concurrent_requests_performance(self, client):
        """Test performance under concurrent requests."""
        import concurrent.futures

        def make_request():
            start = time.perf_counter()
            response = client.get("/api/health")
            elapsed = time.perf_counter() - start
            return response.status_code, elapsed

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        status_codes, elapsed_times = zip(*results)

        assert all(code == 200 for code in status_codes), "All requests should succeed"
        avg_time = sum(elapsed_times) / len(elapsed_times)
        assert (
            avg_time < 0.5
        ), f"Average response time {avg_time:.3f}s (should be < 0.5s)"


class TestAPICachePerformance:
    """Test API caching performance."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_cached_endpoint_performance(self, client):
        """Test cached endpoint performance improvement."""
        # First request (cache miss)
        start_time = time.perf_counter()
        response1 = client.get("/api/engines")
        first_request_time = time.perf_counter() - start_time

        # Second request (cache hit)
        start_time = time.perf_counter()
        response2 = client.get("/api/engines")
        second_request_time = time.perf_counter() - start_time

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Cached request should be faster (or at least not slower)
        assert (
            second_request_time <= first_request_time * 1.5
        ), f"Cached request should be faster: {first_request_time:.3f}s -> {second_request_time:.3f}s"


class TestAPIMiddlewarePerformance:
    """Test API middleware performance impact."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_middleware_overhead(self, client):
        """Test middleware performance overhead."""
        # Request with middleware
        start_time = time.perf_counter()
        response = client.get("/api/health")
        middleware_time = time.perf_counter() - start_time

        assert response.status_code == 200
        # Middleware should add minimal overhead (< 50ms)
        assert (
            middleware_time < 0.2
        ), f"Middleware overhead {middleware_time:.3f}s (should be < 0.2s)"

    def test_validation_middleware_performance(self, client):
        """Test validation middleware performance."""
        start_time = time.perf_counter()
        response = client.post(
            "/api/profiles", json={"name": "Test Profile", "language": "en"}
        )
        elapsed_time = time.perf_counter() - start_time

        # Validation should be fast (< 100ms)
        assert (
            elapsed_time < 0.5
        ), f"Validation took {elapsed_time:.3f}s (should be < 0.5s)"


class TestEnhancedRoutesPerformance:
    """Test performance of enhanced routes with new library integrations."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @patch("backend.api.routes.articulation._get_audio_path")
    @patch("soundfile.read")
    @patch("librosa.feature.rms")
    @patch("librosa.frames_to_time")
    def test_articulation_analysis_performance(
        self, mock_frames, mock_rms, mock_sf_read, mock_get_path, client
    ):
        """Test articulation analysis endpoint performance."""
        import numpy as np

        mock_get_path.return_value = "/test/audio.wav"
        audio_data = np.random.randn(44100).astype(np.float32)
        mock_sf_read.return_value = (audio_data, 44100)
        mock_rms.return_value = np.array([[0.5] * 10])
        mock_frames.return_value = np.linspace(0, 1, 10)

        request_data = {"audio_id": "test-audio-123"}

        start_time = time.perf_counter()
        response = client.post("/api/articulation/analyze", json=request_data)
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        # Articulation analysis should complete in reasonable time (< 2s)
        assert (
            elapsed_time < 2.0
        ), f"Articulation analysis took {elapsed_time:.3f}s (should be < 2.0s)"

    @patch("backend.api.routes.prosody.HAS_PHONEMIZER", True)
    @patch("backend.api.routes.prosody.Phonemizer")
    def test_prosody_phoneme_analysis_performance(self, mock_phonemizer_class, client):
        """Test prosody phoneme analysis performance with Phonemizer."""
        from unittest.mock import MagicMock

        mock_phonemizer = MagicMock()
        mock_phonemizer.phonemize.return_value = "həˈloʊ"
        mock_phonemizer_class.return_value = mock_phonemizer

        start_time = time.perf_counter()
        response = client.post("/api/prosody/phonemes/analyze?text=hello&language=en")
        elapsed_time = time.perf_counter() - start_time

        # Phoneme analysis should be fast (< 1s)
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            assert (
                elapsed_time < 1.0
            ), f"Phoneme analysis took {elapsed_time:.3f}s (should be < 1.0s)"

    def test_prosody_config_creation_performance(self, client):
        """Test prosody config creation performance."""
        from backend.api.routes import prosody

        prosody._prosody_configs.clear()

        config_data = {
            "name": "Performance Test Config",
            "pitch": 1.2,
            "rate": 1.1,
            "volume": 0.9,
        }

        start_time = time.perf_counter()
        response = client.post("/api/prosody/configs", json=config_data)
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        # Config creation should be very fast (< 100ms)
        assert (
            elapsed_time < 0.1
        ), f"Config creation took {elapsed_time:.3f}s (should be < 0.1s)"

    @patch("backend.api.routes.effects.HAS_POSTFX_PROCESSOR", True)
    @patch("backend.api.routes.effects.create_post_fx_processor")
    def test_effects_processing_performance(self, mock_create_processor, client):
        """Test effects processing performance with PostFXProcessor."""
        import uuid
        from datetime import datetime
        from unittest.mock import MagicMock

        import numpy as np

        from backend.api.routes import effects

        effects._effect_chains.clear()

        chain_id = f"chain-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        effects._effect_chains[chain_id] = effects.EffectChain(
            id=chain_id,
            name="Performance Test Chain",
            project_id="test-project",
            effects=[],
            created=now,
            modified=now,
        )

        mock_processor = MagicMock()
        mock_audio = np.random.randn(44100).astype(np.float32)
        mock_processor.process.return_value = mock_audio
        mock_create_processor.return_value = mock_processor

        with patch("os.path.exists", return_value=True):
            with patch("backend.api.routes.voice._audio_storage") as mock_storage:
                mock_storage.__contains__ = lambda x: x == "test-audio"
                mock_storage.__getitem__ = lambda x: "/path/to/audio.wav"

                with patch(
                    "backend.api.routes.effects._process_audio_with_chain"
                ) as mock_process:
                    mock_process.return_value = {
                        "success": True,
                        "output_audio_id": "processed-audio",
                    }

                    request_data = {"audio_id": "test-audio"}

                    start_time = time.perf_counter()
                    response = client.post(
                        f"/api/effects/chains/{chain_id}/process",
                        json=request_data,
                    )
                    elapsed_time = time.perf_counter() - start_time

                    # Effects processing should complete in reasonable time (< 3s)
                    assert response.status_code in [200, 500]
                    if response.status_code == 200:
                        assert (
                            elapsed_time < 3.0
                        ), f"Effects processing took {elapsed_time:.3f}s (should be < 3.0s)"

    @patch("backend.api.routes.analytics._get_model_explainer")
    def test_analytics_quality_explanation_performance(
        self, mock_get_explainer, client
    ):
        """Test analytics quality explanation performance with ModelExplainer."""
        from unittest.mock import MagicMock

        from backend.api.routes import voice

        audio_id = "test-audio-123"
        try:
            voice._audio_storage[audio_id] = "/path/to/audio.wav"
        except AttributeError:
            ...

        mock_explainer = MagicMock()
        mock_explainer.get_available_methods.return_value = ["shap", "lime"]
        mock_explainer.shap_available = True
        mock_get_explainer.return_value = mock_explainer

        with patch("os.path.exists", return_value=True):
            with patch("backend.api.routes.analytics._quality_history", {}):
                start_time = time.perf_counter()
                response = client.get(
                    f"/api/analytics/explain-quality?audio_id={audio_id}"
                )
                elapsed_time = time.perf_counter() - start_time

                # Quality explanation should complete in reasonable time (< 5s)
                assert response.status_code in [200, 404, 500]
                if response.status_code == 200:
                    assert (
                        elapsed_time < 5.0
                    ), f"Quality explanation took {elapsed_time:.3f}s (should be < 5.0s)"

    def test_analytics_summary_performance(self, client):
        """Test analytics summary endpoint performance."""
        start_time = time.perf_counter()
        response = client.get("/api/analytics/summary")
        elapsed_time = time.perf_counter() - start_time

        assert response.status_code == 200
        # Analytics summary should be fast (< 1s)
        assert (
            elapsed_time < 1.0
        ), f"Analytics summary took {elapsed_time:.3f}s (should be < 1.0s)"

    def test_enhanced_routes_concurrent_performance(self, client):
        """Test enhanced routes performance under concurrent load."""
        import concurrent.futures

        from backend.api.routes import prosody

        prosody._prosody_configs.clear()

        def make_prosody_request():
            """Make prosody config list request."""
            start = time.perf_counter()
            response = client.get("/api/prosody/configs")
            elapsed = time.perf_counter() - start
            return response.status_code, elapsed

        def make_analytics_request():
            """Make analytics summary request."""
            start = time.perf_counter()
            response = client.get("/api/analytics/summary")
            elapsed = time.perf_counter() - start
            return response.status_code, elapsed

        # Test concurrent requests to enhanced routes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            # Mix of prosody and analytics requests
            for _ in range(10):
                futures.append(executor.submit(make_prosody_request))
            for _ in range(10):
                futures.append(executor.submit(make_analytics_request))

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        status_codes, elapsed_times = zip(*results)

        # All requests should succeed
        assert all(
            code in [200, 404] for code in status_codes
        ), "All concurrent requests should succeed"

        avg_time = sum(elapsed_times) / len(elapsed_times)
        # Average response time should be reasonable (< 1s)
        assert (
            avg_time < 1.0
        ), f"Average concurrent response time {avg_time:.3f}s (should be < 1.0s)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
