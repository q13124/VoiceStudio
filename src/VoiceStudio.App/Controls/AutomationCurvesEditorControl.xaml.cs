using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Automation curves editor control.
  ///
  /// DEFERRED FEATURE: Multi-track curve editing for audio automation.
  /// Win2D/CanvasControl rendering disabled during Phase 0 for XAML compiler stability.
  /// This stub maintains binding surface compatibility.
  /// Full implementation planned for v1.1+ release.
  /// See: docs/governance/FUTURE_WORK.md
  /// </summary>
  public sealed partial class AutomationCurvesEditorControl : UserControl
  {
    public static readonly DependencyProperty SelectedTrackIdProperty =
        DependencyProperty.Register(
            nameof(SelectedTrackId),
            typeof(string),
            typeof(AutomationCurvesEditorControl),
            new PropertyMetadata(string.Empty));

    public static readonly DependencyProperty SelectedCurveProperty =
        DependencyProperty.Register(
            nameof(SelectedCurve),
            typeof(AutomationCurve),
            typeof(AutomationCurvesEditorControl),
            new PropertyMetadata(null));

    public string SelectedTrackId
    {
      get => (string)GetValue(SelectedTrackIdProperty);
      set => SetValue(SelectedTrackIdProperty, value);
    }

    public AutomationCurve? SelectedCurve
    {
      get => (AutomationCurve?)GetValue(SelectedCurveProperty);
      set => SetValue(SelectedCurveProperty, value);
    }

    public AutomationCurvesEditorControl()
    {
      InitializeComponent();
    }
  }
}