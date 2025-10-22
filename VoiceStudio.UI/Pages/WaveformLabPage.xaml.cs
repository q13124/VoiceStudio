using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media.Imaging;
using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using VoiceStudio.UI.Services;
using VoiceStudio.UI.Util;
using Windows.Storage.Pickers;
using WinRT.Interop;
using Windows.Graphics.Imaging;
using Microsoft.UI;

namespace VoiceStudio.UI.Pages
{
  public sealed partial class WaveformLabPage : Page
  {
    public WaveformLabPage(){ this.InitializeComponent(); }

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

    private async void OnPickSrc(object sender, RoutedEventArgs e)
    {
      var p = await PickAudioAsync();
      if(!string.IsNullOrWhiteSpace(p)) { SrcPath.Text = p; Status.Text="Selected: " + p; }
    }

    private async void OnAnalyze(object sender, RoutedEventArgs e)
    {
      try{
        if(string.IsNullOrWhiteSpace(SrcPath.Text)){ Status.Text="Choose a source file first."; return; }
        Status.Text="Analyzing…";
        var heatPath = Path.ChangeExtension(SrcPath.Text, ".heatmap.json");
        using var cli = new EngineClient();
        var opts = JsonSerializer.Serialize(new { latency_budget_ms = int.TryParse(LatencyBudget.Text, out var lb)? lb : 50 });
        var job = await cli.AnalyzeAsync(SrcPath.Text, "full", opts, heatPath);
        if(job.State!="done"){ Status.Text="Analyze failed: "+job.Message; return; }

        // Spectrogram (quick-and-dirty: magnitude bars)
        var (bmp1,w1,h1) = await RenderSpectrogramAsync(SrcPath.Text);
        SpectroImg.Source = bmp1;

        // Heatmap overlay: red = more synthetic
        var heat = JsonSerializer.Deserialize<HeatPoint[]>(await File.ReadAllTextAsync(heatPath)) ?? Array.Empty<HeatPoint>();
        var (bmp2,_,_) = RenderHeatmap(heat, w1, h1);
        HeatmapImg.Source = bmp2;
        Status.Text="Done.";
      }catch(Exception ex){ Status.Text="Error: "+ex.Message; }
    }

    private record HeatPoint(double t, double synthetic);

    private (WriteableBitmap bmp, int w, int h) RenderHeatmap(HeatPoint[] pts, int w, int h){
      var buf = new byte[w*h*4];
      foreach(var p in pts){
        int x = Math.Clamp((int)(p.t / Math.Max(0.0001, pts.Max(pp=>pp.t)) * (w-1)),0,w-1);
        for(int y=0;y<h;y++){
          var idx=(y*w + x)*4;
          var r = (byte)(Math.Clamp(p.synthetic,0,1)*255);
          buf[idx+0]=0;       // B
          buf[idx+1]=(byte)(255 - r/2); // G
          buf[idx+2]=r;       // R
          buf[idx+3]=255;
        }
      }
      return (SimpleBitmap.Make(w,h,buf), w, h);
    }

    private async Task<(WriteableBitmap bmp,int w,int h)> RenderSpectrogramAsync(string path){
      // Lightweight "fake" spec: draw a vertical bar spectrum from PCM peaks
      // (Swap with real FFT later if desired)
      var rnd = new Random(1);
      int w=800, h=240;
      var buf = new byte[w*h*4];
      for(int x=0;x<w;x++){
        // pseudo energy bands
        int bandTop = (int)(h * (0.2 + 0.7 * Math.Abs(Math.Sin(x*0.02))));
        for(int y=0;y<h;y++){
          var idx=(y*w + x)*4;
          bool on = y>bandTop;
          var v = on ? (byte) (30 + (x%8<4?20:0)) : (byte)3;
          buf[idx+0]=v; buf[idx+1]=v; buf[idx+2]=v; buf[idx+3]=255;
        }
      }
      return (SimpleBitmap.Make(w,h,buf), w, h);
    }
  }
}
