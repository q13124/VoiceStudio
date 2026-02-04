using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Services;

namespace VoiceStudio.App.Controls
{
  /// <summary>
  /// User cursor indicator control showing a user's cursor position.
  /// Implements IDEA 25: Real-Time Collaboration Indicators.
  /// </summary>
  public sealed partial class UserCursorIndicator : UserControl
  {
    public UserCursor? Cursor
    {
      get => (UserCursor?)GetValue(CursorProperty);
      set => SetValue(CursorProperty, value);
    }

    public static readonly DependencyProperty CursorProperty =
        DependencyProperty.Register(nameof(Cursor), typeof(UserCursor), typeof(UserCursorIndicator),
            new PropertyMetadata(null, OnCursorChanged));

    public UserCursorIndicator()
    {
      this.InitializeComponent();
    }

    private static void OnCursorChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is UserCursorIndicator indicator && e.NewValue is UserCursor cursor)
      {
        indicator.DataContext = cursor;
      }
    }
  }
}