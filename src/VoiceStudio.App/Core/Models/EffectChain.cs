using System;
using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Parameter for an audio effect.
  /// </summary>
  public class EffectParameter
  {
    public string Name { get; set; } = string.Empty;
    public double Value { get; set; }
    public double MinValue { get; set; }
    public double MaxValue { get; set; } = 1.0;
    public string? Unit { get; set; } // "dB", "Hz", "ms", etc.
  }

  /// <summary>
  /// An audio effect in a chain.
  /// </summary>
  public class Effect
  {
    public string Id { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty; // "eq", "compressor", "reverb", "delay", "filter", "normalize", "denoise", etc.
    public string Name { get; set; } = string.Empty;
    public bool Enabled { get; set; } = true;
    public int Order { get; set; } // Position in chain (0 = first)
    public List<EffectParameter> Parameters { get; set; } = new();
  }

  /// <summary>
  /// A chain of audio effects.
  /// </summary>
  public class EffectChain
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string ProjectId { get; set; } = string.Empty;
    public List<Effect> Effects { get; set; } = new();
    public DateTime Created { get; set; }
    public DateTime Modified { get; set; }
  }

  /// <summary>
  /// A preset configuration for an effect.
  /// </summary>
  public class EffectPreset
  {
    public string Id { get; set; } = string.Empty;
    public string EffectType { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public List<EffectParameter> Parameters { get; set; } = new();
    public DateTime Created { get; set; }
    public DateTime Modified { get; set; }
  }
}