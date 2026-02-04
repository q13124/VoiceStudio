using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Automation curves editor control.
  ///
  /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
  /// during Phase 0 (build reliability). This stub preserves basic selection/binding surface.
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