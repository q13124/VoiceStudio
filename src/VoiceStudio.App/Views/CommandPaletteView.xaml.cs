using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.Services;
using VoiceStudio.App.ViewModels;

namespace VoiceStudio.App.Views
{
  public sealed partial class CommandPaletteView : UserControl
  {
    public CommandPaletteViewModel ViewModel { get; }

    public CommandPaletteView()
    {
      this.InitializeComponent();
      ViewModel = new CommandPaletteViewModel(
          ServiceProvider.GetPanelRegistry()
      );
      this.DataContext = ViewModel;
    }
  }
}