using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Controls
{
  public sealed partial class FloatingWindowHost : UserControl
  {
    public static readonly DependencyProperty PanelIdProperty =
        DependencyProperty.Register(
            nameof(PanelId),
            typeof(string),
            typeof(FloatingWindowHost),
            new PropertyMetadata(string.Empty));

    public static new readonly DependencyProperty ContentProperty =
        DependencyProperty.Register(
            nameof(Content),
            typeof(UIElement),
            typeof(FloatingWindowHost),
            new PropertyMetadata(null, OnContentChanged));

    public string PanelId
    {
      get => (string)GetValue(PanelIdProperty);
      set => SetValue(PanelIdProperty, value);
    }

    public new UIElement? Content
    {
      get => (UIElement?)GetValue(ContentProperty);
      set => SetValue(ContentProperty, value);
    }

    public FloatingWindowHost()
    {
      this.InitializeComponent();
    }

    private static void OnContentChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
      if (d is FloatingWindowHost host)
      {
        host.ContentPresenter.Content = e.NewValue;
      }
    }
  }
}