using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using UltraClone.EngineService.routing;

namespace UltraClone.EngineService
{
  public static class RoutingAdapter
  {
    static string Cfg => Path.Combine(AppContext.BaseDirectory, "..","..","config","engines.config.json");
    public static (string engine, string[] chain) Choose(string lang="en", string needQuality="high", string needLatency="normal")
    {
      var cfgPath = Path.GetFullPath(Cfg);
      var router  = new EngineRouter(cfgPath);
      var (engine, chain) = router.Choose(lang, needQuality, needLatency);
      return (engine, chain.ToArray());
    }

    public static (bool ok, string engine, string dst, string log) Dispatch(string text, string dst, string[] chain, string optsJson)
    {
      var pd = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
      var py = Path.Combine(pd,"VoiceStudio","pyenv","Scripts","python.exe");
      var op = Path.Combine(pd,"VoiceStudio","workers","ops","engine_dispatch.py");
      var psi = new ProcessStartInfo(py, $"{op} --text \"{text.Replace("\"","\\\"")}\" --dst \"{dst}\" --chain \"{string.Join(",", chain)}\" --opts \"{optsJson.Replace("\"","\\\"")}\"");
      psi.UseShellExecute=true;
      var p = Process.Start(psi);
      p.WaitForExit();
      var ok  = File.Exists(dst) && p.ExitCode==0;
      return (ok, chain.Length>0? chain[0] : "", dst, $"exit={p.ExitCode}");
    }
  }
}
