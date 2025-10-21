using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.ComponentModel;

namespace VoiceStudioWinUI.ViewModels
{
  public class TtsOptionsViewModel : INotifyPropertyChanged
  {
    public event PropertyChangedEventHandler PropertyChanged;
    void Notify(string n) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(n));

    // Engine & language
    string _engine = "xtts";
    public string Engine { get => _engine; set { _engine = value; Notify(nameof(Engine)); } }
    string _language = "en";
    public string Language { get => _language; set { _language = value; Notify(nameof(Language)); } }

    // AI / Prosody
    double _stability = 0.62;
    public double Stability { get => _stability; set { _stability = value; Notify(nameof(Stability)); } }

    double _articulation = 0.55;
    public double Articulation { get => _articulation; set { _articulation = value; Notify(nameof(Articulation)); } }

    double _pauseVariation = 0.15;
    public double PauseVariation { get => _pauseVariation; set { _pauseVariation = value; Notify(nameof(PauseVariation)); } }

    string _breathStyle = "Podcast";
    public string BreathStyle { get => _breathStyle; set { _breathStyle = value; Notify(nameof(BreathStyle)); } }

    string _voiceAge = "25";
    public string VoiceAge { get => _voiceAge; set { _voiceAge = value; Notify(nameof(VoiceAge)); } }

    double _fatigue = 0.0;
    public double Fatigue { get => _fatigue; set { _fatigue = value; Notify(nameof(Fatigue)); } }

    // Accent Morph (wheel -> 2D)
    double _accentX = 0.5;
    public double AccentX { get => _accentX; set { _accentX = value; Notify(nameof(AccentX)); } }
    double _accentY = 0.5;
    public double AccentY { get => _accentY; set { _accentY = value; Notify(nameof(AccentY)); } }

    // DSP / Output
    double _deesser = 0.35, _eqHigh=0.18, _compressor=0.5, _proximity=0.22;
    public double DeEsser { get => _deesser; set { _deesser=value; Notify(nameof(DeEsser)); } }
    public double EQHigh { get => _eqHigh; set { _eqHigh=value; Notify(nameof(EQHigh)); } }
    public double Compressor { get => _compressor; set { _compressor=value; Notify(nameof(Compressor)); } }
    public double Proximity { get => _proximity; set { _proximity=value; Notify(nameof(Proximity)); } }

    double _lufsTarget = -23.0;
    public double LUFSTarget { get => _lufsTarget; set { _lufsTarget=value; Notify(nameof(LUFSTarget)); } }

    string _outputMode = "Broadcast";
    public string OutputMode { get => _outputMode; set { _outputMode=value; Notify(nameof(OutputMode)); } }

    // Phoneme overrides / Emotion curve JSON (can be fed from dedicated editors)
    string _phonemeOverridesJson = "{}";
    public string PhonemeOverridesJson { get => _phonemeOverridesJson; set { _phonemeOverridesJson=value; Notify(nameof(PhonemeOverridesJson)); } }

    string _emotionCurveJson = "{\"neutral\":0.8,\"warmth\":0.2}";
    public string EmotionCurveJson { get => _emotionCurveJson; set { _emotionCurveJson=value; Notify(nameof(EmotionCurveJson)); } }

    public string ToOptionsJson()
    {
      var payload = new {
        engine = Engine,
        language = Language,
        stability = Stability,
        articulation_strength = Articulation,
        pause_variation = PauseVariation,
        breath_style = BreathStyle,
        voice_age = VoiceAge,
        vocal_fatigue = Fatigue,
        accent_blend_x = AccentX,
        accent_blend_y = AccentY,
        deesser = DeEsser,
        eq_high = EQHigh,
        compressor = Compressor,
        proximity = Proximity,
        lufs_target = LUFSTarget,
        output_mode = OutputMode,
        phoneme_overrides_json = SafeJson(PhonemeOverridesJson),
        emotion_curve_json = SafeJson(EmotionCurveJson)
      };
      var opts = new JsonSerializerOptions { WriteIndented=false, DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull };
      return JsonSerializer.Serialize(payload, opts);
    }

    static object SafeJson(string s)
    {
      try{ return JsonSerializer.Deserialize<object>(s); } catch{ return null; }
    }
  }
}
