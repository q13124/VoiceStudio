using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudioWinUI.ViewModels;
using System.Text;

namespace VoiceStudioWinUI.Controls
{
  public sealed partial class MasteringRackControl : UserControl
  {
    public TtsOptionsViewModel VM { get; } = new();
    public MasteringRackControl()
    {
      this.InitializeComponent();
      this.DataContext = VM;
      OptionsPreview.Text = VM.ToOptionsJson();
      VM.PropertyChanged += (_, __) => OptionsPreview.Text = VM.ToOptionsJson();
    }

    private async void OnRenderClick(object sender, RoutedEventArgs e)
    {
      // Example: produce optionsJson; you can call gRPC Engine.Tts here.
      var json = VM.ToOptionsJson();
      ContentDialog d = new ContentDialog{
        XamlRoot = this.XamlRoot,
        Title="Current Tuning → optionsJson",
        Content=json,
        PrimaryButtonText="OK"
      };
      await d.ShowAsync();
      // TODO: EngineClient.Tts(text, dst, json, selectedVoiceProfile)
    }
  }
}
