using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Models;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// Macro node editor control.
  ///
  /// DEFERRED FEATURE: Node-based visual programming for macros.
  /// Win2D/CanvasControl rendering disabled during Phase 0 for XAML compiler stability.
  /// This stub maintains binding surface compatibility with MacroView.
  /// Full implementation planned for v1.1+ release.
  /// See: docs/governance/FUTURE_WORK.md
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