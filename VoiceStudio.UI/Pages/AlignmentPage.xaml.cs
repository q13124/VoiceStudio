using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.IO;
using VoiceStudio.UI.Services;

namespace VoiceStudio.UI.Pages
{
  public sealed partial class AlignmentPage : Page
  {
    public AlignmentPage(){ InitializeComponent(); }

    private async void OnRender(object s, RoutedEventArgs e)
    {
      try{
        var dst = Path.Combine(Path.GetTempPath(),"alignment_render.wav");
        var opts = System.Text.Json.JsonSerializer.Serialize(new {
          engine="xtts",
          prosody_overrides_json_path = Lane.OverridesJsonPath
        });
        using var cli = new EngineClient();
        var rep = await cli.TtsAsync(InputText.Text, "", dst, opts);
        if(rep.State=="done"){ Status.Text="Rendered: "+dst; }
        else { Status.Text="Error: "+rep.Message; }
      }catch(Exception ex){ Status.Text="Exception: "+ex.Message; }
    }
  }
}