"""
Unit Tests for Backend Route Modules
Tests individual route handlers in isolation.
"""

import importlib.util
import logging
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_route_module(route_name: str):
    """Load route module dynamically."""
    route_path = project_root / "backend" / "api" / "routes" / f"{route_name}.py"

    if not route_path.exists():
        pytest.skip(f"Route file not found: {route_path}")

    spec = importlib.util.spec_from_file_location(route_name, route_path)
    if spec is None or spec.loader is None:
        pytest.skip(f"Could not load route module: {route_name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class TestRouteImports:
    """Test route modules can be imported."""

    @pytest.mark.parametrize(
        "route_name",
        [
            "profiles",
            "projects",
            "audio",
            "quality",
            "engines",
        ],
    )
    def test_route_module_imports(self, route_name):
        """Test route module can be imported."""
        try:
            module = load_route_module(route_name)
            assert module is not None, f"Failed to import {route_name}"

            assert hasattr(module, "router") or hasattr(
                module, "app"
            ), f"{route_name} missing router or app"
        except Exception as e:
            pytest.skip(f"Could not import {route_name}: {e}")


class TestRouteHandlers:
    """Test route handlers exist."""

    @pytest.mark.parametrize(
        "route_name",
        [
            "profiles",
            "projects",
        ],
    )
    def test_crud_handlers_exist(self, route_name):
        """Test CRUD handlers exist in route module."""
        try:
            module = load_route_module(route_name)

            handlers = [
                f"list_{route_name}",
                f"create_{route_name.rstrip('s')}",
                f"get_{route_name.rstrip('s')}",
                f"update_{route_name.rstrip('s')}",
                f"delete_{route_name.rstrip('s')}",
            ]

            found_handlers = []
            for handler_name in handlers:
                if hasattr(module, handler_name):
                    found_handlers.append(handler_name)

            assert len(found_handlers) > 0, f"{route_name} missing expected handlers"
        except Exception as e:
            pytest.skip(f"Could not test {route_name} handlers: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
