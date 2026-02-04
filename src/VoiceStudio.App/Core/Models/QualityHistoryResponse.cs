using System.Collections.Generic;

namespace VoiceStudio.Core.Models
{
  /// <summary>
  /// Response containing quality history entries for a voice profile.
  /// </summary>
  public class QualityHistoryResponse
  {
    /// <summary>
    /// List of quality history entries.
    /// </summary>
    public List<QualityHistoryEntry> Entries { get; set; } = new();

    /// <summary>
    /// Total number of entries.
    /// </summary>
    public int Total { get; set; }
  }
}