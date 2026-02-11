using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Animation;
using Windows.UI.ViewManagement;

namespace VoiceStudio.App.Controls;

public sealed partial class LoadingOverlay : UserControl
{
  private static readonly UISettings UiSettings = new();

  public static readonly DependencyProperty IsLoadingProperty =
      DependencyProperty.Register(
          nameof(IsLoading),
          typeof(bool),
          typeof(LoadingOverlay),
          new PropertyMetadata(false, OnIsLoadingChanged));

  public static readonly DependencyProperty LoadingMessageProperty =
      DependencyProperty.Register(
          nameof(LoadingMessage),
          typeof(string),
          typeof(LoadingOverlay),
          new PropertyMetadata("Loading..."));

  public bool IsLoading
  {
    get => (bool)GetValue(IsLoadingProperty);
    set => SetValue(IsLoadingProperty, value);
  }

  public string LoadingMessage
  {
    get => (string)GetValue(LoadingMessageProperty);
    set => SetValue(LoadingMessageProperty, value);
  }

  public LoadingOverlay()
  {
    this.InitializeComponent();
  }

  private static void OnIsLoadingChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
  {
    if (d is LoadingOverlay overlay)
    {
      if (overlay.IsLoading)
      {
        overlay.Visibility = Visibility.Visible;
        overlay.PlayFadeInAnimation();
      }
      else
      {
        overlay.Visibility = Visibility.Collapsed;
      }
    }
  }

  private void PlayFadeInAnimation()
  {
    // Check system animation preference - skip animation if user prefers reduced motion
    if (!UiSettings.AnimationsEnabled)
    {
      LoadingGrid.Opacity = 1;
      return;
    }

    // Trigger the FadeInAnimation storyboard
    if (Resources.TryGetValue("FadeInAnimation", out var resource) && resource is Storyboard fadeIn)
    {
      Storyboard.SetTarget(fadeIn, LoadingGrid);
      fadeIn.Begin();
    }
    else
    {
      // Fallback: just set opacity directly
      LoadingGrid.Opacity = 1;
    }
  }
}