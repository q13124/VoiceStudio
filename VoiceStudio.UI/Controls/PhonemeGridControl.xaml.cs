using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.UI.ViewModels;

namespace VoiceStudio.UI.Controls
{
  public sealed partial class PhonemeGridControl : UserControl
  {
    public PhonemeGridViewModel VM { get; } = new();
    public PhonemeGridControl()
    {
      this.InitializeComponent();
      this.DataContext = VM;
      // seed some rows
      VM.Items.Add(new PhonemeItem{ Grapheme="th", IPA="θ", Override=""});
      VM.Items.Add(new PhonemeItem{ Grapheme="r", IPA="ɹ", Override=""});
      VM.Items.Add(new PhonemeItem{ Grapheme="a", IPA="ɑ", Override=""});
      Grid.ItemsSource = VM.Items;
    }

    private void OnCopy(object sender, RoutedEventArgs e)
    {
      var json = VM.ToJson();
      // Bridge: write to a well-known temp file the Mastering Rack can read if desired
      var path = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "voicestudio_phoneme_overrides.json");
      System.IO.File.WriteAllText(path, json);
      Status.Text = $"Wrote overrides: {path}";
    }
  }
}
