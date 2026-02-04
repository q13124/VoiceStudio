using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Automation curve editor control.
  ///
  /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
  /// during Phase 0 (build reliability). This stub keeps the bindings surface used by panels.
  /// </summary>
  public sealed partial class AutomationCurveEditorControl : UserControl
  {
    public static readonly DependencyProperty CurveProperty =
        DependencyProperty.Register(
            nameof(Curve),
            typeof(AutomationCurve),
            typeof(AutomationCurveEditorControl),
            new PropertyMetadata(null));

    public AutomationCurve? Curve
    {
      get => (AutomationCurve?)GetValue(CurveProperty);
      set => SetValue(CurveProperty, value);
    }

    public static readonly DependencyProperty TrackIdProperty =
        DependencyProperty.Register(
            nameof(TrackId),
            typeof(string),
            typeof(AutomationCurveEditorControl),
            new PropertyMetadata(null));

    public string? TrackId
    {
      get => (string?)GetValue(TrackIdProperty);
      set => SetValue(TrackIdProperty, value);
    }

    public bool HasSelectedPoint { get; private set; }

    public AutomationCurveEditorControl()
    {
      InitializeComponent();
    }

    /// <summary>
    /// Loads curves asynchronously (placeholder implementation).
    /// </summary>
    public System.Threading.Tasks.Task LoadCurvesAsync()
    {
      // Note: Implement curve loading
      // This is a placeholder to restore compilation
      return System.Threading.Tasks.Task.CompletedTask;
    }
  }
}