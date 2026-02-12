"""
Engine package entrypoint with lazy loading to avoid eager import of optional or
heavy dependencies (e.g., Diffusers/Transformers used by Deforum).
"""

from __future__ import annotations

import importlib
import re
from typing import Any

__all__ = [
    "RVCEngine",
    "create_rvc_engine",
    "get_engine_class",
    "EngineRouter",
    "router",
    "QualityOptimizer",
    "get_synthesis_params_from_preset",
    "optimize_synthesis_for_quality",
    "calculate_all_metrics",
    "calculate_similarity",
    "calculate_mos_score",
    "calculate_naturalness",
    "calculate_snr",
    "detect_artifacts",
    "clear_metrics_cache",
    "get_cache_stats",
    "QualityComparison",
    "compare_audio_samples",
    # Cancellation support
    "CancellationToken",
    "OperationCancelledError",
    "EngineProtocol",
]


def _load(dotted: str) -> Any:
    """Import an object given a dotted path of the form 'module:attr'."""
    module_path, attr = dotted.split(":")
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def _to_snake(name: str) -> str:
    """Convert CamelCase names to snake_case module names."""
    snake = re.sub(r"(.)([A-Z][a-z0-9]+)", r"\1_\2", name)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", snake)
    return snake.lower()


_ENGINE_CLASSES = {
    # Keep this minimal; add optional engines only when needed.
    # Most engines are auto-discovered from manifests via _discover_engines_from_manifests()
    "rvc": "app.core.engines.rvc_engine:RVCEngine",
    "deforum": "app.core.engines.deforum_engine:DeforumEngine",
}

# Cache for discovered engines from manifests
_ENGINE_CLASSES_DISCOVERED = False


def _discover_engines_from_manifests():
    """Auto-discover engines from manifest files and add to _ENGINE_CLASSES."""
    global _ENGINE_CLASSES_DISCOVERED
    if _ENGINE_CLASSES_DISCOVERED:
        return
    
    try:
        from .manifest_loader import find_engine_manifests, get_engine_entry_point, load_engine_manifest
        
        # Find all engine manifests
        manifests = find_engine_manifests("engines")
        
        for engine_id, manifest_path in manifests.items():
            # Skip if already registered
            if engine_id in _ENGINE_CLASSES:
                continue
            
            try:
                manifest = load_engine_manifest(manifest_path)
                entry_point = get_engine_entry_point(manifest)
                
                if entry_point:
                    # Add to registry in format "module:class"
                    _ENGINE_CLASSES[engine_id] = entry_point
            except Exception as e:
                # Log but don't fail - some engines may have invalid manifests
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Failed to discover engine {engine_id} from manifest: {e}")
        
        _ENGINE_CLASSES_DISCOVERED = True
    except Exception as e:
        # If manifest discovery fails, engines will still work via explicit registration
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Engine manifest discovery failed (non-critical): {e}")


_EXPLICIT_MODULES = {
    # Base protocol and cancellation
    "EngineProtocol": "app.core.engines.base",
    "CancellationToken": "app.core.engines.base",
    "OperationCancelledError": "app.core.engines.base",
    # Router and config
    "EngineRouter": "app.core.engines.router",
    "router": "app.core.engines.router",
    "EngineConfig": "app.core.engines.config",
    "get_engine_config": "app.core.engines.config",
    # Quality metrics and helpers
    "calculate_all_metrics": "app.core.engines.quality_metrics",
    "calculate_mos_score": "app.core.engines.quality_metrics",
    "calculate_naturalness": "app.core.engines.quality_metrics",
    "calculate_similarity": "app.core.engines.quality_metrics",
    "calculate_snr": "app.core.engines.quality_metrics",
    "clear_metrics_cache": "app.core.engines.quality_metrics",
    "detect_artifacts": "app.core.engines.quality_metrics",
    "get_cache_stats": "app.core.engines.quality_metrics",
    "QualityComparison": "app.core.engines.quality_comparison",
    "compare_audio_samples": "app.core.engines.quality_comparison",
    "QualityOptimizer": "app.core.engines.quality_optimizer",
    "optimize_synthesis_for_quality": "app.core.engines.quality_optimizer",
    "PROFESSIONAL_THRESHOLDS": "app.core.engines.quality_optimizer",
    "QUALITY_TIERS": "app.core.engines.quality_optimizer",
    "QUALITY_PRESETS": "app.core.engines.quality_presets",
    "ENGINE_PRESET_MAPPINGS": "app.core.engines.quality_presets",
    "get_engine_preset": "app.core.engines.quality_presets",
    "get_preset_description": "app.core.engines.quality_presets",
    "get_preset_target_metrics": "app.core.engines.quality_presets",
    "get_quality_preset": "app.core.engines.quality_presets",
    "get_synthesis_params_from_preset": "app.core.engines.quality_presets",
    "list_quality_presets": "app.core.engines.quality_presets",
    # ONNX helpers
    "convert_pytorch_to_onnx": "app.core.engines.onnx_converter",
    "get_onnx_model_info": "app.core.engines.onnx_converter",
    "optimize_onnx_model": "app.core.engines.onnx_converter",
    "quantize_onnx_model": "app.core.engines.onnx_converter",
    "validate_onnx_model": "app.core.engines.onnx_converter",
    "ONNXInferenceEngine": "app.core.engines.onnx_wrapper",
    "create_onnx_inference_engine": "app.core.engines.onnx_wrapper",
    "HAS_ONNX": "app.core.engines.onnx_converter",
}


def get_engine_class(engine_id: str):
    """Return an engine class by id using lazy import."""
    # Auto-discover engines from manifests on first call
    _discover_engines_from_manifests()
    
    try:
        dotted = _ENGINE_CLASSES[engine_id]
    except KeyError as exc:
        raise KeyError(
            f"Unknown engine_id={engine_id!r}. Known: {sorted(_ENGINE_CLASSES)}"
        ) from exc
    return _load(dotted)


def _resolve_module_for_attr(name: str) -> str | None:
    """Map attribute names to modules without importing heavy deps eagerly."""
    if name in _EXPLICIT_MODULES:
        return _EXPLICIT_MODULES[name]

    if name.startswith("create_"):
        target = name[len("create_") :]
        if not target.endswith("_engine"):
            target += "_engine"
        return f"{__name__}.{target}"

    if name.endswith("Engine"):
        module_name = _to_snake(name)
        return f"{__name__}.{module_name}"

    return None


def __getattr__(name: str) -> Any:
    # Auto-discover engines from manifests on first access
    _discover_engines_from_manifests()
    
    module_path = _resolve_module_for_attr(name)
    if not module_path:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    try:
        module = importlib.import_module(module_path)
        value = getattr(module, name)
        globals()[name] = value
        return value
    except Exception as exc:  # noqa: BLE001 - propagate detailed errors
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r} (import failed from {module_path})"
        ) from exc


# RVCEngine and create_rvc_engine are resolved lazily via __getattr__
