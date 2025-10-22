using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.UI.Services;
using Windows.Storage.Pickers;
using WinRT.Interop;

namespace VoiceStudio.UI.Pages
{
  public sealed partial class CloneLabPage : Page
  {
    public CloneLabPage(){ this.InitializeComponent(); UpdatePreview(); }

    private nint GetHwnd()
    {
      var window = (Application.Current as App)?.GetWindow();
      return WindowNative.GetWindowHandle(window);
    }

    private async Task<string?> PickAudioAsync()
    {
      var p = new FileOpenPicker();
      InitializeWithWindow.Initialize(p, GetHwnd());
      p.FileTypeFilter.Add(".wav");
      p.FileTypeFilter.Add(".flac");
      p.FileTypeFilter.Add(".mp3");
      var f = await p.PickSingleFileAsync();
      return f?.Path;
    }

    private async void OnPickRef(object sender, RoutedEventArgs e)
    {
      var p = await PickAudioAsync();
      if(!string.IsNullOrWhiteSpace(p)){ RefAudio.Text = p; UpdatePreview(); }
    }

    private void UpdatePreview()
    {
      var prov = new {
        profile = ProfileName.Text ?? "",
        owner = OwnerName.Text ?? "",
        source = SourceKind.SelectedItem?.ToString() ?? "Self",
        consent = ConsentCheck.IsChecked == true,
        timestamp = DateTimeOffset.UtcNow,
        input_file = RefAudio.Text ?? "",
        provenance = new {
          tool="VoiceStudio", version="1.0.0", method="clone_profile_ref_audio_only"
        }
      };
      ProvPreview.Text = JsonSerializer.Serialize(prov, new JsonSerializerOptions{ WriteIndented=true });
    }

    private async void OnCreateProfile(object sender, RoutedEventArgs e)
    {
      try{
        if(ConsentCheck.IsChecked != true){ CloneStatus.Text="You must certify consent/rights."; return; }
        if(string.IsNullOrWhiteSpace(ProfileName.Text)){ CloneStatus.Text="Profile name required."; return; }
        if(string.IsNullOrWhiteSpace(RefAudio.Text) || !File.Exists(RefAudio.Text)){ CloneStatus.Text="Pick a valid reference audio."; return; }

        // choose target folder under %ProgramData%\VoiceStudio\profiles\<name>
        var baseDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "VoiceStudio", "profiles");
        Directory.CreateDirectory(baseDir);
        var outDir = Path.Combine(baseDir, string.Concat(ProfileName.Text.Split(Path.GetInvalidFileNameChars())));
        Directory.CreateDirectory(outDir);

        // write provenance
        var provPath = Path.Combine(outDir, "provenance.json");
        UpdatePreview();
        await File.WriteAllTextAsync(provPath, ProvPreview.Text);

        // call service CloneVoice(ref -> profile dir)
        using var cli = new EngineClient();
        var opts = JsonSerializer.Serialize(new {
          owner = OwnerName.Text ?? "",
          source = SourceKind.SelectedItem?.ToString() ?? "Self",
          consent = true
        });
        var job = await cli.CloneAsync(RefAudio.Text, outDir, opts);
        if(job.State=="done"){
          CloneStatus.Text=$"Profile created: {job.ArtifactPath}";
        }else{
          CloneStatus.Text=$"Clone failed: {job.Message}";
        }
      }catch(Exception ex){
        CloneStatus.Text="Error: "+ex.Message;
      }
    }
  }
}
