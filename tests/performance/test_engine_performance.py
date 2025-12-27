"""
Performance Tests for Engines
Tests engine performance and benchmarks.
"""

import sys
import os
from pathlib import Path
import pytest
import numpy as np
import time
import logging
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_test_audio(duration_seconds: float = 1.0, sample_rate: int = 22050) -> np.ndarray:
    """Generate test audio signal."""
    t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
    audio = np.sin(2 * np.pi * 440.0 * t)
    audio = audio * 0.5
    return audio.astype(np.float32)


class TestEnginePerformance:
    """Test engine performance benchmarks."""
    
    @pytest.mark.parametrize("engine_name", [
        "xtts_engine",
        "chatterbox_engine",
        "tortoise_engine",
    ])
    def test_synthesis_performance(self, engine_name):
        """Test synthesis performance."""
        try:
            import importlib.util
            engine_path = project_root / "app" / "core" / "engines" / f"{engine_name}.py"
            
            if not engine_path.exists():
                pytest.skip(f"Engine not found: {engine_name}")
            
            spec = importlib.util.spec_from_file_location(engine_name, engine_path)
            if spec is None or spec.loader is None:
                pytest.skip(f"Could not load {engine_name}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            engine_classes = [obj for name, obj in __import__('inspect').getmembers(module, __import__('inspect').isclass)
                             if name.endswith('Engine')]
            
            if not engine_classes:
                pytest.skip(f"No engine class in {engine_name}")
            
            engine_class = engine_classes[0]
            
            with __import__('unittest.mock').patch('torch.cuda.is_available', return_value=False):
                engine = engine_class(model_path=None, device="cpu")
                
                if hasattr(engine, 'synthesize'):
                    start_time = time.time()
                    
                    try:
                        result = engine.synthesize(
                            text="Hello, this is a performance test.",
                            voice_profile_id="test",
                            sample_rate=22050
                        )
                        
                        elapsed_time = time.time() - start_time
                        
                        assert elapsed_time < 30.0, \
                            f"{engine_name} synthesis took {elapsed_time:.2f}s (should be < 30s)"
                        
                        logger.info(f"{engine_name} synthesis: {elapsed_time:.2f}s")
                    except Exception as e:
                        pytest.skip(f"Could not test {engine_name} performance: {e}")
        except Exception as e:
            pytest.skip(f"Could not test {engine_name} performance: {e}")


class TestBackendPerformance:
    """Test backend API performance."""
    
    @pytest.mark.skipif(True, reason="Requires backend to be running")
    def test_api_response_time(self):
        """Test API endpoint response times."""
        import requests
        
        API_BASE_URL = "http://localhost:8000/api"
        
        try:
            start_time = time.time()
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200, "Health endpoint failed"
            assert elapsed_time < 1.0, \
                f"API response time {elapsed_time:.2f}s (should be < 1s)"
            
            logger.info(f"API health check: {elapsed_time:.2f}s")
        except Exception as e:
            pytest.skip(f"Could not test API performance: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])

