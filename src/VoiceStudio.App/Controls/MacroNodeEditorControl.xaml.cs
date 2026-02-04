using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Macro node editor control.
  ///
  /// NOTE: Win2D/CanvasControl rendering is temporarily disabled to restore XAML compiler stability
  /// during Phase 0 (build reliability). This stub keeps the bindings surface used by MacroView.
  /// </summary>
  public sealed partial class MacroNodeEditorControl : UserControl
  {
    public static readonly DependencyProperty MacroProperty =
        DependencyProperty.Register(
            nameof(Macro),
            typeof(Macro),
            typeof(MacroNodeEditorControl),
            new PropertyMetadata(null));

    public Macro? Macro
    {
      get => (Macro?)GetValue(MacroProperty);
      set => SetValue(MacroProperty, value);
    }

    public static readonly DependencyProperty HasSelectedNodeProperty =
        DependencyProperty.Register(
            nameof(HasSelectedNode),
            typeof(bool),
            typeof(MacroNodeEditorControl),
            new PropertyMetadata(false));

    public bool HasSelectedNode
    {
      get => (bool)GetValue(HasSelectedNodeProperty);
      private set => SetValue(HasSelectedNodeProperty, value);
    }

    public static readonly DependencyProperty HasUnsavedChangesProperty =
        DependencyProperty.Register(
            nameof(HasUnsavedChanges),
            typeof(bool),
            typeof(MacroNodeEditorControl),
            new PropertyMetadata(false));

    public bool HasUnsavedChanges
    {
      get => (bool)GetValue(HasUnsavedChangesProperty);
      private set => SetValue(HasUnsavedChangesProperty, value);
    }

    public MacroNodeEditorControl()
    {
      InitializeComponent();
    }
  }
}