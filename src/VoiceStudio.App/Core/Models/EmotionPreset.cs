using System;
using System.Text.Json.Serialization;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Emotion preset model matching backend API.
  /// </summary>
  public class EmotionPreset
  {
    [JsonPropertyName("preset_id")]
    public string PresetId { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string? Description { get; set; }

    [JsonPropertyName("primary_emotion")]
    public string PrimaryEmotion { get; set; } = string.Empty;

    [JsonPropertyName("primary_intensity")]
    public double PrimaryIntensity { get; set; }

    [JsonPropertyName("secondary_emotion")]
    public string? SecondaryEmotion { get; set; }

    [JsonPropertyName("secondary_intensity")]
    public double SecondaryIntensity { get; set; }

    [JsonPropertyName("created_at")]
    public string CreatedAt { get; set; } = string.Empty;

    [JsonPropertyName("updated_at")]
    public string UpdatedAt { get; set; } = string.Empty;
  }

  /// <summary>
  /// Request to create an emotion preset.
  /// </summary>
  public class EmotionPresetCreateRequest
  {
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string? Description { get; set; }

    [JsonPropertyName("primary_emotion")]
    public string PrimaryEmotion { get; set; } = string.Empty;

    [JsonPropertyName("primary_intensity")]
    public double PrimaryIntensity { get; set; }

    [JsonPropertyName("secondary_emotion")]
    public string? SecondaryEmotion { get; set; }

    [JsonPropertyName("secondary_intensity")]
    public double SecondaryIntensity { get; set; }
  }

  /// <summary>
  /// Request to update an emotion preset.
  /// </summary>
  public class EmotionPresetUpdateRequest
  {
    [JsonPropertyName("name")]
    public string? Name { get; set; }

    [JsonPropertyName("description")]
    public string? Description { get; set; }

    [JsonPropertyName("primary_emotion")]
    public string? PrimaryEmotion { get; set; }

    [JsonPropertyName("primary_intensity")]
    public double? PrimaryIntensity { get; set; }

    [JsonPropertyName("secondary_emotion")]
    public string? SecondaryEmotion { get; set; }

    [JsonPropertyName("secondary_intensity")]
    public double? SecondaryIntensity { get; set; }
  }
}