import json, os, torch

def device_auto():
    # Prefer CUDA, then CPU
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

def mp_float(opts, key, default=None):
    try:
        return float(opts.get(key, default))
    except Exception:
        return default

def mp_str(opts, key, default=None):
    v = opts.get(key, default)
    return None if v is None else str(v)

def parse_options(options_json:str|None) -> dict:
    try:
        return json.loads(options_json or "{}")
    except Exception:
        return {}

def apply_parameter_map(engine_kwargs:dict, options:dict):
    """
    Map UI ParameterMap keys -> engine kwargs (generic examples).
    You already exposed these keys via VoiceStudio.UI.ViewModels.ParameterMap.
    """
    # AI/Prosody controls
    if "stability" in options:         engine_kwargs["stability"] = mp_float(options, "stability", 0.6)
    if "articulation_strength" in options or "ArticulationPrecision" in options:
        engine_kwargs["articulation"] = mp_float(options, "articulation_strength", mp_float(options, "ArticulationPrecision", 0.6))
    if "pause_variation" in options:   engine_kwargs["pause_variation"] = mp_float(options, "pause_variation", 0.15)
    if "voice_age" in options:         engine_kwargs["voice_age"] = mp_str(options, "voice_age", "25")
    if "vocal_fatigue" in options:     engine_kwargs["fatigue"] = mp_float(options, "vocal_fatigue", 0.0)
    if "breath_style" in options:      engine_kwargs["breath_style"] = mp_str(options, "breath_style", "Neutral")
    if "emotion_curve_json" in options:
        engine_kwargs["emotion_curve"] = json.loads(options["emotion_curve_json"]) if isinstance(options["emotion_curve_json"], str) else options["emotion_curve_json"]
    # Output & DSP (service may apply post-fx; we keep as metadata here)
    if "lufs_target" in options:       engine_kwargs["lufs_target"] = mp_float(options, "lufs_target", -23.0)
    if "output_mode" in options:       engine_kwargs["output_mode"] = mp_str(options, "output_mode", "Broadcast")
    # Accent morphing
    if "accent_blend_x" in options:    engine_kwargs["accent_x"] = mp_float(options, "accent_blend_x", 0.5)
    if "accent_blend_y" in options:    engine_kwargs["accent_y"] = mp_float(options, "accent_blend_y", 0.5)
    # Phoneme overrides
    if "phoneme_overrides_json" in options:
        engine_kwargs["phoneme_overrides"] = json.loads(options["phoneme_overrides_json"]) if isinstance(options["phoneme_overrides_json"], str) else options["phoneme_overrides_json"]
    return engine_kwargs
