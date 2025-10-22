using System.Collections.Generic;

namespace VoiceStudio.UI.ViewModels
{
  // Single source of truth for mapping UX sliders/knobs → engine options
  public static class ParameterMap
  {
    // TTS/Clone engine option names expected by the service
    public static Dictionary<string,string> Map = new()
    {
      // UX control id       // service option key
      ["ArticulationPrecision"] = "articulation_strength",
      ["BreathStyle"]           = "breath_style",
      ["AccentMorphX"]          = "accent_blend_x",
      ["AccentMorphY"]          = "accent_blend_y",
      ["EmotionCurve"]          = "emotion_curve_json",
      ["PauseVariation"]        = "pause_variation",
      ["Stability"]             = "stability",
      ["VoiceAge"]              = "voice_age",
      ["Fatigue"]               = "vocal_fatigue",
      ["FormantShift"]          = "formant_shift",
      ["DeEsser"]               = "deesser",
      ["EQHigh"]                = "eq_high",
      ["Compressor"]            = "compressor",
      ["Proximity"]             = "proximity",
      ["LUFSTarget"]            = "lufs_target",
      ["PhonemeOverride"]       = "phoneme_overrides_json",
      ["OutputMode"]            = "output_mode",
      ["LatencyBudgetMs"]       = "latency_budget_ms"
    };
  }
}
