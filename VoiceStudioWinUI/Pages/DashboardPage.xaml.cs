using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System.Diagnostics;
using System.IO;

namespace VoiceStudioWinUI.Pages
{
  public sealed partial class DashboardPage : Page
  {
    public DashboardPage(){ this.InitializeComponent(); }

    private async void OnGenSbom(object sender, RoutedEventArgs e)
    {
      var root = Directory.GetParent(Directory.GetParent(System.AppContext.BaseDirectory!)!.FullName)!.Parent!.FullName;
      var script = Path.Combine(root, "scripts", "Generate-SBOM.ps1");
      if(!File.Exists(script)){
        var d = new ContentDialog{ XamlRoot = this.XamlRoot, Title="SBOM", Content="Generate-SBOM.ps1 not found.", PrimaryButtonText="OK" };
        await d.ShowAsync(); return;
      }
      var psi = new ProcessStartInfo("powershell.exe", $"-ExecutionPolicy Bypass -File `"{script}`""){ UseShellExecute=true, Verb="runas" };
      Process.Start(psi);
    }

    private async void OnOpenSbomFolder(object sender, RoutedEventArgs e)
    {
      var dir = Path.Combine(System.Environment.GetFolderPath(System.Environment.SpecialFolder.CommonApplicationData), "VoiceStudio", "artifacts", "sbom");
      Directory.CreateDirectory(dir);
      Process.Start("explorer.exe", dir);
      var d = new ContentDialog{ XamlRoot = this.XamlRoot, Title="SBOM", Content=$"Opened: {dir}", PrimaryButtonText="OK" };
      await d.ShowAsync();
    }
  }
}
