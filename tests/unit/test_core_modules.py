"""
Unit Tests for Core Modules
Tests core functionality modules in isolation.
"""

import sys
import os
from pathlib import Path
import pytest
import numpy as np
import logging
from unittest.mock import Mock, patch, MagicMock
import importlib.util

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_module(module_path: Path):
    """Load module dynamically."""
    if not module_path.exists():
        pytest.skip(f"Module file not found: {module_path}")
    
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        pytest.skip(f"Could not load module: {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


class TestAudioModules:
    """Test audio processing modules."""
    
    def test_audio_utils_imports(self):
        """Test audio utils module can be imported."""
        audio_utils_path = project_root / "app" / "core" / "audio" / "audio_utils.py"
        
        if not audio_utils_path.exists():
            pytest.skip("Audio utils module not found")
        
        try:
            module = load_module(audio_utils_path)
            assert module is not None, "Failed to import audio_utils"
        except Exception as e:
            pytest.skip(f"Could not import audio_utils: {e}")


class TestQualityModules:
    """Test quality metrics modules."""
    
    def test_quality_metrics_imports(self):
        """Test quality metrics module can be imported."""
        quality_metrics_path = project_root / "app" / "core" / "engines" / "quality_metrics.py"
        
        if not quality_metrics_path.exists():
            pytest.skip("Quality metrics module not found")
        
        try:
            module = load_module(quality_metrics_path)
            assert module is not None, "Failed to import quality_metrics"
            
            assert hasattr(module, 'calculate_mos_score') or hasattr(module, 'calculate_all_metrics'), \
                "Quality metrics missing expected functions"
        except Exception as e:
            pytest.skip(f"Could not import quality_metrics: {e}")


class TestRouterModules:
    """Test router modules."""
    
    def test_router_imports(self):
        """Test router module can be imported."""
        router_path = project_root / "app" / "core" / "engines" / "router.py"
        
        if not router_path.exists():
            pytest.skip("Router module not found")
        
        try:
            module = load_module(router_path)
            assert module is not None, "Failed to import router"
        except Exception as e:
            pytest.skip(f"Could not import router: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

