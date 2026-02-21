"""Verify all engine adapter modules import without errors.

Parametrized tests auto-discover every Python file under app/core/engines/
and confirm each module loads cleanly.  Engines whose optional dependencies
(GPU libraries, ML frameworks, etc.) are not installed are skipped gracefully
rather than marked as failures.
"""

import importlib
import inspect
import os

import pytest

ENGINE_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "app", "core", "engines"
    )
)

UTILITY_MODULES = frozenset(
    {
        "base",
        "config",
        "dependency_validator",
        "engine_audit",
        "engine_registry",
        "language_detector",
        "llm_interface",
        "manifest_loader",
        "metrics",
        "onnx_converter",
        "onnx_wrapper",
        "performance_metrics",
        "protocols",
        "quality_comparison",
        "quality_metrics",
        "quality_metrics_batch",
        "quality_metrics_cache",
        "quality_optimizer",
        "quality_presets",
        "realtime_optimizer",
        "router",
        "router_optimized",
        "s2s_protocol",
        "test_quality_metrics",
    }
)


def get_engine_modules():
    """Discover all non-private, non-base Python modules in app/core/engines/."""
    modules = []
    for f in sorted(os.listdir(ENGINE_DIR)):
        if f.endswith(".py") and not f.startswith("_") and f != "base.py":
            modules.append(f[:-3])
    return modules


def get_adapter_modules():
    """Return only modules expected to contain an Engine class."""
    return [m for m in get_engine_modules() if m not in UTILITY_MODULES]


# ---------------------------------------------------------------------------
# Test 1: Every module imports without errors
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_name", get_engine_modules())
def test_engine_module_imports(module_name):
    """Each engine module should import without errors."""
    fqn = f"app.core.engines.{module_name}"
    try:
        mod = importlib.import_module(fqn)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
        return

    assert hasattr(mod, "__name__")


# ---------------------------------------------------------------------------
# Test 2: Adapter modules expose at least one Engine class
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_name", get_adapter_modules())
def test_engine_class_discoverable(module_name):
    """Each adapter module should expose at least one class with 'Engine' in its name."""
    fqn = f"app.core.engines.{module_name}"
    try:
        mod = importlib.import_module(fqn)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing: {exc}")
        return

    adapter_keywords = (
        "Engine", "Translator", "Converter",
        "Synthesizer", "Extractor",
        "Provider", "Client",
    )
    found = [
        name
        for name, obj in inspect.getmembers(mod, inspect.isclass)
        if obj.__module__ == mod.__name__
        and not name.startswith("_")
        and any(kw in name for kw in adapter_keywords)
    ]

    assert found, (
        f"{fqn} has no discoverable adapter class"
    )


# ---------------------------------------------------------------------------
# Test 3: Engine classes that subclass EngineProtocol declare required methods
# ---------------------------------------------------------------------------

REQUIRED_PROTOCOL_METHODS = {"initialize", "cleanup"}


@pytest.mark.parametrize("module_name", get_adapter_modules())
def test_engine_protocol_contract(module_name):
    """Engine classes inheriting EngineProtocol must implement required methods."""
    fqn = f"app.core.engines.{module_name}"
    try:
        mod = importlib.import_module(fqn)
    except ImportError as exc:
        pytest.skip(
            f"Optional dependency missing: {exc}"
        )
        return

    try:
        from app.core.engines.base import EngineProtocol
    except ImportError as exc:
        pytest.skip(f"Cannot import base: {exc}")
        return

    subclasses = [
        (n, o)
        for n, o in inspect.getmembers(mod, inspect.isclass)
        if issubclass(o, EngineProtocol)
        and o is not EngineProtocol
        and o.__module__ == mod.__name__
    ]

    if not subclasses:
        pytest.skip(
            f"{module_name}: no EngineProtocol subclass"
        )
        return

    for cls_name, cls in subclasses:
        for method in REQUIRED_PROTOCOL_METHODS:
            assert hasattr(cls, method), (
                f"{cls_name} missing '{method}'"
            )
