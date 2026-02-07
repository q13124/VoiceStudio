using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace VoiceStudio.Core.Models
{
  public class VoiceProfile
  {
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Language { get; set; } = string.Empty;
    public string Emotion { get; set; } = string.Empty;
    public double QualityScore { get; set; }
    public List<string> Tags { get; set; } = new List<string>();

    /// <summary>
    /// URL or path to the profile's avatar image.
    /// </summary>
    public string? AvatarUrl { get; set; }

    /// <summary>
    /// URL or path to the reference audio used for voice cloning.
    /// </summary>
    public string? ReferenceAudioUrl { get; set; }

    /// <summary>
    /// Computed display initial for avatar fallback when no image is available.
    /// </summary>
    [JsonIgnore]
    public string DisplayInitial => string.IsNullOrEmpty(Name) ? "?" : Name[0].ToString().ToUpperInvariant();
  }
}