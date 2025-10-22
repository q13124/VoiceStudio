using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Text.Json;

namespace VoiceStudio.UI.Controls
{
  public sealed partial class AlignmentLaneControl : UserControl
  {
    public class Row { public string Word{get;set;}=""; public double Start{get;set;} ; public double Dur{get;set;}; public double Pitch{get;set;}=0; public double Speed{get;set;}=0; public double Energy{get;set;}=0; }
    public ObservableCollection<Row> Items { get; } = new();
    public string OverridesJsonPath { get; private set; } = System.IO.Path.Combine(System.IO.Path.GetTempPath(),"voicestudio_prosody_overrides.json");

    public AlignmentLaneControl(){ InitializeComponent(); Grid.ItemsSource = Items; }

    public string ToOverridesJson(){
      var payload = new System.Collections.Generic.Dictionary<string,object>();
      var list = new System.Collections.Generic.List<object>();
      foreach(var r in Items){ list.Add(new { word=r.Word, t=r.Start, d=r.Dur, pitch=r.Pitch, speed=r.Speed, energy=r.Energy }); }
      payload["overrides"]=list;
      return JsonSerializer.Serialize(payload, new JsonSerializerOptions{ WriteIndented=true });
    }

    private async void OnSave(object s, RoutedEventArgs e){
      var json = ToOverridesJson();
      await File.WriteAllTextAsync(OverridesJsonPath, json);
      Status.Text=$"Saved: {OverridesJsonPath}";
    }

    private async void OnLoad(object s, RoutedEventArgs e){
      var dlg = new Windows.Storage.Pickers.FileOpenPicker();
      var hwnd = WinRT.Interop.WindowNative.GetWindowHandle((Application.Current as App)?.GetWindow());
      WinRT.Interop.InitializeWithWindow.Initialize(dlg, hwnd);
      dlg.FileTypeFilter.Add(".json");
      var f = await dlg.PickSingleFileAsync();
      if(f==null) return;
      var text = await Windows.Storage.FileIO.ReadTextAsync(f);
      try{
        var arr = JsonSerializer.Deserialize<System.Text.Json.Nodes.JsonArray>(text);
        Items.Clear();
        double last=0;
        foreach(var node in arr){
          string word = node?["word"]?.ToString() ?? "";
          double start = double.TryParse(node?["start"]?.ToString(), out var s0) ? s0 : last;
          double dur = double.TryParse(node?["dur"]?.ToString(), out var d0) ? d0 : 0.2;
          Items.Add(new Row{ Word=word, Start=start, Dur=dur, Pitch=0, Speed=0, Energy=0 });
          last = start+dur;
        }
        Status.Text=$"Loaded {Items.Count} words.";
      }catch(Exception ex){ Status.Text="Load error: "+ex.Message; }
    }
  }
}