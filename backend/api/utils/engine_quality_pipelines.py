"""
Engine-Specific Quality Enhancement Pipelines (IDEA 58).

Provides configurable quality enhancement pipelines optimized for each engine's
characteristics (XTTS, Chatterbox, Tortoise).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Try to import audio utilities
try:
    import os
    import sys
    app_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "app")
    if os.path.exists(app_path) and app_path not in sys.path:
        sys.path.insert(0, app_path)

    from core.audio.advanced_quality_enhancement import enhance_voice_quality_advanced
    from core.audio.audio_utils import enhance_voice_quality

    from app.core.engines.quality_metrics import calculate_all_metrics

    HAS_AUDIO_UTILS = True
    HAS_ADVANCED_ENHANCEMENT = True
    HAS_QUALITY_METRICS = True
except ImportError as e:
    logger.warning(f"Audio utilities not available: {e}")
    HAS_AUDIO_UTILS = False
    HAS_ADVANCED_ENHANCEMENT = False
    HAS_QUALITY_METRICS = False


# Default pipeline configurations for each engine
ENGINE_PIPELINE_PRESETS = {
    "xtts_v2": {
        "default": {
            "steps": ["denoise", "normalize", "remove_artifacts"],
            "denoise": {"enabled": True, "strength": 0.7},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "description": "Fast enhancement for XTTS output"
        },
        "light": {
            "steps": ["normalize"],
            "denoise": {"enabled": False},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": False},
            "description": "Light enhancement for speed"
        },
        "maximum": {
            "steps": ["denoise", "normalize", "remove_artifacts", "spectral_enhance"],
            "denoise": {"enabled": True, "strength": 0.9},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "spectral_enhance": {"enabled": True},
            "description": "Maximum quality enhancement"
        }
    },
    "chatterbox": {
        "default": {
            "steps": ["denoise", "normalize", "remove_artifacts", "preserve_emotion"],
            "denoise": {"enabled": True, "strength": 0.6},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "preserve_emotion": {"enabled": True},
            "description": "Balanced enhancement preserving emotion"
        },
        "light": {
            "steps": ["normalize", "remove_artifacts"],
            "denoise": {"enabled": False},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "preserve_emotion": {"enabled": True},
            "description": "Light enhancement for emotion preservation"
        },
        "maximum": {
            "steps": ["denoise", "normalize", "remove_artifacts", "spectral_enhance", "preserve_emotion"],
            "denoise": {"enabled": True, "strength": 0.8},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "spectral_enhance": {"enabled": True},
            "preserve_emotion": {"enabled": True},
            "description": "Maximum enhancement with emotion preservation"
        }
    },
    "tortoise": {
        "default": {
            "steps": ["denoise", "normalize", "remove_artifacts", "spectral_enhance"],
            "denoise": {"enabled": True, "strength": 0.5},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "spectral_enhance": {"enabled": True},
            "description": "Maximum quality enhancement for Tortoise"
        },
        "ultra": {
            "steps": ["denoise", "normalize", "remove_artifacts", "spectral_enhance", "enhance_prosody"],
            "denoise": {"enabled": True, "strength": 0.7},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "spectral_enhance": {"enabled": True},
            "enhance_prosody": {"enabled": True},
            "description": "Ultra quality enhancement"
        },
        "light": {
            "steps": ["normalize", "remove_artifacts"],
            "denoise": {"enabled": False},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "description": "Light enhancement for faster processing"
        }
    }
}


def get_engine_pipeline(
    engine_id: str,
    preset_name: str = "default"
) -> dict[str, Any]:
    """
    Get pipeline configuration for an engine and preset.

    Args:
        engine_id: Engine identifier (e.g., "xtts_v2", "chatterbox", "tortoise")
        preset_name: Preset name (e.g., "default", "light", "maximum")

    Returns:
        Pipeline configuration dictionary
    """
    engine_presets = ENGINE_PIPELINE_PRESETS.get(engine_id, {})
    if not engine_presets:
        logger.warning(f"No presets found for engine {engine_id}, using generic")
        return _get_generic_pipeline(preset_name)

    pipeline = engine_presets.get(preset_name)
    if not pipeline:
        logger.warning(f"Preset {preset_name} not found for {engine_id}, using default")
        pipeline = engine_presets.get("default", {})

    return pipeline.copy()


def _get_generic_pipeline(preset_name: str) -> dict[str, Any]:
    """Get a generic pipeline configuration."""
    generic_presets = {
        "default": {
            "steps": ["denoise", "normalize", "remove_artifacts"],
            "denoise": {"enabled": True, "strength": 0.7},
            "normalize": {"enabled": True, "target_lufs": -23.0},
            "remove_artifacts": {"enabled": True},
            "description": "Generic enhancement pipeline"
        }
    }
    return generic_presets.get(preset_name, generic_presets["default"]).copy()


def apply_engine_pipeline(
    audio: np.ndarray,
    sample_rate: int,
    engine_id: str,
    pipeline_config: dict[str, Any] | None = None,
    preset_name: str = "default",
    reference_audio: str | None = None
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Apply engine-specific quality enhancement pipeline to audio.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        engine_id: Engine identifier
        pipeline_config: Optional custom pipeline configuration
        preset_name: Preset name if pipeline_config not provided
        reference_audio: Optional reference audio path for voice matching

    Returns:
        Tuple of (enhanced_audio, quality_metrics)
    """
    # Get pipeline configuration
    if pipeline_config is None:
        pipeline_config = get_engine_pipeline(engine_id, preset_name)

    processed_audio = audio.copy()
    quality_metrics = {}

    # Apply pipeline steps in order
    steps = pipeline_config.get("steps", [])

    # Check if advanced enhancement should be used
    use_advanced = (
        "spectral_enhance" in steps or
        "enhance_prosody" in steps or
        HAS_ADVANCED_ENHANCEMENT
    )

    if use_advanced and HAS_ADVANCED_ENHANCEMENT:
        try:
            processed_audio = enhance_voice_quality_advanced(
                processed_audio,
                sample_rate,
                reference_audio=reference_audio,
                normalize=pipeline_config.get("normalize", {}).get("enabled", True),
                denoise=pipeline_config.get("denoise", {}).get("enabled", True),
                spectral_enhance="spectral_enhance" in steps,
                preserve_formants="preserve_emotion" in steps,
                remove_artifacts="remove_artifacts" in steps,
                enhance_prosody="enhance_prosody" in steps,
                target_lufs=pipeline_config.get("normalize", {}).get("target_lufs", -23.0)
            )
            logger.debug(f"Applied advanced enhancement pipeline for {engine_id}")
        except Exception as e:
            logger.warning(f"Advanced enhancement failed, falling back: {e}")
            use_advanced = False

    if not use_advanced and HAS_AUDIO_UTILS:
        try:
            processed_audio = enhance_voice_quality(
                processed_audio,
                sample_rate,
                normalize=pipeline_config.get("normalize", {}).get("enabled", True),
                denoise=pipeline_config.get("denoise", {}).get("enabled", True),
                target_lufs=pipeline_config.get("normalize", {}).get("target_lufs", -23.0)
            )
            logger.debug(f"Applied standard enhancement pipeline for {engine_id}")
        except Exception as e:
            logger.warning(f"Enhancement failed: {e}")

    # Calculate quality metrics if available
    if HAS_QUALITY_METRICS:
        try:
            quality_metrics = calculate_all_metrics(
                audio=processed_audio,
                reference_audio=reference_audio,
                sample_rate=sample_rate
            )
        except Exception as e:
            logger.warning(f"Quality metrics calculation failed: {e}")

    return processed_audio, quality_metrics


def preview_engine_pipeline(
    audio: np.ndarray,
    sample_rate: int,
    engine_id: str,
    pipeline_config: dict[str, Any] | None = None,
    preset_name: str = "default",
    reference_audio: str | None = None
) -> tuple[np.ndarray, dict[str, Any], dict[str, Any]]:
    """
    Preview engine pipeline effects (returns both original and enhanced for comparison).

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        engine_id: Engine identifier
        pipeline_config: Optional custom pipeline configuration
        preset_name: Preset name if pipeline_config not provided
        reference_audio: Optional reference audio path

    Returns:
        Tuple of (enhanced_audio, before_metrics, after_metrics)
    """
    # Calculate before metrics
    before_metrics = {}
    if HAS_QUALITY_METRICS:
        try:
            before_metrics = calculate_all_metrics(
                audio=audio,
                reference_audio=reference_audio,
                sample_rate=sample_rate
            )
        except Exception as e:
            logger.warning(f"Before metrics calculation failed: {e}")

    # Apply pipeline
    enhanced_audio, after_metrics = apply_engine_pipeline(
        audio=audio,
        sample_rate=sample_rate,
        engine_id=engine_id,
        pipeline_config=pipeline_config,
        preset_name=preset_name,
        reference_audio=reference_audio
    )

    return enhanced_audio, before_metrics, after_metrics


def compare_enhancement(
    audio: np.ndarray,
    sample_rate: int,
    engine_id: str,
    pipeline_config: dict[str, Any] | None = None,
    preset_name: str = "default",
    reference_audio: str | None = None
) -> dict[str, Any]:
    """
    Compare audio before and after enhancement, returning improvement metrics.

    Args:
        audio: Input audio array
        sample_rate: Sample rate in Hz
        engine_id: Engine identifier
        pipeline_config: Optional custom pipeline configuration
        preset_name: Preset name if pipeline_config not provided
        reference_audio: Optional reference audio path

    Returns:
        Comparison dictionary with improvement metrics
    """
    _enhanced_audio, before_metrics, after_metrics = preview_engine_pipeline(
        audio=audio,
        sample_rate=sample_rate,
        engine_id=engine_id,
        pipeline_config=pipeline_config,
        preset_name=preset_name,
        reference_audio=reference_audio
    )

    comparison = {
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "improvements": {}
    }

    # Calculate improvements
    if before_metrics and after_metrics:
        for key in ["mos_score", "similarity", "naturalness", "snr_db"]:
            before_val = before_metrics.get(key)
            after_val = after_metrics.get(key)

            if before_val is not None and after_val is not None:
                improvement = after_val - before_val
                improvement_percent = (improvement / before_val) * 100 if before_val > 0 else 0.0

                comparison["improvements"][key] = {
                    "before": before_val,
                    "after": after_val,
                    "improvement": improvement,
                    "improvement_percent": improvement_percent
                }

    return comparison


def list_engine_presets(engine_id: str) -> list[str]:
    """
    List available presets for an engine.

    Args:
        engine_id: Engine identifier

    Returns:
        List of preset names
    """
    engine_presets = ENGINE_PIPELINE_PRESETS.get(engine_id, {})
    return list(engine_presets.keys())


def get_pipeline_description(
    engine_id: str,
    preset_name: str = "default"
) -> str:
    """
    Get description for a pipeline preset.

    Args:
        engine_id: Engine identifier
        preset_name: Preset name

    Returns:
        Description string
    """
    pipeline = get_engine_pipeline(engine_id, preset_name)
    return pipeline.get("description", "Quality enhancement pipeline")
