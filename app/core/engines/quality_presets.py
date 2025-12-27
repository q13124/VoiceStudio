"""
Quality Presets for Voice Cloning
Unified quality preset system across all engines
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Quality presets with comprehensive settings
QUALITY_PRESETS = {
    "fast": {
        "description": "Fast synthesis with good quality",
        "target_metrics": {
            "mos_score": 3.5,
            "similarity": 0.75,
            "naturalness": 0.70,
            "snr_db": 25.0,
        },
        "engine_preference": "xtts",
        "enhance_quality": False,
        "enhance_prosody": False,
        "denoise_strength": 0.5,
        "spectral_enhance": False,
        "preserve_formants": False,
        "remove_artifacts": True,
    },
    "standard": {
        "description": "Balanced quality and speed",
        "target_metrics": {
            "mos_score": 4.0,
            "similarity": 0.80,
            "naturalness": 0.75,
            "snr_db": 28.0,
        },
        "engine_preference": "chatterbox",
        "enhance_quality": True,
        "enhance_prosody": False,
        "denoise_strength": 0.7,
        "spectral_enhance": True,
        "preserve_formants": True,
        "remove_artifacts": True,
    },
    "high": {
        "description": "High quality synthesis",
        "target_metrics": {
            "mos_score": 4.3,
            "similarity": 0.85,
            "naturalness": 0.80,
            "snr_db": 30.0,
        },
        "engine_preference": "chatterbox",
        "enhance_quality": True,
        "enhance_prosody": False,
        "denoise_strength": 0.8,
        "spectral_enhance": True,
        "preserve_formants": True,
        "remove_artifacts": True,
    },
    "ultra": {
        "description": "Ultra-high quality synthesis",
        "target_metrics": {
            "mos_score": 4.5,
            "similarity": 0.90,
            "naturalness": 0.85,
            "snr_db": 32.0,
        },
        "engine_preference": "tortoise",
        "enhance_quality": True,
        "enhance_prosody": True,
        "denoise_strength": 0.9,
        "spectral_enhance": True,
        "preserve_formants": True,
        "remove_artifacts": True,
    },
    "professional": {
        "description": "Professional studio quality",
        "target_metrics": {
            "mos_score": 4.5,
            "similarity": 0.90,
            "naturalness": 0.88,
            "snr_db": 35.0,
        },
        "engine_preference": "tortoise",
        "enhance_quality": True,
        "enhance_prosody": True,
        "denoise_strength": 0.95,
        "spectral_enhance": True,
        "preserve_formants": True,
        "remove_artifacts": True,
    },
}

# Engine-specific quality preset mappings
ENGINE_PRESET_MAPPINGS = {
    "tortoise": {
        "fast": "ultra_fast",
        "standard": "fast",
        "high": "standard",
        "ultra": "high_quality",
        "professional": "ultra_quality",
    },
    "xtts": {
        "fast": None,  # Use default
        "standard": None,
        "high": None,
        "ultra": None,
        "professional": None,
    },
    "chatterbox": {
        "fast": None,
        "standard": None,
        "high": None,
        "ultra": None,
        "professional": None,
    },
}


def get_quality_preset(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get quality preset configuration.
    
    Args:
        preset_name: Preset name ("fast", "standard", "high", "ultra", "professional")
    
    Returns:
        Preset configuration dictionary or None if not found
    """
    return QUALITY_PRESETS.get(preset_name.lower())


def get_engine_preset(
    engine_name: str, quality_preset: str
) -> Optional[str]:
    """
    Get engine-specific preset name for a quality preset.
    
    Args:
        engine_name: Engine name ("tortoise", "xtts", "chatterbox")
        quality_preset: Quality preset name
    
    Returns:
        Engine-specific preset name or None
    """
    engine_mappings = ENGINE_PRESET_MAPPINGS.get(engine_name.lower())
    if not engine_mappings:
        return None

    return engine_mappings.get(quality_preset.lower())


def get_synthesis_params_from_preset(
    preset_name: str, engine_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get synthesis parameters from quality preset.
    
    Args:
        preset_name: Quality preset name
        engine_name: Optional engine name for engine-specific presets
    
    Returns:
        Dictionary of synthesis parameters
    """
    preset = get_quality_preset(preset_name)
    if not preset:
        logger.warning(f"Unknown quality preset: {preset_name}")
        preset = QUALITY_PRESETS["standard"]

    params = {
        "enhance_quality": preset["enhance_quality"],
        "calculate_quality": True,
        "denoise_strength": preset.get("denoise_strength", 0.7),
    }

    # Add advanced enhancement parameters if available
    if preset.get("spectral_enhance"):
        params["spectral_enhance"] = True
    if preset.get("preserve_formants"):
        params["preserve_formants"] = True
    if preset.get("enhance_prosody"):
        params["enhance_prosody"] = True
    if preset.get("remove_artifacts"):
        params["remove_artifacts"] = True

    # Add engine-specific preset if available
    if engine_name:
        engine_preset = get_engine_preset(engine_name, preset_name)
        if engine_preset:
            params["quality_preset"] = engine_preset

    return params


def list_quality_presets() -> Dict[str, Dict[str, Any]]:
    """
    List all available quality presets.
    
    Returns:
        Dictionary of preset names to preset configurations
    """
    return QUALITY_PRESETS.copy()


def get_preset_description(preset_name: str) -> str:
    """
    Get description for a quality preset.
    
    Args:
        preset_name: Preset name
    
    Returns:
        Preset description
    """
    preset = get_quality_preset(preset_name)
    if preset:
        return preset.get("description", "")
    return ""


def get_preset_target_metrics(preset_name: str) -> Dict[str, float]:
    """
    Get target quality metrics for a preset.
    
    Args:
        preset_name: Preset name
    
    Returns:
        Dictionary of target metrics
    """
    preset = get_quality_preset(preset_name)
    if preset:
        return preset.get("target_metrics", {}).copy()
    return {}

