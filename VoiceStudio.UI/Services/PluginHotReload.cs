using System;
using System.IO;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.UI.Services
{
  public class PluginHotReload : IDisposable
  {
    FileSystemWatcher _w;
    Action<string>? _on;
    public PluginHotReload(Action<string>? onChange)
    {
      _on = onChange;
      var pd = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
      var stamp = Path.Combine(pd, "VoiceStudio","plugins","registry","registry.json.stamp");
      Directory.CreateDirectory(Path.GetDirectoryName(stamp)!);
      _w = new FileSystemWatcher(Path.GetDirectoryName(stamp)!, Path.GetFileName(stamp));
      _w.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.CreationTime;
      _w.Changed += (_, __)=> _on?.Invoke("Plugin registry changed");
      _w.Created += (_, __)=> _on?.Invoke("Plugin registry updated");
      _w.EnableRaisingEvents = true;
    }
    public void Dispose(){ _w?.Dispose(); }
  }
}
