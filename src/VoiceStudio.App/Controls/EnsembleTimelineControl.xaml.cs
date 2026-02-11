using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Ensemble timeline control.
  ///
  /// DEFERRED FEATURE: Multi-voice ensemble timeline editing.
  /// Rendering/interaction disabled during Phase 0 for XAML compiler stability.
  /// This stub maintains binding surface compatibility.
  /// Full implementation planned for v1.1+ release.
  /// See: docs/governance/FUTURE_WORK.md
  /// </summary>
  public sealed partial class EnsembleTimelineControl : UserControl
  {
    public EnsembleTimelineControl()
    {
      InitializeComponent();
    }

    public string MixMode { get; set; } = "sequential";

    /// <summary>
    /// Sets the timeline blocks (placeholder implementation).
    /// </summary>
    public void SetTimelineBlocks(System.Collections.Generic.List<VoiceTimelineBlock> _)
    {
      // Note: Implement timeline block rendering
      // This is a placeholder to restore compilation
    }
  }
}