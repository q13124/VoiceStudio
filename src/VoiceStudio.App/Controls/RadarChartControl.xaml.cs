using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Radar/spider chart visualization control.
  ///
  /// DEFERRED FEATURE: Multi-axis quality comparison visualization.
  /// Win2D/CanvasControl rendering disabled during Phase 0 for XAML compiler stability.
  /// This stub maintains binding surface compatibility.
  /// Full implementation planned for v1.1+ release.
  /// See: docs/governance/FUTURE_WORK.md
  /// </summary>
  public sealed partial class RadarChartControl : UserControl
  {
    public RadarChartControl()
    {
      InitializeComponent();
    }

    public RadarData? Data { get; set; }
    public Brush? RadarColor { get; set; }
  }
}