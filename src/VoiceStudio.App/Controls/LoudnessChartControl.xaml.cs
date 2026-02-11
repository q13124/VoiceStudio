using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using System.Collections.Generic;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Loudness (LUFS) chart visualization control.
  ///
  /// DEFERRED FEATURE: Real-time loudness metering and visualization.
  /// Win2D/CanvasControl rendering disabled during Phase 0 for XAML compiler stability.
  /// This stub maintains binding surface compatibility.
  /// Full implementation planned for v1.1+ release.
  /// See: docs/governance/FUTURE_WORK.md
  /// </summary>
  public sealed partial class LoudnessChartControl : UserControl
  {
    public LoudnessChartControl()
    {
      InitializeComponent();
    }

    public List<double> Times { get; set; } = new();
    public List<double> LufsValues { get; set; } = new();
    public double? IntegratedLufs { get; set; }
    public double? PeakLufs { get; set; }
    public double Duration { get; set; }
    public Brush? LineColor { get; set; }
    public double PlaybackPosition { get; set; } = -1.0;
  }
}