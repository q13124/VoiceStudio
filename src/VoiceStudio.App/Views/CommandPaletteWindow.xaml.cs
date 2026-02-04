using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Windows.Graphics;

namespace VoiceStudio.App.Views
{
  public sealed partial class CommandPaletteWindow : Window
  {
    public CommandPaletteWindow()
    {
      this.InitializeComponent();

      // Phase 0: XAML compiler stability - avoid Width/Height on <Window> in XAML.
      // Set initial size from code instead.
      this.AppWindow.Resize(new SizeInt32(900, 560));
    }
  }
}