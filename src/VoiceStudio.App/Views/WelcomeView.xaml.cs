using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.App.Views;

public sealed partial class WelcomeView : ContentDialog
{
  public bool ShowOnStartup
  {
    get => ShowOnStartupCheckBox?.IsChecked ?? true;
    set
    {
      if (ShowOnStartupCheckBox != null)
      {
        ShowOnStartupCheckBox.IsChecked = value;
      }
    }
  }

  public WelcomeView()
  {
    this.InitializeComponent();
  }
}